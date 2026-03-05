# 📦 프로젝트 파일 구조

## 필수 파일 (19개)

### 📖 문서 (4개)
- `README.md` - 프로젝트 전체 소개 및 가이드
- `QUICKSTART.md` - 초보자용 단계별 가이드 ⭐ **여기서 시작!**
- `DEPLOYMENT_GUIDE.md` - Chronos2 배포 상세 가이드
- `.gitignore` - Git 제외 파일 목록

### 🐍 Python 코드 (5개)
- `config.py` - AWS 클라이언트 설정
- `tools.py` - 8개 도구 함수 (데이터 로드, 예측, 발주 계산 등)
- `agents.py` - 7개 전문 Agent 정의
- `main.py` - 메인 코디네이터 (전체 워크플로우)
- `deploy_chronos2_official.py` - Chronos2 배포 스크립트

### 🧪 테스트 (2개)
- `test_aws_direct.py` - AWS 환경 전체 테스트 ⭐ **실제 테스트**
- `test_mock.py` - 로컬 Mock 테스트 (AWS 불필요)

### 🔧 설정 및 스크립트 (4개)
- `requirements.txt` - Python 의존성
- `Dockerfile` - Docker 이미지
- `setup_s3.sh` - S3 데이터 업로드 스크립트
- `bedrock-policy.json` - Bedrock IAM 정책
- `iam-policy.json` - SageMaker IAM 정책

### 📊 샘플 데이터 (4개)
- `sample_data/product_1.csv` - 상품1 판매 데이터
- `sample_data/product_2.csv` - 상품2 판매 데이터
- `sample_data/current_stock.json` - 현재 재고
- `sample_data/product_config.json` - 상품 설정

---

## 시작 순서

### 1️⃣ 처음 사용하는 경우
```
QUICKSTART.md 읽기 → 단계별 따라하기 → test_aws_direct.py 실행
```

### 2️⃣ 빠르게 시작하는 경우
```bash
pip install -r requirements.txt
export S3_BUCKET_NAME="inventory-demo-$(date +%s)"
./setup_s3.sh
# SageMaker Studio에서 Chronos2 배포
export SAGEMAKER_ENDPOINT_NAME="chronos2-inventory"
python3 test_aws_direct.py
```

### 3️⃣ 로컬에서만 테스트
```bash
pip install -r requirements.txt
python3 test_mock.py
```

---

## 파일별 역할

| 파일 | 역할 | 필수 여부 |
|------|------|----------|
| `QUICKSTART.md` | 초보자 가이드 | ⭐ 시작점 |
| `README.md` | 전체 문서 | ✅ 필수 |
| `test_aws_direct.py` | 실제 테스트 | ⭐ 테스트 |
| `test_mock.py` | 로컬 테스트 | 선택 |
| `config.py` | AWS 설정 | ✅ 필수 |
| `tools.py` | 핵심 로직 | ✅ 필수 |
| `agents.py` | Agent 정의 | ✅ 필수 |
| `main.py` | 워크플로우 | 선택 |
| `setup_s3.sh` | 데이터 업로드 | ✅ 필수 |
| `requirements.txt` | 의존성 | ✅ 필수 |

---

## 삭제된 파일 (불필요)

다음 파일들은 개발 과정에서 생성되었으나 최종 버전에서 제거되었습니다:

- `ARCHITECTURE.md` - 너무 상세한 아키텍처 문서
- `FUNCTION_GUIDE.md` - 중복된 함수 설명
- `WORKFLOW_DIAGRAM.md` - 복잡한 다이어그램
- `agent.py`, `forecaster.py` - 사용하지 않는 코드
- `test_forecaster.py`, `test_run.py`, `test_aws_mock.py` - 중복 테스트
- `deploy_chronos2.py`, `deploy_jumpstart.py` - 중복 배포 스크립트
- `isengard_quickstart.sh`, `setup_aws_env.sh` - 특정 환경용 스크립트
- `test_aws_connection.py` - 중복 연결 테스트

---

## GitHub 업로드 전 체크리스트

- [ ] `README.md` 확인
- [ ] `QUICKSTART.md` 확인
- [ ] GitHub 저장소 URL 업데이트
- [ ] 샘플 데이터 확인
- [ ] `.gitignore` 확인
- [ ] 라이선스 파일 추가 (선택)

---

## Git 명령어

```bash
cd inventory-agent

# Git 초기화
git init

# 모든 파일 추가
git add .

# 커밋
git commit -m "Initial commit: Chronos2 기반 재고관리 자동화 시스템"

# GitHub 저장소 연결
git remote add origin https://github.com/your-username/inventory-agent.git

# 푸시
git push -u origin main
```

---

**✅ 준비 완료!** GitHub에 업로드할 수 있습니다.
