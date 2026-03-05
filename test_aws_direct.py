#!/usr/bin/env python3
"""AWS 환경 직접 테스트 (Agent 없이 Tool만 사용)"""
import os
import json
import numpy as np

# AWS 자격증명은 환경 변수로 설정하세요:
# export AWS_ACCESS_KEY_ID="your-key"
# export AWS_SECRET_ACCESS_KEY="your-secret"
# export AWS_SESSION_TOKEN="your-token"  # 임시 자격증명인 경우
# export S3_BUCKET_NAME="your-bucket"
# export AWS_REGION="us-west-2"

from tools import (
    load_sales_from_s3, analyze_sales_data,
    load_inventory_from_s3, load_product_config_from_s3,
    calculate_order_quantity, validate_order_decision
)

def mock_chronos2_predict(analysis_result):
    """Mock Chronos2 예측"""
    result = analysis_result if isinstance(analysis_result, dict) else json.loads(analysis_result)
    
    predictions = []
    for input_data in result["inputs"]:
        target = input_data["target"]
        mean_val = np.mean(target)
        std_val = np.std(target)
        
        prediction_length = result["prediction_length"]
        mean_forecast = [float(mean_val + np.random.randn() * std_val * 0.1) 
                        for _ in range(prediction_length)]
        
        predictions.append({
            "item_id": input_data["item_id"],
            "mean": mean_forecast,
            "0.1": [float(mean_val - std_val) for _ in range(prediction_length)],
            "0.9": [float(mean_val + std_val) for _ in range(prediction_length)]
        })
    
    return {"predictions": {"predictions": predictions}, "analysis": result}

def main():
    print("🚀 AWS 환경 테스트 (Tool 직접 호출)\n")
    
    product_id = "product_1"
    
    try:
        # 1. S3에서 판매 데이터 로드
        print(f"[1/6] {product_id} 판매 데이터 로드...")
        sales_data = load_sales_from_s3(product_id)
        print(f"✅ {len(sales_data['data'])}행 로드 완료")
        
        # 2. 데이터 전처리
        print("\n[2/6] 데이터 전처리...")
        analysis_result = analyze_sales_data(json.dumps(sales_data))
        print(f"✅ Target: {len(analysis_result['inputs'][0]['target'])}개")
        print(f"✅ 예측 길이: {analysis_result['prediction_length']}일")
        
        # 3. Mock Chronos2 예측
        print("\n[3/6] 수요 예측 (Mock Chronos2)...")
        forecast_result = mock_chronos2_predict(analysis_result)
        pred = forecast_result["predictions"]["predictions"][0]
        print(f"✅ 예측값: {[round(v, 2) for v in pred['mean']]}")
        
        # 4. 재고 및 설정 로드
        print("\n[4/6] 재고 및 설정 로드...")
        inventory_data = load_inventory_from_s3()
        config_data = load_product_config_from_s3()
        print(f"✅ 현재 재고: {inventory_data['inventory'][product_id]['current_stock']}")
        print(f"✅ 안전재고: {config_data['config'][product_id]['safety_stock']}")
        
        # 5. 발주량 계산
        print("\n[5/6] 발주량 계산...")
        order_result = calculate_order_quantity(
            json.dumps(forecast_result),
            json.dumps(inventory_data),
            json.dumps(config_data)
        )
        print(f"✅ 발주량: {order_result[product_id]['order_quantity']}")
        
        # 6. 검증
        print("\n[6/6] 발주 검증...")
        validation_result = validate_order_decision(
            json.dumps(order_result),
            json.dumps(config_data)
        )
        status = "✅ 승인" if validation_result[product_id]['approved'] else "❌ 거부"
        print(f"{status} (가동률: {validation_result[product_id]['utilization']}%)")
        
        # 최종 결과
        print("\n" + "="*60)
        print("✅ AWS 환경 테스트 성공!")
        print("="*60)
        
        print("\n📊 최종 결과:")
        result = {
            "order": order_result[product_id],
            "validation": validation_result[product_id]
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print("\n✨ 다음 단계:")
        print("  1. SageMaker Chronos2 엔드포인트 배포")
        print("  2. tools.py의 predict_demand를 실제 엔드포인트로 연결")
        print("  3. Multi-Agent 워크플로우 실행")
        
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
