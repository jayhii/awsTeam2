import boto3
import json
import time

# AWS 클라이언트
apigateway = boto3.client('apigateway', region_name='us-east-2')
lambda_client = boto3.client('lambda', region_name='us-east-2')
sts = boto3.client('sts', region_name='us-east-2')

# AWS 계정 ID 가져오기
account_id = sts.get_caller_identity()['Account']
region = 'us-east-2'

print("=" * 70)
print("API Gateway에 /projects 엔드포인트 추가")
print("=" * 70)

# 1. API Gateway 찾기
print("\n[1단계] API Gateway 찾기...")
apis = apigateway.get_rest_apis()
hr_api = None
for api in apis['items']:
    if 'HR' in api['name'] or 'hr' in api['name'].lower():
        hr_api = api
        break

if not hr_api:
    print("  ✗ HR API Gateway를 찾을 수 없습니다")
    exit(1)

api_id = hr_api['id']
print(f"  ✓ API Gateway: {hr_api['name']} (ID: {api_id})")

# 2. 루트 리소스 찾기
print("\n[2단계] 루트 리소스 찾기...")
resources = apigateway.get_resources(restApiId=api_id)
root_resource = None
for resource in resources['items']:
    if resource['path'] == '/':
        root_resource = resource
        break

if not root_resource:
    print("  ✗ 루트 리소스를 찾을 수 없습니다")
    exit(1)

root_id = root_resource['id']
print(f"  ✓ 루트 리소스 ID: {root_id}")

# 3. /projects 리소스 생성
print("\n[3단계] /projects 리소스 생성...")
try:
    projects_resource = apigateway.create_resource(
        restApiId=api_id,
        parentId=root_id,
        pathPart='projects'
    )
    projects_resource_id = projects_resource['id']
    print(f"  ✓ /projects 리소스 생성 완료 (ID: {projects_resource_id})")
except apigateway.exceptions.ConflictException:
    print(f"  ℹ️  /projects 리소스가 이미 존재합니다")
    # 기존 리소스 찾기
    for resource in resources['items']:
        if resource['path'] == '/projects':
            projects_resource_id = resource['id']
            print(f"  ✓ 기존 리소스 사용 (ID: {projects_resource_id})")
            break

# 4. GET 메서드 생성
print("\n[4단계] GET 메서드 생성...")
try:
    apigateway.put_method(
        restApiId=api_id,
        resourceId=projects_resource_id,
        httpMethod='GET',
        authorizationType='NONE',
        apiKeyRequired=False
    )
    print(f"  ✓ GET 메서드 생성 완료")
except apigateway.exceptions.ConflictException:
    print(f"  ℹ️  GET 메서드가 이미 존재합니다")

# 5. Lambda 통합 설정
print("\n[5단계] Lambda 함수 통합...")
lambda_function_name = 'ProjectsList'
lambda_arn = f"arn:aws:lambda:{region}:{account_id}:function:{lambda_function_name}"
uri = f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"

try:
    apigateway.put_integration(
        restApiId=api_id,
        resourceId=projects_resource_id,
        httpMethod='GET',
        type='AWS_PROXY',
        integrationHttpMethod='POST',
        uri=uri
    )
    print(f"  ✓ Lambda 통합 완료: {lambda_function_name}")
except Exception as e:
    print(f"  ✗ Lambda 통합 실패: {str(e)}")

# 6. Lambda 권한 추가
print("\n[6단계] Lambda 실행 권한 추가...")
statement_id = f"apigateway-{api_id}-projects-get"
source_arn = f"arn:aws:execute-api:{region}:{account_id}:{api_id}/*/GET/projects"

try:
    lambda_client.add_permission(
        FunctionName=lambda_function_name,
        StatementId=statement_id,
        Action='lambda:InvokeFunction',
        Principal='apigateway.amazonaws.com',
        SourceArn=source_arn
    )
    print(f"  ✓ Lambda 권한 추가 완료")
except lambda_client.exceptions.ResourceConflictException:
    print(f"  ℹ️  Lambda 권한이 이미 존재합니다")
except Exception as e:
    print(f"  ⚠️  Lambda 권한 추가 실패: {str(e)}")

# 7. OPTIONS 메서드 추가 (CORS)
print("\n[7단계] CORS 설정 (OPTIONS 메서드)...")
try:
    # OPTIONS 메서드 생성
    apigateway.put_method(
        restApiId=api_id,
        resourceId=projects_resource_id,
        httpMethod='OPTIONS',
        authorizationType='NONE'
    )
    
    # MOCK 통합
    apigateway.put_integration(
        restApiId=api_id,
        resourceId=projects_resource_id,
        httpMethod='OPTIONS',
        type='MOCK',
        requestTemplates={
            'application/json': '{"statusCode": 200}'
        }
    )
    
    # 통합 응답
    apigateway.put_integration_response(
        restApiId=api_id,
        resourceId=projects_resource_id,
        httpMethod='OPTIONS',
        statusCode='200',
        responseParameters={
            'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
            'method.response.header.Access-Control-Allow-Methods': "'GET,OPTIONS'",
            'method.response.header.Access-Control-Allow-Origin': "'*'"
        }
    )
    
    # 메서드 응답
    apigateway.put_method_response(
        restApiId=api_id,
        resourceId=projects_resource_id,
        httpMethod='OPTIONS',
        statusCode='200',
        responseParameters={
            'method.response.header.Access-Control-Allow-Headers': True,
            'method.response.header.Access-Control-Allow-Methods': True,
            'method.response.header.Access-Control-Allow-Origin': True
        }
    )
    
    print(f"  ✓ CORS 설정 완료")
except Exception as e:
    print(f"  ⚠️  CORS 설정 실패: {str(e)}")

# 8. API 배포
print("\n[8단계] API 배포 중...")
try:
    deployment = apigateway.create_deployment(
        restApiId=api_id,
        stageName='prod',
        description='Added /projects endpoint'
    )
    print(f"  ✓ API 배포 완료 (배포 ID: {deployment['id']})")
    print(f"  배포 시간: 약 10-15초 소요...")
    time.sleep(15)
except Exception as e:
    print(f"  ✗ API 배포 실패: {str(e)}")

# 9. 최종 확인
print("\n" + "=" * 70)
print("완료!")
print("=" * 70)
print(f"\nAPI 엔드포인트:")
print(f"  https://{api_id}.execute-api.{region}.amazonaws.com/prod/projects")
print(f"\n테스트 명령:")
print(f"  curl https://{api_id}.execute-api.{region}.amazonaws.com/prod/projects")
print(f"\n프론트엔드 설정 업데이트:")
print(f"  VITE_API_BASE_URL=https://{api_id}.execute-api.{region}.amazonaws.com/prod")
