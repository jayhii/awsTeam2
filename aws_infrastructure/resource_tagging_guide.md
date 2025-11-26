# Team2 리소스 태깅 가이드

## 개요
모든 AWS 리소스는 Team2 태그를 포함해야 하며, IAM 정책을 통해 태그 기반 접근 제어가 적용됩니다.

## 필수 태그

모든 리소스에 다음 태그를 적용해야 합니다:

```json
{
  "Team": "Team2",
  "Project": "HR-Resource-Optimization",
  "Environment": "dev|staging|prod"
}
```

## 리소스별 태깅 요구사항

### 1. Lambda 함수
- **태그**: Team=Team2, Project=HR-Resource-Optimization, Environment=prod
- **IAM 역할**: LambdaExecutionRole-Team2
- **접근 제어**: Team2 태그가 있는 Lambda만 실행 가능

**적용 예시**:
```json
{
  "FunctionName": "ResumeParser",
  "Role": "arn:aws:iam::ACCOUNT_ID:role/LambdaExecutionRole-Team2",
  "Tags": {
    "Team": "Team2",
    "Project": "HR-Resource-Optimization",
    "Environment": "prod"
  }
}
```

### 2. DynamoDB 테이블
- **태그**: Team=Team2, Project=HR-Resource-Optimization
- **접근 제어**: Team2 태그가 있는 테이블만 Lambda에서 접근 가능

**적용 예시**:
```json
{
  "TableName": "Employees",
  "Tags": [
    {"Key": "Team", "Value": "Team2"},
    {"Key": "Project", "Value": "HR-Resource-Optimization"}
  ]
}
```

**테이블 목록**:
- Employees
- Projects
- EmployeeAffinity
- MessengerLogs
- CompanyEvents
- TechTrends

### 3. S3 버킷
- **태그**: Team=Team2, Project=HR-Resource-Optimization
- **접근 제어**: Team2 태그가 있는 버킷만 Lambda에서 접근 가능

**적용 예시**:
```bash
aws s3api put-bucket-tagging \
  --bucket hr-resumes-bucket \
  --tagging 'TagSet=[{Key=Team,Value=Team2},{Key=Project,Value=HR-Resource-Optimization}]'
```

**버킷 목록**:
- hr-frontend-hosting
- hr-resumes-bucket
- hr-reports-bucket
- hr-data-lake

### 4. OpenSearch 도메인
- **태그**: Team=Team2, Project=HR-Resource-Optimization
- **접근 제어**: Team2 태그가 있는 도메인만 Lambda에서 접근 가능

**적용 예시**:
```json
{
  "DomainName": "hr-employee-search",
  "Tags": [
    {"Key": "Team", "Value": "Team2"},
    {"Key": "Project", "Value": "HR-Resource-Optimization"}
  ]
}
```

### 5. API Gateway
- **태그**: Team=Team2, Project=HR-Resource-Optimization
- **IAM 역할**: APIGatewayExecutionRole-Team2

**적용 예시**:
```bash
aws apigateway tag-resource \
  --resource-arn arn:aws:apigateway:REGION::/restapis/API_ID \
  --tags Team=Team2,Project=HR-Resource-Optimization
```

## IAM 정책 예시

### Lambda 실행 역할 정책
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/*",
      "Condition": {
        "StringEquals": {
          "aws:ResourceTag/Team": "Team2"
        }
      }
    }
  ]
}
```

### S3 접근 정책
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::*/*",
      "Condition": {
        "StringEquals": {
          "aws:ResourceTag/Team": "Team2"
        }
      }
    }
  ]
}
```

## 태그 적용 스크립트

### DynamoDB 테이블 태깅
```bash
#!/bin/bash

TABLES=("Employees" "Projects" "EmployeeAffinity" "MessengerLogs" "CompanyEvents" "TechTrends")

for table in "${TABLES[@]}"; do
  aws dynamodb tag-resource \
    --resource-arn arn:aws:dynamodb:REGION:ACCOUNT_ID:table/$table \
    --tags Key=Team,Value=Team2 Key=Project,Value=HR-Resource-Optimization
  echo "Tagged table: $table"
done
```

### S3 버킷 태깅
```bash
#!/bin/bash

BUCKETS=("hr-frontend-hosting" "hr-resumes-bucket" "hr-reports-bucket" "hr-data-lake")

for bucket in "${BUCKETS[@]}"; do
  aws s3api put-bucket-tagging \
    --bucket $bucket \
    --tagging "TagSet=[{Key=Team,Value=Team2},{Key=Project,Value=HR-Resource-Optimization}]"
  echo "Tagged bucket: $bucket"
done
```

### Lambda 함수 태깅
```bash
#!/bin/bash

FUNCTIONS=("ResumeParser" "AffinityScoreCalculator" "ProjectRecommendationEngine" "DomainAnalysisEngine" "QuantitativeAnalysis" "QualitativeAnalysis" "TechTrendCollector" "VectorEmbeddingGenerator")

for func in "${FUNCTIONS[@]}"; do
  aws lambda tag-resource \
    --resource arn:aws:lambda:REGION:ACCOUNT_ID:function:$func \
    --tags Team=Team2,Project=HR-Resource-Optimization,Environment=prod
  echo "Tagged function: $func"
done
```

## 태그 검증

### 모든 Team2 리소스 조회
```bash
# Lambda 함수
aws lambda list-functions --query "Functions[?Tags.Team=='Team2'].FunctionName"

# DynamoDB 테이블
aws resourcegroupstaggingapi get-resources \
  --resource-type-filters dynamodb:table \
  --tag-filters Key=Team,Values=Team2

# S3 버킷
aws resourcegroupstaggingapi get-resources \
  --resource-type-filters s3:bucket \
  --tag-filters Key=Team,Values=Team2
```

## 주의사항

1. **모든 신규 리소스는 생성 시 반드시 Team2 태그를 포함해야 합니다**
2. **태그가 없는 리소스는 Lambda 함수에서 접근할 수 없습니다**
3. **IAM 정책은 태그 기반 접근 제어를 강제합니다**
4. **Environment 태그는 dev, staging, prod 중 하나여야 합니다**
5. **태그 변경 시 IAM 정책 캐시로 인해 최대 5분의 지연이 발생할 수 있습니다**

## 문제 해결

### Lambda 함수가 DynamoDB에 접근할 수 없는 경우
1. DynamoDB 테이블에 Team=Team2 태그가 있는지 확인
2. Lambda 함수의 IAM 역할이 LambdaExecutionRole-Team2인지 확인
3. Lambda 함수에 Team=Team2 태그가 있는지 확인

### S3 버킷 접근 오류
1. S3 버킷에 Team=Team2 태그가 있는지 확인
2. Lambda 실행 역할에 S3 접근 정책이 포함되어 있는지 확인
3. 버킷 정책에서 태그 기반 접근을 허용하는지 확인
