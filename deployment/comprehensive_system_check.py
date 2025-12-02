"""
HR Resource Optimization 시스템 종합 점검
모든 구성 요소의 상태를 확인하고 문제를 진단합니다.
"""
import boto3
import json
import requests
from decimal import Decimal
from datetime import datetime

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

print("=" * 80)
print("HR Resource Optimization 시스템 종합 점검")
print(f"점검 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

issues = []
warnings = []
successes = []

# 1. DynamoDB 테이블 확인
print("\n[1/7] DynamoDB 테이블 상태 확인")
print("-" * 80)

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
client = boto3.client('dynamodb', region_name='us-east-2')

required_tables = {
    'Employees': 300,
    'Projects': 100,
    'MessengerLogs': 2000,
    'EmployeeAffinity': 5,
    'CompanyEvents': 6,
    'EmployeeEvaluations': 0,
    'TechTrends': 0
}

try:
    response = client.list_tables()
    existing_tables = response.get('TableNames', [])
    
    for table_name, expected_count in required_tables.items():
        if table_name in existing_tables:
            table = dynamodb.Table(table_name)
            item_count = table.item_count
            
            if expected_count > 0:
                if item_count >= expected_count * 0.9:  # 90% 이상이면 OK
                    print(f"  ✓ {table_name:25s}: {item_count:,}개 (예상: {expected_count:,}개)")
                    successes.append(f"{table_name} 테이블 정상")
                elif item_count > 0:
                    print(f"  ⚠ {table_name:25s}: {item_count:,}개 (예상: {expected_count:,}개) - 데이터 부족")
                    warnings.append(f"{table_name} 테이블에 데이터가 부족합니다 ({item_count}/{expected_count})")
                else:
                    print(f"  ✗ {table_name:25s}: 데이터 없음")
                    issues.append(f"{table_name} 테이블이 비어있습니다")
            else:
                if item_count == 0:
                    print(f"  ○ {table_name:25s}: 데이터 없음 (선택사항)")
                else:
                    print(f"  ✓ {table_name:25s}: {item_count:,}개")
                    successes.append(f"{table_name} 테이블에 데이터 있음")
        else:
            print(f"  ✗ {table_name:25s}: 테이블 없음")
            issues.append(f"{table_name} 테이블이 존재하지 않습니다")
            
except Exception as e:
    print(f"  ✗ DynamoDB 조회 실패: {str(e)}")
    issues.append(f"DynamoDB 접근 오류: {str(e)}")

# 2. Lambda 함수 확인
print("\n[2/7] Lambda 함수 상태 확인")
print("-" * 80)

lambda_client = boto3.client('lambda', region_name='us-east-2')

required_lambdas = [
    'ProjectsList',
    'EmployeesList',
    'RecommendationEngine',
    'DomainAnalysis',
    'QuantitativeAnalysis',
    'QualitativeAnalysis'
]

for lambda_name in required_lambdas:
    try:
        response = lambda_client.get_function(FunctionName=lambda_name)
        config = response['Configuration']
        
        last_modified = config['LastModified']
        code_size = config['CodeSize']
        runtime = config['Runtime']
        
        print(f"  ✓ {lambda_name:25s}: {runtime}, {code_size:,} bytes, 수정: {last_modified}")
        successes.append(f"{lambda_name} Lambda 함수 정상")
        
    except lambda_client.exceptions.ResourceNotFoundException:
        print(f"  ✗ {lambda_name:25s}: 함수 없음")
        issues.append(f"{lambda_name} Lambda 함수가 존재하지 않습니다")
    except Exception as e:
        print(f"  ✗ {lambda_name:25s}: 오류 - {str(e)[:50]}")
        issues.append(f"{lambda_name} Lambda 함수 조회 오류")

# 3. API Gateway 확인
print("\n[3/7] API Gateway 상태 확인")
print("-" * 80)

api_base_url = "https://ifeniowvpb.execute-api.us-east-2.amazonaws.com/prod"
api_id = "ifeniowvpb"

apigateway = boto3.client('apigateway', region_name='us-east-2')

try:
    api_info = apigateway.get_rest_api(restApiId=api_id)
    print(f"  ✓ API 이름: {api_info['name']}")
    print(f"  ✓ API ID: {api_info['id']}")
    
    # 리소스 확인
    resources = apigateway.get_resources(restApiId=api_id)
    
    required_endpoints = ['/projects', '/employees', '/recommendations', '/domain-analysis']
    found_endpoints = [r['path'] for r in resources['items']]
    
    for endpoint in required_endpoints:
        if endpoint in found_endpoints:
            print(f"  ✓ 엔드포인트: {endpoint}")
            successes.append(f"API Gateway {endpoint} 엔드포인트 존재")
        else:
            print(f"  ✗ 엔드포인트: {endpoint} - 없음")
            issues.append(f"API Gateway {endpoint} 엔드포인트가 없습니다")
    
except Exception as e:
    print(f"  ✗ API Gateway 조회 실패: {str(e)}")
    issues.append(f"API Gateway 접근 오류: {str(e)}")

# 4. API 엔드포인트 테스트
print("\n[4/7] API 엔드포인트 응답 테스트")
print("-" * 80)

test_endpoints = {
    '/projects': {'expected_field': 'projects', 'expected_count': 100},
    '/employees': {'expected_field': 'employees', 'expected_count': 300}
}

for endpoint, config in test_endpoints.items():
    url = f"{api_base_url}{endpoint}"
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if config['expected_field'] in data:
                count = len(data[config['expected_field']])
                expected = config['expected_count']
                
                if count >= expected * 0.9:
                    print(f"  ✓ {endpoint:20s}: {count}개 항목 반환")
                    successes.append(f"{endpoint} API 정상 응답")
                    
                    # 첫 번째 항목 필드 체크
                    if count > 0:
                        first_item = data[config['expected_field']][0]
                        
                        if endpoint == '/projects':
                            required_fields = ['project_id', 'project_name', 'start_date', 'end_date', 'team_members', 'team_size']
                            missing_fields = [f for f in required_fields if f not in first_item]
                            
                            if missing_fields:
                                print(f"    ⚠ 누락된 필드: {', '.join(missing_fields)}")
                                warnings.append(f"{endpoint} API 응답에 필드 누락: {', '.join(missing_fields)}")
                            else:
                                print(f"    ✓ 모든 필수 필드 포함")
                                
                                # team_members 구조 확인
                                if first_item.get('team_members'):
                                    first_member = first_item['team_members'][0]
                                    if 'user_id' in first_member:
                                        print(f"    ✓ team_members에 user_id 포함")
                                    else:
                                        print(f"    ✗ team_members에 user_id 없음")
                                        issues.append(f"{endpoint} API의 team_members에 user_id가 없습니다")
                else:
                    print(f"  ⚠ {endpoint:20s}: {count}개 항목 (예상: {expected}개)")
                    warnings.append(f"{endpoint} API 응답 데이터 부족 ({count}/{expected})")
            else:
                print(f"  ✗ {endpoint:20s}: 응답 형식 오류")
                issues.append(f"{endpoint} API 응답에 {config['expected_field']} 필드가 없습니다")
        else:
            print(f"  ✗ {endpoint:20s}: HTTP {response.status_code}")
            issues.append(f"{endpoint} API가 {response.status_code} 오류를 반환합니다")
            
    except requests.exceptions.Timeout:
        print(f"  ✗ {endpoint:20s}: 타임아웃")
        issues.append(f"{endpoint} API 응답 타임아웃")
    except Exception as e:
        print(f"  ✗ {endpoint:20s}: {str(e)[:50]}")
        issues.append(f"{endpoint} API 테스트 실패: {str(e)[:50]}")

# 5. S3 버킷 확인
print("\n[5/7] S3 버킷 상태 확인")
print("-" * 80)

s3_client = boto3.client('s3', region_name='us-east-2')

required_buckets = [
    'hr-resource-optimization-frontend-hosting-prod',
    'hr-resumes-team2'
]

for bucket_name in required_buckets:
    try:
        response = s3_client.head_bucket(Bucket=bucket_name)
        
        # 버킷 내 파일 수 확인
        objects = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=10)
        file_count = objects.get('KeyCount', 0)
        
        if file_count > 0:
            print(f"  ✓ {bucket_name:50s}: {file_count}+ 파일")
            successes.append(f"{bucket_name} S3 버킷 정상")
        else:
            print(f"  ⚠ {bucket_name:50s}: 파일 없음")
            warnings.append(f"{bucket_name} S3 버킷이 비어있습니다")
            
    except s3_client.exceptions.NoSuchBucket:
        print(f"  ✗ {bucket_name:50s}: 버킷 없음")
        issues.append(f"{bucket_name} S3 버킷이 존재하지 않습니다")
    except Exception as e:
        print(f"  ✗ {bucket_name:50s}: {str(e)[:50]}")
        issues.append(f"{bucket_name} S3 버킷 접근 오류")

# 6. 프론트엔드 배포 확인
print("\n[6/7] 프론트엔드 배포 상태 확인")
print("-" * 80)

frontend_url = "http://hr-resource-optimization-frontend-hosting-prod.s3-website.us-east-2.amazonaws.com"

try:
    response = requests.get(frontend_url, timeout=10)
    
    if response.status_code == 200:
        content = response.text
        
        # 기본 체크
        if '<html' in content.lower():
            print(f"  ✓ 프론트엔드 접근 가능")
            successes.append("프론트엔드 배포 정상")
            
            # React 앱 체크
            if 'root' in content:
                print(f"  ✓ React 앱 구조 확인")
            else:
                print(f"  ⚠ React 앱 구조 불확실")
                warnings.append("프론트엔드 React 앱 구조 확인 필요")
                
            # API URL 체크
            if 'ifeniowvpb.execute-api' in content:
                print(f"  ✓ API URL 설정 확인")
            else:
                print(f"  ⚠ API URL 설정 불확실")
                warnings.append("프론트엔드 API URL 설정 확인 필요")
        else:
            print(f"  ✗ 프론트엔드 응답 형식 오류")
            issues.append("프론트엔드가 올바른 HTML을 반환하지 않습니다")
    else:
        print(f"  ✗ 프론트엔드 접근 실패: HTTP {response.status_code}")
        issues.append(f"프론트엔드가 {response.status_code} 오류를 반환합니다")
        
except Exception as e:
    print(f"  ✗ 프론트엔드 접근 실패: {str(e)[:50]}")
    issues.append(f"프론트엔드 접근 오류: {str(e)[:50]}")

# 7. 데이터 일관성 확인
print("\n[7/7] 데이터 일관성 확인")
print("-" * 80)

try:
    # 프로젝트 데이터 샘플 확인
    projects_table = dynamodb.Table('Projects')
    response = projects_table.scan(Limit=5)
    projects = response['Items']
    
    if projects:
        # period 필드 확인
        has_period = sum(1 for p in projects if 'period' in p)
        has_team_composition = sum(1 for p in projects if 'team_composition' in p)
        
        print(f"  ✓ 프로젝트 샘플: {len(projects)}개")
        print(f"    - period 필드: {has_period}/{len(projects)}개")
        print(f"    - team_composition 필드: {has_team_composition}/{len(projects)}개")
        
        if has_period == len(projects) and has_team_composition == len(projects):
            successes.append("프로젝트 데이터 구조 정상")
        else:
            warnings.append("일부 프로젝트 데이터 구조가 불완전합니다")
    
    # 직원 데이터 샘플 확인
    employees_table = dynamodb.Table('Employees')
    response = employees_table.scan(Limit=5)
    employees = response['Items']
    
    if employees:
        has_basic_info = sum(1 for e in employees if 'basic_info' in e)
        has_skills = sum(1 for e in employees if 'skills' in e)
        
        print(f"  ✓ 직원 샘플: {len(employees)}개")
        print(f"    - basic_info 필드: {has_basic_info}/{len(employees)}개")
        print(f"    - skills 필드: {has_skills}/{len(employees)}개")
        
        if has_basic_info == len(employees) and has_skills == len(employees):
            successes.append("직원 데이터 구조 정상")
        else:
            warnings.append("일부 직원 데이터 구조가 불완전합니다")
            
except Exception as e:
    print(f"  ✗ 데이터 일관성 확인 실패: {str(e)}")
    issues.append(f"데이터 일관성 확인 오류: {str(e)}")

# 최종 요약
print("\n" + "=" * 80)
print("점검 결과 요약")
print("=" * 80)

print(f"\n✓ 정상: {len(successes)}개")
print(f"⚠ 경고: {len(warnings)}개")
print(f"✗ 문제: {len(issues)}개")

if issues:
    print("\n🔴 발견된 문제:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")

if warnings:
    print("\n🟡 경고 사항:")
    for i, warning in enumerate(warnings, 1):
        print(f"  {i}. {warning}")

# 권장 조치
print("\n" + "=" * 80)
print("권장 조치 사항")
print("=" * 80)

if issues:
    print("\n🔧 즉시 조치 필요:")
    
    if any('테이블이 비어있습니다' in issue for issue in issues):
        print("  1. DynamoDB 테이블에 데이터 로드:")
        print("     python deployment/load_extended_data.py")
    
    if any('Lambda 함수가 존재하지 않습니다' in issue for issue in issues):
        print("  2. Lambda 함수 배포:")
        print("     python deployment/deploy_all_lambdas.py")
    
    if any('엔드포인트가 없습니다' in issue for issue in issues):
        print("  3. API Gateway 설정:")
        print("     python deployment/setup_api_gateway.py")
    
    if any('user_id가 없습니다' in issue for issue in issues):
        print("  4. Lambda 함수 재배포:")
        print("     python deployment/redeploy_projects_lambda.py")

if warnings:
    print("\n⚠️  확인 권장:")
    
    if any('데이터가 부족합니다' in warning for warning in warnings):
        print("  1. 데이터 재로드 고려")
    
    if any('프론트엔드' in warning for warning in warnings):
        print("  2. 프론트엔드 재배포:")
        print("     cd frontend && npm run build")
        print("     aws s3 sync build/ s3://hr-resource-optimization-frontend-hosting-prod --region us-east-2")

if not issues and not warnings:
    print("\n✅ 모든 시스템이 정상 작동 중입니다!")
    print("\n다음 단계:")
    print("  1. 프론트엔드 접속: http://hr-resource-optimization-frontend-hosting-prod.s3-website.us-east-2.amazonaws.com")
    print("  2. 프로젝트 관리 페이지에서 데이터 확인")
    print("  3. 인력 추천 기능 테스트")

print("\n" + "=" * 80)
print("점검 완료")
print("=" * 80)
