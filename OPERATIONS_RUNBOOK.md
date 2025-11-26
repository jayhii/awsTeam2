# HR Resource Optimization System - 운영 런북 (Operations Runbook)

## 개요

이 운영 런북은 HR Resource Optimization System의 일상적인 운영, 문제 해결, 유지보수 절차를 제공합니다. 시스템 관리자와 DevOps 팀이 신속하게 문제를 진단하고 해결할 수 있도록 구성되었습니다.

## 목차

1. [시스템 아키텍처 개요](#시스템-아키텍처-개요)
2. [일상 운영 작업](#일상-운영-작업)
3. [일반적인 문제 및 해결 방법](#일반적인-문제-및-해결-방법)
4. [모니터링 및 알림](#모니터링-및-알림)
5. [성능 최적화](#성능-최적화)
6. [보안 운영](#보안-운영)
7. [백업 및 복구](#백업-및-복구)
8. [긴급 대응 절차](#긴급-대응-절차)
9. [정기 유지보수](#정기-유지보수)
10. [에스컬레이션 절차](#에스컬레이션-절차)

---

## 시스템 아키텍처 개요

### 주요 컴포넌트

| 컴포넌트 | 서비스 | 용도 | 리전 |
|----------|---------|------|------|
| API Gateway | AWS API Gateway | REST API 엔드포인트 | us-east-2 |
| Lambda Functions | AWS Lambda | 비즈니스 로직 실행 (8개 함수) | us-east-2 |
| DynamoDB | AWS DynamoDB | NoSQL 데이터베이스 (6개 테이블) | us-east-2 |
| OpenSearch | AWS OpenSearch | 벡터 검색 엔진 | us-east-2 |
| S3 | AWS S3 | 객체 스토리지 (4개 버킷) | us-east-2 |
| Bedrock | AWS Bedrock | AI/ML 서비스 (Claude, Titan) | us-east-2 |
| CloudWatch | AWS CloudWatch | 모니터링 및 로깅 | us-east-2 |

### Lambda 함수 목록

1. **ResumeParser**: 이력서 파싱 및 데이터 추출
2. **AffinityScoreCalculator**: 직원 간 친밀도 계산
3. **ProjectRecommendationEngine**: 프로젝트 인력 추천
4. **DomainAnalysisEngine**: 도메인 분석 및 확장 전략
5. **QuantitativeAnalysis**: 정량적 인력 평가
6. **QualitativeAnalysis**: 정성적 인력 평가
7. **TechTrendCollector**: 기술 트렌드 수집
8. **VectorEmbeddingGenerator**: 벡터 임베딩 생성

### DynamoDB 테이블 목록

1. **Employees-Team2**: 직원 프로필
2. **Projects-Team2**: 프로젝트 정보
3. **EmployeeAffinity-Team2**: 직원 간 친밀도
4. **MessengerLogs-Team2**: 메신저 로그
5. **CompanyEvents-Team2**: 회사 행사
6. **TechTrends-Team2**: 기술 트렌드

---

## 일상 운영 작업

### 1. 시스템 상태 확인 (Daily Health Check)

**빈도**: 매일 오전 9시

**체크리스트**:


```bash
#!/bin/bash
# daily_health_check.sh

echo "=== HR Resource Optimization System - Daily Health Check ==="
echo "Date: $(date)"
echo ""

# 1. Lambda 함수 상태 확인
echo "1. Lambda Functions Status:"
aws lambda list-functions \
  --query "Functions[?Tags.Team=='Team2'].{Name:FunctionName,State:State,LastModified:LastModified}" \
  --output table

# 2. DynamoDB 테이블 상태 확인
echo "2. DynamoDB Tables Status:"
for table in Employees Projects EmployeeAffinity MessengerLogs CompanyEvents TechTrends; do
  status=$(aws dynamodb describe-table --table-name ${table}-Team2 --query "Table.TableStatus" --output text 2>/dev/null)
  echo "  ${table}-Team2: ${status:-NOT_FOUND}"
done

# 3. OpenSearch 클러스터 상태 확인
echo "3. OpenSearch Cluster Status:"
aws opensearch describe-domain --domain-name hr-resource-optimization-team2 \
  --query "DomainStatus.{Status:Processing,Health:ClusterConfig.InstanceType}" \
  --output table

# 4. API Gateway 상태 확인
echo "4. API Gateway Status:"
aws apigateway get-rest-apis \
  --query "items[?tags.Team=='Team2'].{Name:name,Id:id}" \
  --output table

# 5. CloudWatch 알람 상태 확인
echo "5. Active Alarms:"
aws cloudwatch describe-alarms \
  --state-value ALARM \
  --query 'MetricAlarms[?contains(AlarmName, `team2`)].{Name:AlarmName,Reason:StateReason}' \
  --output table

# 6. 최근 24시간 에러 로그 확인
echo "6. Recent Errors (Last 24 hours):"
for func in ResumeParser AffinityScoreCalculator ProjectRecommendationEngine; do
  error_count=$(aws logs filter-log-events \
    --log-group-name /aws/lambda/${func} \
    --filter-pattern "ERROR" \
    --start-time $(($(date +%s) - 86400))000 \
    --query 'length(events)' \
    --output text 2>/dev/null)
  echo "  ${func}: ${error_count:-0} errors"
done

echo ""
echo "=== Health Check Complete ==="
```

**실행 방법**:
```bash
chmod +x daily_health_check.sh
./daily_health_check.sh > health_check_$(date +%Y%m%d).log
```

### 2. 로그 검토

**빈도**: 매일

**절차**:

1. **CloudWatch Logs 대시보드 확인**
   - AWS Console → CloudWatch → Dashboards
   - `HR-Lambda-Metrics-Team2` 대시보드 열기
   - 에러 스파이크 확인

2. **에러 로그 분석**
```bash
# 최근 1시간 에러 로그
aws logs filter-log-events \
  --log-group-name /aws/lambda/ResumeParser \
  --filter-pattern "ERROR" \
  --start-time $(($(date +%s) - 3600))000 \
  | jq -r '.events[].message'

# 에러 패턴 분석
aws logs filter-log-events \
  --log-group-name /aws/lambda/ResumeParser \
  --filter-pattern "ERROR" \
  --start-time $(($(date +%s) - 86400))000 \
  | jq -r '.events[].message' \
  | grep -oP 'Exception: \K.*' \
  | sort | uniq -c | sort -rn
```

3. **성능 메트릭 확인**
```bash
# Lambda 평균 실행 시간
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=ProjectRecommendationEngine \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average \
  --output table
```

### 3. 용량 관리

**빈도**: 주간

**DynamoDB 용량 확인**:
```bash
# 테이블별 용량 소비 확인
for table in Employees Projects EmployeeAffinity; do
  echo "Table: ${table}-Team2"
  aws cloudwatch get-metric-statistics \
    --namespace AWS/DynamoDB \
    --metric-name ConsumedReadCapacityUnits \
    --dimensions Name=TableName,Value=${table}-Team2 \
    --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 86400 \
    --statistics Average,Maximum \
    --output table
done
```

**S3 스토리지 사용량 확인**:
```bash
# 버킷별 크기 확인
aws s3 ls | grep team2 | awk '{print $3}' | while read bucket; do
  size=$(aws s3 ls s3://${bucket} --recursive --summarize | grep "Total Size" | awk '{print $3}')
  echo "${bucket}: ${size} bytes"
done
```

### 4. 데이터 정리

**빈도**: 주간

**오래된 로그 정리**:
```bash
# 30일 이상 된 로그 그룹 보존 기간 설정
for log_group in $(aws logs describe-log-groups --query 'logGroups[?contains(logGroupName, `/aws/lambda/`)].logGroupName' --output text); do
  aws logs put-retention-policy \
    --log-group-name ${log_group} \
    --retention-in-days 30
done
```

**S3 라이프사이클 정책 확인**:
```bash
# 버킷별 라이프사이클 정책 확인
aws s3api get-bucket-lifecycle-configuration --bucket hr-resumes-bucket-team2
```

---

## 일반적인 문제 및 해결 방법

### 문제 1: Lambda 함수 타임아웃

**증상**:
- CloudWatch 알람: `lambda-errors-FUNCTION_NAME-team2` 발생
- 로그에 "Task timed out after X seconds" 메시지

**진단**:
```bash
# 최근 타임아웃 발생 확인
aws logs filter-log-events \
  --log-group-name /aws/lambda/ProjectRecommendationEngine \
  --filter-pattern "Task timed out" \
  --start-time $(($(date +%s) - 3600))000

# 평균 실행 시간 확인
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=ProjectRecommendationEngine \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum
```

**해결 방법**:

1. **타임아웃 증가** (임시 조치):
```bash
aws lambda update-function-configuration \
  --function-name ProjectRecommendationEngine \
  --timeout 300
```

2. **메모리 증가** (성능 향상):
```bash
aws lambda update-function-configuration \
  --function-name ProjectRecommendationEngine \
  --memory-size 2048
```

3. **코드 최적화** (근본 해결):
   - 불필요한 API 호출 제거
   - 데이터베이스 쿼리 최적화
   - 병렬 처리 구현

**예방 조치**:
- 정기적인 성능 프로파일링
- 코드 리뷰 시 성능 고려
- 부하 테스트 수행

### 문제 2: DynamoDB 스로틀링

**증상**:
- CloudWatch 알람: `dynamodb-read-throttle-*` 또는 `dynamodb-write-throttle-*` 발생
- 로그에 "ProvisionedThroughputExceededException" 메시지

**진단**:
```bash
# 스로틀링 이벤트 확인
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ReadThrottleEvents \
  --dimensions Name=TableName,Value=Employees-Team2 \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# 현재 용량 모드 확인
aws dynamodb describe-table --table-name Employees-Team2 \
  --query "Table.BillingModeSummary"
```

**해결 방법**:

1. **On-Demand 모드로 전환** (권장):
```bash
aws dynamodb update-table \
  --table-name Employees-Team2 \
  --billing-mode PAY_PER_REQUEST
```

2. **Provisioned 용량 증가**:
```bash
aws dynamodb update-table \
  --table-name Employees-Team2 \
  --provisioned-throughput ReadCapacityUnits=100,WriteCapacityUnits=50
```

3. **Auto Scaling 설정**:
```bash
# Auto Scaling 정책 생성
aws application-autoscaling register-scalable-target \
  --service-namespace dynamodb \
  --resource-id table/Employees-Team2 \
  --scalable-dimension dynamodb:table:ReadCapacityUnits \
  --min-capacity 5 \
  --max-capacity 100
```

**예방 조치**:
- 쿼리 패턴 최적화
- 배치 작업 시간 분산
- GSI 활용

### 문제 3: Bedrock API 스로틀링

**증상**:
- 로그에 "ThrottlingException" 메시지
- API 응답 시간 증가

**진단**:
```bash
# Bedrock 호출 에러 확인
aws logs filter-log-events \
  --log-group-name /aws/lambda/QualitativeAnalysis \
  --filter-pattern "ThrottlingException" \
  --start-time $(($(date +%s) - 3600))000
```

**해결 방법**:

1. **재시도 로직 확인**:
   - Lambda 함수 코드에 exponential backoff 구현 확인
   - 최대 재시도 횟수 조정

2. **할당량 증가 요청**:
```bash
# 현재 할당량 확인
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

3. **캐싱 구현**:
   - 동일한 입력에 대한 응답 캐싱
   - DynamoDB 또는 ElastiCache 활용

**예방 조치**:
- 배치 처리 구현
- 요청 속도 제한
- 대체 모델 준비

### 문제 4: OpenSearch 클러스터 Red 상태

**증상**:
- OpenSearch 클러스터 상태가 Red
- 검색 쿼리 실패

**진단**:
```bash
# 클러스터 상태 확인
aws opensearch describe-domain --domain-name hr-resource-optimization-team2 \
  --query "DomainStatus.{Status:Processing,Health:ClusterConfig}"

# 클러스터 헬스 API 호출
OPENSEARCH_ENDPOINT=$(cd deployment/terraform && terraform output -raw opensearch_endpoint)
curl -XGET "https://${OPENSEARCH_ENDPOINT}/_cluster/health?pretty"

# 인덱스 상태 확인
curl -XGET "https://${OPENSEARCH_ENDPOINT}/_cat/indices?v"
```

**해결 방법**:

1. **샤드 재할당**:
```bash
# 미할당 샤드 확인
curl -XGET "https://${OPENSEARCH_ENDPOINT}/_cat/shards?v" | grep UNASSIGNED

# 샤드 수동 재할당
curl -XPOST "https://${OPENSEARCH_ENDPOINT}/_cluster/reroute" -H 'Content-Type: application/json' -d'
{
  "commands": [
    {
      "allocate_replica": {
        "index": "employee_profiles",
        "shard": 0,
        "node": "node-1"
      }
    }
  ]
}'
```

2. **스토리지 증가**:
```bash
# 현재 스토리지 사용량 확인
curl -XGET "https://${OPENSEARCH_ENDPOINT}/_cat/allocation?v"

# Terraform으로 스토리지 증가
cd deployment/terraform
# monitoring.tf 파일에서 ebs_options.volume_size 증가
terraform apply
```

3. **노드 추가**:
```bash
# Terraform으로 노드 수 증가
cd deployment/terraform
# opensearch.tf 파일에서 instance_count 증가
terraform apply
```

**예방 조치**:
- 정기적인 인덱스 최적화
- 오래된 데이터 삭제
- 스토리지 모니터링

### 문제 5: API Gateway 5XX 에러

**증상**:
- CloudWatch 알람: `api-gateway-5xx-errors-team2` 발생
- 클라이언트가 500 Internal Server Error 수신

**진단**:
```bash
# API Gateway 로그 확인
aws logs filter-log-events \
  --log-group-name API-Gateway-Execution-Logs_*/prod \
  --filter-pattern "5XX" \
  --start-time $(($(date +%s) - 3600))000

# Lambda 통합 에러 확인
aws logs filter-log-events \
  --log-group-name /aws/lambda/ProjectRecommendationEngine \
  --filter-pattern "ERROR" \
  --start-time $(($(date +%s) - 3600))000
```

**해결 방법**:

1. **Lambda 함수 에러 수정**:
   - CloudWatch Logs에서 스택 트레이스 확인
   - 코드 수정 및 재배포

2. **IAM 권한 확인**:
```bash
# Lambda 실행 역할 확인
aws lambda get-function --function-name ProjectRecommendationEngine \
  --query "Configuration.Role"

# 역할 정책 확인
aws iam get-role-policy --role-name LambdaExecutionRole-Team2 --policy-name Team2-DynamoDB-Access
```

3. **API Gateway 통합 설정 확인**:
```bash
# API Gateway 통합 확인
aws apigateway get-integration \
  --rest-api-id API_ID \
  --resource-id RESOURCE_ID \
  --http-method POST
```

**예방 조치**:
- 입력 검증 강화
- 에러 핸들링 개선
- 통합 테스트 수행

---

## 모니터링 및 알림

### CloudWatch 대시보드

**주요 대시보드**:

1. **HR-Lambda-Metrics-Team2**
   - URL: `https://console.aws.amazon.com/cloudwatch/home?region=us-east-2#dashboards:name=HR-Lambda-Metrics-Team2`
   - 메트릭: Invocations, Errors, Duration, Throttles

2. **HR-API-Gateway-Metrics-Team2**
   - URL: `https://console.aws.amazon.com/cloudwatch/home?region=us-east-2#dashboards:name=HR-API-Gateway-Metrics-Team2`
   - 메트릭: Count, 4XXError, 5XXError, Latency

3. **HR-DynamoDB-Metrics-Team2**
   - URL: `https://console.aws.amazon.com/cloudwatch/home?region=us-east-2#dashboards:name=HR-DynamoDB-Metrics-Team2`
   - 메트릭: ConsumedCapacity, Throttles, Errors

### 알람 대응 절차

**알람 수신 시 절차**:

1. **알람 확인**
   - 이메일 또는 SNS 알림 확인
   - 알람 이름 및 상태 확인

2. **영향 범위 평가**
   - 단일 컴포넌트 vs 전체 시스템
   - 사용자 영향 정도

3. **초기 대응**
   - 해당 섹션의 트러블슈팅 가이드 참조
   - 로그 및 메트릭 확인

4. **문제 해결**
   - 임시 조치 적용
   - 근본 원인 분석
   - 영구 해결책 구현

5. **사후 조치**
   - 인시던트 보고서 작성
   - 재발 방지 대책 수립
   - 런북 업데이트

### 알람별 대응 가이드

| 알람 이름 | 우선순위 | 초기 대응 시간 | 대응 절차 |
|-----------|----------|----------------|-----------|
| lambda-errors-* | P2 | 30분 | [문제 1](#문제-1-lambda-함수-타임아웃) 참조 |
| api-gateway-5xx-errors | P1 | 15분 | [문제 5](#문제-5-api-gateway-5xx-에러) 참조 |
| api-gateway-latency | P2 | 1시간 | 성능 최적화 섹션 참조 |
| dynamodb-*-throttle | P2 | 30분 | [문제 2](#문제-2-dynamodb-스로틀링) 참조 |

---

## 성능 최적화

### Lambda 함수 최적화

**메모리 및 타임아웃 조정**:


```bash
# 함수별 권장 설정
declare -A LAMBDA_CONFIG=(
  ["ResumeParser"]="memory=1024,timeout=300"
  ["AffinityScoreCalculator"]="memory=512,timeout=180"
  ["ProjectRecommendationEngine"]="memory=2048,timeout=300"
  ["DomainAnalysisEngine"]="memory=1024,timeout=300"
  ["QuantitativeAnalysis"]="memory=512,timeout=120"
  ["QualitativeAnalysis"]="memory=1024,timeout=180"
  ["TechTrendCollector"]="memory=512,timeout=180"
  ["VectorEmbeddingGenerator"]="memory=1024,timeout=180"
)

# 설정 적용
for func in "${!LAMBDA_CONFIG[@]}"; do
  config=${LAMBDA_CONFIG[$func]}
  memory=$(echo $config | cut -d',' -f1 | cut -d'=' -f2)
  timeout=$(echo $config | cut -d',' -f2 | cut -d'=' -f2)
  
  aws lambda update-function-configuration \
    --function-name $func \
    --memory-size $memory \
    --timeout $timeout
done
```

**Cold Start 최소화**:

1. **Provisioned Concurrency 설정**:
```bash
# 자주 호출되는 함수에 적용
aws lambda put-provisioned-concurrency-config \
  --function-name ProjectRecommendationEngine \
  --provisioned-concurrent-executions 5 \
  --qualifier $LATEST
```

2. **Lambda Layer 활용**:
   - 공통 라이브러리를 Layer로 분리
   - 배포 패키지 크기 감소

### DynamoDB 최적화

**쿼리 패턴 최적화**:

```python
# Bad: Scan 사용
response = table.scan(
    FilterExpression=Attr('skill').eq('Java')
)

# Good: Query with GSI
response = table.query(
    IndexName='SkillIndex',
    KeyConditionExpression=Key('skill').eq('Java')
)
```

**배치 작업 최적화**:

```python
# Bad: 개별 put_item
for item in items:
    table.put_item(Item=item)

# Good: batch_write_item
with table.batch_writer() as batch:
    for item in items:
        batch.put_item(Item=item)
```

### OpenSearch 최적화

**인덱스 최적화**:

```bash
# 인덱스 설정 최적화
curl -XPUT "https://${OPENSEARCH_ENDPOINT}/employee_profiles/_settings" -H 'Content-Type: application/json' -d'
{
  "index": {
    "refresh_interval": "30s",
    "number_of_replicas": 1
  }
}'

# 강제 병합 (세그먼트 최적화)
curl -XPOST "https://${OPENSEARCH_ENDPOINT}/employee_profiles/_forcemerge?max_num_segments=1"
```

**쿼리 최적화**:

```json
{
  "query": {
    "bool": {
      "must": [
        {
          "knn": {
            "profile_vector": {
              "vector": [0.1, 0.2, ...],
              "k": 10
            }
          }
        }
      ],
      "filter": [
        {
          "term": {
            "role": "Software Engineer"
          }
        }
      ]
    }
  }
}
```

---

## 보안 운영

### IAM 권한 감사

**정기 감사** (월간):

```bash
# Team2 관련 IAM 역할 확인
aws iam list-roles --query "Roles[?contains(RoleName, 'Team2')].{Name:RoleName,Created:CreateDate}"

# 역할별 정책 확인
for role in $(aws iam list-roles --query "Roles[?contains(RoleName, 'Team2')].RoleName" --output text); do
  echo "Role: $role"
  aws iam list-attached-role-policies --role-name $role
  aws iam list-role-policies --role-name $role
done

# 최근 30일간 사용되지 않은 역할 확인
aws iam generate-credential-report
aws iam get-credential-report --query 'Content' --output text | base64 -d | grep Team2
```

### 태그 기반 접근 제어 검증

```bash
# 모든 Team2 리소스 확인
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Team,Values=Team2 \
  --region us-east-2 \
  --output table

# 태그 누락 리소스 확인
python deployment/scripts/audit_team2_tags.py
```

### 보안 패치 및 업데이트

**Lambda 런타임 업데이트**:

```bash
# 현재 런타임 버전 확인
aws lambda list-functions \
  --query "Functions[?Tags.Team=='Team2'].{Name:FunctionName,Runtime:Runtime}" \
  --output table

# 런타임 업데이트 (Python 3.11 → 3.12)
for func in $(aws lambda list-functions --query "Functions[?Tags.Team=='Team2' && Runtime=='python3.11'].FunctionName" --output text); do
  aws lambda update-function-configuration \
    --function-name $func \
    --runtime python3.12
done
```

### 암호화 키 로테이션

```bash
# KMS 키 로테이션 상태 확인
aws kms get-key-rotation-status --key-id KEY_ID

# 자동 로테이션 활성화
aws kms enable-key-rotation --key-id KEY_ID
```

---

## 백업 및 복구

### DynamoDB 백업

**On-Demand 백업**:

```bash
# 전체 테이블 백업
for table in Employees Projects EmployeeAffinity MessengerLogs CompanyEvents TechTrends; do
  aws dynamodb create-backup \
    --table-name ${table}-Team2 \
    --backup-name ${table}-backup-$(date +%Y%m%d)
done

# 백업 목록 확인
aws dynamodb list-backups --table-name Employees-Team2
```

**Point-in-Time Recovery (PITR)**:

```bash
# PITR 활성화 확인
aws dynamodb describe-continuous-backups --table-name Employees-Team2

# PITR 활성화
aws dynamodb update-continuous-backups \
  --table-name Employees-Team2 \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true

# 특정 시점으로 복구
aws dynamodb restore-table-to-point-in-time \
  --source-table-name Employees-Team2 \
  --target-table-name Employees-Team2-Restored \
  --restore-date-time $(date -u -d '2 hours ago' +%Y-%m-%dT%H:%M:%S)
```

### S3 백업

**버전 관리 확인**:

```bash
# 버킷별 버전 관리 상태 확인
for bucket in $(aws s3 ls | grep team2 | awk '{print $3}'); do
  versioning=$(aws s3api get-bucket-versioning --bucket $bucket --query 'Status' --output text)
  echo "${bucket}: ${versioning:-Disabled}"
done

# 버전 관리 활성화
aws s3api put-bucket-versioning \
  --bucket hr-resumes-bucket-team2 \
  --versioning-configuration Status=Enabled
```

**크로스 리전 복제**:

```bash
# 복제 규칙 설정
aws s3api put-bucket-replication \
  --bucket hr-resumes-bucket-team2 \
  --replication-configuration file://replication-config.json
```

### OpenSearch 스냅샷

**자동 스냅샷 설정**:

```bash
# 스냅샷 리포지토리 생성
curl -XPUT "https://${OPENSEARCH_ENDPOINT}/_snapshot/backup_repo" -H 'Content-Type: application/json' -d'
{
  "type": "s3",
  "settings": {
    "bucket": "hr-opensearch-snapshots-team2",
    "region": "us-east-2",
    "role_arn": "arn:aws:iam::ACCOUNT_ID:role/OpenSearchSnapshotRole"
  }
}'

# 수동 스냅샷 생성
curl -XPUT "https://${OPENSEARCH_ENDPOINT}/_snapshot/backup_repo/snapshot_$(date +%Y%m%d)" -H 'Content-Type: application/json' -d'
{
  "indices": "employee_profiles,project_requirements",
  "ignore_unavailable": true,
  "include_global_state": false
}'

# 스냅샷 목록 확인
curl -XGET "https://${OPENSEARCH_ENDPOINT}/_snapshot/backup_repo/_all?pretty"
```

**스냅샷 복구**:

```bash
# 스냅샷 복구
curl -XPOST "https://${OPENSEARCH_ENDPOINT}/_snapshot/backup_repo/snapshot_20251126/_restore" -H 'Content-Type: application/json' -d'
{
  "indices": "employee_profiles",
  "ignore_unavailable": true,
  "include_global_state": false,
  "rename_pattern": "(.+)",
  "rename_replacement": "restored_$1"
}'
```

### 복구 테스트

**분기별 복구 테스트**:

```bash
#!/bin/bash
# disaster_recovery_test.sh

echo "=== Disaster Recovery Test ==="
echo "Date: $(date)"

# 1. DynamoDB 복구 테스트
echo "1. Testing DynamoDB restore..."
aws dynamodb restore-table-from-backup \
  --target-table-name Employees-Team2-Test \
  --backup-arn $(aws dynamodb list-backups --table-name Employees-Team2 --query 'BackupSummaries[0].BackupArn' --output text)

# 2. S3 복구 테스트
echo "2. Testing S3 restore..."
aws s3 cp s3://hr-resumes-bucket-team2/test-file.pdf s3://hr-resumes-bucket-team2-test/test-file.pdf

# 3. OpenSearch 복구 테스트
echo "3. Testing OpenSearch restore..."
curl -XPOST "https://${OPENSEARCH_ENDPOINT}/_snapshot/backup_repo/latest/_restore" -H 'Content-Type: application/json' -d'
{
  "indices": "employee_profiles",
  "rename_pattern": "(.+)",
  "rename_replacement": "test_$1"
}'

echo "=== Test Complete ==="
```

---

## 긴급 대응 절차

### P1 인시던트 (전체 시스템 장애)

**정의**: 서비스 전체가 사용 불가능한 상태

**대응 절차**:

1. **인시던트 선언** (0-5분)
   - 인시던트 채널 생성 (Slack/Teams)
   - 관련 팀원 호출
   - 경영진 통보

2. **초기 평가** (5-15분)
```bash
# 전체 시스템 상태 확인
./deployment/scripts/emergency_check.sh

# API Gateway 상태
aws apigateway get-rest-apis --query "items[?tags.Team=='Team2']"

# Lambda 함수 상태
aws lambda list-functions --query "Functions[?Tags.Team=='Team2'].{Name:FunctionName,State:State}"

# DynamoDB 테이블 상태
for table in Employees Projects EmployeeAffinity; do
  aws dynamodb describe-table --table-name ${table}-Team2 --query "Table.TableStatus"
done

# OpenSearch 클러스터 상태
aws opensearch describe-domain --domain-name hr-resource-optimization-team2
```

3. **임시 복구** (15-30분)
   - 영향받은 컴포넌트 재시작
   - 트래픽 우회 (필요 시)
   - 백업에서 복구 (필요 시)

4. **근본 원인 분석** (30분-2시간)
   - 로그 분석
   - 메트릭 분석
   - 타임라인 재구성

5. **영구 해결** (2-4시간)
   - 코드 수정
   - 인프라 변경
   - 배포 및 검증

6. **사후 조치** (24시간 이내)
   - 포스트모템 작성
   - 재발 방지 대책
   - 런북 업데이트

### P2 인시던트 (부분 기능 장애)

**정의**: 일부 기능이 사용 불가능하거나 성능 저하

**대응 절차**:

1. **영향 범위 확인** (0-10분)
2. **해당 컴포넌트 트러블슈팅** (10-30분)
3. **문제 해결** (30분-2시간)
4. **모니터링 강화** (지속)

### 롤백 절차

**Lambda 함수 롤백**:

```bash
# 이전 버전 확인
aws lambda list-versions-by-function --function-name ProjectRecommendationEngine

# 특정 버전으로 롤백
aws lambda update-alias \
  --function-name ProjectRecommendationEngine \
  --name prod \
  --function-version 5

# 또는 Terraform으로 롤백
cd deployment/terraform
git checkout HEAD~1 -- lambda.tf
terraform apply
```

**Terraform 인프라 롤백**:

```bash
cd deployment/terraform

# 현재 상태 백업
terraform state pull > backup.tfstate

# 이전 상태로 롤백
terraform state push previous.tfstate

# 또는 특정 리소스만 롤백
terraform apply -target=aws_lambda_function.recommendation_engine
```

---

## 정기 유지보수

### 일간 작업

- [ ] 시스템 상태 확인 (Health Check)
- [ ] CloudWatch 알람 검토
- [ ] 에러 로그 분석
- [ ] 성능 메트릭 확인

### 주간 작업

- [ ] 용량 관리 (DynamoDB, S3)
- [ ] 오래된 로그 정리
- [ ] 보안 패치 확인
- [ ] 백업 검증

### 월간 작업

- [ ] IAM 권한 감사
- [ ] 비용 분석 및 최적화
- [ ] 성능 최적화 검토
- [ ] 문서 업데이트

### 분기별 작업

- [ ] 복구 테스트 (DR Test)
- [ ] 보안 감사
- [ ] 아키텍처 리뷰
- [ ] 용량 계획

### 연간 작업

- [ ] 전체 시스템 아키텍처 리뷰
- [ ] 기술 스택 업그레이드
- [ ] 재해 복구 계획 업데이트
- [ ] 팀 교육 및 훈련

---

## 에스컬레이션 절차

### 에스컬레이션 레벨

| 레벨 | 담당자 | 대응 시간 | 연락 방법 |
|------|--------|-----------|-----------|
| L1 | 운영 엔지니어 | 즉시 | Slack, 이메일 |
| L2 | 시니어 엔지니어 | 30분 | 전화, Slack |
| L3 | 시스템 아키텍트 | 1시간 | 전화 |
| L4 | CTO | 2시간 | 전화 |

### 에스컬레이션 기준

**L1 → L2**:
- 30분 내 해결 불가
- 알려지지 않은 문제
- 여러 컴포넌트 영향

**L2 → L3**:
- 1시간 내 해결 불가
- 아키텍처 변경 필요
- 데이터 손실 위험

**L3 → L4**:
- 2시간 내 해결 불가
- 비즈니스 크리티컬
- 보안 침해 의심

### 연락처

```
L1: operations@example.com, #ops-team (Slack)
L2: senior-eng@example.com, +1-555-0101
L3: architect@example.com, +1-555-0102
L4: cto@example.com, +1-555-0103

AWS Support: https://console.aws.amazon.com/support/
```

---

## 부록

### A. 유용한 스크립트

**시스템 상태 요약**:
```bash
#!/bin/bash
# system_status.sh

echo "=== System Status Summary ==="
echo "Lambda Functions: $(aws lambda list-functions --query "length(Functions[?Tags.Team=='Team2'])")"
echo "DynamoDB Tables: $(aws dynamodb list-tables --query "length(TableNames[?contains(@, 'Team2')])")"
echo "Active Alarms: $(aws cloudwatch describe-alarms --state-value ALARM --query "length(MetricAlarms[?contains(AlarmName, 'team2')])")"
echo "Recent Errors: $(aws logs filter-log-events --log-group-name /aws/lambda/ResumeParser --filter-pattern ERROR --start-time $(($(date +%s) - 3600))000 --query 'length(events)')"
```

### B. 체크리스트

**배포 전 체크리스트**:
- [ ] 코드 리뷰 완료
- [ ] 단위 테스트 통과
- [ ] 통합 테스트 통과
- [ ] 성능 테스트 완료
- [ ] 보안 스캔 완료
- [ ] 문서 업데이트
- [ ] 롤백 계획 수립
- [ ] 모니터링 설정 확인

**인시던트 대응 체크리스트**:
- [ ] 인시던트 선언
- [ ] 영향 범위 확인
- [ ] 초기 대응 수행
- [ ] 로그 수집
- [ ] 근본 원인 분석
- [ ] 영구 해결책 구현
- [ ] 포스트모템 작성
- [ ] 재발 방지 대책

### C. 참고 문서

- [API 문서](API_DOCUMENTATION.md)
- [배포 가이드](deployment/DEPLOYMENT_GUIDE.md)
- [모니터링 가이드](deployment/MONITORING_GUIDE.md)
- [AWS Lambda 모범 사례](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [DynamoDB 모범 사례](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [OpenSearch 모범 사례](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/bp.html)

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 2025-11-26 | 1.0.0 | 초기 버전 작성 | DevOps Team |

---

**문서 유지보수**: 이 런북은 분기별로 검토하고 업데이트해야 합니다.

**피드백**: 개선 사항이나 추가 필요한 내용은 operations@example.com으로 연락 주세요.
