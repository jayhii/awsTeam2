"""
프론트엔드 API 연결 문제 진단
"""
import requests
import json

API_BASE_URL = "https://ifeniowvpb.execute-api.us-east-2.amazonaws.com/prod"
FRONTEND_URL = "http://hr-resource-optimization-frontend-hosting-prod.s3-website.us-east-2.amazonaws.com"

print("=" * 80)
print("프론트엔드 API 연결 문제 진단")
print("=" * 80)

# 1. 프론트엔드 접근 확인
print("\n[1/5] 프론트엔드 접근 확인")
print("-" * 80)

try:
    response = requests.get(FRONTEND_URL, timeout=10)
    print(f"✓ 프론트엔드 접근 가능: HTTP {response.status_code}")
    
    # API URL 확인
    content = response.text
    if 'ifeniowvpb.execute-api' in content:
        print(f"✓ API URL이 프론트엔드에 포함되어 있음")
    else:
        print(f"✗ API URL이 프론트엔드에 없음 - 하드코딩된 URL 확인 필요")
        
except Exception as e:
    print(f"✗ 프론트엔드 접근 실패: {str(e)}")

# 2. API 엔드포인트 직접 테스트
print("\n[2/5] API 엔드포인트 직접 테스트")
print("-" * 80)

endpoints = ['/projects', '/employees']

for endpoint in endpoints:
    url = f"{API_BASE_URL}{endpoint}"
    print(f"\n테스트: {endpoint}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"  상태 코드: {response.status_code}")
        
        # CORS 헤더 확인
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        print(f"  CORS 헤더:")
        for key, value in cors_headers.items():
            if value:
                print(f"    ✓ {key}: {value}")
            else:
                print(f"    ✗ {key}: 없음")
        
        if response.status_code == 200:
            data = response.json()
            if endpoint == '/projects':
                count = len(data.get('projects', []))
                print(f"  ✓ 데이터: {count}개 프로젝트")
            elif endpoint == '/employees':
                count = len(data.get('employees', []))
                print(f"  ✓ 데이터: {count}명 직원")
        else:
            print(f"  ✗ 오류: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print(f"  ✗ 연결 오류 - API Gateway에 연결할 수 없음")
    except requests.exceptions.Timeout:
        print(f"  ✗ 타임아웃")
    except Exception as e:
        print(f"  ✗ 오류: {str(e)}")

# 3. OPTIONS 요청 테스트 (CORS preflight)
print("\n[3/5] CORS Preflight 요청 테스트")
print("-" * 80)

for endpoint in endpoints:
    url = f"{API_BASE_URL}{endpoint}"
    print(f"\nOPTIONS: {endpoint}")
    
    try:
        response = requests.options(url, timeout=10)
        print(f"  상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  ✓ OPTIONS 메서드 정상")
            
            # CORS 헤더 확인
            allow_origin = response.headers.get('Access-Control-Allow-Origin')
            allow_methods = response.headers.get('Access-Control-Allow-Methods')
            
            if allow_origin == '*':
                print(f"  ✓ CORS 허용: 모든 도메인")
            elif allow_origin:
                print(f"  ⚠ CORS 허용: {allow_origin}")
            else:
                print(f"  ✗ CORS 헤더 없음")
                
            if allow_methods:
                print(f"  ✓ 허용 메서드: {allow_methods}")
        else:
            print(f"  ✗ OPTIONS 요청 실패")
            
    except Exception as e:
        print(f"  ✗ 오류: {str(e)}")

# 4. 프론트엔드에서 사용하는 API URL 확인
print("\n[4/5] 프론트엔드 설정 확인")
print("-" * 80)

try:
    # index.html 다운로드
    response = requests.get(FRONTEND_URL, timeout=10)
    content = response.text
    
    # JavaScript 파일 찾기
    import re
    js_files = re.findall(r'src="(/assets/[^"]+\.js)"', content)
    
    if js_files:
        print(f"✓ JavaScript 파일 발견: {len(js_files)}개")
        
        # 첫 번째 JS 파일 확인
        js_url = f"{FRONTEND_URL}{js_files[0]}"
        print(f"\nJS 파일 확인: {js_files[0]}")
        
        try:
            js_response = requests.get(js_url, timeout=10)
            js_content = js_response.text
            
            # API URL 찾기
            api_urls = re.findall(r'https://[^"\']+\.execute-api\.[^"\']+', js_content)
            
            if api_urls:
                print(f"✓ API URL 발견:")
                for url in set(api_urls):
                    print(f"  - {url}")
                    
                # 올바른 URL인지 확인
                if API_BASE_URL in api_urls[0]:
                    print(f"✓ 올바른 API URL 사용 중")
                else:
                    print(f"✗ 잘못된 API URL 사용 중")
                    print(f"  예상: {API_BASE_URL}")
                    print(f"  실제: {api_urls[0]}")
            else:
                print(f"⚠ API URL을 찾을 수 없음 (빌드 시 환경 변수 확인 필요)")
                
        except Exception as e:
            print(f"✗ JS 파일 다운로드 실패: {str(e)}")
    else:
        print(f"⚠ JavaScript 파일을 찾을 수 없음")
        
except Exception as e:
    print(f"✗ 프론트엔드 설정 확인 실패: {str(e)}")

# 5. 문제 진단 및 해결 방법
print("\n[5/5] 문제 진단 및 해결 방법")
print("-" * 80)

print("\n가능한 원인:")
print("1. CORS 설정 문제")
print("   - API Gateway에서 CORS 헤더가 제대로 반환되지 않음")
print("   - 해결: Lambda 함수에서 CORS 헤더 추가")
print()
print("2. API URL 불일치")
print("   - 프론트엔드가 잘못된 API URL을 사용")
print("   - 해결: 프론트엔드 재빌드 및 배포")
print()
print("3. API Gateway 배포 문제")
print("   - 최신 변경사항이 prod 스테이지에 배포되지 않음")
print("   - 해결: API Gateway 재배포")
print()
print("4. 네트워크 문제")
print("   - 브라우저에서 API에 접근할 수 없음")
print("   - 해결: 브라우저 개발자 도구에서 Network 탭 확인")

print("\n" + "=" * 80)
print("권장 조치:")
print("=" * 80)
print("\n1. 브라우저 개발자 도구 확인 (F12)")
print("   - Console 탭: 오류 메시지 확인")
print("   - Network 탭: 실패한 요청 확인")
print()
print("2. API Gateway 재배포")
print("   python deployment/redeploy_api_gateway.py")
print()
print("3. 프론트엔드 재배포 (Node.js 설치 후)")
print("   cd frontend && npm run build")
print("   aws s3 sync build/ s3://hr-resource-optimization-frontend-hosting-prod --region us-east-2")
print()
print("4. 브라우저 캐시 강제 새로고침")
print("   Ctrl + Shift + R")

print("\n" + "=" * 80)
print("진단 완료")
print("=" * 80)
