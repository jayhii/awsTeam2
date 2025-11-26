# HR Resource Optimization System

AI 기반 인력 배치 최적화 및 프로젝트 투입 인력 추천 시스템

## 프로젝트 개요

본 시스템은 AWS 클라우드 기반의 서버리스 아키텍처를 활용하여 조직의 인력 배치를 최적화하고 프로젝트 투입 인력을 추천합니다. 직원의 이력 정보, 기술 스택, 프로젝트 참여 이력, 그리고 직원 간 친밀도를 종합적으로 분석하여 최적의 팀 구성을 제안합니다.

## 주요 기능

- **이력서 자동 파싱**: AWS Textract와 Bedrock Claude를 활용한 이력서 자동 분석
- **프로젝트 인력 추천**: 기술 적합도, 프로젝트 이력, 친밀도를 종합한 AI 추천
- **친밀도 분석**: 프로젝트 협업, 메신저 커뮤니케이션, 행사 참여 등 다각도 분석
- **도메인 확장 분석**: 신규 사업 도메인 진입 가능성 및 전략 제시
- **정량/정성 평가**: 경력 데이터 기반 정량 평가 + AI 기반 정성 평가
- **벡터 기반 유사도 검색**: OpenSearch를 활용한 인력 매칭

## 기술 스택

### AWS Services
- **Lambda**: 서버리스 컴퓨팅
- **DynamoDB**: NoSQL 데이터베이스
- **S3**: 객체 스토리지
- **API Gateway**: REST API 엔드포인트
- **Bedrock**: AI/ML 서비스 (Claude, Titan Embeddings)
- **Textract**: 문서 텍스트 추출
- **OpenSearch**: 벡터 검색 엔진
- **EventBridge**: 이벤트 스케줄링
- **CloudWatch**: 모니터링 및 로깅

### Development
- **Python 3.11**: 주 개발 언어
- **Terraform**: Infrastructure as Code
- **pytest**: 테스트 프레임워크
- **Hypothesis**: Property-based 테스트

## 프로젝트 구조

```
awsTeam2/
├── lambda_functions/          # Lambda 함수들
│   ├── resume_parser/         # 이력서 파싱
│   ├── affinity_calculator/   # 친밀도 계산
│   ├── recommendation_engine/ # 추천 엔진
│   ├── domain_analysis/       # 도메인 분석
│   ├── quantitative_analysis/ # 정량 분석
│   ├── qualitative_analysis/  # 정성 분석
│   ├── tech_trend_collector/  # 기술 트렌드 수집
│   └── vector_embedding/      # 벡터 임베딩 생성
├── common/                    # 공통 유틸리티
│   ├── models.py             # 데이터 모델
│   └── utils.py              # 유틸리티 함수
├── tests/                     # 테스트
│   ├── unit/                 # 단위 테스트
│   ├── integration/          # 통합 테스트
│   └── property/             # Property-based 테스트
├── deployment/                # 배포 스크립트
│   ├── terraform/            # Terraform 설정
│   ├── deploy.sh             # 배포 스크립트 (Linux/Mac)
│   └── deploy.ps1            # 배포 스크립트 (Windows)
├── aws_infrastructure/        # AWS 인프라 설정
├── test_data/                # 테스트 데이터
└── .kiro/specs/              # 프로젝트 스펙 문서
```

## 개발 환경 설정

### 사전 요구사항

- Python 3.11 이상
- AWS CLI 설치 및 구성
- Terraform 1.5 이상
- Git

### 설정 단계

#### Windows (PowerShell)

```powershell
# 1. 저장소 클론 (이미 완료된 경우 생략)
git clone <repository-url>
cd awsTeam2

# 2. Python 가상 환경 설정
.\setup_env.ps1

# 3. AWS CLI 구성 확인
aws configure list

# 4. Terraform 초기화
cd deployment/terraform
terraform init
```

#### Linux/Mac (Bash)

```bash
# 1. 저장소 클론 (이미 완료된 경우 생략)
git clone <repository-url>
cd awsTeam2

# 2. 스크립트 실행 권한 부여
chmod +x setup_env.sh

# 3. Python 가상 환경 설정
./setup_env.sh

# 4. AWS CLI 구성 확인
aws configure list

# 5. Terraform 초기화
cd deployment/terraform
terraform init
```

## 테스트 실행

```bash
# 가상 환경 활성화 (Windows)
.\venv\Scripts\Activate.ps1

# 가상 환경 활성화 (Linux/Mac)
source venv/bin/activate

# 모든 테스트 실행
pytest

# 단위 테스트만 실행
pytest -m unit

# Property-based 테스트만 실행
pytest -m property

# 통합 테스트만 실행
pytest -m integration

# 커버리지 리포트 생성
pytest --cov-report=html
```

## 배포

자세한 배포 가이드는 [DEPLOYMENT_GUIDE.md](deployment/DEPLOYMENT_GUIDE.md)를 참조하세요.

```bash
# 개발 환경 배포
cd deployment
./deploy.sh dev

# 프로덕션 환경 배포
./deploy.sh prod
```

## AWS 리소스 태깅

모든 AWS 리소스는 다음 태그를 포함합니다:
- `Team`: Team2
- `Project`: HR-Resource-Optimization
- `Environment`: dev/staging/prod

## 보안

- IAM 태그 기반 접근 제어
- 모든 데이터 암호화 (at rest & in transit)
- 최소 권한 원칙 적용
- PII 데이터 익명화 처리

## 모니터링 및 알림

시스템은 포괄적인 모니터링 및 알림 기능을 제공합니다:

### CloudWatch 대시보드

자동으로 생성되는 3개의 대시보드:

1. **HR-Lambda-Metrics-Team2**
   - Lambda 함수 호출 수
   - 에러 발생 건수
   - 실행 시간 (Duration)
   - 스로틀링 이벤트

2. **HR-API-Gateway-Metrics-Team2**
   - API 요청 수
   - 4XX/5XX 에러
   - 레이턴시 (Latency)
   - 통합 레이턴시 (Integration Latency)

3. **HR-DynamoDB-Metrics-Team2**
   - 읽기/쓰기 용량 단위 소비량
   - 사용자 에러
   - 시스템 에러
   - 읽기/쓰기 스로틀링 이벤트

### CloudWatch 알람

자동으로 설정되는 알람:

- **Lambda 에러 알람** (8개): 각 Lambda 함수별 에러율 모니터링
- **API Gateway 레이턴시 알람**: 평균 응답 시간 > 5초
- **API Gateway 5XX 에러 알람**: 서버 에러 > 10건
- **DynamoDB 스로틀링 알람** (6개): 주요 테이블별 읽기/쓰기 스로틀링

### SNS 알림

- 알람 발생 시 이메일 알림
- `terraform.tfvars`에서 이메일 주소 설정:
  ```hcl
  alarm_email_addresses = ["admin@example.com"]
  ```

### 로그 모니터링

```bash
# Lambda 함수 로그 확인
aws logs tail /aws/lambda/ResumeParser --follow

# 에러 로그 필터링
aws logs filter-log-events \
  --log-group-name /aws/lambda/ResumeParser \
  --filter-pattern "ERROR"
```

자세한 내용은 [배포 가이드의 모니터링 섹션](deployment/DEPLOYMENT_GUIDE.md#모니터링-및-알림-설정)을 참조하세요.

## 문서

- [Requirements](../.kiro/specs/hr-resource-optimization/requirements.md)
- [Design](../.kiro/specs/hr-resource-optimization/design.md)
- [Tasks](../.kiro/specs/hr-resource-optimization/tasks.md)
- [Deployment Guide](deployment/DEPLOYMENT_GUIDE.md)

## 라이선스

내부 프로젝트 - Team2

## 연락처

프로젝트 관련 문의: Team2
