# 데이터 로드 가이드

## 개요
생성된 300명의 직원 데이터와 2000개의 메신저 로그를 AWS 서비스에 반영하는 방법입니다.

## 사전 요구사항

1. AWS CLI 설정 완료
2. DynamoDB 테이블 생성 완료 (`Employees`, `MessengerLogs`)
3. 적절한 IAM 권한 (DynamoDB 쓰기 권한)

## 빠른 실행

### Windows (PowerShell)
```powershell
cd deployment
python load_extended_data.py
```

### Linux/macOS
```bash
cd deployment
python3 load_extended_data.py
```

## 단계별 실행

### 1. AWS 자격 증명 확인
```bash
aws sts get-caller-identity
```

### 2. DynamoDB 테이블 확인
```bash
aws dynamodb list-tables --region us-east-2
```

`Employees`와 `MessengerLogs` 테이블이 있어야 합니다.

### 3. 데이터 로드 실행
```bash
cd deployment
python load_extended_data.py
```

예상 소요 시간: 2-3분

### 4. 데이터 확인
```bash
# 직원 수 확인
aws dynamodb scan --table-name Employees --select COUNT --region us-east-2

# 메신저 로그 수 확인
aws dynamodb scan --table-name MessengerLogs --select COUNT --region us-east-2
```


## 자동 처리 흐름

데이터 로드 후 자동으로 실행되는 프로세스:

1. **DynamoDB → Lambda (Vector Embedding)**
   - DynamoDB Stream이 변경 감지
   - `VectorEmbedding` Lambda 함수 자동 트리거
   - Bedrock으로 임베딩 생성

2. **Lambda → OpenSearch**
   - 생성된 벡터를 OpenSearch에 저장
   - `employee_profiles` 인덱스에 색인

3. **검색 가능**
   - API를 통해 직원 검색 및 추천 가능

## 문제 해결

### 오류: "Table not found"
```bash
# 테이블 생성 (Terraform 사용)
cd deployment/terraform
terraform apply
```

### 오류: "AccessDenied"
```bash
# IAM 권한 확인
aws iam get-user
aws iam list-attached-user-policies --user-name YOUR_USERNAME
```

필요한 권한: `dynamodb:PutItem`, `dynamodb:BatchWriteItem`

### 오류: "ProvisionedThroughputExceededException"
```bash
# On-Demand 모드로 전환
aws dynamodb update-table --table-name Employees --billing-mode PAY_PER_REQUEST
aws dynamodb update-table --table-name MessengerLogs --billing-mode PAY_PER_REQUEST
```

## 개별 로드 (선택사항)

직원 데이터만 로드:
```bash
cd deployment
python load_employees.py
```

메신저 로그만 로드:
```bash
cd deployment
python load_all_data.py  # 메신저 로그 포함
```

## 데이터 초기화

기존 데이터 삭제 후 재로드:
```bash
# 테이블 삭제 (주의!)
aws dynamodb delete-table --table-name Employees
aws dynamodb delete-table --table-name MessengerLogs

# 테이블 재생성
cd deployment/terraform
terraform apply

# 데이터 재로드
cd ..
python load_extended_data.py
```

## 다음 단계

1. OpenSearch 인덱스 확인
2. API 테스트 실행
3. 프론트엔드에서 데이터 조회 확인
