import boto3

api = boto3.client('apigateway', region_name='us-east-2')

print("OPTIONS 통합 추가 중...")
try:
    api.put_integration(
        restApiId='ifeniowvpb',
        resourceId='aync80',
        httpMethod='OPTIONS',
        type='MOCK',
        requestTemplates={'application/json': '{"statusCode": 200}'}
    )
    print("✓ OPTIONS 통합 추가 완료")
except Exception as e:
    print(f"ℹ️  {str(e)}")

print("\nAPI 배포 중...")
try:
    result = api.create_deployment(
        restApiId='ifeniowvpb',
        stageName='prod',
        description='Deploy /projects endpoint'
    )
    print(f"✓ 배포 완료! (ID: {result['id']})")
    print("\nAPI 엔드포인트:")
    print("  https://ifeniowvpb.execute-api.us-east-2.amazonaws.com/prod/projects")
except Exception as e:
    print(f"✗ 배포 실패: {str(e)}")
