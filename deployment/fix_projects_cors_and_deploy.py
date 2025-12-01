import boto3
import time

# AWS 클라이언트
apigateway = boto3.client('apigateway', region_name='us-east-2')

print("=" * 70)
print("CORS 수정 및 API 배포")
print("=" * 70)

api_id = 'ifeniowvpb'
projects_resource_id = 'aync80'

# 1. GET 메서드 응답 추가
print("\n[1단계] GET 메서드 응답 설정...")
try:
    apigateway.put_method_response(
        restApiId=api_id,
        resourceId=projects_resource_id,
        httpMethod='GET',
        statusCode='200',
        responseParameters={
            'method.response.header.Access-Control-Allow-Origin': True
        }
    )
    print(f"  ✓ GET 메서드 응답 설정 완료")
except Exception as e:
    print(f"  ℹ️  {str(e)}")

# 2. GET 통합 응답 추가
print("\n[2단계] GET 통합 응답 설정...")
try:
    apigateway.put_integration_response(
        restApiId=api_id,
        resourceId=projects_resource_id,
        httpMethod='GET',
        statusCode='200',
        responseParameters={
            'method.response.header.Access-Control-Allow-Origin': "'*'"
        }
    )
    print(f"  ✓ GET 통합 응답 설정 완료")
except Exception as e:
    print(f"  ℹ️  {str(e)}")

# 3. OPTIONS 메서드 응답 추가 (CORS preflight)
print("\n[3단계] OPTIONS 메서드 응답 설정...")
try:
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
    print(f"  ✓ OPTIONS 메서드 응답 설정 완료")
except Exception as e:
    print(f"  ℹ️  {str(e)}")

# 4. OPTIONS 통합 응답 추가
print("\n[4단계] OPTIONS 통합 응답 설정...")
try:
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
    print(f"  ✓ OPTIONS 통합 응답 설정 완료")
except Exception as e:
    print(f"  ℹ️  {str(e)}")

# 5. API 배포
print("\n[5단계] API 배포 중...")
try:
    deployment = apigateway.create_deployment(
        restApiId=api_id,
        stageName='prod',
        description='Fixed CORS and deployed /projects endpoint'
    )
    print(f"  ✓ API 배포 완료 (배포 ID: {deployment['id']})")
    print(f"  배포 시간: 약 10-15초 소요...")
    time.sleep(15)
    print(f"  ✓ 배포 완료!")
except Exception as e:
    print(f"  ✗ API 배포 실패: {str(e)}")

# 6. 최종 확인
print("\n" + "=" * 70)
print("완료!")
print("=" * 70)
print(f"\nAPI 엔드포인트:")
print(f"  https://{api_id}.execute-api.us-east-2.amazonaws.com/prod/projects")
print(f"\n테스트 명령:")
print(f"  curl https://{api_id}.execute-api.us-east-2.amazonaws.com/prod/projects")
print(f"\n프론트엔드 .env 파일 업데이트:")
print(f"  VITE_API_BASE_URL=https://{api_id}.execute-api.us-east-2.amazonaws.com/prod")
print(f"\n또는 frontend/src/config/api.ts 파일에서:")
print(f"  export const API_BASE_URL = 'https://{api_id}.execute-api.us-east-2.amazonaws.com/prod';")
