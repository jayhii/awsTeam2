# HR Resource Optimization System - 배포 가이드

## 개요
이 가이드는 AWS 계정 정보만 입력하면 전체 인프라를 자동으로 배포하는 방법을 설명합니다.

## 사전 요구사항

### 1. AWS CLI 설치
```bash
# Windows
choco install awscli

# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### 2. Terraform 설치
```bash
# Windows
choco install terraform

# macOS
brew install terraform

# Linux
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

### 3. Python 3.11 설치
```bash
# Windows
choco install python --version=3.11

# macOS
brew install python@3.11

# Linux
sudo apt-get install python3.11
```

## 배포 단계

### Step 1: AWS 자격 증명 설정

#### 방법 1: AWS CLI 설정 (권장)
```bash
aws configure
```

입력 정보:
- AWS Access Key ID: [YOUR_ACCESS_KEY]
- AWS Secret Access Key: [YOUR_SECRET_KEY]
- Default region name: us-east-2
- Default output format: json

#### 방법 2: 환경 변수 설정
```bash
# Windows (PowerShell)
$env:AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
$env:AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
$env:AWS_DEFAULT_REGION="us-east-2"

# Linux/macOS
export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
export AWS_DEFAULT_REGION="us-east-2"
```

### Step 2: Terraform 변수 설정

`awsTeam2/deployment/terraform/terraform.tfvars` 파일 생성:

```hcl
aws_region       = "us-east-2"
environment      = "prod"
project_name     = "hr-resource-optimization"
external_api_key = "YOUR_EXTERNAL_API_KEY"  # 선택사항
```

### Step 3: Lambda 함수 패키징

```bash
cd awsTeam2/deployment
python scripts/package_lambdas.py
```

이 스크립트는 자동으로:
- Lambda 함수 코드를 ZIP 파일로 패키징
- 필요한 Python 라이브러리를 Lambda Layer로 패키징
- `lambda_functions/` 및 `lambda_layers/` 디렉토리에 저장

### Step 4: Terraform 초기화

```bash
cd terraform
terraform init
```

### Step 5: 배포 계획 확인

```bash
terraform plan
```

생성될 리소스 확인:
- DynamoDB 테이블 6개
- S3 버킷 4개
- Lambda 함수 8개
- OpenSearch 도메인 1개
- API Gateway 1개
- IAM 역할 및 정책
- EventBridge 규칙

### Step 6: 인프라 배포

```bash
terraform apply
```

확인 메시지가 나오면 `yes` 입력

배포 시간: 약 15-20분

### Step 7: 테스트 데이터 로드

```bash
cd ../scripts
python load_test_data.py
```

이 스크립트는 자동으로:
- DynamoDB 테이블에 테스트 데이터 삽입
- S3 버킷에 샘플 이력서 업로드
- OpenSearch 인덱스 생성 및 초기 데이터 로드

### Step 8: 배포 확인

```bash
# API Gateway URL 확인
terraform output api_gateway_url

# OpenSearch 엔드포인트 확인
terraform output opensearch_endpoint

# Lambda 함수 목록 확인
aws lambda list-functions --query "Functions[?Tags.Team=='Team2'].FunctionName"

# DynamoDB 테이블 확인
aws dynamodb list-tables --query "TableNames[?contains(@, 'Employees') || contains(@, 'Projects')]"
```

## 원클릭 배포 스크립트

전체 과정을 자동화한 스크립트:

### Windows (PowerShell)
```powershell
.\deploy.ps1 -AccessKey "YOUR_ACCESS_KEY" -SecretKey "YOUR_SECRET_KEY"
```

### Linux/macOS
```bash
./deploy.sh YOUR_ACCESS_KEY YOUR_SECRET_KEY
```

## 배포 후 설정

### 1. Bedrock 모델 액세스 활성화

AWS Console에서:
1. Bedrock 서비스로 이동
2. Model access 메뉴 선택
3. Claude v2 및 Titan Embeddings 모델 활성화

### 2. OpenSearch 인덱스 생성

```bash
python scripts/create_opensearch_indices.py
```

### 3. 프론트엔드 배포

```bash
cd ../frontend
npm install
npm run build
aws s3 sync dist/ s3://hr-resource-optimization-frontend-hosting-prod/
```

## 리소스 정리

전체 인프라 삭제:

```bash
cd terraform
terraform destroy
```

확인 메시지가 나오면 `yes` 입력

## 트러블슈팅

### 문제 1: Terraform 초기화 실패
```bash
# 캐시 삭제 후 재시도
rm -rf .terraform
terraform init
```

### 문제 2: Lambda 함수 배포 실패
```bash
# Lambda 패키지 재생성
cd ../scripts
python package_lambdas.py --force
cd ../terraform
terraform apply
```

### 문제 3: OpenSearch 도메인 생성 실패
- OpenSearch 도메인 이름이 이미 사용 중인지 확인
- VPC 설정이 올바른지 확인
- 계정의 서비스 할당량 확인

### 문제 4: IAM 권한 오류
```bash
# 현재 사용자의 권한 확인
aws sts get-caller-identity
aws iam get-user
```

필요한 권한:
- IAM 역할 생성 및 관리
- Lambda 함수 생성 및 관리
- DynamoDB 테이블 생성 및 관리
- S3 버킷 생성 및 관리
- OpenSearch 도메인 생성 및 관리
- API Gateway 생성 및 관리

### 문제 5: Team2 태그 접근 제어 오류
```bash
# 모든 리소스에 Team2 태그가 있는지 확인
aws resourcegroupstaggingapi get-resources --tag-filters Key=Team,Values=Team2

# 특정 리소스에 태그 추가
aws lambda tag-resource --resource arn:aws:lambda:us-east-2:ACCOUNT_ID:function:FUNCTION_NAME --tags Team=Team2
```

## 비용 예상

월간 예상 비용 (us-east-2 기준):

| 서비스 | 예상 비용 |
|--------|----------|
| Lambda | $50-100 |
| DynamoDB | $30-50 |
| S3 | $10-20 |
| OpenSearch | $150-200 |
| API Gateway | $20-30 |
| Bedrock | $100-200 (사용량에 따라) |
| **총계** | **$360-600/월** |

비용 절감 팁:
- 개발 환경에서는 OpenSearch 인스턴스 크기 축소
- 사용하지 않는 시간에는 리소스 중지
- S3 Lifecycle 정책 활용
- Lambda 메모리 및 타임아웃 최적화

## 지원

문제가 발생하면:
1. CloudWatch Logs 확인
2. Terraform 상태 파일 확인
3. AWS Support 문의

## 다음 단계

배포 완료 후:
1. API 엔드포인트 테스트
2. 프론트엔드 연동
3. 모니터링 대시보드 설정
4. 알림 설정
5. 백업 정책 구성
