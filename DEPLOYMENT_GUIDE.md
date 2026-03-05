# Chronos2 SageMaker 엔드포인트 배포 가이드

## 방법 1: Python 스크립트 (권장)

### 사전 요구사항
```bash
pip install sagemaker
```

### 배포 실행
```bash
cd inventory-agent
python3 deploy_jumpstart.py
```

---

## 방법 2: SageMaker Studio (가장 쉬움)

### 단계:
1. AWS Console → SageMaker Studio 열기
2. 왼쪽 메뉴 → **JumpStart** 클릭
3. 검색창에 **"chronos"** 입력
4. **Chronos-T5-Large** 선택
5. **Deploy** 버튼 클릭
6. 엔드포인트 이름 입력: `chronos2-inventory`
7. 인스턴스 타입: `ml.g5.xlarge` (기본값)
8. **Deploy** 클릭
9. 5-10분 대기

### 배포 후:
```bash
export SAGEMAKER_ENDPOINT_NAME="chronos2-inventory"
```

---

## 방법 3: Notebook에서 배포

### SageMaker Notebook 생성:
```python
import sagemaker
from sagemaker.jumpstart.model import JumpStartModel

# 모델 로드
model = JumpStartModel(model_id="huggingface-forecasting-chronos-t5-large")

# 배포
predictor = model.deploy(
    initial_instance_count=1,
    instance_type="ml.g5.xlarge",
    endpoint_name="chronos2-inventory"
)

print(f"Endpoint: {predictor.endpoint_name}")
```

---

## 방법 4: 기존 엔드포인트 사용

### 엔드포인트 목록 확인:
```bash
aws sagemaker list-endpoints --region us-west-2
```

### 기존 엔드포인트 사용:
```bash
export SAGEMAKER_ENDPOINT_NAME="existing-endpoint-name"
```

---

## 배포 확인

### 엔드포인트 상태 확인:
```bash
aws sagemaker describe-endpoint \
  --endpoint-name chronos2-inventory \
  --region us-west-2 \
  --query 'EndpointStatus'
```

### 테스트:
```bash
cd inventory-agent
python3 test_aws_direct.py
```

---

## 비용 정보

- **인스턴스**: ml.g5.xlarge
- **시간당 비용**: ~$1.006
- **월간 예상**: ~$734 (24/7 운영 시)

### 비용 절감:
- 사용 후 엔드포인트 삭제:
```bash
aws sagemaker delete-endpoint \
  --endpoint-name chronos2-inventory \
  --region us-west-2
```

---

## 트러블슈팅

### 1. IAM 권한 오류
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "sagemaker:CreateEndpoint",
      "sagemaker:CreateEndpointConfig",
      "sagemaker:CreateModel",
      "sagemaker:DescribeEndpoint"
    ],
    "Resource": "*"
  }]
}
```

### 2. 인스턴스 할당량 초과
- AWS Support에 할당량 증가 요청
- 또는 다른 인스턴스 타입 사용: `ml.g4dn.xlarge`

### 3. 리전 지원 안됨
- `us-west-2` 또는 `us-east-1` 사용 권장

---

## 다음 단계

배포 완료 후:
```bash
# 환경 변수 설정
export SAGEMAKER_ENDPOINT_NAME="chronos2-inventory"
export S3_BUCKET_NAME="inventory-demo-hyunkai-1772679739"

# 전체 테스트
cd inventory-agent
python3 test_aws_direct.py
```
