# 🚀 빠른 시작 가이드

이 가이드는 **처음 사용하는 분들을 위한 단계별 설명**입니다.

---

## ✅ 체크리스트

시작하기 전에 다음을 준비하세요:

- [ ] AWS 계정
- [ ] Python 3.12 이상 설치
- [ ] AWS CLI 설치 및 설정
- [ ] 터미널(명령 프롬프트) 사용 가능

---

## 📝 단계별 가이드

### 1단계: 프로젝트 다운로드

```bash
# GitHub에서 다운로드
git clone https://github.com/your-username/inventory-agent.git

# 프로젝트 폴더로 이동
cd inventory-agent
```

---

### 2단계: Python 패키지 설치

```bash
# 필요한 패키지 설치 (1-2분 소요)
pip install -r requirements.txt
```

**설치되는 패키지:**
- `boto3`: AWS 연동
- `pandas`, `numpy`: 데이터 처리
- `matplotlib`: 그래프 생성
- `sagemaker`: SageMaker 연동
- `strands-agents`, `bedrock-agentcore`: Agent 프레임워크

---

### 3단계: AWS 자격증명 설정

**방법 A: AWS CLI 사용 (권장)**

```bash
aws configure
```

입력 항목:
- AWS Access Key ID: `AKIA...`
- AWS Secret Access Key: `wJalr...`
- Default region name: `us-west-2`
- Default output format: `json`

**방법 B: 환경 변수 사용**

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_SESSION_TOKEN="your-token"  # 임시 자격증명인 경우
```

**확인:**

```bash
aws sts get-caller-identity
```

성공 시 계정 정보가 표시됩니다.

---

### 4단계: S3 버킷 생성 및 데이터 업로드

```bash
# 버킷 이름 설정 (자동으로 고유한 이름 생성)
export S3_BUCKET_NAME="inventory-demo-$(date +%s)"

# 스크립트 실행 권한 부여
chmod +x setup_s3.sh

# S3 버킷 생성 및 샘플 데이터 업로드
./setup_s3.sh
```

**업로드되는 데이터:**
- `sales/product_1.csv`: 상품1 판매 데이터
- `sales/product_2.csv`: 상품2 판매 데이터
- `inventory/current_stock.json`: 현재 재고
- `config/product_config.json`: 상품 설정

**확인:**

```bash
aws s3 ls s3://$S3_BUCKET_NAME/ --recursive
```

---

### 5단계: Chronos2 모델 배포

**⚠️ 중요: 이 단계가 가장 중요합니다!**

#### 방법 A: SageMaker Studio (가장 쉬움 - 추천)

1. **AWS Console 접속**
   - https://console.aws.amazon.com/sagemaker

2. **SageMaker Studio 열기**
   - 왼쪽 메뉴 → "Studio" 클릭

3. **JumpStart 열기**
   - 왼쪽 메뉴 → "JumpStart" 클릭

4. **Chronos 검색**
   - 검색창에 "chronos" 입력

5. **모델 선택**
   - "Chronos-T5-Large" 또는 "pytorch-forecasting-chronos-2" 클릭

6. **배포 설정**
   - Endpoint name: `chronos2-inventory`
   - Instance type: `ml.g5.2xlarge` (기본값)
   - "Deploy" 버튼 클릭

7. **대기**
   - 5-10분 대기 (커피 한 잔 ☕)
   - 상태가 "InService"가 되면 완료

#### 방법 B: Python 스크립트

```bash
python3 deploy_chronos2_official.py
```

**문제 발생 시:**
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) 참고
- 또는 방법 A 사용

---

### 6단계: 환경 변수 설정

```bash
# Chronos2 엔드포인트 이름 (5단계에서 설정한 이름)
export SAGEMAKER_ENDPOINT_NAME="chronos2-inventory"

# S3 버킷 이름 (4단계에서 생성한 이름)
export S3_BUCKET_NAME="your-bucket-name"

# 리전
export AWS_REGION="us-west-2"
```

**확인:**

```bash
echo $SAGEMAKER_ENDPOINT_NAME
echo $S3_BUCKET_NAME
```

---

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
✅ 예측값: [152.8, 150.28, 149.92, 150.7, 150.37, 146.65, 153.07]

[4/6] 재고 및 설정 로드...
✅ 현재 재고: 250
✅ 안전재고: 150

[5/6] 발주량 계산...
✅ 발주량: 654.08

[6/6] 발주 검증...
✅ 승인 (가동률: 90.41%)

============================================================
✅ AWS 환경 테스트 성공!
============================================================

📊 최종 결과:
{
  "order": {
    "product_name": "프리미엄 무선 이어폰",
    "forecast_demand": [152.8, 150.28, ...],
    "order_quantity": 654.08,
    ...
  }
}
```

**✅ 성공!** 시스템이 정상 작동합니다.

---

## 🎉 완료!

축하합니다! 재고관리 시스템이 준비되었습니다.

### 다음 단계

1. **자신의 데이터로 테스트**
   - `sample_data/` 폴더의 CSV 파일 수정
   - `./setup_s3.sh` 재실행

2. **발주 로직 커스터마이징**
   - `tools.py`의 `calculate_order_quantity` 함수 수정

3. **Multi-Agent 워크플로우 실행**
   - `main.py` 실행 (현재는 Bedrock inference profile 설정 필요)

---

## ❓ 문제 해결

### 문제 1: AWS 자격증명 오류

```
Error: The security token included in the request is invalid
```

**해결:**
```bash
aws configure
# 자격증명 다시 입력
```

### 문제 2: S3 버킷 접근 오류

```
Error: Access Denied
```

**해결:**
- IAM 사용자에 S3 권한 추가
- 또는 다른 버킷 이름 사용

### 문제 3: SageMaker 엔드포인트 없음

```
Error: Could not find endpoint
```

**해결:**
- 5단계 다시 확인
- 엔드포인트 이름 확인:
```bash
aws sagemaker list-endpoints --region us-west-2
```

### 문제 4: Python 패키지 오류

```
ModuleNotFoundError: No module named 'xxx'
```

**해결:**
```bash
pip install -r requirements.txt --upgrade
```

---

## 💰 비용 관리

### 사용 후 리소스 삭제

```bash
# SageMaker 엔드포인트 삭제 (중요!)
aws sagemaker delete-endpoint \
  --endpoint-name chronos2-inventory \
  --region us-west-2

# S3 버킷 삭제 (선택)
aws s3 rb s3://$S3_BUCKET_NAME --force
```

### 예상 비용

- **테스트 (1시간)**: ~$1
- **하루 운영**: ~$24
- **한 달 (24/7)**: ~$800

---

## 📚 더 알아보기

- [README.md](README.md) - 전체 문서
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 배포 상세 가이드
- [Chronos2 공식 문서](https://github.com/amazon-science/chronos-forecasting)

---

**도움이 필요하신가요?**
- [GitHub Issues](https://github.com/your-username/inventory-agent/issues)에 질문을 남겨주세요!
