#!/usr/bin/env python3
"""Deploy Chronos-2 to SageMaker using JumpStart (Official Method)"""
import boto3
from sagemaker.jumpstart.model import JumpStartModel

print("🚀 Chronos-2 SageMaker 배포 (공식 방법)\n")

# 설정
region = 'us-west-2'
role = None  # SageMaker Notebook에서 자동 감지

# IAM Role 설정
if role is None:
    try:
        import sagemaker
        role = sagemaker.get_execution_role()
        print(f"✅ IAM Role (자동): {role}")
    except:
        sts = boto3.client('sts', region_name=region)
        account_id = sts.get_caller_identity()['Account']
        role = f"arn:aws:iam::{account_id}:role/Admin"
        print(f"✅ IAM Role (수동): {role}")

# Chronos-2 모델 생성
print("\n📦 Chronos-2 모델 설정...")
print("   Model ID: pytorch-forecasting-chronos-2")
print("   Instance: ml.g5.2xlarge (GPU)")

js_model = JumpStartModel(
    model_id="pytorch-forecasting-chronos-2",
    instance_type="ml.g5.2xlarge",  # GPU 인스턴스
    role=role,
)

print("✅ 모델 설정 완료")

# 배포
print("\n🔄 엔드포인트 배포 중...")
print("   예상 시간: 5-10분")
print("   비용: ~$1.006/시간\n")

try:
    predictor = js_model.deploy()
    
    print("\n" + "="*60)
    print("✅ 배포 완료!")
    print("="*60)
    
    endpoint_name = predictor.endpoint_name
    print(f"\n엔드포인트: {endpoint_name}")
    print(f"\n환경 변수 설정:")
    print(f'export SAGEMAKER_ENDPOINT_NAME="{endpoint_name}"')
    
    # 테스트
    print("\n🧪 테스트 예측...")
    test_payload = {
        "inputs": [{
            "target": [120, 135, 142, 158, 165, 180, 145, 130, 138, 148, 152, 160, 175, 150, 135, 140, 145, 155, 162, 170]
        }],
        "parameters": {"prediction_length": 7}
    }
    
    result = predictor.predict(test_payload)
    forecast = result['predictions'][0]['mean']
    print(f"✅ 예측 성공: {[round(v, 2) for v in forecast]}")
    
    print("\n📝 다음 단계:")
    print("  1. 환경 변수 설정")
    print("  2. cd inventory-agent && python3 test_aws_direct.py")
    print("\n⚠️  사용 후 삭제:")
    print(f"  aws sagemaker delete-endpoint --endpoint-name {endpoint_name} --region {region}")
    
except Exception as e:
    print(f"\n❌ 배포 실패: {e}")
    print("\n가능한 원인:")
    print("  1. IAM 권한 부족 (SageMaker 권한 필요)")
    print("  2. ml.g5.2xlarge 할당량 초과")
    print("  3. 리전 미지원 (us-west-2 권장)")
    
    import traceback
    traceback.print_exc()
