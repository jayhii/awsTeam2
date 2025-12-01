# 이력서 업로드 기능 문제 해결 가이드

## 🔍 문제 진단 체크리스트

이력서 업로드 기능이 동작하지 않을 때 다음 항목들을 순서대로 확인하세요.

## 1️⃣ 인프라 구성 요소 확인

### S3 버킷 확인

```bash
# 이력서 버킷이 존재하는지 확인
aws s3 ls | grep resume

# 예상 출력: hr-resource-optimization-resumes-prod
```

**버킷이 없는 경우:**
```bash
# Terraform으로 생성
cd deployment/terraform
terraform apply -target=aws_s3_bucket.resumes
```

### Lambda 함수 확인

```bash
# resume 관련 Lambda 함수 확인
aws lambda list-functions --query 'Functions[?contains(FunctionName, `resume`)].{Name:FunctionName, Runtime:Runtime, Status:State}' --output table
```

**예상 출력:**
- `hr-resource-optimization-resume-upload-prod` (Python 3.11)
- `hr-resource-optimization-resume-parser-prod` (Python 3.11)

**Lambda 함수가 없는 경우:**
```bash
cd deployment/terraform
terraform apply -target=aws_lambda_function.resume_upload
terraform apply -target=aws_lambda_function.resume_parser
```

### API Gateway 엔드포인트 확인

```bash
# API Gateway URL 확인
cd deployment/terraform
terraform output api_gateway_url

# 예상 출력: https://xxxxxxxxxx.execute-api.ap-northeast-2.amazonaws.com/prod
```

**엔드포인트 테스트:**
```bash
# /resume/upload-url 엔드포인트 테스트
curl -X POST https://YOUR_API_URL/prod/resume/upload-url \
  -H "Content-Type: application/json" \
  -d '{"file_name": "test.pdf", "content_type": "application/pdf"}'
```

## 2️⃣ 권한 설정 확인

### Lambda 실행 역할 권한

```bash
# Lambda 함수의 실행 역할 확인
aws lambda get-function --function-name hr-resource-optimization-resume-upload-prod \
  --query 'Configuration.Role'

# 역할의 정책 확인
aws iam list-attached-role-policies --role-name hr-resource-optimization-lambda-role
```

**필요한 권한:**
- ✅ S3 PutObject (이력서 버킷)
- ✅ S3 GetObject (이력서 버킷)
- ✅ Textract DetectDocumentText
- ✅ Bedrock InvokeModel
- ✅ DynamoDB PutItem, GetItem, UpdateItem
- ✅ CloudWatch Logs 쓰기

### S3 버킷 정책 확인

```bash
# 버킷 정책 확인
aws s3api get-bucket-policy --bucket hr-resource-optimization-resumes-prod
```

### CORS 설정 확인

```bash
# S3 버킷 CORS 설정 확인
aws s3api get-bucket-cors --bucket hr-resource-optimization-resumes-prod
```

**CORS가 설정되지 않은 경우:**
```bash
# CORS 설정 추가
aws s3api put-bucket-cors --bucket hr-resource-optimization-resumes-prod --cors-configuration file://cors-config.json
```

`cors-config.json`:
```json
{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3000
    }
  ]
}
```

## 3️⃣ 프론트엔드 설정 확인

### 환경 변수 확인

`frontend/.env` 파일을 확인하세요:

```bash
# .env 파일 확인
cat frontend/.env
```

**필수 환경 변수:**
```env
VITE_API_BASE_URL=https://xxxxxxxxxx.execute-api.ap-northeast-2.amazonaws.com/prod
```

**환경 변수가 없거나 잘못된 경우:**
```bash
# API Gateway URL 가져오기
cd deployment/terraform
API_URL=$(terraform output -raw api_gateway_url)

# .env 파일 업데이트
echo "VITE_API_BASE_URL=$API_URL" > frontend/.env

# 프론트엔드 재시작
cd frontend
npm run dev
```

### 브라우저 콘솔 확인

1. 브라우저 개발자 도구 열기 (F12)
2. Console 탭에서 에러 메시지 확인
3. Network 탭에서 API 요청 확인

**일반적인 에러:**

#### CORS 에러
```
Access to fetch at 'https://...' from origin 'http://localhost:5173' has been blocked by CORS policy
```

**해결 방법:**
```bash
# API Gateway CORS 재배포
cd deployment
python enable_cors.py
```

#### 404 Not Found
```
POST https://.../resume/upload-url 404 (Not Found)
```

**해결 방법:**
```bash
# API Gateway 재배포
cd deployment/terraform
terraform apply
```

#### 500 Internal Server Error
```
POST https://.../resume/upload-url 500 (Internal Server Error)
```

**해결 방법:**
```bash
# Lambda 로그 확인
aws logs tail /aws/lambda/hr-resource-optimization-resume-upload-prod --follow
```

## 4️⃣ Lambda 함수 로그 확인

### resume-upload Lambda 로그

```bash
# 최근 로그 확인
aws logs tail /aws/lambda/hr-resource-optimization-resume-upload-prod --since 10m

# 실시간 로그 모니터링
aws logs tail /aws/lambda/hr-resource-optimization-resume-upload-prod --follow
```

**일반적인 에러:**

#### 환경 변수 누락
```
KeyError: 'RESUMES_BUCKET'
```

**해결 방법:**
```bash
# Lambda 환경 변수 설정
aws lambda update-function-configuration \
  --function-name hr-resource-optimization-resume-upload-prod \
  --environment Variables={RESUMES_BUCKET=hr-resource-optimization-resumes-prod}
```

#### S3 권한 부족
```
botocore.exceptions.ClientError: An error occurred (AccessDenied) when calling the PutObject operation
```

**해결 방법:**
```bash
# Lambda 실행 역할에 S3 권한 추가
cd deployment/terraform
terraform apply -target=aws_iam_role_policy.lambda_s3_policy
```

### resume-parser Lambda 로그

```bash
# 최근 로그 확인
aws logs tail /aws/lambda/hr-resource-optimization-resume-parser-prod --since 10m

# 실시간 로그 모니터링
aws logs tail /aws/lambda/hr-resource-optimization-resume-parser-prod --follow
```

**일반적인 에러:**

#### Textract 권한 부족
```
botocore.exceptions.ClientError: An error occurred (AccessDeniedException) when calling the DetectDocumentText operation
```

**해결 방법:**
```bash
# Lambda 실행 역할에 Textract 권한 추가
cd deployment/terraform
terraform apply -target=aws_iam_role_policy.lambda_textract_policy
```

#### Bedrock 권한 부족
```
botocore.exceptions.ClientError: An error occurred (AccessDeniedException) when calling the InvokeModel operation
```

**해결 방법:**
```bash
# Bedrock 권한 추가
python deployment/add_bedrock_permission.py
```

## 5️⃣ 엔드투엔드 테스트

### 수동 테스트 스크립트

```bash
# test_resume_upload.sh
#!/bin/bash

API_URL="https://YOUR_API_URL/prod"
TEST_FILE="test_data/sample_resume_choi_jungwoo.pdf"

echo "1. Presigned URL 요청..."
RESPONSE=$(curl -s -X POST "$API_URL/resume/upload-url" \
  -H "Content-Type: application/json" \
  -d '{"file_name": "test_resume.pdf", "content_type": "application/pdf"}')

echo "Response: $RESPONSE"

UPLOAD_URL=$(echo $RESPONSE | jq -r '.upload_url')
FILE_KEY=$(echo $RESPONSE | jq -r '.file_key')

echo "2. S3에 파일 업로드..."
curl -X PUT "$UPLOAD_URL" \
  -H "Content-Type: application/pdf" \
  --data-binary "@$TEST_FILE"

echo "3. S3에서 파일 확인..."
aws s3 ls s3://hr-resource-optimization-resumes-prod/uploads/

echo "4. Lambda 로그 확인..."
sleep 5
aws logs tail /aws/lambda/hr-resource-optimization-resume-parser-prod --since 1m
```

### Python 테스트 스크립트

```python
# test_resume_upload.py
import requests
import json

API_URL = "https://YOUR_API_URL/prod"
TEST_FILE = "test_data/sample_resume_choi_jungwoo.pdf"

# 1. Presigned URL 요청
print("1. Presigned URL 요청...")
response = requests.post(
    f"{API_URL}/resume/upload-url",
    json={
        "file_name": "test_resume.pdf",
        "content_type": "application/pdf"
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

if response.status_code == 200:
    data = response.json()
    upload_url = data['upload_url']
    file_key = data['file_key']
    
    # 2. S3에 파일 업로드
    print("\n2. S3에 파일 업로드...")
    with open(TEST_FILE, 'rb') as f:
        upload_response = requests.put(
            upload_url,
            data=f,
            headers={'Content-Type': 'application/pdf'}
        )
    
    print(f"Upload Status: {upload_response.status_code}")
    
    if upload_response.status_code == 200:
        print("✅ 업로드 성공!")
        print(f"File Key: {file_key}")
    else:
        print("❌ 업로드 실패!")
else:
    print("❌ Presigned URL 생성 실패!")
```

## 6️⃣ 일반적인 문제와 해결 방법

### 문제 1: "업로드 URL 생성 실패"

**원인:**
- Lambda 함수가 배포되지 않음
- API Gateway 통합이 잘못됨
- Lambda 실행 역할 권한 부족

**해결:**
```bash
# 1. Lambda 함수 재배포
cd deployment/terraform
terraform apply -target=aws_lambda_function.resume_upload

# 2. API Gateway 재배포
terraform apply -target=aws_api_gateway_deployment.hr_api

# 3. 권한 확인
aws lambda get-function-configuration \
  --function-name hr-resource-optimization-resume-upload-prod \
  --query 'Role'
```

### 문제 2: "파일 업로드 실패"

**원인:**
- Presigned URL이 만료됨 (1시간 유효)
- S3 버킷 정책 문제
- CORS 설정 문제

**해결:**
```bash
# 1. 새로운 Presigned URL 요청
# 2. S3 버킷 정책 확인
aws s3api get-bucket-policy --bucket hr-resource-optimization-resumes-prod

# 3. CORS 설정 확인
aws s3api get-bucket-cors --bucket hr-resource-optimization-resumes-prod
```

### 문제 3: "파싱이 시작되지 않음"

**원인:**
- S3 이벤트 트리거가 설정되지 않음
- Lambda 함수가 S3 이벤트를 받지 못함

**해결:**
```bash
# S3 이벤트 알림 설정 확인
aws s3api get-bucket-notification-configuration \
  --bucket hr-resource-optimization-resumes-prod

# Terraform으로 재설정
cd deployment/terraform
terraform apply -target=aws_s3_bucket_notification.resume_upload
```

### 문제 4: "Textract 에러"

**원인:**
- Textract 권한 부족
- 지원하지 않는 파일 형식
- 파일이 너무 큼

**해결:**
```bash
# 1. Textract 권한 추가
cd deployment/terraform
terraform apply -target=aws_iam_role_policy.lambda_textract_policy

# 2. 파일 형식 확인 (PDF만 지원)
# 3. 파일 크기 확인 (10MB 이하)
```

### 문제 5: "Bedrock 에러"

**원인:**
- Bedrock 권한 부족
- Bedrock 모델 액세스가 활성화되지 않음
- 잘못된 모델 ID

**해결:**
```bash
# 1. Bedrock 권한 추가
python deployment/add_bedrock_permission.py

# 2. Bedrock 모델 액세스 활성화
# AWS Console > Bedrock > Model access > Enable models

# 3. 사용 가능한 모델 확인
python deployment/check_available_models.py
```

## 7️⃣ 모니터링 및 알림 설정

### CloudWatch 대시보드 생성

```bash
# 모니터링 설정
cd deployment
./setup_monitoring.ps1
```

### CloudWatch 알람 설정

```bash
# Lambda 에러 알람
aws cloudwatch put-metric-alarm \
  --alarm-name resume-upload-errors \
  --alarm-description "Resume upload Lambda errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=hr-resource-optimization-resume-upload-prod
```

## 8️⃣ 완전 재배포

모든 방법이 실패한 경우, 완전히 재배포하세요:

```bash
# 1. 기존 리소스 제거
cd deployment/terraform
terraform destroy -target=aws_lambda_function.resume_upload
terraform destroy -target=aws_lambda_function.resume_parser
terraform destroy -target=aws_s3_bucket.resumes

# 2. 재배포
terraform apply

# 3. Lambda 함수 재패키징 및 업로드
cd ..
./package_lambdas.ps1

# 4. API Gateway 재배포
cd terraform
terraform apply -target=aws_api_gateway_deployment.hr_api

# 5. 프론트엔드 환경 변수 업데이트
API_URL=$(terraform output -raw api_gateway_url)
echo "VITE_API_BASE_URL=$API_URL" > ../../frontend/.env

# 6. 프론트엔드 재시작
cd ../../frontend
npm run dev
```

## 📞 추가 지원

위의 모든 방법을 시도해도 문제가 해결되지 않으면:

1. CloudWatch Logs에서 전체 에러 로그 수집
2. API Gateway 실행 로그 활성화 및 확인
3. X-Ray 트레이싱 활성화하여 요청 흐름 추적
4. 프로젝트 관리자에게 문의

---

**마지막 업데이트: 2025-12-01**
