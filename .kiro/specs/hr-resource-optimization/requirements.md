# Requirements Document

## Introduction

본 시스템은 조직의 인력 배치 최적화 및 프로젝트 투입 인력 추천을 위한 AI 기반 인사 관리 플랫폼입니다. 개인의 이력 정보, 기술 스택, 프로젝트 참여 이력, 인력 간 친밀도를 분석하여 최적의 팀 구성과 신규 도메인 확장 전략을 제공합니다. AWS 클라우드 인프라를 활용하여 확장 가능하고 안전한 서비스를 구현합니다.

## Glossary

- **HR System**: 인력 배치 최적화 및 프로젝트 투입 추천을 수행하는 본 시스템
- **Employee Profile**: 개인의 이력 정보, 기술 스택, 프로젝트 참여 이력을 포함하는 직원 프로필
- **Project**: 특정 기술 스택과 인력이 요구되는 업무 단위
- **Domain**: 사업 영역 또는 기술 분야
- **Affinity Score**: 인력 간의 협업 친밀도를 나타내는 점수
- **Skill Match Score**: 개인의 기술 스택과 프로젝트 요구 기술 간의 적합도 점수
- **Recommendation Engine**: 프로젝트 투입 인력을 추천하는 AI 엔진
- **Domain Analysis Engine**: 신규 도메인 확장 가능성을 분석하는 엔진
- **Freelancer**: 프리랜서 인력
- **Career Hire**: 경력직 신규 입사자
- **Bedrock**: AWS의 생성형 AI 서비스로 Claude 모델을 활용하는 플랫폼
- **Claude Model**: Anthropic의 대규모 언어 모델로 텍스트 분석 및 추론에 사용
- **Textract**: AWS의 문서 텍스트 추출 서비스
- **OpenSearch**: 유사도 검색 및 벡터 검색을 위한 검색 엔진
- **LangGraph**: Lambda에서 실행되는 AI 워크플로우 오케스트레이션 프레임워크
- **Vector Embedding**: 텍스트를 수치 벡터로 변환한 표현
- **Quantitative Analysis**: 정량적 분석 파이프라인
- **Qualitative Analysis**: 정성적 분석 파이프라인
- **Terraform**: 인프라를 코드로 관리하는 IaC(Infrastructure as Code) 도구
- **IaC**: Infrastructure as Code, 인프라를 코드로 정의하고 관리하는 방법론
- **us-east-2**: 본 시스템이 배포되는 AWS 리전 (오하이오)

## Requirements

### Requirement 1

**User Story:** 인사 담당자로서, 개인의 이력 정보와 직무별 요구 기술 스택을 고려한 팀 인력 배치를 원합니다. 이를 통해 최적의 팀 구성으로 프로젝트 성공률을 높이고자 합니다.

#### Acceptance Criteria

1. WHEN 인사 담당자가 직무별 요구 기술 스택을 입력하면 THEN THE HR System SHALL 해당 기술 스택을 보유한 직원 목록을 반환해야 합니다
2. WHEN 직원 프로필이 생성되거나 업데이트되면 THEN THE HR System SHALL 기술 스택 정보를 파싱하고 정규화하여 저장해야 합니다
3. WHEN 팀 구성 요청이 발생하면 THEN THE HR System SHALL 각 직원의 Skill Match Score를 계산하여 상위 후보자를 추천해야 합니다
4. WHEN 추천 결과가 생성되면 THEN THE HR System SHALL 각 후보자의 기술 스택, 경력 연수, 과거 프로젝트 성과를 포함한 상세 정보를 제공해야 합니다

### Requirement 2

**User Story:** 프로젝트 관리자로서, 개인의 프로젝트 참여 이력, 신규 프로젝트의 요구 기술, 인력 간의 친밀도를 기반으로 프로젝트 투입 인력 추천을 받고 싶습니다. 이를 통해 팀 시너지를 극대화하고자 합니다.

#### Acceptance Criteria

1. WHEN 신규 프로젝트 정보가 입력되면 THEN THE HR System SHALL 프로젝트 요구 기술, 기간, 난이도를 분석하여 DynamoDB에 저장해야 합니다
2. WHEN 프로젝트 투입 인력 추천 요청이 발생하면 THEN THE Recommendation Engine SHALL 기술 적합도, 프로젝트 참여 이력, Affinity Score를 종합하여 최적 후보자 목록을 생성해야 합니다
3. WHEN 두 명 이상의 직원이 과거 프로젝트에서 협업한 이력이 있으면 THEN THE HR System SHALL 해당 협업 이력을 기반으로 Affinity Score를 계산하여 DynamoDB에 저장해야 합니다
4. WHEN 추천 결과가 제공되면 THEN THE HR System SHALL 각 후보자의 추천 근거(기술 점수, 이력 점수, 친밀도 점수)를 함께 제공해야 합니다
5. WHEN 직원이 현재 다른 프로젝트에 투입되어 있으면 THEN THE HR System SHALL 해당 직원의 가용성 정보를 추천 결과에 포함해야 합니다

### Requirement 2-1

**User Story:** 인사 담당자로서, 직원 간 친밀도를 다각도로 분석하여 팀 구성 시 협업 효율성을 예측하고 싶습니다. 이를 통해 팀 내 갈등을 최소화하고 생산성을 극대화하고자 합니다.

#### Acceptance Criteria

1. WHEN 두 명 이상의 직원이 동일한 프로젝트에 참여한 이력이 있으면 THEN THE HR System SHALL 프로젝트 참여 기간 중복도를 계산하여 협업 이력 점수를 산출해야 합니다
2. WHEN 사내 메신저 대화 데이터가 수집되면 THEN THE HR System SHALL 개인정보를 익명화 처리한 후 직원 간 연락 빈도를 분석해야 합니다
3. WHEN 연락 빈도가 분석되면 THEN THE HR System SHALL 메시지 송수신 횟수, 응답 속도, 대화 지속 기간을 종합하여 커뮤니케이션 점수를 계산해야 합니다
4. WHEN 사내 행사 참여 데이터가 수집되면 THEN THE HR System SHALL 동일 행사 참여 이력을 분석하여 사회적 친밀도 점수를 산출해야 합니다
5. WHEN 연차 정보와 메신저 데이터가 결합되면 THEN THE HR System SHALL 월급 지급일 또는 연차 사용일에 연락한 빈도를 분석하여 개인적 친밀도 지표를 계산해야 합니다
6. WHEN 모든 친밀도 지표가 계산되면 THEN THE HR System SHALL 협업 이력, 커뮤니케이션, 사회적 친밀도, 개인적 친밀도를 가중 평균하여 종합 Affinity Score를 생성해야 합니다
7. WHEN Affinity Score가 생성되면 THEN THE HR System SHALL 점수를 DynamoDB에 저장하고 주기적으로 업데이트해야 합니다

### Requirement 3

**User Story:** 인사 담당자로서, 신규 경력직 및 프리랜서 투입 시 이력 점검 및 평가를 통한 적정성 여부를 판단하고 싶습니다. 이를 통해 채용 리스크를 최소화하고자 합니다.

#### Acceptance Criteria

1. WHEN 신규 경력직 또는 프리랜서의 이력서가 업로드되면 THEN THE HR System SHALL 이력서에서 기술 스택, 프로젝트 경험, 경력 기간을 자동으로 추출해야 합니다
2. WHEN 이력 정보가 추출되면 THEN THE HR System SHALL 기재된 기술 스택의 최신성과 시장 수요를 분석하여 평가 점수를 산출해야 합니다
3. WHEN 프로젝트 경험이 분석되면 THEN THE HR System SHALL 프로젝트 규모, 역할, 성과를 평가하여 적정성 점수를 계산해야 합니다
4. WHEN 적정성 평가가 완료되면 THEN THE HR System SHALL 종합 평가 점수와 함께 강점, 약점, 추천 투입 프로젝트를 제시해야 합니다
5. IF 이력서에 검증이 필요한 정보가 포함되어 있으면 THEN THE HR System SHALL 해당 항목을 플래그하고 추가 검증 요청을 생성해야 합니다

### Requirement 4

**User Story:** 경영진으로서, 기존 인력 및 경력직 입사 시 과거 프로젝트 이력 기반으로 신규 도메인을 도출하고 싶습니다. 이를 통해 전략적 사업 확장 기회를 발견하고자 합니다.

#### Acceptance Criteria

1. WHEN 전체 직원의 프로젝트 이력이 수집되면 THEN THE Domain Analysis Engine SHALL 프로젝트 도메인, 기술 스택, 산업 분야를 분류하여 분석해야 합니다
2. WHEN 도메인 분석이 수행되면 THEN THE Domain Analysis Engine SHALL 현재 보유하지 않은 잠재적 신규 도메인을 식별해야 합니다
3. WHEN 신규 도메인이 식별되면 THEN THE HR System SHALL 해당 도메인 진입에 필요한 기술 갭과 보유 인력의 전환 가능성을 분석해야 합니다
4. WHEN 경력직이 신규 입사하면 THEN THE HR System SHALL 해당 인력의 과거 프로젝트 도메인을 분석하여 조직의 도메인 포트폴리오를 업데이트해야 합니다

### Requirement 5

**User Story:** 경영진으로서, 신규 도메인에 대한 팀 또는 프로젝트 참여 인력 구성을 추천받고 싶습니다. 이를 통해 신규 사업 진입 시 최적의 팀을 구성하고자 합니다.

#### Acceptance Criteria

1. WHEN 신규 도메인 진입이 결정되면 THEN THE HR System SHALL 해당 도메인에 필요한 핵심 기술 스택과 역할을 정의해야 합니다
2. WHEN 도메인별 필요 역량이 정의되면 THEN THE Recommendation Engine SHALL 현재 인력 중 해당 역량을 보유하거나 학습 가능한 직원을 식별해야 합니다
3. WHEN 후보 인력이 식별되면 THEN THE HR System SHALL 팀 구성 시뮬레이션을 수행하여 최적의 팀 조합을 제안해야 합니다
4. WHEN 팀 구성안이 생성되면 THEN THE HR System SHALL 각 팀원의 역할, 필요 교육, 예상 성과를 포함한 상세 계획을 제공해야 합니다

### Requirement 6

**User Story:** 인사 담당자로서, 역량과 적성에 적합한 인력 배치를 통해 직무 만족도를 향상시키고 인력 이탈을 방지하고 싶습니다. 이를 통해 조직의 안정성을 높이고자 합니다.

#### Acceptance Criteria

1. WHEN 직원의 프로젝트 참여 이력이 누적되면 THEN THE HR System SHALL 직원의 선호 도메인, 기술 영역, 협업 스타일을 분석해야 합니다
2. WHEN 직원 만족도 데이터가 수집되면 THEN THE HR System SHALL 프로젝트 유형, 팀 구성, 역할과 만족도 간의 상관관계를 분석해야 합니다
3. WHEN 신규 프로젝트 배치가 계획되면 THEN THE HR System SHALL 직원의 선호도와 과거 만족도 패턴을 고려하여 배치 적합성을 평가해야 합니다
4. IF 직원이 연속으로 낮은 만족도를 보이면 THEN THE HR System SHALL 이탈 위험 알림을 생성하고 대안 배치를 제안해야 합니다

### Requirement 7

**User Story:** 시스템 관리자로서, 대량의 인력 데이터와 프로젝트 이력을 안전하게 저장하고 빠르게 조회할 수 있기를 원합니다. 이를 통해 시스템의 성능과 보안을 보장하고자 합니다.

#### Acceptance Criteria

1. WHEN 직원 프로필 데이터가 저장되면 THEN THE HR System SHALL 개인정보를 암호화하여 데이터베이스에 저장해야 합니다
2. WHEN 대량의 프로젝트 이력 조회 요청이 발생하면 THEN THE HR System SHALL 5초 이내에 결과를 반환해야 합니다
3. WHEN 데이터베이스 쿼리가 실행되면 THEN THE HR System SHALL 인덱싱을 활용하여 검색 성능을 최적화해야 합니다
4. WHEN 시스템 장애가 발생하면 THEN THE HR System SHALL 자동으로 백업 데이터를 복구하고 서비스를 재개해야 합니다
5. WHEN 사용자가 데이터에 접근하면 THEN THE HR System SHALL 역할 기반 접근 제어를 통해 권한을 검증해야 합니다

### Requirement 8

**User Story:** 데이터 분석가로서, 인력 분석 결과를 시각화하여 경영진에게 보고하고 싶습니다. 이를 통해 데이터 기반 의사결정을 지원하고자 합니다.

#### Acceptance Criteria

1. WHEN 분석 결과가 생성되면 THEN THE HR System SHALL 기술 스택 분포, 도메인 커버리지, 팀 구성 현황을 차트로 시각화해야 합니다
2. WHEN 대시보드가 로드되면 THEN THE HR System SHALL 실시간 인력 가용성, 프로젝트 진행 현황, 추천 대기 건수를 표시해야 합니다
3. WHEN 사용자가 특정 기간을 선택하면 THEN THE HR System SHALL 해당 기간의 인력 배치 이력과 성과 지표를 필터링하여 표시해야 합니다
4. WHEN 보고서 생성 요청이 발생하면 THEN THE HR System SHALL PDF 또는 Excel 형식으로 분석 결과를 내보내기해야 합니다

### Requirement 9

**User Story:** 시스템 아키텍트로서, AWS 클라우드 인프라를 활용하여 확장 가능하고 안정적인 시스템을 구축하고 싶습니다. 이를 통해 비즈니스 성장에 대응하고자 합니다.

#### Acceptance Criteria

1. WHEN 시스템 부하가 증가하면 THEN THE HR System SHALL 자동으로 컴퓨팅 리소스를 확장하여 성능을 유지해야 합니다
2. WHEN API 요청이 발생하면 THEN THE HR System SHALL API Gateway를 통해 요청을 라우팅하고 인증을 수행해야 합니다
3. WHEN 머신러닝 모델 학습이 필요하면 THEN THE HR System SHALL 별도의 컴퓨팅 환경에서 학습을 수행하고 결과를 저장해야 합니다
4. WHEN 정적 파일(이력서, 보고서)이 업로드되면 THEN THE HR System SHALL 객체 스토리지에 안전하게 저장하고 접근 URL을 반환해야 합니다
5. WHEN 시스템 이벤트가 발생하면 THEN THE HR System SHALL 로그를 중앙 집중식으로 수집하고 모니터링해야 합니다

### Requirement 9-1

**User Story:** 보안 관리자로서, IAM 태그 기반 접근 제어를 통해 Team2 리소스에 대한 접근을 제한하고 싶습니다. 이를 통해 리소스 격리와 보안을 강화하고자 합니다.

#### Acceptance Criteria

1. WHEN AWS 리소스가 생성되면 THEN THE HR System SHALL Team=Team2 태그를 자동으로 적용해야 합니다
2. WHEN Lambda 함수가 DynamoDB에 접근하려고 하면 THEN THE HR System SHALL 대상 테이블에 Team=Team2 태그가 있는지 검증해야 합니다
3. WHEN Lambda 함수가 S3 버킷에 접근하려고 하면 THEN THE HR System SHALL 대상 버킷에 Team=Team2 태그가 있는지 검증해야 합니다
4. WHEN Lambda 함수가 OpenSearch 도메인에 접근하려고 하면 THEN THE HR System SHALL 대상 도메인에 Team=Team2 태그가 있는지 검증해야 합니다
5. IF 리소스에 Team=Team2 태그가 없으면 THEN THE HR System SHALL 접근을 거부하고 오류를 반환해야 합니다
6. WHEN IAM 역할이 생성되면 THEN THE HR System SHALL LambdaExecutionRole-Team2 또는 APIGatewayExecutionRole-Team2 명명 규칙을 따라야 합니다
7. WHEN 태그 기반 접근 제어 정책이 적용되면 THEN THE HR System SHALL 모든 리소스 접근 시 태그를 검증해야 합니다

### Requirement 10

**User Story:** 개발자로서, 이력서 파싱 및 데이터 추출 기능이 정확하게 동작하기를 원합니다. 이를 통해 수동 입력 오류를 줄이고 업무 효율성을 높이고자 합니다.

#### Acceptance Criteria

1. WHEN PDF 또는 Word 형식의 이력서가 S3에 업로드되면 THEN THE HR System SHALL Textract를 사용하여 텍스트를 추출해야 합니다
2. WHEN Textract가 텍스트를 추출하면 THEN THE HR System SHALL Lambda 함수를 트리거하여 추출된 텍스트를 처리해야 합니다
3. WHEN 이력서 텍스트가 Lambda로 전달되면 THEN THE HR System SHALL Claude Model을 통해 이름, 연락처, 학력, 경력, 기술 스택을 식별하여 추출해야 합니다
4. WHEN 기술 스택이 추출되면 THEN THE HR System SHALL 표준 기술 명칭으로 정규화하여 DynamoDB에 저장해야 합니다
5. IF 이력서 형식이 지원되지 않으면 THEN THE HR System SHALL 오류 메시지를 반환하고 수동 입력 옵션을 제공해야 합니다
6. WHEN 파싱 결과가 생성되면 THEN THE HR System SHALL 사용자에게 검토 및 수정 기회를 제공해야 합니다

### Requirement 11

**User Story:** 데이터 과학자로서, 인력 간 유사도를 벡터 기반으로 분석하여 최적의 팀 매칭을 수행하고 싶습니다. 이를 통해 협업 시너지를 극대화하고자 합니다.

#### Acceptance Criteria

1. WHEN 직원 프로필이 생성되거나 업데이트되면 THEN THE HR System SHALL 프로필 정보를 Vector Embedding으로 변환해야 합니다
2. WHEN Vector Embedding이 생성되면 THEN THE HR System SHALL OpenSearch에 벡터를 인덱싱하여 저장해야 합니다
3. WHEN 유사 인력 검색 요청이 발생하면 THEN THE HR System SHALL OpenSearch를 통해 벡터 유사도 검색을 수행해야 합니다
4. WHEN 유사도 검색 결과가 반환되면 THEN THE HR System SHALL 유사도 점수와 함께 상위 후보자 목록을 제공해야 합니다
5. WHEN 팀 구성 시뮬레이션이 수행되면 THEN THE HR System SHALL 벡터 유사도를 활용하여 팀원 간 시너지를 예측해야 합니다

### Requirement 12

**User Story:** 시스템 관리자로서, 외부 API를 통해 최신 기술 트렌드 정보를 수집하고 싶습니다. 이를 통해 기술 스택 평가의 정확성을 높이고자 합니다.

#### Acceptance Criteria

1. WHEN 기술 트렌드 업데이트 스케줄이 실행되면 THEN THE HR System SHALL 외부 API를 호출하여 최신 기술 트렌드 데이터를 수집해야 합니다
2. WHEN 외부 API 응답이 수신되면 THEN THE HR System SHALL 데이터를 파싱하여 DynamoDB에 저장해야 합니다
3. WHEN 기술 스택 평가가 수행되면 THEN THE HR System SHALL 저장된 트렌드 데이터를 참조하여 기술의 최신성을 판단해야 합니다
4. IF 외부 API 호출이 실패하면 THEN THE HR System SHALL 캐시된 데이터를 사용하고 재시도 로직을 실행해야 합니다
5. WHEN 트렌드 데이터가 업데이트되면 THEN THE HR System SHALL 기존 직원 프로필의 기술 평가 점수를 재계산해야 합니다

### Requirement 13

**User Story:** AI 엔지니어로서, LangGraph를 활용하여 복잡한 AI 워크플로우를 오케스트레이션하고 싶습니다. 이를 통해 다단계 분석 프로세스를 효율적으로 관리하고자 합니다.

#### Acceptance Criteria

1. WHEN 복잡한 분석 요청이 API Gateway를 통해 수신되면 THEN THE HR System SHALL LangGraph 워크플로우를 실행하는 Lambda 함수를 호출해야 합니다
2. WHEN LangGraph 워크플로우가 시작되면 THEN THE HR System SHALL 정의된 노드 순서에 따라 각 분석 단계를 실행해야 합니다
3. WHEN 각 워크플로우 노드가 실행되면 THEN THE HR System SHALL Bedrock의 Claude Model을 호출하여 AI 추론을 수행해야 합니다
4. WHEN 워크플로우 중간 결과가 생성되면 THEN THE HR System SHALL 결과를 DynamoDB에 저장하여 상태를 유지해야 합니다
5. WHEN 워크플로우가 완료되면 THEN THE HR System SHALL 최종 결과를 API Gateway를 통해 클라이언트에 반환해야 합니다
6. IF 워크플로우 실행 중 오류가 발생하면 THEN THE HR System SHALL 오류를 로깅하고 적절한 에러 응답을 반환해야 합니다

### Requirement 14

**User Story:** 프론트엔드 개발자로서, S3에 호스팅된 정적 웹사이트를 통해 사용자에게 빠르고 안정적인 UI를 제공하고 싶습니다. 이를 통해 사용자 경험을 향상시키고자 합니다.

#### Acceptance Criteria

1. WHEN 사용자가 웹사이트에 접속하면 THEN THE HR System SHALL S3에 호스팅된 정적 파일을 제공해야 합니다
2. WHEN 프론트엔드가 API 요청을 보내면 THEN THE HR System SHALL API Gateway를 통해 백엔드 Lambda 함수로 라우팅해야 합니다
3. WHEN API Gateway가 요청을 수신하면 THEN THE HR System SHALL 인증 토큰을 검증하고 권한을 확인해야 합니다
4. WHEN 백엔드 처리가 완료되면 THEN THE HR System SHALL JSON 형식의 응답을 프론트엔드에 반환해야 합니다
5. WHEN 정적 파일이 업데이트되면 THEN THE HR System SHALL S3 버킷에 새 파일을 배포하고 캐시를 무효화해야 합니다

### Requirement 15

**User Story:** 데이터 엔지니어로서, 정량적 분석과 정성적 분석을 결합하여 종합적인 인력 평가를 수행하고 싶습니다. 이를 통해 다각도의 평가 결과를 제공하고자 합니다.

#### Acceptance Criteria

1. WHEN 인력 평가 요청이 발생하면 THEN THE HR System SHALL 정량적 분석 파이프라인과 정성적 분석 파이프라인을 병렬로 실행해야 합니다
2. WHEN 정량적 분석이 수행되면 THEN THE HR System SHALL 경력 연수, 프로젝트 수, 기술 스택 개수 등 수치 데이터를 분석해야 합니다
3. WHEN 정성적 분석이 수행되면 THEN THE HR System SHALL Claude Model을 사용하여 프로젝트 설명, 역할, 성과를 분석해야 합니다
4. WHEN 두 분석이 완료되면 THEN THE HR System SHALL 정량적 점수와 정성적 평가를 가중 평균하여 종합 점수를 계산해야 합니다
5. WHEN 종합 평가 결과가 생성되면 THEN THE HR System SHALL DynamoDB에 저장하고 사용자에게 반환해야 합니다
