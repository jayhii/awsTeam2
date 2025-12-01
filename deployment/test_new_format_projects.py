import boto3
import json

lambda_client = boto3.client('lambda', region_name='us-east-2')

print("새로운 형식 프로젝트 테스트")
print("=" * 70)

response = lambda_client.invoke(
    FunctionName='ProjectsList',
    InvocationType='RequestResponse',
    Payload=json.dumps({'httpMethod': 'GET', 'path': '/projects'})
)

payload = json.loads(response['Payload'].read())
body = json.loads(payload.get('body', '{}'))
projects = body.get('projects', [])

# 새로운 형식 프로젝트 찾기 (PRJ로 시작)
new_format_projects = [p for p in projects if p['project_id'].startswith('PRJ')]

print(f"\n새로운 형식 프로젝트: {len(new_format_projects)}개")

if new_format_projects:
    sample = new_format_projects[0]
    print(f"\n샘플 프로젝트:")
    print(f"  ID: {sample['project_id']}")
    print(f"  이름: {sample['project_name']}")
    print(f"  산업: {sample['client_industry']}")
    print(f"  예산 규모: {sample.get('budget_scale', 'N/A')}")
    print(f"  기간: {sample.get('start_date')} ~ {sample.get('end_date')}")
    print(f"  팀 규모: {sample.get('team_size', 0)}명")
    
    team_members = sample.get('team_members', [])
    if team_members:
        print(f"  팀원 ({len(team_members)}명):")
        for member in team_members[:5]:
            print(f"    - {member.get('user_id')} ({member.get('role')})")
    else:
        print(f"  ⚠️  팀원 정보 없음")
    
    tech_stack = sample.get('tech_stack', {})
    if tech_stack:
        print(f"  기술 스택:")
        for category, techs in tech_stack.items():
            if techs:
                print(f"    {category}: {', '.join(techs[:3])}...")
