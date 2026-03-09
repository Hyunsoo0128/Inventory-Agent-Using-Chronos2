# 🚀 Chronos2 기반 쇼핑몰 수요예측-재고관리 자동화 시스템

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![AWS](https://img.shields.io/badge/AWS-SageMaker%20%7C%20Bedrock-orange.svg)](https://aws.amazon.com/)

> Amazon Chronos2 시계열 예측 모델과 Multi-Agent 시스템을 활용한 지능형 재고관리 자동화

---

## 📖 목차

- [시스템 소개](#시스템-소개)
- [Chronos2란?](#chronos2란)
- [빠른 시작](#빠른-시작)
- [상세 가이드](#상세-가이드)
- [파일 구조](#파일-구조)

---

## 🎯 시스템 소개

이 시스템은 **쇼핑몰의 상품별 수요를 예측**하고, **자동으로 발주 결정**을 내리는 AI 기반 재고관리 솔루션입니다.

### 핵심 기능

1. **공변량 기반 수요 예측**
   - 프로모션, 요일, 가격 등을 고려한 정확한 예측
   - Chronos2 제로샷 러닝으로 별도 학습 불필요

2. **자동 발주 결정**
   - 리드타임, 안전재고 자동 계산
   - 창고 용량 제약 검증

3. **Multi-Agent 아키텍처**
   - 데이터 로딩, 전처리, 예측, 검증 등 역할 분리
   - 각 Agent가 전문화된 작업 수행

### 시스템 흐름

```
📦 S3 데이터 → 🔄 전처리 → 🤖 Chronos2 예측 → 🧠 발주 결정 → ✅ 검증 → 📊 시각화
```

---

## 🎓 Chronos2란?

**Chronos2**는 Amazon이 개발한 **제로샷 시계열 예측 모델**입니다.

### 왜 Chronos2인가?

| 기존 방식 | Chronos2 |
|----------|----------|
| 데이터 수집 → 모델 학습 → 예측 (수주 소요) | 데이터 입력 → 즉시 예측 (수분 소요) |
| 수천~수만 개 데이터 필요 | 수십~수백 개로 충분 |
| 도메인별 재학습 필요 | 별도 학습 불필요 |

### 공변량(Covariates) 지원

```python
# 단순 예측
target = [120, 135, 142, ...]  # 과거 판매량만

# 공변량 기반 예측 (정확도 20-40% 향상)
target = [120, 135, 142, ...]
covariates = {
    "promotion": [0, 1, 1, ...],  # 프로모션 여부
    "day_of_week": [1, 2, 3, ...], # 요일
    "price": [29.99, 24.99, ...]   # 가격
}
```

---

## 🚀 빠른 시작

### 사전 요구사항

- AWS 계정
- Python 3.12+
- AWS CLI 설정

### 1단계: 저장소 클론

```bash
git clone https://github.com/Hyunsoo0128/inventory-agent.git
cd inventory-agent
```

### 2단계: 의존성 설치

```bash
pip install -r requirements.txt
```

### 3단계: AWS 자격증명 설정

```bash
aws configure
# 또는
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
```

### 4단계: S3 버킷 생성 및 데이터 업로드

```bash
export S3_BUCKET_NAME="inventory-demo-$(date +%s)"
chmod +x setup_s3.sh
./setup_s3.sh
```

### 5단계: Chronos2 엔드포인트 배포

**방법 A: deploy-chronos-to-amazon-sagemaker**

하기 레포 참고
https://github.com/amazon-science/chronos-forecasting/blob/main/notebooks/deploy-chronos-to-amazon-sagemaker.ipynb

**방법 B: Python 스크립트**

```bash
python3 deploy_chronos2_official.py
```

상세 가이드: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

### 6단계: 환경 변수 설정

```bash
export SAGEMAKER_ENDPOINT_NAME="chronos2-inventory"
export S3_BUCKET_NAME="your-bucket-name"
```

### 7단계: 테스트 실행

```bash
python3 test_aws_direct.py
```

**예상 출력:**

```
🚀 AWS 환경 테스트 (Tool 직접 호출)

[1/6] product_1 판매 데이터 로드...
✅ 27행 로드 완료

[2/6] 데이터 전처리...
✅ Target: 20개
✅ 예측 길이: 7일

[3/6] 수요 예측 (Chronos2)...
✅ 예측값: [152.8, 150.28, 149.92, ...]

[4/6] 재고 및 설정 로드...
✅ 현재 재고: 250

[5/6] 발주량 계산...
✅ 발주량: 654.08

[6/6] 발주 검증...
✅ 승인 (가동률: 90.41%)

============================================================
✅ AWS 환경 테스트 성공!
============================================================
```

---

## 📚 상세 가이드

### 데이터 형식

#### 판매 데이터 (CSV)

```csv
date,sales,promotion,day_of_week,is_weekend,price
2024-01-01,120,0,1,0,29.99    # 과거 데이터
2024-01-02,135,0,2,0,29.99
...
2024-01-20,170,1,6,1,24.99
2024-01-21,,1,7,1,24.99       # 미래 공변량 (sales 비어있음)
2024-01-22,,0,1,0,29.99
```

- **과거**: `sales` 포함 (target)
- **미래**: `sales` 비어있음, 공변량만 포함
- Chronos2가 미래 공변량을 활용하여 예측

#### 재고 데이터 (JSON)

```json
{
  "product_1": {
    "current_stock": 250,
    "last_updated": "2024-01-20T18:00:00Z"
  }
}
```

#### 상품 설정 (JSON)

```json
{
  "product_1": {
    "name": "프리미엄 무선 이어폰",
    "safety_stock": 150,
    "lead_time_days": 5,
    "warehouse_capacity": 1000,
    "min_order_quantity": 100,
    "supplier": "supplier_A"
  }
}
```

### S3 데이터 구조

```
s3://your-bucket/
├── sales/
│   ├── product_1.csv
│   └── product_2.csv
├── inventory/
│   └── current_stock.json
└── config/
    └── product_config.json
```

### 발주 로직

```python
# 1. 리드타임 동안 예상 수요
total_demand = sum(forecast[:lead_time_days])

# 2. 필요 재고 = 수요 + 안전재고
required = total_demand + safety_stock

# 3. 발주량 = 필요 재고 - 현재 재고
order_quantity = max(0, required - current_stock)

# 4. 최소 발주량 적용
if order_quantity > 0 and order_quantity < min_order_quantity:
    order_quantity = min_order_quantity
```

---

## 📁 파일 구조

```
inventory-agent/
├── README.md                    # 이 파일
├── DEPLOYMENT_GUIDE.md          # Chronos2 배포 가이드
├── requirements.txt             # Python 의존성
├── Dockerfile                   # Docker 이미지
│
├── config.py                    # AWS 설정
├── tools.py                     # 8개 도구 함수
├── agents.py                    # 7개 전문 Agent
├── main.py                      # 메인 코디네이터
│
├── deploy_chronos2_official.py # Chronos2 배포 스크립트
├── setup_s3.sh                  # S3 데이터 업로드
├── test_aws_direct.py           # 전체 워크플로우 테스트
├── test_mock.py                 # 로컬 테스트 (AWS 불필요)
│
├── bedrock-policy.json          # Bedrock IAM 정책
├── iam-policy.json              # SageMaker IAM 정책
│
└── sample_data/                 # 샘플 데이터
    ├── product_1.csv
    ├── product_2.csv
    ├── current_stock.json
    └── product_config.json
```

### 핵심 파일 설명

| 파일 | 설명 |
|------|------|
| `config.py` | AWS 클라이언트 설정 (SageMaker, S3, Bedrock) |
| `tools.py` | 8개 도구: 데이터 로드, 전처리, 예측, 발주 계산 등 |
| `agents.py` | 7개 Agent: 각 도구를 사용하는 전문 Agent |
| `main.py` | 메인 코디네이터: 전체 워크플로우 오케스트레이션 |
| `test_aws_direct.py` | 도구 직접 호출 테스트 (Agent 없이) |
| `test_mock.py` | Mock 모드 테스트 (AWS 없이 로컬 실행) |

---

## 🧪 테스트

### 로컬 테스트 (AWS 불필요)

```bash
python3 test_mock.py
```

Mock 데이터로 전체 로직 검증

### AWS 테스트 (실제 환경)

```bash
python3 test_aws_direct.py
```

S3 + Chronos2 + 전체 워크플로우 테스트

---

## 💰 비용

| 항목 | 비용 |
|------|------|
| SageMaker (ml.g5.2xlarge) | ~$1.006/시간 |
| Bedrock (Claude 3.5 Sonnet) | ~$3/1M tokens |
| S3 스토리지 | ~$0.023/GB |
| **월간 예상 (24/7 운영)** | **~$800-1000** |

### 비용 절감

- 사용 후 엔드포인트 삭제:
```bash
aws sagemaker delete-endpoint --endpoint-name chronos2-inventory
```

- 또는 [Scale to Zero](https://docs.aws.amazon.com/sagemaker/latest/dg/endpoint-auto-scaling-zero-instances.html) 설정

---

## 🔧 트러블슈팅

### 1. Bedrock 권한 오류

```bash
# bedrock-policy.json 적용
aws iam put-role-policy \
  --role-name YourRole \
  --policy-name BedrockAccess \
  --policy-document file://bedrock-policy.json
```

### 2. SageMaker 엔드포인트 없음

[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) 참고

### 3. S3 접근 오류

```bash
# 버킷 권한 확인
aws s3 ls s3://your-bucket-name
```

---

## 📖 참고 자료

- [Chronos2 공식 GitHub](https://github.com/amazon-science/chronos-forecasting)
- [Chronos2 논문](https://www.arxiv.org/abs/2510.15821)
- [SageMaker JumpStart](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-jumpstart.html)
- [Amazon Bedrock](https://aws.amazon.com/bedrock/)

---

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능
