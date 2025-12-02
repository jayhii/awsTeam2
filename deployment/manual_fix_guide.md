# 도메인 분석 엔드포인트 수동 복구 가이드

## 현재 상황
- `/domain-analysis` 엔드포인트에서 403 오류 발생
- Lambda 통합이 누락되었거나 API가 배포되지 않음

## AWS Console에서 수동 복구 (5분 소요)

### 1단계: API Gateway 접속
1. AWS Console 로그인
2. 서비스 → API Gateway
3. `HR-Resource-Optimization-API` 선택 (또는 API ID: `xoc7x1m6p8`)

### 2단계: 리소스 확인
1. 왼쪽 메뉴에서 **Resources** 클릭
2. 리소스 목록에서 다음 경로들을 찾기:
   - `/domain-analysis`
   - `/recommendations`
   - `/quantitative-analysis`
   - `/qualitative-analysis`

### 3단계: 각 엔드포인트 통합 확인 및 수정

#### `/domain-analysis` 복구

1. **리소스 선택**
   - `/domain-analysis` 클릭

2. **POST 메서드 확인**
   - POST 메서드가 있는지 확인
   - 없으면: Actions → Create Method → POST 선택 → 체크 표시 클릭

3. **Lambda 통합 설정**
   - Integration type: **Lambda Function** 선택
   - Use Lambda Proxy integration: **체크**
   - Lambda Region: **us-east-2**
   - Lambda Function: **DomainAnalysisEngine** 입력
   - **Save** 클릭
   - "Add Permission to Lambda Function" 팝업 → **OK** 클릭

4. **CORS 설정**
   - `/domain-analysis` 리소스 선택
   - Actions → **Enable CORS**
   - 기본 설정 유지:
     - Access-Control-Allow-Origin: `*`
     - Access-Control-Allow-Headers: `Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token`
     - Access-Control-Allow-Methods: POST,OPTIONS
   - **Enable CORS and replace existing CORS headers** 클릭
   - **Yes, replace existing values** 클릭

#### 다른 엔드포인트도 동일하게 복구

**`/recommendations`**
- Lambda Function: **ProjectRecommendationEngine**
- Method: POST

**`/quantitative-analysis`**
- Lambda Function: **QuantitativeAnalysis**
- Method: POST

**`/qualitative-analysis`**
- Lambda Function: **QualitativeAnalysis**
- Method: POST

### 4단계: API 배포 (중요!)

1. **Deploy API**
   - Actions → **Deploy API** 클릭
   - Deployment stage: **prod** 선택
   - Deployment description: "Fix domain-analysis and other endpoints" (선택사항)
   - **Deploy** 클릭

2. **배포 확인**
   - Stage: prod가 선택된 상태에서
   - Invoke URL 확인: `https://xoc7x1m6p8.execute-api.us-east-2.amazonaws.com/prod`

### 5단계: 검증

#### 브라우저에서 테스트
```
URL: https://xoc7x1m6p8.execute-api.us-east-2.amazonaws.com/prod/domain-analysis
Method: POST
Body: {"analysis_type": "new_domains"}
```

#### PowerShell에서 테스트
```powershell
python deployment/test_all_endpoints.py
```

예상 결과:
```
✓ POST /domain-analysis - 200
✓ POST /recommendations - 200
✓ POST /quantitative-analysis - 200
✓ POST /qualitative-analysis - 200
```

## Lambda 함수 이름 참조표

| 엔드포인트 | Lambda 함수 이름 |
|-----------|-----------------|
| `/domain-analysis` | `DomainAnalysisEngine` |
| `/recommendations` | `ProjectRecommendationEngine` |
| `/quantitative-analysis` | `QuantitativeAnalysis` |
| `/qualitative-analysis` | `QualitativeAnalysis` |
| `/employees` | `EmployeesList` |
| `/projects` | `ProjectsList` |

## 문제 해결

### Lambda 함수를 찾을 수 없는 경우
1. Lambda 콘솔로 이동
2. 함수 목록에서 해당 함수 확인
3. 함수가 없으면 배포 필요:
   ```powershell
   cd lambda_functions/domain_analysis
   # 함수 배포 스크립트 실행
   ```

### 여전히 403 오류가 발생하는 경우
1. API Gateway → Stages → prod 선택
2. Logs/Tracing 탭에서 CloudWatch Logs 활성화
3. 요청 재시도 후 로그 확인

### CORS 오류가 발생하는 경우
1. 각 리소스에서 OPTIONS 메서드 확인
2. OPTIONS 메서드의 Method Response에서:
   - Status: 200
   - Response Headers:
     - Access-Control-Allow-Headers
     - Access-Control-Allow-Methods
     - Access-Control-Allow-Origin
3. Integration Response에서 Header Mappings 확인

## 완료 후 프론트엔드 테스트

1. 프론트엔드 애플리케이션 열기
2. 도메인 분석 탭으로 이동
3. "신규 도메인 분석 시작" 버튼 클릭
4. 결과 확인

## 참고
- API Gateway 변경사항은 반드시 **Deploy API**를 해야 적용됩니다
- 배포 없이 테스트하면 이전 버전이 실행됩니다
- 각 Lambda 함수는 API Gateway에서 호출할 수 있는 권한이 필요합니다 (자동으로 추가됨)
