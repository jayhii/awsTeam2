# CloudWatch 모니터링 및 알림 가이드

## 개요

HR Resource Optimization System은 AWS CloudWatch를 활용한 포괄적인 모니터링 및 알림 시스템을 제공합니다. 이 가이드는 모니터링 설정, 대시보드 사용, 알람 관리 방법을 설명합니다.

## 자동 생성 리소스

Terraform 배포 시 자동으로 생성되는 모니터링 리소스:

### 1. CloudWatch 대시보드 (3개)

#### HR-Lambda-Metrics-Team2
Lambda 함수의 성능 및 상태를 모니터링합니다.

**메트릭:**
- **Invocations**: 함수 호출 횟수
- **Errors**: 에러 발생 건수
- **Duration**: 평균 실행 시간 (ms)
- **Throttles**: 스로틀링 이벤트

**모니터링 대상 Lambda 함수:**
- ResumeParser
- AffinityScoreCalculator
- ProjectRecommendationEngine
- DomainAnalysisEngine
- QuantitativeAnalysis
- QualitativeAnalysis
- TechTrendCollector
- VectorEmbeddingGenerator

#### HR-API-Gateway-Metrics-Team2
API Gateway의 요청 처리 상태를 모니터링합니다.

**메트릭:**
- **Count**: 총 요청 수
- **4XXError**: 클라이언트 에러 (잘못된 요청)
- **5XXError**: 서버 에러 (내부 오류)
- **Latency**: 전체 응답 시간
- **IntegrationLatency**: 백엔드 처리 시간

#### HR-DynamoDB-Metrics-Team2
DynamoDB 테이블의 성능 및 용량을 모니터링합니다.

**메트릭:**
- **ConsumedReadCapacityUnits**: 읽기 용량 소비량
- **ConsumedWriteCapacityUnits**: 쓰기 용량 소비량
- **UserErrors**: 사용자 에러 (잘못된 요청)
- **SystemErrors**: 시스템 에러
- **ReadThrottleEvents**: 읽기 스로틀링
- **WriteThrottleEvents**: 쓰기 스로틀링

**모니터링 대상 테이블:**
- Employees
- Projects
- EmployeeAffinity
- MessengerLogs
- CompanyEvents
- TechTrends

### 2. CloudWatch 알람 (16개)

#### Lambda 에러 알람 (8개)
각 Lambda 함수별로 에러율을 모니터링합니다.

**알람 조건:**
- 5분 동안 에러 5건 이상 발생 시
- 2회 연속 임계값 초과 시 알람 발생

**알람 목록:**
- `lambda-errors-resume-parser-team2`
- `lambda-errors-affinity-calculator-team2`
- `lambda-errors-recommendation-engine-team2`
- `lambda-errors-domain-analysis-team2`
- `lambda-errors-quantitative-analysis-team2`
- `lambda-errors-qualitative-analysis-team2`
- `lambda-errors-tech-trend-collector-team2`
- `lambda-errors-vector-embedding-team2`

#### API Gateway 알람 (2개)

**레이턴시 알람:**
- 이름: `api-gateway-latency-team2`
- 조건: 5분 평균 레이턴시 > 5000ms
- 설명: API 응답 시간이 5초를 초과하면 알람

**5XX 에러 알람:**
- 이름: `api-gateway-5xx-errors-team2`
- 조건: 5분 동안 5XX 에러 > 10건
- 설명: 서버 에러가 임계값을 초과하면 알람

#### DynamoDB 스로틀링 알람 (6개)

주요 테이블의 읽기/쓰기 스로틀링을 모니터링합니다.

**알람 조건:**
- 5분 동안 스로틀링 5건 이상 발생 시
- 2회 연속 임계값 초과 시 알람 발생

**알람 목록:**
- `dynamodb-read-throttle-employees-team2`
- `dynamodb-write-throttle-employees-team2`
- `dynamodb-read-throttle-projects-team2`
- `dynamodb-write-throttle-projects-team2`
- `dynamodb-read-throttle-affinity-team2`
- `dynamodb-write-throttle-affinity-team2`

### 3. SNS Topic

**Topic 이름:** `hr-resource-optimization-alarms-team2`

**용도:**
- 모든 CloudWatch 알람의 알림 대상
- 이메일, SMS 등 다양한 프로토콜 지원

## 설정 방법

### 1. 자동 설정 스크립트 사용

#### Linux/macOS
```bash
cd deployment
chmod +x setup_monitoring.sh
./setup_monitoring.sh
```

#### Windows (PowerShell)
```powershell
cd deployment
.\setup_monitoring.ps1
```

스크립트 기능:
- CloudWatch 대시보드 확인
- SNS Topic 확인
- 현재 구독 목록 조회
- 이메일 알림 구독 추가
- CloudWatch 알람 상태 확인

### 2. 수동 설정

#### 이메일 알림 구독

**방법 1: Terraform 변수 사용 (권장)**

`deployment/terraform/terraform.tfvars` 파일에 추가:
```hcl
alarm_email_addresses = [
  "admin@example.com",
  "devops@example.com",
  "team-lead@example.com"
]
```

Terraform 재배포:
```bash
cd deployment/terraform
terraform apply
```

**방법 2: AWS CLI 사용**

```bash
# SNS Topic ARN 확인
SNS_TOPIC_ARN=$(cd deployment/terraform && terraform output -raw sns_topic_arn)

# 이메일 구독 추가
aws sns subscribe \
  --topic-arn $SNS_TOPIC_ARN \
  --protocol email \
  --notification-endpoint your-email@example.com
```

**방법 3: AWS Console 사용**

1. AWS Console → SNS 서비스
2. Topics → `hr-resource-optimization-alarms-team2` 선택
3. "Create subscription" 클릭
4. Protocol: Email 선택
5. Endpoint: 이메일 주소 입력
6. "Create subscription" 클릭
7. 이메일 확인 링크 클릭

## 대시보드 사용법

### 대시보드 접근

**AWS Console:**
```
https://console.aws.amazon.com/cloudwatch/home?region=us-east-2#dashboards:
```

**AWS CLI:**
```bash
# 대시보드 목록 확인
aws cloudwatch list-dashboards --query 'DashboardEntries[?contains(DashboardName, `Team2`)].DashboardName'

# 특정 대시보드 조회
aws cloudwatch get-dashboard --dashboard-name HR-Lambda-Metrics-Team2
```

### 대시보드 커스터마이징

1. AWS Console에서 대시보드 열기
2. "Actions" → "View/edit source" 클릭
3. JSON 편집
4. "Update" 클릭

또는 Terraform 파일 수정:
```bash
# deployment/terraform/monitoring.tf 파일 편집
vim deployment/terraform/monitoring.tf

# 변경사항 적용
terraform apply
```

### 시간 범위 변경

대시보드 상단에서 시간 범위 선택:
- 1시간
- 3시간
- 12시간
- 1일
- 1주일
- 커스텀 범위

### 자동 새로고침

대시보드 상단에서 자동 새로고침 간격 설정:
- 10초
- 1분
- 5분
- 15분

## 알람 관리

### 알람 상태 확인

**AWS CLI:**
```bash
# 모든 알람 상태 확인
aws cloudwatch describe-alarms \
  --query 'MetricAlarms[?contains(AlarmName, `team2`)].{Name:AlarmName,State:StateValue}' \
  --output table

# 특정 알람 상세 정보
aws cloudwatch describe-alarms \
  --alarm-names lambda-errors-resume-parser-team2
```

**AWS Console:**
```
https://console.aws.amazon.com/cloudwatch/home?region=us-east-2#alarmsV2:
```

### 알람 임계값 조정

`deployment/terraform/monitoring.tf` 파일에서 임계값 수정:

```hcl
resource "aws_cloudwatch_metric_alarm" "lambda_errors_resume_parser" {
  # ...
  threshold = 10  # 5에서 10으로 변경
  # ...
}
```

변경사항 적용:
```bash
cd deployment/terraform
terraform apply
```

### 알람 일시 중지

**AWS CLI:**
```bash
# 알람 비활성화
aws cloudwatch disable-alarm-actions \
  --alarm-names lambda-errors-resume-parser-team2

# 알람 재활성화
aws cloudwatch enable-alarm-actions \
  --alarm-names lambda-errors-resume-parser-team2
```

**AWS Console:**
1. CloudWatch → Alarms
2. 알람 선택
3. "Actions" → "Disable"

### 알람 테스트

알람이 정상 작동하는지 테스트:

```bash
# Lambda 함수에 잘못된 입력 전송
aws lambda invoke \
  --function-name ResumeParser \
  --payload '{"invalid": "data"}' \
  response.json

# 여러 번 반복하여 임계값 초과
for i in {1..10}; do
  aws lambda invoke \
    --function-name ResumeParser \
    --payload '{"invalid": "data"}' \
    response.json
  sleep 1
done

# 알람 상태 확인 (약 5-10분 후)
aws cloudwatch describe-alarms \
  --alarm-names lambda-errors-resume-parser-team2 \
  --query 'MetricAlarms[0].StateValue'
```

## 로그 모니터링

### CloudWatch Logs 접근

**AWS CLI:**
```bash
# 로그 그룹 목록
aws logs describe-log-groups \
  --query 'logGroups[?contains(logGroupName, `/aws/lambda/`)].logGroupName'

# 최근 로그 스트림
aws logs tail /aws/lambda/ResumeParser --follow

# 에러 로그 필터링
aws logs filter-log-events \
  --log-group-name /aws/lambda/ResumeParser \
  --filter-pattern "ERROR"

# 특정 기간 로그
aws logs filter-log-events \
  --log-group-name /aws/lambda/ResumeParser \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --end-time $(date +%s)000
```

**AWS Console:**
```
https://console.aws.amazon.com/cloudwatch/home?region=us-east-2#logsV2:log-groups
```

### 로그 인사이트 쿼리

CloudWatch Logs Insights를 사용한 고급 쿼리:

```sql
-- 에러 발생 빈도
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() by bin(5m)

-- 가장 느린 Lambda 실행
fields @timestamp, @duration
| sort @duration desc
| limit 20

-- 특정 사용자 ID 관련 로그
fields @timestamp, @message
| filter @message like /user_id: U_001/
| sort @timestamp desc

-- API Gateway 5XX 에러
fields @timestamp, @message
| filter status >= 500
| stats count() by status
```

## 메트릭 조회

### 주요 메트릭 확인

**Lambda 함수 호출 수:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=ResumeParser \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

**API Gateway 요청 수:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiName,Value=HR-Resource-Optimization-API \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

**DynamoDB 용량 소비:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=Employees \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

## 커스텀 알람 추가

새로운 알람이 필요한 경우 `deployment/terraform/monitoring.tf`에 추가:

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

## 비용 최적화

### 모니터링 비용 절감 팁

1. **로그 보존 기간 설정**
```bash
# 로그 보존 기간을 7일로 설정
aws logs put-retention-policy \
  --log-group-name /aws/lambda/ResumeParser \
  --retention-in-days 7
```

2. **불필요한 메트릭 필터 제거**
```bash
# 메트릭 필터 목록 확인
aws logs describe-metric-filters \
  --log-group-name /aws/lambda/ResumeParser
```

3. **대시보드 위젯 최적화**
- 필요한 메트릭만 표시
- 시간 범위를 적절히 설정
- 자동 새로고침 간격 조정

## 트러블슈팅

### 문제 1: 알람이 발생하지 않음

**확인 사항:**
1. 알람 상태 확인
```bash
aws cloudwatch describe-alarms --alarm-names lambda-errors-resume-parser-team2
```

2. SNS 구독 확인
```bash
aws sns list-subscriptions-by-topic --topic-arn YOUR_TOPIC_ARN
```

3. 이메일 구독 확인 (Pending → Confirmed)

### 문제 2: 대시보드가 표시되지 않음

**해결 방법:**
1. Terraform 상태 확인
```bash
cd deployment/terraform
terraform state list | grep cloudwatch_dashboard
```

2. 대시보드 재생성
```bash
terraform taint aws_cloudwatch_dashboard.lambda_metrics
terraform apply
```

### 문제 3: 로그가 표시되지 않음

**확인 사항:**
1. Lambda 함수 실행 권한
2. CloudWatch Logs 권한
3. 로그 그룹 존재 여부

```bash
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/
```

## 모범 사례

1. **알람 임계값 조정**
   - 초기 임계값은 보수적으로 설정
   - 실제 운영 데이터를 기반으로 조정
   - False positive를 최소화

2. **알림 채널 다양화**
   - 중요 알람: 이메일 + SMS
   - 일반 알람: 이메일만
   - 정보성 알람: Slack/Teams 통합

3. **정기적인 검토**
   - 주간 대시보드 리뷰
   - 월간 알람 임계값 검토
   - 분기별 모니터링 전략 평가

4. **문서화**
   - 알람 대응 절차 문서화
   - 에스컬레이션 프로세스 정의
   - 온콜 담당자 지정

## 참고 자료

- [AWS CloudWatch 문서](https://docs.aws.amazon.com/cloudwatch/)
- [CloudWatch 알람 모범 사례](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Best_Practice_Recommended_Alarms_AWS_Services.html)
- [CloudWatch Logs Insights 쿼리 문법](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CWL_QuerySyntax.html)

