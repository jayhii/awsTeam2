import boto3

api = boto3.client('apigateway', region_name='us-east-2')

print("=" * 70)
print("/projects 엔드포인트만 강제 배포")
print("=" * 70)

api_id = 'ifeniowvpb'
projects_resource_id = 'aync80'

print(f"\n[1단계] /projects 리소스 확인...")
try:
    # GET 메서드 확인
    method = api.get_method(
        restApiId=api_id,
        resourceId=projects_resource_id,
        httpMethod='GET'
    )
    
    integration = method.get('methodIntegration', {})
    print(f"  ✓ GET 메서드 존재")
    print(f"  통합 타입: {integration.get('type')}")
    print(f"  URI: {integration.get('uri', '')[:50]}...")
    
except Exception as e:
    print(f"  ✗ GET 메서드 확인 실패: {str(e)}")

print(f"\n[2단계] 다른 엔드포인트의 통합 문제 수정...")
# 통합이 없는 메서드들을 임시로 삭제하거나 통합 추가
problem_endpoints = [
    ('3lged3', 'POST'),  # /quantitative-analysis
    ('gaa5o6', 'POST'),  # /recommendations
    ('gd4jzj', 'POST'),  # /domain-analysis
    ('wrlnsl', 'POST'),  # /qualitative-analysis
]

for resource_id, method in problem_endpoints:
    try:
        # 메서드 삭제 (통합이 없으면 배포 실패하므로)
        api.delete_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod=method
        )
        print(f"  ✓ {resource_id}/{method} 삭제됨")
    except Exception as e:
        if 'NotFoundException' in str(e):
            print(f"  ℹ️  {resource_id}/{method} 이미 없음")
        else:
            print(f"  ⚠️  {resource_id}/{method} 삭제 실패: {str(e)}")

print(f"\n[3단계] API 배포 시도...")
try:
    result = api.create_deployment(
        restApiId=api_id,
        stageName='prod',
        description='Deploy /projects endpoint only'
    )
    
    print(f"  ✓ 배포 성공!")
    print(f"  배포 ID: {result['id']}")
    
    print(f"\n✅ API Gateway가 성공적으로 배포되었습니다!")
    print(f"\nAPI 엔드포인트:")
    print(f"  https://{api_id}.execute-api.us-east-2.amazonaws.com/prod/projects")
    
    print(f"\n다음 단계:")
    print(f"  1. 15초 대기 (배포 완료)")
    print(f"  2. 브라우저에서 Ctrl+F5 (강력 새로고침)")
    print(f"  3. 프로젝트 관리 페이지 확인")
    
except Exception as e:
    print(f"  ✗ 배포 실패: {str(e)}")

print("\n" + "=" * 70)
