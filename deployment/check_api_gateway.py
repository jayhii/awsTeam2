import boto3
import json

# AWS 클라이언트
apigateway = boto3.client('apigateway', region_name='us-east-2')

print("=" * 70)
print("API Gateway 설정 확인")
print("=" * 70)

# 1. API Gateway 목록 조회
print("\n[1단계] API Gateway 목록 조회 중...")
try:
    apis = apigateway.get_rest_apis()
    
    hr_api = None
    for api in apis['items']:
        if 'HR' in api['name'] or 'hr' in api['name'].lower():
            hr_api = api
            break
    
    if not hr_api:
        print("  ✗ HR 관련 API Gateway를 찾을 수 없습니다")
        print("\n  사용 가능한 API:")
        for api in apis['items']:
            print(f"    - {api['name']} (ID: {api['id']})")
        exit(1)
    
    api_id = hr_api['id']
    api_name = hr_api['name']
    
    print(f"  ✓ API Gateway 발견: {api_name}")
    print(f"  API ID: {api_id}")
    
except Exception as e:
    print(f"  ✗ API Gateway 조회 실패: {str(e)}")
    exit(1)

# 2. 리소스 목록 조회
print("\n[2단계] API 리소스 확인 중...")
try:
    resources = apigateway.get_resources(restApiId=api_id)
    
    print(f"  총 {len(resources['items'])}개의 리소스 발견")
    
    # /projects 리소스 찾기
    projects_resource = None
    for resource in resources['items']:
        path = resource.get('path', '')
        if path == '/projects':
            projects_resource = resource
            break
    
    if projects_resource:
        print(f"  ✓ /projects 리소스 존재")
        print(f"    리소스 ID: {projects_resource['id']}")
        
        # 메서드 확인
        methods = projects_resource.get('resourceMethods', {})
        print(f"    지원 메서드: {', '.join(methods.keys())}")
        
        # GET 메서드 상세 확인
        if 'GET' in methods:
            print(f"\n  [GET /projects 메서드 상세]")
            method_response = apigateway.get_method(
                restApiId=api_id,
                resourceId=projects_resource['id'],
                httpMethod='GET'
            )
            
            # 통합 정보
            integration = method_response.get('methodIntegration', {})
            integration_type = integration.get('type', 'Unknown')
            uri = integration.get('uri', '')
            
            print(f"    통합 타입: {integration_type}")
            
            if 'lambda' in uri.lower():
                # Lambda 함수 이름 추출
                import re
                match = re.search(r'function:([^/]+)', uri)
                if match:
                    function_name = match.group(1)
                    print(f"    연결된 Lambda: {function_name}")
                else:
                    print(f"    Lambda URI: {uri}")
            else:
                print(f"    URI: {uri}")
        
    else:
        print(f"  ✗ /projects 리소스가 없습니다")
        print(f"\n  사용 가능한 리소스:")
        for resource in resources['items']:
            path = resource.get('path', '')
            methods = resource.get('resourceMethods', {})
            if methods:
                print(f"    {path} - {', '.join(methods.keys())}")
    
except Exception as e:
    print(f"  ✗ 리소스 조회 실패: {str(e)}")
    import traceback
    traceback.print_exc()

# 3. 배포 스테이지 확인
print("\n[3단계] 배포 스테이지 확인 중...")
try:
    stages = apigateway.get_stages(restApiId=api_id)
    
    print(f"  총 {len(stages['item'])}개의 스테이지 발견")
    
    for stage in stages['item']:
        stage_name = stage['stageName']
        deployment_id = stage.get('deploymentId', 'N/A')
        last_updated = stage.get('lastUpdatedDate', 'N/A')
        
        print(f"\n  스테이지: {stage_name}")
        print(f"    배포 ID: {deployment_id}")
        print(f"    최종 업데이트: {last_updated}")
        print(f"    URL: https://{api_id}.execute-api.us-east-2.amazonaws.com/{stage_name}")
    
except Exception as e:
    print(f"  ✗ 스테이지 조회 실패: {str(e)}")

# 4. 최종 엔드포인트 URL
print("\n" + "=" * 70)
print("최종 확인")
print("=" * 70)
print(f"\nAPI Gateway ID: {api_id}")
print(f"프론트엔드 설정 URL: https://xoc7x1m6p8.execute-api.us-east-2.amazonaws.com/prod")
print(f"실제 API URL: https://{api_id}.execute-api.us-east-2.amazonaws.com/prod")

if api_id != 'xoc7x1m6p8':
    print(f"\n⚠️  API ID가 다릅니다!")
    print(f"프론트엔드 설정을 다음으로 변경하세요:")
    print(f"  VITE_API_BASE_URL=https://{api_id}.execute-api.us-east-2.amazonaws.com/prod")
else:
    print(f"\n✓ API ID가 일치합니다")

print("\n다음 단계:")
print("  1. 브라우저에서 직접 API 호출 테스트")
print(f"     curl https://{api_id}.execute-api.us-east-2.amazonaws.com/prod/projects")
print("  2. 프론트엔드 .env 파일 확인")
print("  3. 브라우저 개발자 도구에서 네트워크 탭 확인")
