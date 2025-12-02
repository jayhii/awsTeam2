"""
프론트엔드 API 연결 테스트
실제 API Gateway 엔드포인트 테스트
"""
import requests
import json

API_BASE_URL = "https://ifeniowvpb.execute-api.us-east-2.amazonaws.com/prod"

print("=" * 80)
print("프론트엔드 API 연결 테스트")
print("=" * 80)

# 1. API Gateway 엔드포인트 확인
print(f"\n[1] API Base URL: {API_BASE_URL}")

# 2. /projects 엔드포인트 테스트
print("\n[2] /projects 엔드포인트 테스트")
url = f"{API_BASE_URL}/projects"
print(f"URL: {url}")

try:
    response = requests.get(url, timeout=10)
    print(f"상태 코드: {response.status_code}")
    print(f"응답 헤더:")
    for key, value in response.headers.items():
        if key.lower() in ['content-type', 'access-control-allow-origin', 'content-length']:
            print(f"  {key}: {value}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ 성공!")
        print(f"프로젝트 수: {data.get('count', 0)}개")
        
        if 'projects' in data and len(data['projects']) > 0:
            first_project = data['projects'][0]
            print(f"\n첫 번째 프로젝트 샘플:")
            print(json.dumps(first_project, indent=2, ensure_ascii=False)[:1000])
            
            # 필드 체크
            print(f"\n필드 존재 여부:")
            required_fields = ['project_id', 'project_name', 'start_date', 'end_date', 'team_members', 'team_size']
            for field in required_fields:
                exists = field in first_project
                value = first_project.get(field, 'N/A')
                status = "✅" if exists else "❌"
                
                if isinstance(value, list):
                    preview = f"[{len(value)}개]"
                elif isinstance(value, str) and len(value) > 30:
                    preview = value[:30] + "..."
                else:
                    preview = value
                
                print(f"  {status} {field:20s}: {preview}")
        else:
            print("\n⚠️  프로젝트 데이터가 비어있습니다!")
    
    elif response.status_code == 403:
        print(f"\n❌ 403 Forbidden - API Gateway 권한 문제")
        print(f"응답: {response.text[:500]}")
    
    elif response.status_code == 404:
        print(f"\n❌ 404 Not Found - 엔드포인트가 존재하지 않음")
        print(f"응답: {response.text[:500]}")
    
    else:
        print(f"\n❌ 오류 발생")
        print(f"응답: {response.text[:500]}")

except requests.exceptions.Timeout:
    print("\n❌ 타임아웃 - API 응답 없음")
except requests.exceptions.ConnectionError:
    print("\n❌ 연결 오류 - API Gateway에 연결할 수 없음")
except Exception as e:
    print(f"\n❌ 예외 발생: {str(e)}")

# 3. API Gateway 설정 확인
print("\n" + "=" * 80)
print("[3] API Gateway 설정 확인")
print("=" * 80)

import boto3

try:
    apigateway = boto3.client('apigateway', region_name='us-east-2')
    
    # API ID 추출
    api_id = "ifeniowvpb"
    
    # API 정보 조회
    api_info = apigateway.get_rest_api(restApiId=api_id)
    print(f"\nAPI 이름: {api_info['name']}")
    print(f"API ID: {api_info['id']}")
    print(f"생성일: {api_info['createdDate']}")
    
    # 리소스 목록 조회
    resources = apigateway.get_resources(restApiId=api_id)
    print(f"\n리소스 목록:")
    for resource in resources['items']:
        path = resource.get('path', '/')
        methods = resource.get('resourceMethods', {})
        if methods:
            print(f"  {path:30s} - {', '.join(methods.keys())}")
    
    # /projects 리소스 확인
    projects_resource = None
    for resource in resources['items']:
        if resource.get('path') == '/projects':
            projects_resource = resource
            break
    
    if projects_resource:
        print(f"\n✅ /projects 리소스 존재")
        print(f"리소스 ID: {projects_resource['id']}")
        methods = projects_resource.get('resourceMethods', {})
        print(f"메서드: {', '.join(methods.keys())}")
        
        # GET 메서드 통합 확인
        if 'GET' in methods:
            integration = apigateway.get_integration(
                restApiId=api_id,
                resourceId=projects_resource['id'],
                httpMethod='GET'
            )
            print(f"\nGET 메서드 통합:")
            print(f"  타입: {integration.get('type')}")
            print(f"  URI: {integration.get('uri', 'N/A')[:100]}")
    else:
        print(f"\n❌ /projects 리소스가 존재하지 않음!")
    
    # 배포 스테이지 확인
    stages = apigateway.get_stages(restApiId=api_id)
    print(f"\n배포 스테이지:")
    for stage in stages['item']:
        print(f"  - {stage['stageName']} (배포일: {stage.get('lastUpdatedDate', 'N/A')})")

except Exception as e:
    print(f"\n❌ API Gateway 조회 실패: {str(e)}")

print("\n" + "=" * 80)
print("테스트 완료")
print("=" * 80)
