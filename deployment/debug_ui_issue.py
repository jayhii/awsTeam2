import boto3
import json

lambda_client = boto3.client('lambda', region_name='us-east-2')

print("=" * 70)
print("UI 문제 디버깅")
print("=" * 70)

# Lambda 함수 호출
response = lambda_client.invoke(
    FunctionName='ProjectsList',
    InvocationType='RequestResponse',
    Payload=json.dumps({'httpMethod': 'GET', 'path': '/projects'})
)

payload = json.loads(response['Payload'].read())
body = json.loads(payload.get('body', '{}'))
projects = body.get('projects', [])

print(f"\n총 프로젝트: {len(projects)}개")

if projects:
    sample = projects[0]
    
    print(f"\n샘플 프로젝트 (Lambda 응답):")
    print(f"  project_id: {sample.get('project_id')}")
    print(f"  project_name: {sample.get('project_name')}")
    print(f"  status: {sample.get('status')}")
    print(f"  start_date: {sample.get('start_date')}")
    print(f"  end_date: {sample.get('end_date')}")
    print(f"  team_size: {sample.get('team_size')}")
    print(f"  team_members: {len(sample.get('team_members', []))}명")
    
    # 프론트엔드가 기대하는 필드 확인
    print(f"\n프론트엔드 매핑 확인:")
    print(f"  ❌ 문제 1: end_date가 있는가? {sample.get('end_date', '없음')}")
    print(f"  ❌ 문제 2: team_members 배열이 있는가? {len(sample.get('team_members', []))}개")
    
    # 팀원 상세 정보
    team_members = sample.get('team_members', [])
    if team_members:
        print(f"\n  팀원 상세:")
        for i, member in enumerate(team_members[:3]):
            print(f"    {i+1}. {member.get('name', 'Unknown')} ({member.get('role', 'Unknown')})")
    else:
        print(f"  ⚠️  팀원 배열이 비어있음!")
    
    # 프론트엔드 코드가 사용하는 필드
    print(f"\n프론트엔드가 사용하는 필드:")
    print(f"  assignedMembers 계산: team_members 배열 길이 = {len(team_members)}")
    print(f"  requiredMembers 계산: team_size = {sample.get('team_size', 0)}")
    print(f"  endDate: end_date = {sample.get('end_date', '미정')}")

print("\n" + "=" * 70)
print("원인 분석")
print("=" * 70)

print("""
문제 1: 종료 기간이 '미정'으로 나오는 이유
  - Lambda 응답에 'end_date' 필드가 있는지 확인 필요
  - 프론트엔드가 'end_date'를 읽지 못하면 기본값 '미정' 사용

문제 2: 투입 인력이 0명으로 나오는 이유
  - 프론트엔드가 'team_members' 배열의 길이를 계산
  - 배열이 비어있거나 필드가 없으면 0명으로 표시
  - Lambda 응답에 team_members가 제대로 포함되어 있는지 확인 필요
""")
