"""
API Gateway에 /employees 엔드포인트 생성
"""
import boto3
import json

apigateway = boto3.client('apigateway', region_name='us-east-2')
lambda_client = boto3.client('lambda', region_name='us-east-2')

API_ID = 'ifeniowvpb'
REGION = 'us-east-2'
ACCOUNT_ID = '412677576136'

print("=" * 80)
print("/employees API 엔드포인트 생성")
print("=" * 80)

# 1. 루트 리소스 ID 찾기
print("\n[1/5] 루트 리소스 찾기...")
resources = apigateway.get_resources(restApiId=API_ID)
root_id = None

for resource in resources['items']:
    if resource['path'] == '/':
        root_id = resource['id']
        break

if not root_id:
    print("  ✗ 루트 리소스를 찾을 수 없습니다")
    exit(1)

print(f"  ✓ 루트 리소스 ID: {root_id}")

# 2. /employees 리소스 확인 또는 생성
print("\n[2/5] /employees 리소스 확인...")

employees_resource = None
for resource in resources['items']:
    if resource['path'] == '/employees':
        employees_resource = resource
        print(f"  ✓ /employees 리소스 이미 존재: {resource['id']}")
        break

if not employees_resource:
    print("  /employees 리소스 생성 중...")
    try:
        employees_resource = apigateway.create_resource(
            restApiId=API_ID,
            parentId=root_id,
            pathPart='employees'
        )
        print(f"  ✓ /employees 리소스 생성 완료: {employees_resource['id']}")
    except Exception as e:
        print(f"  ✗ 리소스 생성 실패: {str(e)}")
        exit(1)

resource_id = employees_resource['id']

# 3. GET 메서드 생성
print("\n[3/5] GET 메서드 생성...")

try:
    # 기존 메서드 확인
    try:
        method = apigateway.get_method(
            restApiId=API_ID,
            resourceId=resource_id,
            httpMethod='GET'
        )
        print("  ✓ GET 메서드 이미 존재")
    except apigateway.exceptions.NotFoundException:
        # GET 메서드 생성
        apigateway.put_method(
            restApiId=API_ID,
            resourceId=resource_id,
            httpMethod='GET',
            authorizationType='NONE'
        )
        print("  ✓ GET 메서드 생성 완료")
    
    # Lambda 통합 설정
    lambda_arn = f"arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:EmployeesList"
    
    apigateway.put_integration(
        restApiId=API_ID,
        resourceId=resource_id,
        httpMethod='GET',
        type='AWS_PROXY',
        integrationHttpMethod='POST',
        uri=f"arn:aws:apigateway:{REGION}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
    )
    print("  ✓ Lambda 통합 설정 완료")
    
    # Lambda 권한 추가
    try:
        lambda_client.add_permission(
            FunctionName='EmployeesList',
            StatementId=f'apigateway-employees-{API_ID}',
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=f"arn:aws:execute-api:{REGION}:{ACCOUNT_ID}:{API_ID}/*/*/employees"
        )
        print("  ✓ Lambda 권한 추가 완료")
    except lambda_client.exceptions.ResourceConflictException:
        print("  ✓ Lambda 권한 이미 존재")
    
except Exception as e:
    print(f"  ✗ GET 메서드 설정 실패: {str(e)}")
    exit(1)

# 4. OPTIONS 메서드 생성 (CORS)
print("\n[4/5] OPTIONS 메서드 생성 (CORS)...")

try:
    try:
        apigateway.get_method(
            restApiId=API_ID,
            resourceId=resource_id,
            httpMethod='OPTIONS'
        )
        print("  ✓ OPTIONS 메서드 이미 존재")
    except apigateway.exceptions.NotFoundException:
        # OPTIONS 메서드 생성
        apigateway.put_method(
            restApiId=API_ID,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            authorizationType='NONE'
        )
        
        # MOCK 통합
        apigateway.put_integration(
            restApiId=API_ID,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            type='MOCK',
            requestTemplates={
                'application/json': '{"statusCode": 200}'
            }
        )
        
        # 응답 설정
        apigateway.put_method_response(
            restApiId=API_ID,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': False,
                'method.response.header.Access-Control-Allow-Methods': False,
                'method.response.header.Access-Control-Allow-Origin': False
            }
        )
        
        apigateway.put_integration_response(
            restApiId=API_ID,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': "'Content-Type,Authorization'",
                'method.response.header.Access-Control-Allow-Methods': "'GET,OPTIONS'",
                'method.response.header.Access-Control-Allow-Origin': "'*'"
            }
        )
        
        print("  ✓ OPTIONS 메서드 생성 완료")
        
except Exception as e:
    print(f"  ⚠ OPTIONS 메서드 설정 실패: {str(e)}")

# 5. API 배포
print("\n[5/5] API 배포...")

try:
    deployment = apigateway.create_deployment(
        restApiId=API_ID,
        stageName='prod',
        description='Add /employees endpoint'
    )
    print(f"  ✓ API 배포 완료: {deployment['id']}")
    
except Exception as e:
    print(f"  ✗ API 배포 실패: {str(e)}")
    exit(1)

# 테스트
print("\n" + "=" * 80)
print("엔드포인트 테스트")
print("=" * 80)

import requests
import time

time.sleep(2)  # 배포 완료 대기

url = f"https://{API_ID}.execute-api.{REGION}.amazonaws.com/prod/employees"
print(f"\nURL: {url}")

try:
    response = requests.get(url, timeout=10)
    print(f"상태 코드: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        count = len(data.get('employees', []))
        print(f"✓ 성공! {count}명의 직원 데이터 반환")
    else:
        print(f"✗ 오류: {response.text[:200]}")
        
except Exception as e:
    print(f"✗ 테스트 실패: {str(e)}")

print("\n" + "=" * 80)
print("완료!")
print("=" * 80)
