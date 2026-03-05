#!/usr/bin/env python3
"""Mock test without AWS credentials."""
import json
import pandas as pd
import numpy as np
from io import StringIO

# Mock 데이터 로드 테스트
def test_data_loading():
    print("=== 1. 데이터 로딩 테스트 ===")
    
    # CSV 읽기
    with open('sample_data/product_1.csv', 'r') as f:
        df = pd.read_csv(f)
    
    print(f"✓ CSV 로드 성공: {len(df)} 행")
    print(f"✓ 컬럼: {list(df.columns)}")
    
    # 과거/미래 데이터 분리
    target_data = df['sales'].dropna()
    print(f"✓ 과거 데이터: {len(target_data)} 개")
    print(f"✓ 미래 공변량: {len(df) - len(target_data)} 개")
    
    return df

def test_preprocessing(df):
    print("\n=== 2. 전처리 테스트 ===")
    
    target_col = 'sales'
    covariate_cols = ['promotion', 'day_of_week', 'is_weekend', 'price']
    
    target_data = df[target_col].dropna().tolist()
    
    # Chronos2 입력 형식
    input_data = {
        "target": target_data,
        "item_id": "product_1"
    }
    
    # Past covariates
    past_data = {col: df[col].iloc[:len(target_data)].tolist() for col in covariate_cols}
    input_data["past_covariates"] = past_data
    
    # Future covariates
    future_start = len(target_data)
    if future_start < len(df):
        future_data = {col: df[col].iloc[future_start:].dropna().tolist() for col in covariate_cols}
        input_data["future_covariates"] = future_data
    
    print(f"✓ Target 길이: {len(input_data['target'])}")
    print(f"✓ Past covariates: {list(input_data['past_covariates'].keys())}")
    print(f"✓ Future covariates: {list(input_data['future_covariates'].keys())}")
    print(f"✓ 예측 길이: {len(input_data['future_covariates']['promotion'])}")
    
    return input_data

def test_mock_forecast(input_data):
    print("\n=== 3. Mock 예측 테스트 ===")
    
    # Mock Chronos2 응답
    import numpy as np
    prediction_length = len(input_data['future_covariates']['promotion'])
    
    # 과거 평균 기반 Mock 예측
    historical_mean = np.mean(input_data['target'])
    historical_std = np.std(input_data['target'])
    
    mock_forecast = {
        "predictions": [{
            "item_id": "product_1",
            "mean": [historical_mean + np.random.randn() * historical_std * 0.1 
                    for _ in range(prediction_length)],
            "0.1": [historical_mean - historical_std for _ in range(prediction_length)],
            "0.9": [historical_mean + historical_std for _ in range(prediction_length)]
        }]
    }
    
    print(f"✓ 예측 생성 완료")
    print(f"✓ 예측값 (평균): {[round(v, 2) for v in mock_forecast['predictions'][0]['mean']]}")
    
    return mock_forecast

def test_order_calculation(forecast):
    print("\n=== 4. 발주량 계산 테스트 ===")
    
    # Mock 재고 및 설정
    inventory = {
        "product_1": {
            "current_stock": 250,
            "last_updated": "2024-01-20T18:00:00Z"
        }
    }
    
    config = {
        "product_1": {
            "name": "프리미엄 무선 이어폰",
            "safety_stock": 150,
            "lead_time_days": 5,
            "warehouse_capacity": 1000,
            "min_order_quantity": 100,
            "supplier": "supplier_A"
        }
    }
    
    pred = forecast["predictions"][0]
    forecast_mean = pred["mean"]
    lead_time = config["product_1"]["lead_time_days"]
    safety_stock = config["product_1"]["safety_stock"]
    current_stock = inventory["product_1"]["current_stock"]
    min_order = config["product_1"]["min_order_quantity"]
    
    total_demand = sum(forecast_mean[:lead_time])
    required = total_demand + safety_stock
    order_qty = max(0, required - current_stock)
    
    if order_qty > 0 and order_qty < min_order:
        order_qty = min_order
    
    order = {
        "product_name": config["product_1"]["name"],
        "forecast_demand": [round(v, 2) for v in forecast_mean],
        "total_demand_during_lead_time": round(total_demand, 2),
        "current_stock": current_stock,
        "safety_stock": safety_stock,
        "order_quantity": round(order_qty, 2),
        "supplier": config["product_1"]["supplier"],
        "reason": f"리드타임 {lead_time}일 수요 + 안전재고 확보"
    }
    
    print(f"✓ 예측 수요 (7일): {order['forecast_demand']}")
    print(f"✓ 리드타임 {lead_time}일 수요: {order['total_demand_during_lead_time']}")
    print(f"✓ 현재 재고: {order['current_stock']}")
    print(f"✓ 안전재고: {order['safety_stock']}")
    print(f"✓ 발주량: {order['order_quantity']}")
    
    return order, config

def test_validation(order, config):
    print("\n=== 5. 검증 테스트 ===")
    
    cfg = config["product_1"]
    new_stock = order["current_stock"] + order["order_quantity"]
    
    is_valid = new_stock <= cfg["warehouse_capacity"]
    
    validation = {
        "approved": is_valid,
        "new_stock_level": round(new_stock, 2),
        "warehouse_capacity": cfg["warehouse_capacity"],
        "utilization": round(new_stock / cfg["warehouse_capacity"] * 100, 2),
        "warning": None if is_valid else "창고 용량 초과"
    }
    
    print(f"✓ 발주 후 재고: {validation['new_stock_level']}")
    print(f"✓ 창고 용량: {validation['warehouse_capacity']}")
    print(f"✓ 가동률: {validation['utilization']}%")
    print(f"✓ 승인 여부: {'✅ 승인' if validation['approved'] else '❌ 거부'}")
    
    return validation

def main():
    print("🚀 Inventory Agent Mock Test\n")
    
    try:
        # 1. 데이터 로딩
        df = test_data_loading()
        
        # 2. 전처리
        input_data = test_preprocessing(df)
        
        # 3. Mock 예측
        forecast = test_mock_forecast(input_data)
        
        # 4. 발주량 계산
        order, config = test_order_calculation(forecast)
        
        # 5. 검증
        validation = test_validation(order, config)
        
        # 최종 결과
        print("\n" + "="*60)
        print("✅ 모든 테스트 통과!")
        print("="*60)
        
        print("\n📊 최종 결과:")
        result = {
            "order": {k: (float(v) if isinstance(v, (np.floating, np.integer)) else 
                         [float(x) if isinstance(x, (np.floating, np.integer)) else x for x in v] if isinstance(v, list) else v)
                     for k, v in order.items()},
            "validation": {k: (float(v) if isinstance(v, (np.floating, np.integer)) else 
                              bool(v) if isinstance(v, np.bool_) else v)
                          for k, v in validation.items()}
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
