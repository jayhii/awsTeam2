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
# OpenSearch 엔드포인트 확인
cd terraform
OPENSEARCH_ENDPOINT=$(terraform output -raw opensearch_endpoint)

# 인덱스 생성 스크립트 실행
cd ..
python create_opensearch_indices.py $OPENSEARCH_ENDPOINT
```

이 스크립트는 다음 인덱스를 생성합니다:
- `employee_profiles`: 직원 프로필 벡터 검색용 (1536차원 knn_vector)
- `project_requirements`: 프로젝트 요구사항 벡터 검색용 (1536차원 knn_vector)

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

**증상**: `terraform init` 실행 시 오류 발생

**원인**:
- 네트워크 연결 문제
- Terraform 버전 불일치
- 손상된 캐시 파일

**해결 방법**:
```bash
# 캐시 삭제 후 재시도
rm -rf .terraform .terraform.lock.hcl
terraform init

# 특정 버전의 provider 사용
terraform init -upgrade

# 프록시 환경에서 실행 시
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
terraform init
```

### 문제 2: Lambda 함수 배포 실패

**증상**: Lambda 함수 생성 또는 업데이트 실패

**원인**:
- ZIP 파일 크기 초과 (50MB 제한)
- 잘못된 핸들러 경로
- IAM 역할 권한 부족
- 의존성 패키징 오류

**해결 방법**:
```bash
# Lambda 패키지 재생성
cd deployment
python package_lambdas.py --force

# ZIP 파일 크기 확인
ls -lh lambda_functions/*/*.zip

# 의존성 크기 줄이기 (불필요한 패키지 제거)
pip install --target ./package --no-deps boto3  # boto3는 Lambda에 기본 포함

# 핸들러 경로 확인
cd ../terraform
terraform state show aws_lambda_function.resume_parser | grep handler

# Lambda Layer 사용 (큰 의존성의 경우)
cd ../deployment
python package_lambda_layer.py
```

**Lambda 함수별 일반적인 오류**:

**Resume Parser**:
- Textract 권한 부족: IAM 정책에 `textract:DetectDocumentText` 추가
- S3 접근 오류: 버킷에 Team2 태그 확인

**Vector Embedding**:
- DynamoDB Stream 권한 부족: `dynamodb:GetRecords`, `dynamodb:GetShardIterator` 추가
- OpenSearch 연결 실패: 보안 그룹 및 네트워크 설정 확인

**Recommendation Engine**:
- OpenSearch 쿼리 타임아웃: Lambda 타임아웃 증가 (300초)
- 메모리 부족: Lambda 메모리 2048MB로 증가

### 문제 3: OpenSearch 도메인 생성 실패

**증상**: OpenSearch 도메인 생성 중 오류 발생

**원인**:
- 도메인 이름 중복
- 서비스 할당량 초과
- VPC 설정 오류
- 인스턴스 타입 미지원

**해결 방법**:

```bash
# 기존 도메인 확인
aws opensearch list-domain-names

# 서비스 할당량 확인
aws service-quotas get-service-quota \
  --service-code opensearch \
  --quota-code L-BC8F2E48

# 도메인 이름 변경 (terraform.tfvars)
opensearch_domain_name = "hr-optimization-v2"

# VPC 설정 확인
aws ec2 describe-vpcs
aws ec2 describe-subnets --filters "Name=vpc-id,Values=vpc-xxxxx"

# 인스턴스 타입 변경 (더 작은 인스턴스로 시작)
opensearch_instance_type = "t3.small.search"  # 개발 환경용
```

**OpenSearch 상태 확인**:
```bash
# 도메인 상태 확인
aws opensearch describe-domain --domain-name hr-resource-optimization-team2

# 클러스터 헬스 확인
curl -XGET "https://OPENSEARCH_ENDPOINT/_cluster/health?pretty"

# 인덱스 목록 확인
curl -XGET "https://OPENSEARCH_ENDPOINT/_cat/indices?v"
```

### 문제 4: IAM 권한 오류

**증상**: `AccessDenied` 또는 `UnauthorizedOperation` 오류

**원인**:
- 불충분한 IAM 권한
- 태그 기반 접근 제어 위반
- 리소스 정책 제한

**해결 방법**:

```bash
# 현재 사용자의 권한 확인
aws sts get-caller-identity
aws iam get-user
aws iam list-attached-user-policies --user-name YOUR_USERNAME

# 필요한 권한 확인
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::ACCOUNT_ID:user/YOUR_USERNAME \
  --action-names lambda:CreateFunction dynamodb:CreateTable \
  --resource-arns "*"
```

**필요한 최소 권한 정책**:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:AttachRolePolicy",
        "iam:PutRolePolicy",
        "iam:PassRole",
        "lambda:*",
        "dynamodb:*",
        "s3:*",
        "opensearch:*",
        "apigateway:*",
        "events:*",
        "logs:*",
        "cloudwatch:*",
        "sns:*"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "us-east-2"
        }
      }
    }
  ]
}
```

**태그 기반 접근 제어 문제**:
```bash
# 리소스에 Team2 태그가 있는지 확인
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Team,Values=Team2 \
  --resource-type-filters lambda dynamodb s3

# 누락된 태그 추가
aws lambda tag-resource \
  --resource arn:aws:lambda:us-east-2:ACCOUNT_ID:function:FUNCTION_NAME \
  --tags Team=Team2,Project=HR-Resource-Optimization

aws dynamodb tag-resource \
  --resource-arn arn:aws:dynamodb:us-east-2:ACCOUNT_ID:table/TABLE_NAME \
  --tags Key=Team,Value=Team2
```

### 문제 5: Team2 태그 접근 제어 오류

**증상**: Lambda 함수가 DynamoDB/S3/OpenSearch 접근 시 `AccessDenied` 오류

**원인**:
- 리소스에 Team2 태그 누락
- IAM 정책의 태그 조건 불일치
- 태그 전파 지연

**해결 방법**:

```bash
# 모든 리소스에 Team2 태그가 있는지 확인
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Team,Values=Team2 \
  --region us-east-2

# 특정 리소스 타입별 태그 확인
# Lambda 함수
aws lambda list-functions \
  --query "Functions[?Tags.Team=='Team2'].FunctionName"

# DynamoDB 테이블
aws dynamodb list-tables | jq -r '.TableNames[]' | while read table; do
  aws dynamodb describe-table --table-name $table \
    --query "Table.{Name:TableName,Tags:Tags}" --output json
done

# S3 버킷
aws s3api list-buckets --query "Buckets[].Name" --output text | while read bucket; do
  aws s3api get-bucket-tagging --bucket $bucket 2>/dev/null || echo "$bucket: No tags"
done

# 누락된 태그 일괄 추가 스크립트
python deployment/scripts/add_team2_tags.py
```

**태그 전파 확인**:
```bash
# Terraform으로 생성된 리소스의 태그 확인
cd terraform
terraform state list | while read resource; do
  terraform state show $resource | grep -A 5 "tags"
done
```

### 문제 6: DynamoDB 스로틀링

**증상**: `ProvisionedThroughputExceededException` 오류

**원인**:
- 읽기/쓰기 용량 부족
- 핫 파티션 (특정 키에 요청 집중)
- 버스트 용량 소진

**해결 방법**:

```bash
# 현재 용량 확인
aws dynamodb describe-table --table-name Employees-Team2 \
  --query "Table.{Read:ProvisionedThroughput.ReadCapacityUnits,Write:ProvisionedThroughput.WriteCapacityUnits}"

# On-Demand 모드로 전환 (권장)
aws dynamodb update-table \
  --table-name Employees-Team2 \
  --billing-mode PAY_PER_REQUEST

# 또는 Provisioned 용량 증가
aws dynamodb update-table \
  --table-name Employees-Team2 \
  --provisioned-throughput ReadCapacityUnits=50,WriteCapacityUnits=50

# 스로틀링 메트릭 확인
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name UserErrors \
  --dimensions Name=TableName,Value=Employees-Team2 \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

**핫 파티션 해결**:
- 파티션 키 설계 재검토
- 복합 키 사용 (파티션 키 + 정렬 키)
- 쓰기 샤딩 패턴 적용

### 문제 7: Bedrock API 호출 실패

**증상**: `ThrottlingException`, `ModelNotAvailableException` 오류

**원인**:
- 모델 액세스 미활성화
- API 호출 제한 초과
- 잘못된 모델 ID
- 리전 미지원

**해결 방법**:

```bash
# Bedrock 모델 액세스 확인
aws bedrock list-foundation-models --region us-east-2

# Claude 모델 활성화 (AWS Console에서 수동 작업 필요)
# 1. Bedrock 콘솔 접속
# 2. Model access 메뉴
# 3. Claude v2 및 Titan Embeddings 활성화

# 모델 호출 테스트
aws bedrock-runtime invoke-model \
  --model-id anthropic.claude-v2 \
  --body '{"prompt":"\n\nHuman: Hello\n\nAssistant:","max_tokens_to_sample":100}' \
  --region us-east-2 \
  output.json

# 할당량 확인
aws service-quotas get-service-quota \
  --service-code bedrock \
  --quota-code L-12345678 \
  --region us-east-2

# 할당량 증가 요청
aws service-quotas request-service-quota-increase \
  --service-code bedrock \
  --quota-code L-12345678 \
  --desired-value 1000 \
  --region us-east-2
```

**재시도 로직 구현** (Lambda 함수 내):
```python
import time
from botocore.exceptions import ClientError

def invoke_bedrock_with_retry(client, model_id, body, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.invoke_model(
                modelId=model_id,
                body=body
            )
            return response
        except ClientError as e:
            if e.response['Error']['Code'] == 'ThrottlingException':
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
            else:
                raise
    raise Exception("Max retries exceeded")
```

### 문제 8: API Gateway 타임아웃

**증상**: API 요청이 30초 후 타임아웃

**원인**:
- Lambda 함수 실행 시간 초과
- 다운스트림 서비스 지연 (Bedrock, OpenSearch)
- 비효율적인 쿼리

**해결 방법**:

```bash
# Lambda 타임아웃 증가
aws lambda update-function-configuration \
  --function-name RecommendationEngine \
  --timeout 300

# API Gateway 통합 타임아웃 확인 (최대 29초)
# 장시간 작업은 비동기 패턴 사용 권장

# CloudWatch Logs에서 느린 쿼리 확인
aws logs filter-log-events \
  --log-group-name /aws/lambda/RecommendationEngine \
  --filter-pattern "[time > 5000]"  # 5초 이상 소요된 요청
```

**비동기 패턴 구현**:
1. 요청 접수 시 작업 ID 반환
2. 백그라운드에서 Lambda 비동기 실행
3. 별도 API로 작업 상태 조회

### 문제 9: 프론트엔드 배포 실패

**증상**: S3 정적 웹사이트 호스팅 접근 불가

**원인**:
- 버킷 정책 미설정
- CORS 설정 누락
- CloudFront 캐시 문제

**해결 방법**:

```bash
# 버킷 정책 확인
aws s3api get-bucket-policy --bucket hr-resource-optimization-frontend-hosting-prod

# 퍼블릭 액세스 설정
aws s3api put-bucket-policy --bucket hr-resource-optimization-frontend-hosting-prod --policy '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::hr-resource-optimization-frontend-hosting-prod/*"
  }]
}'

# 웹사이트 호스팅 활성화
aws s3 website s3://hr-resource-optimization-frontend-hosting-prod/ \
  --index-document index.html \
  --error-document error.html

# CORS 설정
aws s3api put-bucket-cors --bucket hr-resource-optimization-frontend-hosting-prod --cors-configuration '{
  "CORSRules": [{
    "AllowedOrigins": ["*"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3000
  }]
}'

# CloudFront 캐시 무효화 (CloudFront 사용 시)
aws cloudfront create-invalidation \
  --distribution-id DISTRIBUTION_ID \
  --paths "/*"
```

### 문제 10: 테스트 데이터 로드 실패

**증상**: `load_test_data.py` 실행 시 오류

**원인**:
- DynamoDB 테이블 미생성
- 데이터 형식 오류
- 배치 쓰기 제한 초과

**해결 방법**:

```bash
# 테이블 존재 확인
aws dynamodb list-tables | grep Team2

# 테이블 상태 확인
aws dynamodb describe-table --table-name Employees-Team2 \
  --query "Table.TableStatus"

# 데이터 형식 검증
python -c "import json; json.load(open('test_data/employees_extended.json'))"

# 배치 크기 조정 (스크립트 내)
# batch_size = 25에서 10으로 감소

# 수동으로 단일 항목 삽입 테스트
aws dynamodb put-item \
  --table-name Employees-Team2 \
  --item file://test_item.json
```

### 문제 11: 로그 확인 및 디버깅

**일반적인 디버깅 절차**:

```bash
# 1. CloudWatch Logs 확인
aws logs tail /aws/lambda/FUNCTION_NAME --follow

# 2. 최근 에러 로그 필터링
aws logs filter-log-events \
  --log-group-name /aws/lambda/FUNCTION_NAME \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s)000

# 3. Lambda 함수 직접 호출 테스트
aws lambda invoke \
  --function-name FUNCTION_NAME \
  --payload '{"test": "data"}' \
  --log-type Tail \
  response.json

# 4. X-Ray 트레이싱 활성화 (성능 분석)
aws lambda update-function-configuration \
  --function-name FUNCTION_NAME \
  --tracing-config Mode=Active

# 5. 환경 변수 확인
aws lambda get-function-configuration \
  --function-name FUNCTION_NAME \
  --query "Environment"
```

### 긴급 복구 절차

**전체 시스템 장애 시**:

1. **상태 확인**:
```bash
# 모든 Lambda 함수 상태
aws lambda list-functions --query "Functions[?Tags.Team=='Team2'].{Name:FunctionName,State:State}"

# DynamoDB 테이블 상태
aws dynamodb list-tables | grep Team2 | while read table; do
  aws dynamodb describe-table --table-name $table --query "Table.{Name:TableName,Status:TableStatus}"
done

# OpenSearch 클러스터 상태
aws opensearch describe-domain --domain-name hr-resource-optimization-team2 \
  --query "DomainStatus.{Status:DomainStatus,Health:ClusterConfig.InstanceType}"
```

2. **롤백**:
```bash
cd terraform
terraform state pull > backup.tfstate
terraform apply -target=aws_lambda_function.FUNCTION_NAME -auto-approve
```

3. **데이터 복구**:
```bash
# DynamoDB Point-in-Time Recovery
aws dynamodb restore-table-to-point-in-time \
  --source-table-name Employees-Team2 \
  --target-table-name Employees-Team2-Restored \
  --restore-date-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S)

# S3 버전 복구
aws s3api list-object-versions --bucket BUCKET_NAME --prefix KEY
aws s3api get-object --bucket BUCKET_NAME --key KEY --version-id VERSION_ID restored_file
```

### 지원 요청

문제가 해결되지 않으면:

1. **로그 수집**:
```bash
# 진단 정보 수집 스크립트
bash deployment/scripts/collect_diagnostics.sh > diagnostics.log
```

2. **AWS Support 케이스 생성**:
- AWS Console > Support Center
- 케이스 유형: Technical Support
- 서비스: 해당 서비스 선택
- 로그 파일 첨부

3. **커뮤니티 지원**:
- GitHub Issues
- AWS re:Post
- Stack Overflow (태그: aws, terraform, lambda)

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

## 모니터링 및 알림 설정

### 1. CloudWatch 대시보드 확인

배포 후 자동으로 생성된 대시보드:

```bash
# 대시보드 이름 확인
cd terraform
terraform output cloudwatch_dashboards
```

생성된 대시보드:
- **HR-Lambda-Metrics-Team2**: Lambda 함수 메트릭 (호출 수, 에러, 지속 시간, 스로틀링)
- **HR-API-Gateway-Metrics-Team2**: API Gateway 메트릭 (요청 수, 에러, 레이턴시)
- **HR-DynamoDB-Metrics-Team2**: DynamoDB 메트릭 (읽기/쓰기 용량, 에러, 스로틀링)

AWS Console에서 확인:
1. CloudWatch 서비스로 이동
2. 왼쪽 메뉴에서 "Dashboards" 선택
3. 위 대시보드 이름으로 검색

### 2. SNS 알림 구독 설정

알림을 받을 이메일 주소 설정:

#### 방법 1: Terraform 변수로 설정 (권장)

`terraform.tfvars` 파일에 추가:
```hcl
alarm_email_addresses = [
  "admin@example.com",
  "devops@example.com"
]
```

그 후 재배포:
```bash
terraform apply
```

#### 방법 2: AWS Console에서 수동 설정

1. SNS 서비스로 이동
2. "Topics" 메뉴에서 `hr-resource-optimization-alarms-team2` 선택
3. "Create subscription" 클릭
4. Protocol: Email 선택
5. Endpoint: 이메일 주소 입력
6. "Create subscription" 클릭
7. 이메일 확인 링크 클릭

### 3. CloudWatch 알람 확인

자동으로 생성된 알람:

**Lambda 에러 알람** (8개):
- `lambda-errors-resume-parser-team2`
- `lambda-errors-affinity-calculator-team2`
- `lambda-errors-recommendation-engine-team2`
- `lambda-errors-domain-analysis-team2`
- `lambda-errors-quantitative-analysis-team2`
- `lambda-errors-qualitative-analysis-team2`
- `lambda-errors-tech-trend-collector-team2`
- `lambda-errors-vector-embedding-team2`

**API Gateway 알람** (2개):
- `api-gateway-latency-team2`: 레이턴시 > 5초
- `api-gateway-5xx-errors-team2`: 5XX 에러 > 10건

**DynamoDB 스로틀링 알람** (6개):
- `dynamodb-read-throttle-employees-team2`
- `dynamodb-write-throttle-employees-team2`
- `dynamodb-read-throttle-projects-team2`
- `dynamodb-write-throttle-projects-team2`
- `dynamodb-read-throttle-affinity-team2`
- `dynamodb-write-throttle-affinity-team2`

알람 임계값:
- Lambda 에러: 5분 동안 5건 이상
- API Gateway 레이턴시: 5분 평균 5초 이상
- API Gateway 5XX 에러: 5분 동안 10건 이상
- DynamoDB 스로틀링: 5분 동안 5건 이상

### 4. 알람 테스트

알람이 정상 작동하는지 테스트:

```bash
# Lambda 함수 에러 발생 테스트
aws lambda invoke \
  --function-name ResumeParser \
  --payload '{"invalid": "data"}' \
  response.json

# API Gateway 엔드포인트 테스트
curl -X POST https://YOUR_API_ID.execute-api.us-east-2.amazonaws.com/prod/recommendations \
  -H "Content-Type: application/json" \
  -d '{"invalid": "data"}'
```

### 5. 커스텀 알람 추가

추가 알람이 필요한 경우 `deployment/terraform/monitoring.tf` 파일에 추가:

```hcl
resource "aws_cloudwatch_metric_alarm" "custom_alarm" {
  alarm_name          = "custom-alarm-team2"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "YourMetric"
  namespace           = "AWS/YourService"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "커스텀 알람 설명"
  alarm_actions       = [aws_sns_topic.hr_alarms.arn]
  
  dimensions = {
    YourDimension = "YourValue"
  }
  
  tags = {
    Team        = "Team2"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}
```

### 6. 로그 모니터링

CloudWatch Logs에서 Lambda 함수 로그 확인:

```bash
# 최근 로그 확인
aws logs tail /aws/lambda/ResumeParser --follow

# 에러 로그만 필터링
aws logs filter-log-events \
  --log-group-name /aws/lambda/ResumeParser \
  --filter-pattern "ERROR"

# 특정 기간 로그 조회
aws logs filter-log-events \
  --log-group-name /aws/lambda/ResumeParser \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --end-time $(date +%s)000
```

### 7. 메트릭 확인

주요 메트릭 조회:

```bash
# Lambda 함수 호출 수
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=ResumeParser \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# API Gateway 요청 수
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiName,Value=HR-Resource-Optimization-API \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

## 다음 단계

배포 완료 후:
1. API 엔드포인트 테스트
2. 프론트엔드 연동
3. 모니터링 대시보드 확인 및 알림 구독
4. 백업 정책 구성
5. 성능 최적화
