import boto3

api = boto3.client('apigateway', region_name='us-east-2')
api_id = 'ifeniowvpb'

print("=" * 70)
print("모든 리소스 및 메서드 확인")
print("=" * 70)

# 모든 리소스 조회
resources = api.get_resources(restApiId=api_id)

for resource in resources['items']:
    path = resource.get('path', '')
    resource_id = resource['id']
    methods = resource.get('resourceMethods', {})
    
    if not methods:
        continue
    
    print(f"\n리소스: {path} (ID: {resource_id})")
    
    for method in methods.keys():
        print(f"  메서드: {method}")
        
        try:
            method_detail = api.get_method(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod=method
            )
            
            integration = method_detail.get('methodIntegration')
            if integration:
                print(f"    ✓ 통합 존재: {integration.get('type', 'Unknown')}")
            else:
                print(f"    ✗ 통합 없음 - 수정 필요!")
                
        except Exception as e:
            print(f"    ✗ 오류: {str(e)}")

print("\n" + "=" * 70)
print("배포 시도...")
print("=" * 70)

try:
    result = api.create_deployment(
        restApiId=api_id,
        stageName='prod',
        description='Deploy all endpoints'
    )
    print(f"✓ 배포 성공! (ID: {result['id']})")
except Exception as e:
    print(f"✗ 배포 실패: {str(e)}")
