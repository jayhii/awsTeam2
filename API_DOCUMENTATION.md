# HR Resource Optimization System - API 문서

## 개요

HR Resource Optimization System은 AI 기반 인력 배치 최적화 플랫폼의 RESTful API를 제공합니다. 모든 API는 AWS API Gateway를 통해 제공되며, IAM 인증을 사용합니다.

## 기본 정보

- **Base URL**: `https://{API_ID}.execute-api.us-east-2.amazonaws.com/prod`
- **인증 방식**: AWS IAM (Signature Version 4)
- **Content-Type**: `application/json`
- **응답 형식**: JSON

## 인증

모든 API 요청은 AWS Signature Version 4를 사용한 IAM 인증이 필요합니다.

### 인증 헤더 예시

```
Authorization: AWS4-HMAC-SHA256 Credential={access_key}/{date}/{region}/execute-api/aws4_request, SignedHeaders=host;x-amz-date, Signature={signature}
X-Amz-Date: {timestamp}
```

### Python 예시 (boto3 사용)

```python
import boto3
import json

# API Gateway 클라이언트 생성
client = boto3.client('apigateway', region_name='us-east-2')

# 또는 requests + aws-requests-auth 사용
from requests_aws4auth import AWS4Auth
import requests

auth = AWS4Auth(
    aws_access_key_id,
    aws_secret_access_key,
    'us-east-2',
    'execute-api'
)

response = requests.post(
    'https://{API_ID}.execute-api.us-east-2.amazonaws.com/prod/recommendations',
    auth=auth,
    json=payload
)
```

## API 엔드포인트

### 1. 프로젝트 투입 인력 추천

프로젝트 요구사항에 맞는 최적의 인력을 추천합니다.

**Endpoint**: `POST /recommendations`

**요청 본문**:

```json
{
  "project_id": "P_001",
  "required_skills": ["Java", "Spring Boot", "AWS"],
  "team_size": 5,
  "priority": "balanced"
}
```

**요청 파라미터**:

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| project_id | string | 선택 | 프로젝트 ID (기존 프로젝트 참조 시) |
| required_skills | array[string] | 필수 | 필요한 기술 스택 목록 |
| team_size | integer | 선택 | 추천받을 인원 수 (기본값: 10) |
| priority | string | 선택 | 우선순위 ("skill", "affinity", "balanced") (기본값: "balanced") |

**응답 (200 OK)**:

```json
{
  "recommendations": [
    {
      "user_id": "U_001",
      "name": "최정우",
      "role": "Principal Software Engineer",
      "skill_match_score": 92.5,
      "affinity_score": 85.0,
      "availability_score": 100.0,
      "overall_score": 90.3,
      "reasoning": "Java 및 Spring Boot에 대한 13년의 전문 경험을 보유하고 있으며, 금융권 차세대 프로젝트에서 리드 아키텍트로 활동한 경력이 있습니다. 팀원들과의 협업 이력이 우수하며, 현재 가용 상태입니다.",
      "matched_skills": [
        {
          "skill": "Java",
          "level": "Expert",
          "years": 13
        },
        {
          "skill": "Spring Boot",
          "level": "Expert",
          "years": 8
        },
        {
          "skill": "AWS",
          "level": "Advanced",
          "years": 5
        }
      ],
      "team_synergy": [
        {
          "user_id": "U_003",
          "name": "김철수",
          "affinity_score": 85.0,
          "shared_projects": 3
        }
      ],
      "availability": {
        "status": "available",
        "current_project": null,
        "available_from": "2025-11-26"
      }
    }
  ],
  "total_candidates": 15,
  "search_criteria": {
    "required_skills": ["Java", "Spring Boot", "AWS"],
    "team_size": 5,
    "priority": "balanced"
  }
}
```

**에러 응답**:

```json
{
  "error": "ValidationError",
  "message": "required_skills는 필수 항목입니다",
  "status_code": 400
}
```

**상태 코드**:
- `200 OK`: 성공
- `400 Bad Request`: 잘못된 요청 파라미터
- `401 Unauthorized`: 인증 실패
- `403 Forbidden`: 권한 부족
- `500 Internal Server Error`: 서버 오류

---

### 2. 도메인 분석

조직의 프로젝트 이력을 분석하여 신규 도메인 확장 기회를 식별합니다.

**Endpoint**: `POST /domain-analysis`

**요청 본문**:

```json
{
  "analysis_type": "new_domains"
}
```

**요청 파라미터**:

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| analysis_type | string | 필수 | 분석 유형 ("new_domains", "expansion_strategy") |
| include_employees | boolean | 선택 | 직원 정보 포함 여부 (기본값: true) |

**응답 (200 OK)**:

```json
{
  "current_domains": [
    {
      "domain_name": "Finance / Banking",
      "project_count": 15,
      "employee_count": 45,
      "key_technologies": ["Java", "Oracle", "Spring Boot"]
    },
    {
      "domain_name": "E-commerce",
      "project_count": 8,
      "employee_count": 25,
      "key_technologies": ["Node.js", "React", "MongoDB"]
    }
  ],
  "identified_domains": [
    {
      "domain_name": "Healthcare / Medical",
      "feasibility_score": 78.5,
      "required_skills": ["FHIR", "HL7", "HIPAA Compliance", "Python"],
      "skill_gap": ["FHIR", "HL7"],
      "available_skills": ["Python", "REST API", "Database Design"],
      "recommended_team": [
        {
          "user_id": "U_005",
          "name": "이영희",
          "current_skills": ["Python", "REST API"],
          "learning_path": ["FHIR", "HL7"],
          "readiness_score": 75.0
        }
      ],
      "entry_strategy": "기존 Python 개발자들을 대상으로 FHIR/HL7 교육을 진행하고, 소규모 파일럿 프로젝트로 시작하는 것을 권장합니다.",
      "estimated_timeline": "6-9 months",
      "risk_level": "medium"
    }
  ],
  "analysis_summary": {
    "total_domains_analyzed": 12,
    "new_opportunities": 3,
    "high_feasibility_count": 1,
    "medium_feasibility_count": 2
  }
}
```

**상태 코드**:
- `200 OK`: 성공
- `400 Bad Request`: 잘못된 분석 유형
- `401 Unauthorized`: 인증 실패
- `500 Internal Server Error`: 서버 오류

---

### 3. 정량적 인력 평가

직원의 경력, 프로젝트 이력, 기술 스택을 정량적으로 평가합니다.

**Endpoint**: `POST /quantitative-analysis`

**요청 본문**:

```json
{
  "user_id": "U_001"
}
```

**요청 파라미터**:

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| user_id | string | 필수 | 평가할 직원의 ID |

**응답 (200 OK)**:

```json
{
  "user_id": "U_001",
  "name": "최정우",
  "role": "Principal Software Engineer",
  "quantitative_metrics": {
    "experience_score": 95.0,
    "years_of_experience": 13,
    "project_count": 28,
    "skill_diversity": 85.0,
    "skill_count": 15,
    "tech_stack_recency": 88.0,
    "project_scale_average": 92.0,
    "leadership_score": 90.0
  },
  "skill_breakdown": [
    {
      "skill": "Java",
      "years": 13,
      "proficiency": "Expert",
      "market_demand": 95.0,
      "trend_score": 88.0,
      "recency_score": 100.0
    },
    {
      "skill": "Spring Boot",
      "years": 8,
      "proficiency": "Expert",
      "market_demand": 92.0,
      "trend_score": 95.0,
      "recency_score": 100.0
    }
  ],
  "project_experience": [
    {
      "project_id": "P_001",
      "project_name": "차세대 금융 코어 뱅킹 시스템",
      "role": "Lead Application Architect",
      "scale_score": 95.0,
      "complexity_score": 90.0,
      "performance_score": 92.0
    }
  ],
  "overall_score": 91.5,
  "percentile_rank": 95
}
```

**상태 코드**:
- `200 OK`: 성공
- `400 Bad Request`: 잘못된 user_id
- `404 Not Found`: 직원을 찾을 수 없음
- `401 Unauthorized`: 인증 실패
- `500 Internal Server Error`: 서버 오류

---

### 4. 정성적 인력 평가

AI를 활용하여 직원의 이력서와 프로젝트 경험을 정성적으로 평가합니다.

**Endpoint**: `POST /qualitative-analysis`

**요청 본문**:

```json
{
  "user_id": "U_001"
}
```

**요청 파라미터**:

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| user_id | string | 필수 | 평가할 직원의 ID |

**응답 (200 OK)**:

```json
{
  "user_id": "U_001",
  "name": "최정우",
  "role": "Principal Software Engineer",
  "qualitative_evaluation": {
    "strengths": [
      "금융권 대규모 프로젝트 리딩 경험이 풍부함",
      "최신 기술 스택에 대한 깊은 이해와 실무 적용 능력",
      "아키텍처 설계 및 기술 의사결정 능력 우수",
      "팀 리더십과 멘토링 역량 보유"
    ],
    "weaknesses": [
      "프론트엔드 기술 경험이 상대적으로 부족함",
      "클라우드 네이티브 아키텍처 경험이 제한적"
    ],
    "suitable_projects": [
      "대규모 엔터프라이즈 시스템 구축",
      "레거시 시스템 현대화 프로젝트",
      "금융/보험 도메인 프로젝트",
      "마이크로서비스 아키텍처 전환 프로젝트"
    ],
    "development_areas": [
      "Kubernetes 및 컨테이너 오케스트레이션",
      "React/Vue.js 등 모던 프론트엔드 프레임워크",
      "서버리스 아키텍처 패턴"
    ],
    "career_trajectory": "시니어 아키텍트 또는 기술 리더 역할로 성장 가능",
    "risk_flags": [],
    "verification_needed": []
  },
  "ai_confidence_score": 92.0,
  "analysis_timestamp": "2025-11-26T10:30:00Z"
}
```

**상태 코드**:
- `200 OK`: 성공
- `400 Bad Request`: 잘못된 user_id
- `404 Not Found`: 직원을 찾을 수 없음
- `401 Unauthorized`: 인증 실패
- `500 Internal Server Error`: 서버 오류

---

## 공통 에러 응답

모든 API는 다음과 같은 형식의 에러 응답을 반환합니다:

```json
{
  "error": "ErrorType",
  "message": "에러 메시지",
  "status_code": 400,
  "details": {
    "field": "required_skills",
    "reason": "필수 항목입니다"
  }
}
```

### 에러 타입

| 에러 타입 | 설명 | 상태 코드 |
|-----------|------|-----------|
| ValidationError | 요청 파라미터 검증 실패 | 400 |
| AuthenticationError | 인증 실패 | 401 |
| AuthorizationError | 권한 부족 | 403 |
| ResourceNotFound | 리소스를 찾을 수 없음 | 404 |
| RateLimitExceeded | 요청 제한 초과 | 429 |
| InternalServerError | 서버 내부 오류 | 500 |
| ServiceUnavailable | 서비스 일시 중단 | 503 |

## Rate Limiting

API는 다음과 같은 Rate Limit을 적용합니다:

- **기본 제한**: 초당 100 요청
- **버스트 제한**: 200 요청

Rate Limit 초과 시 `429 Too Many Requests` 응답과 함께 다음 헤더가 포함됩니다:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1732618800
Retry-After: 60
```

## CORS 설정

API는 다음 CORS 헤더를 지원합니다:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, X-Amz-Date
Access-Control-Max-Age: 3600
```

## 페이지네이션

대량의 데이터를 반환하는 API는 페이지네이션을 지원합니다:

**요청 파라미터**:
- `page`: 페이지 번호 (기본값: 1)
- `page_size`: 페이지당 항목 수 (기본값: 20, 최대: 100)

**응답 예시**:

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 150,
    "total_pages": 8,
    "has_next": true,
    "has_previous": false
  }
}
```

## 버전 관리

API 버전은 URL 경로에 포함됩니다:

- 현재 버전: `/prod` (v1)
- 향후 버전: `/v2`, `/v3` 등

## SDK 및 클라이언트 라이브러리

### Python SDK

```python
from hr_optimization_client import HRClient

client = HRClient(
    region='us-east-2',
    aws_access_key_id='YOUR_ACCESS_KEY',
    aws_secret_access_key='YOUR_SECRET_KEY'
)

# 인력 추천
recommendations = client.get_recommendations(
    required_skills=['Java', 'Spring Boot'],
    team_size=5
)

# 도메인 분석
analysis = client.analyze_domains(
    analysis_type='new_domains'
)

# 정량적 평가
quantitative = client.quantitative_analysis(
    user_id='U_001'
)

# 정성적 평가
qualitative = client.qualitative_analysis(
    user_id='U_001'
)
```

### JavaScript/TypeScript SDK

```typescript
import { HRClient } from '@hr-optimization/client';

const client = new HRClient({
  region: 'us-east-2',
  credentials: {
    accessKeyId: 'YOUR_ACCESS_KEY',
    secretAccessKey: 'YOUR_SECRET_KEY'
  }
});

// 인력 추천
const recommendations = await client.getRecommendations({
  requiredSkills: ['Java', 'Spring Boot'],
  teamSize: 5
});

// 도메인 분석
const analysis = await client.analyzeDomains({
  analysisType: 'new_domains'
});
```

## 모범 사례

### 1. 에러 처리

```python
try:
    response = client.get_recommendations(
        required_skills=['Java'],
        team_size=5
    )
except ValidationError as e:
    print(f"요청 파라미터 오류: {e.message}")
except AuthenticationError as e:
    print(f"인증 실패: {e.message}")
except RateLimitExceeded as e:
    retry_after = e.retry_after
    print(f"{retry_after}초 후 재시도하세요")
except Exception as e:
    print(f"예상치 못한 오류: {e}")
```

### 2. 재시도 로직

```python
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def get_recommendations_with_retry(client, **kwargs):
    return client.get_recommendations(**kwargs)
```

### 3. 배치 처리

대량의 직원을 평가할 때는 배치 처리를 사용하세요:

```python
import concurrent.futures

def evaluate_employee(user_id):
    quantitative = client.quantitative_analysis(user_id=user_id)
    qualitative = client.qualitative_analysis(user_id=user_id)
    return {
        'user_id': user_id,
        'quantitative': quantitative,
        'qualitative': qualitative
    }

user_ids = ['U_001', 'U_002', 'U_003', ...]

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(evaluate_employee, user_ids))
```

## 지원 및 문의

- **기술 지원**: support@hr-optimization.com
- **API 문서**: https://docs.hr-optimization.com
- **상태 페이지**: https://status.hr-optimization.com
- **GitHub**: https://github.com/hr-optimization/api-client

## 변경 이력

### v1.0.0 (2025-11-26)
- 초기 API 릴리스
- 4개 주요 엔드포인트 제공
- IAM 인증 지원
- Rate Limiting 적용
