#!/usr/bin/env python3
"""Main coordinator agent for inventory management."""
import json
from bedrock_agentcore import BedrockAgentCoreApp
from agents import (
    data_loader_agent, preprocessing_agent, forecasting_agent,
    order_decision_agent, validation_agent, visualization_agent, result_saver_agent
)

app = BedrockAgentCoreApp()

@app.entrypoint
async def entrypoint(payload):
    """재고관리 자동화 메인 코디네이터"""
    print("=== 재고관리 자동화 시작 ===")
    
    product_id = payload.get("product_id", "product_1")
    
    # 1. 데이터 로딩
    print(f"\n[1/7] {product_id} 데이터 로딩...")
    sales_data, inventory_data, config_data = None, None, None
    
    async for msg in data_loader_agent.stream_async(f"{product_id}의 판매 데이터를 로드하세요."):
        if hasattr(msg, 'tool_result'):
            sales_data = msg.tool_result
    
    async for msg in data_loader_agent.stream_async("재고 데이터를 로드하세요."):
        if hasattr(msg, 'tool_result'):
            inventory_data = msg.tool_result
    
    async for msg in data_loader_agent.stream_async("상품 설정을 로드하세요."):
        if hasattr(msg, 'tool_result'):
            config_data = msg.tool_result
    
    # 2. 전처리
    print("\n[2/7] 데이터 전처리...")
    analysis_result = None
    async for msg in preprocessing_agent.stream_async(f"판매 데이터를 분석하세요: {json.dumps(sales_data)}"):
        if hasattr(msg, 'tool_result'):
            analysis_result = msg.tool_result
    
    # 3. 예측
    print("\n[3/7] Chronos2 수요 예측...")
    forecast_result = None
    async for msg in forecasting_agent.stream_async(f"수요를 예측하세요: {json.dumps(analysis_result)}"):
        if hasattr(msg, 'tool_result'):
            forecast_result = msg.tool_result
    
    # 4. 발주량 계산
    print("\n[4/7] 발주량 계산...")
    order_result = None
    async for msg in order_decision_agent.stream_async(
        f"예측: {json.dumps(forecast_result)}\n재고: {json.dumps(inventory_data)}\n설정: {json.dumps(config_data)}\n발주량을 계산하세요."
    ):
        if hasattr(msg, 'tool_result'):
            order_result = msg.tool_result
    
    # 5. 검증
    print("\n[5/7] 발주 검증...")
    validation_result = None
    async for msg in validation_agent.stream_async(f"발주: {json.dumps(order_result)}\n설정: {json.dumps(config_data)}\n검증하세요."):
        if hasattr(msg, 'tool_result'):
            validation_result = msg.tool_result
    
    # 6. 시각화
    print("\n[6/7] 시각화...")
    visualization_result = None
    async for msg in visualization_agent.stream_async(f"예측 결과를 시각화하세요: {json.dumps(forecast_result)}"):
        if hasattr(msg, 'tool_result'):
            visualization_result = msg.tool_result
    
    # 7. 저장
    print("\n[7/7] 결과 저장...")
    save_result = None
    async for msg in result_saver_agent.stream_async(f"발주: {json.dumps(order_result)}\n검증: {json.dumps(validation_result)}\n저장하세요."):
        if hasattr(msg, 'tool_result'):
            save_result = msg.tool_result
    
    # 최종 리포트
    yield f"""
# 재고관리 자동화 결과

## 📊 발주 권장사항
```json
{json.dumps(order_result, indent=2, ensure_ascii=False)}
```

## ✅ 검증 결과
```json
{json.dumps(validation_result, indent=2, ensure_ascii=False)}
```

## 📈 예측 그래프
{visualization_result}

## 💾 저장 위치
- S3 Key: {save_result.get('s3_key', 'N/A')}

---
✨ 처리 완료: {product_id}에 대한 발주 결정이 완료되었습니다.
"""

if __name__ == "__main__":
    app.run()
