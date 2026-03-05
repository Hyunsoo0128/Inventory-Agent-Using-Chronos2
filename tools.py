"""Tools for inventory management system."""
import json
import uuid
import numpy as np
import pandas as pd
from io import StringIO, BytesIO
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from strands import tool
from config import sagemaker_runtime, s3_client, ENDPOINT_NAME, S3_BUCKET_NAME, REGION

@tool
def load_sales_from_s3(product_id: str) -> dict:
    """S3에서 판매 데이터 로드"""
    response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=f"sales/{product_id}.csv")
    csv_text = response['Body'].read().decode('utf-8')
    df = pd.read_csv(StringIO(csv_text))
    return {"data": df.to_dict('records'), "product_id": product_id}

@tool
def load_inventory_from_s3() -> dict:
    """S3에서 재고 데이터 로드"""
    response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key="inventory/current_stock.json")
    return {"inventory": json.loads(response['Body'].read().decode('utf-8'))}

@tool
def load_product_config_from_s3() -> dict:
    """S3에서 상품 설정 로드"""
    response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key="config/product_config.json")
    return {"config": json.loads(response['Body'].read().decode('utf-8'))}

@tool
def analyze_sales_data(sales_data: str) -> dict:
    """판매 데이터 분석 및 Chronos2 입력 형식으로 변환"""
    data = json.loads(sales_data) if isinstance(sales_data, str) else sales_data
    df = pd.DataFrame(data['data'])
    
    target_col = 'sales'
    covariate_cols = ['promotion', 'day_of_week', 'is_weekend', 'price']
    
    target_data = df[target_col].dropna().tolist()
    input_data = {"target": target_data, "item_id": data['product_id']}
    
    past_data = {col: df[col].iloc[:len(target_data)].tolist() for col in covariate_cols}
    input_data["past_covariates"] = past_data
    
    future_start = len(target_data)
    if future_start < len(df):
        future_data = {col: df[col].iloc[future_start:].dropna().tolist() for col in covariate_cols}
        if future_data:
            input_data["future_covariates"] = future_data
    
    prediction_length = len(df) - len(target_data)
    return {"inputs": [input_data], "prediction_length": prediction_length, "product_id": data['product_id']}

@tool
def predict_demand(analysis_result: str) -> dict:
    """Chronos2 모델로 수요 예측"""
    result = json.loads(analysis_result) if isinstance(analysis_result, str) else analysis_result
    
    payload = {
        "inputs": result["inputs"],
        "parameters": {"prediction_length": result["prediction_length"]}
    }
    
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType="application/json",
        Body=json.dumps(payload)
    )
    
    predictions = json.loads(response["Body"].read().decode())
    return {"predictions": predictions, "analysis": result}

@tool
def calculate_order_quantity(forecast_data: str, inventory_data: str, config_data: str) -> dict:
    """발주량 계산"""
    forecast = json.loads(forecast_data) if isinstance(forecast_data, str) else forecast_data
    inventory = json.loads(inventory_data) if isinstance(inventory_data, str) else inventory_data
    config = json.loads(config_data) if isinstance(config_data, str) else config_data
    
    orders = {}
    for pred in forecast["predictions"]["predictions"]:
        pid = pred["item_id"]
        inv = inventory["inventory"][pid]
        cfg = config["config"][pid]
        
        forecast_mean = pred["mean"]
        lead_time = cfg["lead_time_days"]
        safety_stock = cfg["safety_stock"]
        current_stock = inv["current_stock"]
        min_order = cfg["min_order_quantity"]
        
        total_demand = sum(forecast_mean[:lead_time])
        required = total_demand + safety_stock
        order_qty = max(0, required - current_stock)
        
        if order_qty > 0 and order_qty < min_order:
            order_qty = min_order
        
        orders[pid] = {
            "product_name": cfg["name"],
            "forecast_demand": [round(v, 2) for v in forecast_mean],
            "total_demand_during_lead_time": round(total_demand, 2),
            "current_stock": current_stock,
            "safety_stock": safety_stock,
            "order_quantity": round(order_qty, 2),
            "supplier": cfg["supplier"],
            "reason": f"리드타임 {lead_time}일 수요 + 안전재고 확보"
        }
    
    return orders

@tool
def validate_order_decision(order_data: str, config_data: str) -> dict:
    """발주 결정 검증"""
    orders = json.loads(order_data) if isinstance(order_data, str) else order_data
    config = json.loads(config_data) if isinstance(config_data, str) else config_data
    
    validation = {}
    for pid, order in orders.items():
        cfg = config["config"][pid]
        new_stock = order["current_stock"] + order["order_quantity"]
        
        is_valid = new_stock <= cfg["warehouse_capacity"]
        validation[pid] = {
            "approved": is_valid,
            "new_stock_level": round(new_stock, 2),
            "warehouse_capacity": cfg["warehouse_capacity"],
            "utilization": round(new_stock / cfg["warehouse_capacity"] * 100, 2),
            "warning": None if is_valid else "창고 용량 초과"
        }
    
    return validation

@tool
def visualize_forecast(forecast_data: str) -> str:
    """예측 결과 시각화"""
    forecast = json.loads(forecast_data) if isinstance(forecast_data, str) else forecast_data
    
    results = []
    for pred in forecast["predictions"]["predictions"]:
        pid = pred["item_id"]
        original = next(item for item in forecast["analysis"]["inputs"] if item["item_id"] == pid)
        target_data = original["target"]
        
        plt.figure(figsize=(14, 7))
        
        hist_x = range(len(target_data))
        plt.plot(hist_x, target_data, "o-", label="실제 판매", color="blue", linewidth=2, markersize=6)
        
        forecast_start = len(target_data)
        forecast_x = range(forecast_start, forecast_start + len(pred["mean"]))
        plt.plot(forecast_x, pred["mean"], "s-", label="예측 수요", color="red", linewidth=2, markersize=6)
        plt.fill_between(forecast_x, pred["0.1"], pred["0.9"], alpha=0.3, color="red", label="80% 신뢰구간")
        
        plt.axvline(x=forecast_start-0.5, color='gray', linestyle='--', linewidth=1.5, label='예측 시작점')
        
        plt.title(f"{pid} 수요 예측 (Chronos2)", fontsize=16, fontweight='bold', pad=20)
        plt.xlabel("일자 (Day)", fontsize=13)
        plt.ylabel("판매량 (Units)", fontsize=13)
        plt.legend(fontsize=11, loc='best')
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
        buf.seek(0)
        plt.close()
        
        file_key = f"forecasts/{pid}_{uuid.uuid4().hex[:8]}.png"
        s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=file_key, Body=buf.getvalue(), ContentType="image/png")
        
        s3_url = f"https://{S3_BUCKET_NAME}.s3.{REGION}.amazonaws.com/{file_key}"
        results.append(f"![{pid} Forecast]({s3_url})")
    
    return "\n\n".join(results)

@tool
def save_order_result_to_s3(order_data: str, validation_data: str) -> dict:
    """발주 결과를 S3에 저장"""
    orders = json.loads(order_data) if isinstance(order_data, str) else order_data
    validation = json.loads(validation_data) if isinstance(validation_data, str) else validation_data
    
    result = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "orders": orders,
        "validation": validation
    }
    
    file_key = f"results/order_decision_{uuid.uuid4().hex[:8]}.json"
    s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=file_key, Body=json.dumps(result, indent=2, ensure_ascii=False), ContentType="application/json")
    
    return {"success": True, "s3_key": file_key}
