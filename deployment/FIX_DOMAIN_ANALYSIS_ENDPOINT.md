# 도메인 분석 엔드포인트 복구 가이드

## 문제 상황
- `/domain-analysis` 엔드포인트에서 403 오류 발생
- "Missing Authentication Token" 메시지
- 프론트엔드에서 "failed to fetch" 오류

## 원인 분석
다음 엔드포인트들이 API Gateway에 제대로 설정되지 않음:
- ✗ `/domain-analysis` (POST)
- ✗ `/recommendations` (POST)
- ✗ `/quantitative-analysis` (POST)
- ✗ `/qualitative-analysis` (POST)

정상 작동하는 엔드포인트:
- ✓ `/employees` (GET)
- ✓ `/projects` (GET)

## 해결 방법

### 방법 1: 자동 복구 스크립트 실행 (권장)

AWS 자격 증명을 설정한 후 다음 스크립트를 실행:

```powershell
# AWS 자격 증명 설정
.\set_aws_credentials.ps1

# 통합 복구 및 재배포
python deployment/fix_all_integrations.py
```

이 스크립트는 다음을 수행합니다:
1. 모든 리소스의 Lambda 통합 확인
2. 누락된 통합 자동 생성
3. Lambda 권한 추가
4. API Gateway를 prod 스테이지에 재배포

### 방법 2: AWS Console에서 수동 복구

#### 2.1 API Gateway 리소스 확인
1. AWS Console → API Gateway
2. `HR-Resource-Optimization-API` (ID: xoc7x1m6p8) 선택
3. Resources 탭에서 `/domain-analysis` 리소스 확인

#### 2.2 POST 메서드 통합 확인
1. `/domain-analysis` → POST 메서드 선택
2. Integration Request 확인
3. Lambda Function이 `DomainAnalysisEngine`으로 설정되어 있는지 확인

#### 2.3 통합이 없는 경우 생성
1. POST 메서드 선택 → Actions → Delete Method (기존 메서드 삭제)
2. Actions → Create Method → POST 선택
3. Integration type: Lambda Function
4. Lambda Region: us-east-2
5. Lambda Function: `DomainAnalysisEngine`
6. Save

#### 2.4 CORS 설정
1. `/domain-analysis` 리소스 선택
2. Actions → Enable CORS
3. 다음 설정 확인:
   - Access-Control-Allow-Origin: '*'
   - Access-Control-Allow-Headers: 'Content-Type,Authorization'
   - Access-Control-Allow-Methods: 'POST,OPTIONS'
4. Enable CORS and replace existing CORS headers

#### 2.5 API 배포
1. Actions → Deploy API
2. Deployment stage: prod
3. Deploy

### 방법 3: Terraform으로 재배포 (인프라 코드 사용)

```powershell
cd deployment/terraform
terraform plan
terraform apply
```

## Lambda 함수 이름 매핑

올바른 Lambda 함수 이름:
- `/domain-analysis` → `DomainAnalysisEngine` ✓
- `/recommendations` → `ProjectRecommendationEngine` ✓
- `/quantitative-analysis` → `QuantitativeAnalysis` ✓
- `/qualitative-analysis` → `QualitativeAnalysis` ✓

**주의**: `DomainAnalysis`가 아니라 `DomainAnalysisEngine`입니다!

## 검증

복구 후 다음 스크립트로 검증:

```powershell
# 모든 엔드포인트 상태 확인
python deployment/test_all_endpoints.py

# 도메인 분석 API 직접 테스트
python deployment/test_domain_analysis_api.py
```

정상 응답 예시:
```
✓ POST /domain-analysis - 200
```

## 프론트엔드 확인

API 복구 후 프론트엔드에서 테스트:
1. 브라우저 개발자 도구 열기 (F12)
2. Network 탭 선택
3. 도메인 분석 버튼 클릭
4. `/domain-analysis` 요청 확인
   - Status: 200 OK
   - Response에 `current_domains`, `identified_domains` 포함

## 추가 문제 해결

### Lambda 함수가 없는 경우
```powershell
# Lambda 함수 배포
cd lambda_functions/domain_analysis
zip -r function.zip .
aws lambda update-function-code \
  --function-name DomainAnalysisEngine \
  --zip-file fileb://function.zip \
  --region us-east-2
```

### CORS 오류가 계속되는 경우
```powershell
# CORS 재설정
python deployment/enable_cors.py
```

## 참고 파일
- `deployment/fix_all_integrations.py` - 통합 자동 복구
- `deployment/test_all_endpoints.py` - 엔드포인트 상태 확인
- `aws_infrastructure/api_gateway_config.json` - API Gateway 설정
- `aws_infrastructure/lambda_functions_config.json` - Lambda 함수 설정
