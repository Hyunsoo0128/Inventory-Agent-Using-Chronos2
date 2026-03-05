"""Specialized agents for inventory management."""
from strands import Agent
from strands.models import BedrockModel
from tools import (
    load_sales_from_s3, analyze_sales_data, predict_demand,
    load_inventory_from_s3, load_product_config_from_s3,
    calculate_order_quantity, validate_order_decision,
    visualize_forecast, save_order_result_to_s3
)

MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"

data_loader_agent = Agent(
    system_prompt="S3에서 판매/재고/설정 데이터를 로드합니다.",
    tools=[load_sales_from_s3, load_inventory_from_s3, load_product_config_from_s3],
    model=BedrockModel(model_id=MODEL_ID)
)

preprocessing_agent = Agent(
    system_prompt="판매 데이터를 분석하여 Chronos2 입력 형식으로 변환합니다.",
    tools=[analyze_sales_data],
    model=BedrockModel(model_id=MODEL_ID)
)

forecasting_agent = Agent(
    system_prompt="Chronos2 모델로 수요를 예측합니다.",
    tools=[predict_demand],
    model=BedrockModel(model_id=MODEL_ID)
)

order_decision_agent = Agent(
    system_prompt="예측, 재고, 설정을 종합하여 발주량을 계산합니다.",
    tools=[calculate_order_quantity],
    model=BedrockModel(model_id=MODEL_ID)
)

validation_agent = Agent(
    system_prompt="발주 결정이 제약조건을 만족하는지 검증합니다.",
    tools=[validate_order_decision],
    model=BedrockModel(model_id=MODEL_ID)
)

visualization_agent = Agent(
    system_prompt="예측 결과를 그래프로 시각화하여 S3에 저장합니다.",
    tools=[visualize_forecast],
    model=BedrockModel(model_id=MODEL_ID)
)

result_saver_agent = Agent(
    system_prompt="발주 결과를 S3에 저장합니다.",
    tools=[save_order_result_to_s3],
    model=BedrockModel(model_id=MODEL_ID)
)
