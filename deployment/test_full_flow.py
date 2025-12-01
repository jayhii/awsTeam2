import boto3
import json
import requests

print("=" * 70)
print("전체 플로우 테스트")
print("=" * 70)

# 1. DynamoDB 데이터 확인
print("\n[1단계] DynamoDB 프로젝트 데이터 확인...")
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('Projects')

try:
    response = table.scan(Limit=1)
    if response['Items']:
        sample = response['Items'][0]
        print(f"  ✓ DynamoDB에 데이터 존재")
        print(f"  샘플 프로젝트: {sample.get('project_name')}")
        print(f"  팀원 수: {len(sample.get('team_members', []))}명")
    else:
        print(f"  ✗ DynamoDB에 데이터 없음")
except Exception as e:
    print(f"  ✗ DynamoDB 조회 실패: {str(e)}")

# 2. Lambda 함수 테스트
print("\n[2단계] Lambda 함수 테스트...")
lambda_client = boto3.client('lambda', region_name='us-east-2')

try:
    response = lambda_client.invoke(
        FunctionName='ProjectsList',
        InvocationType='RequestResponse',
        Payload=json.dumps({
            'httpMethod': 'GET',
            'path': '/projects'
        })
    )
    
    payload = json.loads(response['Payload'].read())
    if payload.get('statusCode') == 200:
        body = json.loads(payload.get('body', '{}'))
        projects = body.get('projects', [])
        print(f"  ✓ Lambda 함수 정상 작동")
        print(f"  프로젝트 수: {len(projects)}개")
        
        if projects:
            sample = projects[0]
            team_members = sample.get('team_members', [])
            print(f"  샘플 프로젝트: {sample.get('project_name')}")
            print(f"  팀원 수: {len(team_members)}명")
            if team_members:
                print(f"  첫 번째 팀원: {team_members[0].get('name')} ({team_members[0].get('role')})")
    else:
        print(f"  ✗ Lambda 함수 오류: {payload.get('body')}")
except Exception as e:
    print(f"  ✗ Lambda 테스트 실패: {str(e)}")

# 3. API Gateway 엔드포인트 테스트
print("\n[3단계] API Gateway 엔드포인트 테스트...")
api_url = "https://ifeniowvpb.execute-api.us-east-2.amazonaws.com/prod/projects"

try:
    response = requests.get(api_url, timeout=10)
    print(f"  상태 코드: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        projects = data.get('projects', [])
        print(f"  ✓ API Gateway 정상 작동")
        print(f"  프로젝트 수: {len(projects)}개")
        
        if projects:
            sample = projects[0]
            team_members = sample.get('team_members', [])
            print(f"  샘플 프로젝트: {sample.get('project_name')}")
            print(f"  팀원 수: {len(team_members)}명")
    elif response.status_code == 403:
        print(f"  ✗ API Gateway 배포 필요 (403 Forbidden)")
        print(f"  AWS Console에서 수동 배포 필요")
    else:
        print(f"  ✗ API 오류: {response.text[:200]}")
except requests.exceptions.Timeout:
    print(f"  ✗ 타임아웃 - API Gateway가 배포되지 않았을 수 있습니다")
except Exception as e:
    print(f"  ✗ API 테스트 실패: {str(e)}")

# 4. 프론트엔드 설정 확인
print("\n[4단계] 프론트엔드 설정 확인...")
try:
    with open('frontend/src/config/api.ts', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'ifeniowvpb' in content:
            print(f"  ✓ 프론트엔드 API URL 올바름")
        elif 'xoc7x1m6p8' in content:
            print(f"  ✗ 프론트엔드 API URL 업데이트 필요")
            print(f"  현재: xoc7x1m6p8")
            print(f"  변경: ifeniowvpb")
        else:
            print(f"  ℹ️  API URL 확인 필요")
except Exception as e:
    print(f"  ⚠️  파일 확인 실패: {str(e)}")

# 5. 요약
print("\n" + "=" * 70)
print("테스트 요약")
print("=" * 70)
print("\n다음 단계:")
print("  1. API Gateway 배포 (AWS Console)")
print("     - API Gateway → HR-Resource-Optimization-API")
print("     - Actions → Deploy API → Stage: prod")
print("\n  2. 프론트엔드 재시작")
print("     cd frontend")
print("     npm run dev")
print("\n  3. 브라우저에서 확인")
print("     - 프로젝트 관리 탭")
print("     - 투입 인력 수 확인")
