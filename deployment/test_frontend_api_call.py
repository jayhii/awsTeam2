import requests
import json

print("=" * 70)
print("프론트엔드 API 호출 시뮬레이션")
print("=" * 70)

# 프론트엔드가 사용하는 API URL
frontend_api_url = "https://xoc7x1m6p8.execute-api.us-east-2.amazonaws.com/prod/projects"
correct_api_url = "https://ifeniowvpb.execute-api.us-east-2.amazonaws.com/prod/projects"

print(f"\n[1단계] 프론트엔드 설정 확인...")
with open('frontend/src/config/api.ts', 'r', encoding='utf-8') as f:
    content = f.read()
    if 'xoc7x1m6p8' in content:
        print(f"  ❌ 프론트엔드가 잘못된 API URL 사용 중!")
        print(f"  현재: xoc7x1m6p8")
        print(f"  올바른: ifeniowvpb")
        using_wrong_url = True
    elif 'ifeniowvpb' in content:
        print(f"  ✓ 프론트엔드가 올바른 API URL 사용 중")
        using_wrong_url = False
    else:
        print(f"  ⚠️  API URL을 찾을 수 없음")
        using_wrong_url = False

print(f"\n[2단계] 프론트엔드가 호출하는 API 테스트...")
if using_wrong_url:
    print(f"  잘못된 URL 테스트: {frontend_api_url}")
    try:
        response = requests.get(frontend_api_url, timeout=5)
        print(f"  상태 코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            projects = data.get('projects', [])
            print(f"  ✓ 응답 성공: {len(projects)}개 프로젝트")
            if projects:
                sample = projects[0]
                print(f"  샘플 데이터:")
                print(f"    end_date: {sample.get('end_date', '없음')}")
                print(f"    team_members: {len(sample.get('team_members', []))}명")
        else:
            print(f"  ✗ 오류: {response.text[:200]}")
    except Exception as e:
        print(f"  ✗ 호출 실패: {str(e)}")

print(f"\n[3단계] 올바른 API URL 테스트...")
print(f"  올바른 URL: {correct_api_url}")
try:
    response = requests.get(correct_api_url, timeout=5)
    print(f"  상태 코드: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        projects = data.get('projects', [])
        print(f"  ✓ 응답 성공: {len(projects)}개 프로젝트")
        if projects:
            sample = projects[0]
            print(f"  샘플 데이터:")
            print(f"    project_name: {sample.get('project_name')}")
            print(f"    end_date: {sample.get('end_date', '없음')}")
            print(f"    team_size: {sample.get('team_size', 0)}")
            print(f"    team_members: {len(sample.get('team_members', []))}명")
            
            team_members = sample.get('team_members', [])
            if team_members:
                print(f"  팀원 샘플:")
                for member in team_members[:2]:
                    print(f"    - {member.get('name', 'Unknown')} ({member.get('role', 'Unknown')})")
    elif response.status_code == 403:
        print(f"  ✗ 403 Forbidden - API Gateway가 배포되지 않음")
    else:
        print(f"  ✗ 오류: {response.text[:200]}")
except Exception as e:
    print(f"  ✗ 호출 실패: {str(e)}")

print("\n" + "=" * 70)
print("결론")
print("=" * 70)

if using_wrong_url:
    print("""
❌ 문제: 프론트엔드가 잘못된 API URL을 사용하고 있습니다!

해결 방법:
  1. frontend/src/config/api.ts 파일 수정
     변경 전: xoc7x1m6p8
     변경 후: ifeniowvpb
  
  2. 프론트엔드 재빌드 및 재배포
     cd frontend
     npm run build
     aws s3 sync dist/ s3://hr-resource-optimization-frontend-hosting-prod/
  
  3. 브라우저 캐시 삭제 (Ctrl+Shift+Delete)
  4. 페이지 새로고침 (Ctrl+F5)
""")
else:
    print("""
✓ 프론트엔드 설정은 올바릅니다.

다른 가능한 원인:
  1. 브라우저 캐시 - Ctrl+F5로 강력 새로고침
  2. S3에 배포된 파일이 오래됨 - 재배포 필요
  3. API Gateway가 배포되지 않음 - AWS Console에서 배포
""")
