# Design Document

## Overview

HR Resource Optimization System은 AWS 클라우드 기반의 AI 기반 인력 배치 최적화 플랫폼입니다. 본 시스템은 직원의 이력 정보, 기술 스택, 프로젝트 참여 이력, 그리고 직원 간 친밀도를 종합적으로 분석하여 최적의 팀 구성과 프로젝트 투입 인력을 추천합니다. 또한 조직의 프로젝트 이력을 분석하여 신규 도메인 확장 기회를 식별합니다.

시스템은 서버리스 아키텍처를 기반으로 하며, AWS Bedrock의 Claude 모델을 활용한 AI 분석, OpenSearch를 통한 벡터 기반 유사도 검색, DynamoDB를 통한 확장 가능한 데이터 저장소를 제공합니다. 모든 리소스는 Team2 태그 기반 접근 제어를 통해 격리되며, Terraform을 통한 IaC로 관리됩니다.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                            │
│  ┌──────────────┐         ┌──────────────┐                     │
│  │   S3 Static  │────────▶│ CloudFront   │                     │
│  │   Hosting    │         │   (Optional) │                     │
│  └──────────────┘         └──────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway Layer                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Gateway (REST API)                                   │  │
│  │  - IAM Authentication                                     │  │
│  │  - CORS Configuration                                     │  │
│  │  - Request/Response Transformation                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Lambda Function Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Resume     │  │  Affinity    │  │ Recommendation│         │
│  │   Parser     │  │  Calculator  │  │    Engine     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Domain     │  │ Quantitative │  │  Qualitative  │         │
│  │   Analysis   │  │   Analysis   │  │   Analysis    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │ Tech Trend   │  │   Vector     │                            │
│  │  Collector   │  │  Embedding   │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
                │                │                │
                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI/ML Services Layer                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  AWS Bedrock                                              │  │
│  │  - Claude v2 (텍스트 분석, 추론)                          │  │
│  │  - Titan Embeddings (벡터 임베딩)                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  AWS Textract                                             │  │
│  │  - 이력서 텍스트 추출                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                │                │                │
                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Storage Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  DynamoDB    │  │  OpenSearch  │  │     S3       │         │
│  │  - Employees │  │  - Vector    │  │  - Resumes   │         │
│  │  - Projects  │  │    Search    │  │  - Reports   │         │
│  │  - Affinity  │  │  - Employee  │  │  - Data Lake │         │
│  │  - Messenger │  │    Profiles  │  │              │         │
│  │  - Events    │  │  - Project   │  │              │         │
│  │  - Trends    │  │    Reqs      │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Monitoring & Logging Layer                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  CloudWatch                                               │  │
│  │  - Logs                                                   │  │
│  │  - Metrics                                                │  │
│  │  - Alarms                                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Pipelines

#### 1. 이력서 파싱 파이프라인
```
S3 Upload (PDF) → S3 Event → Lambda (Resume Parser)
                                    ↓
                              Textract (텍스트 추출)
                                    ↓
                              Bedrock Claude (구조화)
                                    ↓
                              DynamoDB (Employees)
                                    ↓
                              DynamoDB Stream
                                    ↓
                              Lambda (Vector Embedding)
                                    ↓
                              Bedrock Titan (임베딩 생성)
                                    ↓
                              OpenSearch (인덱싱)
```

#### 2. 친밀도 분석 파이프라인
```
EventBridge (Daily) → Lambda (Affinity Calculator)
                                    ↓
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            DynamoDB          DynamoDB        DynamoDB
            (Messenger)       (Events)        (Projects)
                    │               │               │
                    └───────────────┼───────────────┘
                                    ▼
                            협업 이력 분석
                            커뮤니케이션 분석
                            사회적 친밀도 분석
                            개인적 친밀도 분석
                                    ▼
                            종합 Affinity Score
                                    ▼
                            DynamoDB (EmployeeAffinity)
```

#### 3. 프로젝트 추천 파이프라인
```
API Gateway → Lambda (Recommendation Engine)
                        ↓
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
  DynamoDB        OpenSearch      DynamoDB
  (Projects)      (Vector Search) (Affinity)
        │               │               │
        └───────────────┼───────────────┘
                        ▼
                기술 적합도 계산
                프로젝트 이력 분석
                친밀도 점수 반영
                        ▼
                Bedrock Claude (추천 근거 생성)
                        ▼
                최종 추천 결과 반환
```

#### 4. 도메인 분석 파이프라인
```
API Gateway → Lambda (Domain Analysis)
                        ↓
        ┌───────────────┼───────────────┐
        ▼               ▼               
  DynamoDB        DynamoDB        
  (Employees)     (Projects)      
        │               │               
        └───────────────┼───────────────┘
                        ▼
                프로젝트 도메인 분류
                기술 스택 분석
                        ▼
                Bedrock Claude (신규 도메인 식별)
                        ▼
                진입 전략 생성
                필요 역량 분석
                        ▼
                결과 반환 + DynamoDB 저장
```

## Components and Interfaces

### 1. Frontend Components

#### 1.1 Static Web Application
- **Technology**: React/Vue.js + TypeScript
- **Hosting**: S3 Static Website Hosting
- **Distribution**: CloudFront (Optional)
- **Features**:
  - 대시보드 (인력 현황, 프로젝트 현황)
  - 추천 요청 인터페이스
  - 분석 결과 시각화
  - 이력서 업로드

### 2. API Gateway

#### 2.1 REST API Endpoints

**Base URL**: `https://API_ID.execute-api.us-east-2.amazonaws.com/prod`

**Endpoints**:

1. **POST /recommendations**
   - 프로젝트 투입 인력 추천
   - Request Body:
     ```json
     {
       "project_id": "string",
       "required_skills": ["string"],
       "team_size": number,
       "priority": "skill|affinity|balanced"
     }
     ```
   - Response:
     ```json
     {
       "recommendations": [
         {
           "user_id": "string",
           "name": "string",
           "skill_match_score": number,
           "affinity_score": number,
           "overall_score": number,
           "reasoning": "string"
         }
       ]
     }
     ```

2. **POST /domain-analysis**
   - 신규 도메인 확장 분석
   - Request Body:
     ```json
     {
       "analysis_type": "new_domains|expansion_strategy"
     }
     ```
   - Response:
     ```json
     {
       "identified_domains": [
         {
           "domain_name": "string",
           "feasibility_score": number,
           "required_skills": ["string"],
           "skill_gap": ["string"],
           "recommended_team": ["user_id"]
         }
       ]
     }
     ```

3. **POST /quantitative-analysis**
   - 정량적 인력 평가
   - Request Body:
     ```json
     {
       "user_id": "string"
     }
     ```
   - Response:
     ```json
     {
       "user_id": "string",
       "experience_score": number,
       "project_count": number,
       "skill_diversity": number,
       "overall_score": number
     }
     ```

4. **POST /qualitative-analysis**
   - 정성적 인력 평가
   - Request Body:
     ```json
     {
       "user_id": "string"
     }
     ```
   - Response:
     ```json
     {
       "user_id": "string",
       "strengths": ["string"],
       "weaknesses": ["string"],
       "suitable_projects": ["string"],
       "development_areas": ["string"]
     }
     ```

### 3. Lambda Functions

#### 3.1 ResumeParser
- **Runtime**: Python 3.11
- **Memory**: 1024 MB
- **Timeout**: 300s
- **Trigger**: S3 ObjectCreated Event
- **Purpose**: 이력서 파싱 및 데이터 추출
- **Dependencies**: boto3, PyPDF2
- **Flow**:
  1. S3에서 PDF 다운로드
  2. Textract로 텍스트 추출
  3. Claude로 구조화된 데이터 추출
  4. DynamoDB에 저장

#### 3.2 AffinityScoreCalculator
- **Runtime**: Python 3.11
- **Memory**: 512 MB
- **Timeout**: 180s
- **Trigger**: EventBridge (Daily)
- **Purpose**: 직원 간 친밀도 점수 계산
- **Flow**:
  1. 모든 직원 쌍 조회
  2. 프로젝트 협업 이력 분석
  3. 메신저 커뮤니케이션 분석
  4. 행사 참여 이력 분석
  5. 연차/월급일 연락 빈도 분석
  6. 종합 점수 계산 및 저장

#### 3.3 ProjectRecommendationEngine
- **Runtime**: Python 3.11
- **Memory**: 2048 MB
- **Timeout**: 300s
- **Trigger**: API Gateway
- **Purpose**: 프로젝트 투입 인력 추천
- **Flow**:
  1. 프로젝트 요구사항 벡터화
  2. OpenSearch 유사도 검색
  3. DynamoDB에서 친밀도 조회
  4. 종합 점수 계산
  5. Claude로 추천 근거 생성

#### 3.4 DomainAnalysisEngine
- **Runtime**: Python 3.11
- **Memory**: 1024 MB
- **Timeout**: 300s
- **Trigger**: API Gateway
- **Purpose**: 신규 도메인 확장 분석
- **Flow**:
  1. 전체 프로젝트 이력 수집
  2. Claude로 도메인 분류
  3. 신규 도메인 식별
  4. 진입 전략 생성

#### 3.5 QuantitativeAnalysis
- **Runtime**: Python 3.11
- **Memory**: 512 MB
- **Timeout**: 120s
- **Trigger**: API Gateway
- **Purpose**: 정량적 인력 평가
- **Flow**:
  1. 직원 데이터 조회
  2. 경력 연수, 프로젝트 수 계산
  3. 기술 다양성 분석
  4. 종합 점수 산출

#### 3.6 QualitativeAnalysis
- **Runtime**: Python 3.11
- **Memory**: 1024 MB
- **Timeout**: 180s
- **Trigger**: API Gateway
- **Purpose**: 정성적 인력 평가
- **Flow**:
  1. 직원 프로필 조회
  2. Claude로 자기소개 분석
  3. 프로젝트 경험 평가
  4. 강점/약점 도출

#### 3.7 TechTrendCollector
- **Runtime**: Python 3.11
- **Memory**: 512 MB
- **Timeout**: 180s
- **Trigger**: EventBridge (Weekly)
- **Purpose**: 외부 API에서 기술 트렌드 수집
- **Flow**:
  1. 외부 API 호출
  2. 트렌드 데이터 파싱
  3. DynamoDB에 저장

#### 3.8 VectorEmbeddingGenerator
- **Runtime**: Python 3.11
- **Memory**: 1024 MB
- **Timeout**: 180s
- **Trigger**: DynamoDB Stream
- **Purpose**: 직원 프로필 벡터 임베딩 생성
- **Flow**:
  1. DynamoDB Stream 이벤트 수신
  2. Titan으로 벡터 임베딩 생성
  3. OpenSearch에 인덱싱

### 4. Data Storage

#### 4.1 DynamoDB Tables

**Employees Table**
```
Partition Key: user_id (String)
GSI: RoleIndex (role)
Attributes:
  - basic_info (Map)
  - skills (List)
  - work_experience (List)
  - education (Map)
  - certifications (List)
Stream: Enabled
```

**Projects Table**
```
Partition Key: project_id (String)
GSI: IndustryIndex (client_industry)
Attributes:
  - project_name (String)
  - client_industry (String)
  - period (Map)
  - tech_stack (Map)
  - requirements (List)
  - team_composition (Map)
```

**EmployeeAffinity Table**
```
Partition Key: affinity_id (String)
GSI: Employee1Index (employee_1)
Attributes:
  - employee_pair (Map)
  - project_collaboration (Map)
  - messenger_communication (Map)
  - company_events (Map)
  - personal_closeness (Map)
  - overall_affinity_score (Number)
```

**MessengerLogs Table**
```
Partition Key: log_id (String)
GSI: SenderTimestampIndex (sender_id, timestamp)
Attributes:
  - sender_id (String)
  - receiver_id (String)
  - timestamp (String)
  - response_time_minutes (Number)
  - is_payday (Boolean)
  - is_vacation_day (Boolean)
```

**CompanyEvents Table**
```
Partition Key: event_id (String)
GSI: DateIndex (event_date)
Attributes:
  - event_name (String)
  - event_date (String)
  - event_type (String)
  - participants (List)
  - location (String)
```

**TechTrends Table**
```
Partition Key: tech_name (String)
Attributes:
  - trend_score (Number)
  - market_demand (Number)
  - last_updated (String)
```

#### 4.2 OpenSearch Indices

**employee_profiles Index**
```json
{
  "mappings": {
    "properties": {
      "user_id": {"type": "keyword"},
      "name": {"type": "text"},
      "role": {"type": "keyword"},
      "skills": {
        "type": "nested",
        "properties": {
          "name": {"type": "keyword"},
          "level": {"type": "keyword"},
          "years": {"type": "integer"}
        }
      },
      "profile_vector": {
        "type": "knn_vector",
        "dimension": 1536
      }
    }
  }
}
```

**project_requirements Index**
```json
{
  "mappings": {
    "properties": {
      "project_id": {"type": "keyword"},
      "project_name": {"type": "text"},
      "required_skills": {"type": "keyword"},
      "requirement_vector": {
        "type": "knn_vector",
        "dimension": 1536
      }
    }
  }
}
```

#### 4.3 S3 Buckets

**hr-resumes-bucket**
- Purpose: 이력서 파일 저장
- Lifecycle: 90일 후 Glacier로 이동
- Versioning: Enabled
- Encryption: AES256

**hr-frontend-hosting**
- Purpose: 정적 웹사이트 호스팅
- Website Configuration: Enabled
- Public Access: Allowed

**hr-reports-bucket**
- Purpose: 분석 보고서 저장
- Lifecycle: 365일 후 삭제
- Encryption: AES256

**hr-data-lake**
- Purpose: 원본 데이터 및 로그
- Lifecycle: 30일 후 IA, 180일 후 Glacier
- Encryption: AES256

### 5. AI/ML Services

#### 5.1 AWS Bedrock

**Claude v2 Model**
- Model ID: `anthropic.claude-v2`
- Use Cases:
  - 이력서 텍스트 구조화
  - 프로젝트 설명 분석
  - 정성적 평가 수행
  - 신규 도메인 식별
  - 추천 근거 생성
- Configuration:
  - Max Tokens: 4096
  - Temperature: 0.7
  - Top P: 0.9

**Titan Embeddings Model**
- Model ID: `amazon.titan-embed-text-v1`
- Use Cases:
  - 직원 프로필 벡터화
  - 프로젝트 요구사항 벡터화
- Configuration:
  - Dimensions: 1536

#### 5.2 AWS Textract
- Use Case: PDF 이력서 텍스트 추출
- API: `DetectDocumentText`, `AnalyzeDocument`

### 6. Security & IAM

#### 6.1 IAM Roles

**LambdaExecutionRole-Team2**
- Assume Role Policy: Lambda Service
- Managed Policies:
  - AWSLambdaBasicExecutionRole
- Inline Policies:
  - Team2-DynamoDB-Access (태그 기반)
  - Team2-S3-Access (태그 기반)
  - Team2-Bedrock-Access
  - Team2-Textract-Access
  - Team2-OpenSearch-Access (태그 기반)

**APIGatewayExecutionRole-Team2**
- Assume Role Policy: API Gateway Service
- Inline Policies:
  - Team2-Lambda-Invoke (태그 기반)

#### 6.2 Tag-Based Access Control

모든 리소스는 다음 태그를 포함:
```json
{
  "Team": "Team2",
  "Project": "HR-Resource-Optimization",
  "Environment": "prod"
}
```

IAM 정책은 `aws:ResourceTag/Team` 조건을 사용하여 Team2 리소스만 접근 허용

## Data Models

### Employee Model
```python
{
  "user_id": "U_001",
  "basic_info": {
    "name": "최정우",
    "role": "Principal Software Engineer",
    "years_of_experience": 13,
    "email": "jw.choi@tech-resume.com"
  },
  "self_introduction": "금융권 차세대 프로젝트 경험...",
  "skills": [
    {
      "name": "Java",
      "level": "Expert",
      "years": 13
    }
  ],
  "work_experience": [
    {
      "project_id": "P_001",
      "project_name": "차세대 금융 코어 뱅킹 시스템",
      "role": "Lead Application Architect",
      "period": "2024-01 ~ 2025-07",
      "main_tasks": ["..."],
      "performance_result": "..."
    }
  ],
  "education": {
    "degree": "Computer Science, MS",
    "university": "KAIST"
  },
  "certifications": ["OCM", "AWS SAP"]
}
```

### Project Model
```python
{
  "project_id": "P_001",
  "project_name": "차세대 금융 코어 뱅킹 시스템 구축",
  "client_industry": "Finance / Banking",
  "period": {
    "start": "2024-01-15",
    "end": "2025-07-14",
    "duration_months": 18
  },
  "budget_scale": "150억 원",
  "description": "...",
  "tech_stack": {
    "backend": ["Java 17", "Spring Boot 3.2"],
    "frontend": ["Vue.js 3"],
    "data": ["Oracle Exadata", "Redis"],
    "infra": ["Red Hat OpenShift"]
  },
  "requirements": ["..."],
  "team_composition": {
    "PM": 1,
    "Backend_Dev": 20
  }
}
```

### Affinity Model
```python
{
  "affinity_id": "AFF_001",
  "employee_pair": {
    "employee_1": "U_001",
    "employee_2": "U_002"
  },
  "project_collaboration": {
    "shared_projects": [
      {
        "project_id": "P_001",
        "overlap_period_months": 6,
        "same_team": true
      }
    ],
    "collaboration_score": 75
  },
  "messenger_communication": {
    "total_messages_exchanged": 342,
    "avg_response_time_minutes": 15,
    "communication_score": 68
  },
  "company_events": {
    "shared_events": ["EVT_001", "EVT_002"],
    "social_score": 60
  },
  "personal_closeness": {
    "payday_contact_frequency": 2,
    "vacation_day_contact_frequency": 3,
    "personal_score": 55
  },
  "overall_affinity_score": 67
}
```

### Recommendation Model
```python
{
  "project_id": "P_001",
  "recommendations": [
    {
      "user_id": "U_001",
      "name": "최정우",
      "skill_match_score": 92,
      "affinity_score": 85,
      "availability_score": 100,
      "overall_score": 90,
      "reasoning": "Claude가 생성한 추천 근거",
      "matched_skills": ["Java", "Spring Boot"],
      "team_synergy": ["U_003와 높은 친밀도"]
    }
  ]
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Skill Query Completeness
*For any* skill query and employee database, all returned employees must possess the requested skills
**Validates: Requirements 1.1**

### Property 2: Skill Normalization Consistency
*For any* skill string, normalizing it multiple times should produce the same result
**Validates: Requirements 1.2**

### Property 3: Skill Match Score Ordering
*For any* team requirement and employee pool, recommended candidates must be ordered by descending Skill Match Score
**Validates: Requirements 1.3**

### Property 4: Recommendation Output Completeness
*For any* recommendation result, it must include skill stack, years of experience, and past project performance for each candidate
**Validates: Requirements 1.4**

### Property 5: Project Data Round Trip
*For any* project data, storing it to DynamoDB and retrieving it should return equivalent data
**Validates: Requirements 2.1**

### Property 6: Recommendation Multi-Factor Scoring
*For any* recommendation request, the scoring algorithm must consider skill match, project history, and affinity score
**Validates: Requirements 2.2**

### Property 7: Affinity Score Persistence
*For any* collaboration history between two employees, calculating and storing the affinity score should allow retrieval of the same score
**Validates: Requirements 2.3**

### Property 8: Recommendation Reasoning Completeness
*For any* recommendation result, it must include skill score, history score, and affinity score for each candidate
**Validates: Requirements 2.4**

### Property 9: Availability Information Inclusion
*For any* employee currently assigned to a project, recommendations must include their availability status
**Validates: Requirements 2.5**

### Property 10: Project Overlap Calculation
*For any* two employees with shared project history, the overlap calculation must correctly compute the intersection of their participation periods
**Validates: Requirements 2-1.1**

### Property 11: Messenger Data Anonymization
*For any* messenger log data, after anonymization, no personally identifiable information should be present
**Validates: Requirements 2-1.2**

### Property 12: Communication Score Multi-Factor
*For any* communication analysis, the score must incorporate message count, response time, and conversation duration
**Validates: Requirements 2-1.3**

### Property 13: Event Participation Scoring
*For any* two employees, their social affinity score must reflect the number of shared company events
**Validates: Requirements 2-1.4**

### Property 14: Special Day Contact Analysis
*For any* employee pair, personal closeness score must reflect contact frequency on paydays and vacation days
**Validates: Requirements 2-1.5**

### Property 15: Affinity Score Weighted Average
*For any* set of component affinity scores (collaboration, communication, social, personal), the overall affinity score must be their weighted average
**Validates: Requirements 2-1.6**

### Property 16: Affinity Score Update Persistence
*For any* affinity score update, the new score must be stored in DynamoDB and retrievable
**Validates: Requirements 2-1.7**

### Property 17: Resume Extraction Completeness
*For any* resume upload, the extraction must identify skills, project experience, and career duration
**Validates: Requirements 3.1**

### Property 18: Tech Stack Evaluation Factors
*For any* extracted skill set, the evaluation score must consider both recency and market demand
**Validates: Requirements 3.2**

### Property 19: Project Experience Multi-Factor Evaluation
*For any* project experience, the evaluation must consider project scale, role, and performance
**Validates: Requirements 3.3**

### Property 20: Evaluation Output Completeness
*For any* completed evaluation, the output must include overall score, strengths, weaknesses, and recommended projects
**Validates: Requirements 3.4**

### Property 21: Suspicious Content Flagging
*For any* resume with questionable claims, the system must flag those items for verification
**Validates: Requirements 3.5**

### Property 22: Domain Classification Completeness
*For any* project history collection, the analysis must classify projects by domain, tech stack, and industry
**Validates: Requirements 4.1**

### Property 23: Domain Gap Identification
*For any* organization's project portfolio, the analysis must identify domains not currently covered
**Validates: Requirements 4.2**

### Property 24: Domain Entry Analysis
*For any* identified new domain, the analysis must include skill gap and transition feasibility
**Validates: Requirements 4.3**

### Property 25: Portfolio Update on New Hire
*For any* new hire with project history, their domains must be added to the organization's portfolio
**Validates: Requirements 4.4**

### Property 26: Domain Requirement Definition
*For any* new domain entry decision, the system must define required skills and roles
**Validates: Requirements 5.1**

### Property 27: Domain Candidate Identification
*For any* defined domain requirements, the system must identify employees with matching or learnable skills
**Validates: Requirements 5.2**

### Property 28: Team Composition Optimization
*For any* candidate pool, the team simulation must propose optimal combinations
**Validates: Requirements 5.3**

### Property 29: Team Plan Completeness
*For any* generated team composition, the plan must include roles, training needs, and expected outcomes
**Validates: Requirements 5.4**

### Property 30: Employee Preference Learning
*For any* accumulated project history, the system must infer employee preferences for domains, technologies, and collaboration styles
**Validates: Requirements 6.1**

### Property 31: Satisfaction Correlation Analysis
*For any* satisfaction data collection, the system must compute correlations between project types, team composition, roles, and satisfaction
**Validates: Requirements 6.2**

### Property 32: Assignment Fit Evaluation
*For any* planned project assignment, the evaluation must consider employee preferences and past satisfaction patterns
**Validates: Requirements 6.3**

### Property 33: Data Encryption at Rest
*For any* employee profile data, stored data must be encrypted
**Validates: Requirements 7.1**

### Property 34: Role-Based Access Control
*For any* user access attempt, permissions must be verified based on user role
**Validates: Requirements 7.5**

### Property 35: Visualization Data Completeness
*For any* analysis result visualization, the chart data must include skill distribution, domain coverage, and team composition
**Validates: Requirements 8.1**

### Property 36: Dashboard Metrics Completeness
*For any* dashboard load, it must display availability, project status, and pending recommendations
**Validates: Requirements 8.2**

### Property 37: Date Range Filtering Accuracy
*For any* selected date range, the filtered results must only include data within that range
**Validates: Requirements 8.3**

### Property 38: Export Format Support
*For any* report generation request, the system must support PDF and Excel formats
**Validates: Requirements 8.4**

### Property 39: API Authentication Enforcement
*For any* API request, it must be routed through API Gateway and authenticated
**Validates: Requirements 9.2**

### Property 40: File Upload and URL Generation
*For any* uploaded file, it must be stored in S3 and an access URL must be returned
**Validates: Requirements 9.4**

### Property 41: Resource Tagging Enforcement
*For any* created AWS resource, it must have the Team=Team2 tag applied
**Validates: Requirements 9-1.1**

### Property 42: DynamoDB Tag-Based Access Control
*For any* Lambda function attempting DynamoDB access, the target table must have the Team=Team2 tag
**Validates: Requirements 9-1.2**

### Property 43: S3 Tag-Based Access Control
*For any* Lambda function attempting S3 access, the target bucket must have the Team=Team2 tag
**Validates: Requirements 9-1.3**

### Property 44: OpenSearch Tag-Based Access Control
*For any* Lambda function attempting OpenSearch access, the target domain must have the Team=Team2 tag
**Validates: Requirements 9-1.4**

### Property 45: Untagged Resource Access Denial
*For any* resource without the Team=Team2 tag, access attempts must be denied with an error
**Validates: Requirements 9-1.5**

### Property 46: IAM Role Naming Convention
*For any* created IAM role, its name must match the pattern LambdaExecutionRole-Team2 or APIGatewayExecutionRole-Team2
**Validates: Requirements 9-1.6**

### Property 47: Resume Upload Pipeline Trigger
*For any* PDF or Word resume uploaded to S3, Textract must be invoked
**Validates: Requirements 10.1**

### Property 48: Textract to Lambda Pipeline
*For any* Textract extraction completion, the Lambda function must be triggered
**Validates: Requirements 10.2**

### Property 49: Resume Field Extraction Completeness
*For any* resume text processed by Claude, the extraction must identify name, contact, education, experience, and skills
**Validates: Requirements 10.3**

### Property 50: Skill Normalization and Storage
*For any* extracted skills, they must be normalized to standard names and stored in DynamoDB
**Validates: Requirements 10.4**

### Property 51: Resume Parsing Review Interface
*For any* parsing result, a review interface must be provided to the user
**Validates: Requirements 10.6**

### Property 52: Profile Vector Embedding Generation
*For any* employee profile creation or update, a vector embedding must be generated
**Validates: Requirements 11.1**

### Property 53: Vector Embedding Indexing
*For any* generated vector embedding, it must be indexed in OpenSearch
**Validates: Requirements 11.2**

### Property 54: Vector Similarity Search
*For any* similarity search request, OpenSearch must return results based on vector similarity
**Validates: Requirements 11.3**

### Property 55: Similarity Score Inclusion
*For any* similarity search result, each candidate must include a similarity score
**Validates: Requirements 11.4**

### Property 56: Team Synergy Prediction
*For any* team composition simulation, vector similarity must be used to predict team synergy
**Validates: Requirements 11.5**

### Property 57: Scheduled Trend Collection
*For any* scheduled execution, the system must call external APIs to collect tech trend data
**Validates: Requirements 12.1**

### Property 58: Trend Data Persistence
*For any* external API response, the data must be parsed and stored in DynamoDB
**Validates: Requirements 12.2**

### Property 59: Trend Data Reference in Evaluation
*For any* tech stack evaluation, stored trend data must be referenced to assess recency
**Validates: Requirements 12.3**

### Property 60: API Failure Fallback
*For any* external API failure, the system must use cached data and execute retry logic
**Validates: Requirements 12.4**

### Property 61: Cascading Score Recalculation
*For any* trend data update, existing employee skill evaluation scores must be recalculated
**Validates: Requirements 12.5**

## Error Handling

### 1. Input Validation Errors
- **Invalid Skill Query**: Return 400 Bad Request with error message
- **Malformed Resume**: Return 400 Bad Request with supported format list
- **Invalid Date Range**: Return 400 Bad Request with valid range constraints

### 2. Authentication/Authorization Errors
- **Missing IAM Credentials**: Return 401 Unauthorized
- **Insufficient Permissions**: Return 403 Forbidden
- **Missing Team2 Tag**: Return 403 Forbidden with tag requirement message

### 3. Resource Not Found Errors
- **Employee Not Found**: Return 404 Not Found
- **Project Not Found**: Return 404 Not Found
- **Affinity Score Not Found**: Return 404 Not Found (may indicate no collaboration history)

### 4. External Service Errors
- **Bedrock API Failure**: Retry with exponential backoff, fallback to cached results if available
- **Textract Failure**: Return 503 Service Unavailable, suggest manual input
- **OpenSearch Unavailable**: Return 503 Service Unavailable, fallback to DynamoDB-only search
- **External API Timeout**: Use cached trend data, log for manual review

### 5. Data Consistency Errors
- **DynamoDB Conditional Check Failed**: Retry with updated data
- **Vector Embedding Mismatch**: Regenerate embedding and re-index
- **Affinity Score Calculation Error**: Log error, use default score of 50

### 6. Rate Limiting
- **Bedrock Throttling**: Implement exponential backoff with jitter
- **API Gateway Throttling**: Return 429 Too Many Requests with Retry-After header
- **DynamoDB Throttling**: Use exponential backoff, consider provisioned capacity

### 7. Data Quality Errors
- **Incomplete Resume Data**: Flag for manual review, proceed with available data
- **Suspicious Claims**: Flag for verification, include in evaluation with caveat
- **Missing Required Fields**: Return 400 Bad Request with missing field list

## Testing Strategy

### Unit Testing

**Framework**: pytest (Python)

**Coverage Areas**:
- Lambda function handlers
- Data transformation functions
- Scoring algorithms
- Validation logic
- Error handling

**Example Unit Tests**:
```python
def test_skill_normalization():
    """Test that skill names are normalized consistently"""
    assert normalize_skill("javascript") == "JavaScript"
    assert normalize_skill("JAVASCRIPT") == "JavaScript"
    assert normalize_skill("Java Script") == "JavaScript"

def test_affinity_score_calculation():
    """Test affinity score weighted average"""
    scores = {
        "collaboration": 80,
        "communication": 70,
        "social": 60,
        "personal": 50
    }
    weights = {
        "collaboration": 0.4,
        "communication": 0.3,
        "social": 0.2,
        "personal": 0.1
    }
    assert calculate_affinity_score(scores, weights) == 69.0
```

### Property-Based Testing

**Framework**: Hypothesis (Python)

**Configuration**: Minimum 100 iterations per property

**Property Test Examples**:

```python
from hypothesis import given, strategies as st

@given(st.lists(st.text(min_size=1), min_size=1))
def test_skill_query_completeness(skills):
    """
    Feature: hr-resource-optimization, Property 1: Skill Query Completeness
    For any skill query, all returned employees must possess the requested skills
    """
    employees = generate_random_employees()
    results = query_employees_by_skills(skills)
    
    for employee in results:
        assert all(skill in employee.skills for skill in skills)

@given(st.text(min_size=1))
def test_skill_normalization_consistency(skill_name):
    """
    Feature: hr-resource-optimization, Property 2: Skill Normalization Consistency
    For any skill string, normalizing it multiple times produces the same result
    """
    normalized_once = normalize_skill(skill_name)
    normalized_twice = normalize_skill(normalized_once)
    
    assert normalized_once == normalized_twice

@given(st.dictionaries(
    keys=st.sampled_from(["collaboration", "communication", "social", "personal"]),
    values=st.floats(min_value=0, max_value=100)
))
def test_affinity_weighted_average(component_scores):
    """
    Feature: hr-resource-optimization, Property 15: Affinity Score Weighted Average
    For any component scores, overall score must be their weighted average
    """
    weights = {"collaboration": 0.4, "communication": 0.3, "social": 0.2, "personal": 0.1}
    overall_score = calculate_affinity_score(component_scores, weights)
    
    # Verify it's a weighted average
    expected = sum(component_scores.get(k, 0) * v for k, v in weights.items())
    assert abs(overall_score - expected) < 0.01

@given(st.data())
def test_project_data_round_trip(data):
    """
    Feature: hr-resource-optimization, Property 5: Project Data Round Trip
    For any project data, storing and retrieving should return equivalent data
    """
    project = data.draw(st.builds(Project))
    
    # Store to DynamoDB
    store_project(project)
    
    # Retrieve from DynamoDB
    retrieved = get_project(project.project_id)
    
    assert project == retrieved
```

### Integration Testing

**Framework**: pytest + moto (AWS mocking)

**Test Scenarios**:
1. End-to-end resume parsing pipeline
2. Recommendation engine with real data
3. Affinity score calculation with messenger logs
4. Domain analysis with project history
5. Vector search with OpenSearch

**Example Integration Test**:
```python
@mock_aws
def test_resume_parsing_pipeline():
    """Test complete resume parsing flow"""
    # Setup
    s3 = boto3.client('s3', region_name='us-east-2')
    s3.create_bucket(Bucket='hr-resumes-bucket')
    
    # Upload resume
    s3.put_object(
        Bucket='hr-resumes-bucket',
        Key='uploads/test_resume.pdf',
        Body=b'resume content'
    )
    
    # Verify Lambda was triggered
    # Verify Textract was called
    # Verify DynamoDB has the parsed data
    # Verify OpenSearch has the vector embedding
```

### Load Testing

**Tool**: Locust

**Scenarios**:
- 1000 concurrent users querying recommendations
- 100 resume uploads per minute
- 500 affinity score calculations per minute

**Performance Targets**:
- API response time < 2 seconds (p95)
- Resume parsing < 30 seconds
- Recommendation generation < 5 seconds

### Security Testing

**Areas**:
- IAM tag-based access control enforcement
- Data encryption at rest and in transit
- API authentication and authorization
- Input validation and sanitization
- PII anonymization in messenger logs

**Tools**:
- AWS IAM Policy Simulator
- OWASP ZAP for API security
- Custom scripts for tag enforcement testing

## Deployment Strategy

### Infrastructure as Code

**Tool**: Terraform

**Modules**:
- DynamoDB tables
- S3 buckets
- Lambda functions
- OpenSearch domain
- API Gateway
- IAM roles and policies
- EventBridge rules

### CI/CD Pipeline

**Stages**:
1. **Build**: Package Lambda functions, run linters
2. **Test**: Run unit tests, property tests
3. **Deploy to Dev**: Terraform apply to dev environment
4. **Integration Test**: Run integration tests in dev
5. **Deploy to Staging**: Terraform apply to staging
6. **Load Test**: Run load tests in staging
7. **Deploy to Prod**: Terraform apply to prod with approval
8. **Smoke Test**: Run smoke tests in prod

### Rollback Strategy

- Terraform state versioning
- Lambda function versioning and aliases
- DynamoDB point-in-time recovery
- S3 versioning for critical buckets
- Blue-green deployment for API Gateway

### Monitoring and Alerting

**Metrics**:
- Lambda invocation count, duration, errors
- API Gateway request count, latency, 4xx/5xx errors
- DynamoDB read/write capacity, throttles
- OpenSearch cluster health, query latency
- Bedrock API calls, throttles

**Alerts**:
- Lambda error rate > 5%
- API Gateway p95 latency > 3 seconds
- DynamoDB throttling events
- OpenSearch cluster red status
- Bedrock API throttling

**Tools**:
- CloudWatch Logs and Metrics
- CloudWatch Alarms
- SNS for notifications
- CloudWatch Dashboards

## Scalability Considerations

### Horizontal Scaling

- **Lambda**: Automatic scaling up to account limits
- **DynamoDB**: On-demand billing mode for automatic scaling
- **OpenSearch**: Multi-AZ deployment with 2 nodes, can scale to more nodes
- **API Gateway**: Automatic scaling

### Vertical Scaling

- **Lambda Memory**: Start with 512MB-2048MB, adjust based on profiling
- **OpenSearch Instance Type**: Start with t3.medium, upgrade to r6g for memory-intensive workloads

### Data Partitioning

- **DynamoDB**: Use composite keys for even distribution
- **OpenSearch**: Use index sharding for large datasets
- **S3**: Use prefixes for parallel processing

### Caching Strategy

- **API Gateway**: Enable caching for frequently accessed endpoints
- **Lambda**: Cache Bedrock responses for identical inputs
- **Application**: Cache tech trend data, affinity scores

### Cost Optimization

- **Lambda**: Right-size memory, use ARM architecture (Graviton2)
- **DynamoDB**: Use on-demand for unpredictable workloads, provisioned for steady state
- **S3**: Use lifecycle policies to move old data to Glacier
- **OpenSearch**: Use UltraWarm for infrequently accessed data
- **Bedrock**: Batch requests where possible, cache results

## Security Architecture

### Data Protection

- **Encryption at Rest**: All DynamoDB tables, S3 buckets use AES-256
- **Encryption in Transit**: All API calls use HTTPS/TLS 1.2+
- **Key Management**: AWS KMS for encryption keys
- **PII Handling**: Anonymize messenger logs, encrypt employee profiles

### Access Control

- **IAM Roles**: Least privilege principle
- **Tag-Based Policies**: Team2 tag enforcement
- **API Gateway**: IAM authentication
- **OpenSearch**: Fine-grained access control

### Network Security

- **VPC**: OpenSearch deployed in VPC (optional)
- **Security Groups**: Restrict access to necessary ports
- **NACLs**: Additional network layer protection

### Compliance

- **Audit Logging**: CloudTrail for all API calls
- **Data Retention**: Configurable retention policies
- **GDPR**: Right to deletion, data portability
- **SOC 2**: Compliance-ready architecture

## Maintenance and Operations

### Backup and Recovery

- **DynamoDB**: Point-in-time recovery enabled
- **S3**: Versioning enabled for critical buckets
- **OpenSearch**: Automated snapshots to S3
- **Terraform State**: Remote backend with versioning

### Disaster Recovery

- **RTO**: 4 hours
- **RPO**: 1 hour
- **Strategy**: Multi-AZ deployment, automated backups
- **Runbook**: Documented recovery procedures

### Operational Runbooks

1. **Lambda Function Failure**: Check CloudWatch Logs, verify IAM permissions, check downstream services
2. **DynamoDB Throttling**: Increase capacity or switch to on-demand
3. **OpenSearch Cluster Red**: Check cluster health, increase storage, add nodes
4. **Bedrock API Throttling**: Implement backoff, request limit increase
5. **High API Latency**: Check Lambda cold starts, DynamoDB performance, OpenSearch query performance

### Cost Monitoring

- **AWS Cost Explorer**: Track costs by service and tag
- **Budgets**: Set alerts for cost thresholds
- **Cost Allocation Tags**: Team2 tag for cost attribution
- **Optimization**: Regular review of unused resources, right-sizing

## Future Enhancements

### Phase 2 Features

1. **Real-time Collaboration Tracking**: WebSocket-based live updates
2. **Advanced ML Models**: Custom models for skill matching
3. **Multi-language Support**: Internationalization
4. **Mobile App**: Native iOS/Android apps
5. **Slack/Teams Integration**: Bot for recommendations

### Technical Debt

1. **Refactor Monolithic Lambdas**: Split into smaller functions
2. **Implement Caching Layer**: Redis/ElastiCache
3. **Add GraphQL API**: More flexible querying
4. **Improve Test Coverage**: Target 90%+ coverage
5. **Performance Optimization**: Profile and optimize hot paths

### Scalability Roadmap

1. **Multi-Region Deployment**: Global availability
2. **Event-Driven Architecture**: EventBridge for decoupling
3. **Data Lake**: Centralized analytics
4. **Real-time Analytics**: Kinesis Data Streams
5. **Advanced Monitoring**: Distributed tracing with X-Ray
