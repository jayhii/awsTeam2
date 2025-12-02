import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

print("=" * 70)
print("팀원 매핑 검증")
print("=" * 70)

# 1. 프로젝트 데이터 확인
print("\n[1단계] 프로젝트 팀원 ID 확인...")
projects_table = dynamodb.Table('Projects')
response = projects_table.scan(Limit=1)

if response['Items']:
    sample_project = response['Items'][0]
    print(f"  샘플 프로젝트: {sample_project.get('project_name')}")
    
    team_comp = sample_project.get('team_composition', {})
    all_user_ids = []
    
    for role, members in team_comp.items():
        if isinstance(members, list):
            all_user_ids.extend(members)
            print(f"  {role}: {members}")
    
    print(f"\n  총 팀원 ID: {len(all_user_ids)}개")
    print(f"  샘플 ID: {all_user_ids[:3]}")
else:
    print("  ✗ 프로젝트 데이터 없음")
    exit(1)

# 2. 직원 데이터 확인
print("\n[2단계] 직원 데이터 확인...")
employees_table = dynamodb.Table('Employees')

found_count = 0
not_found = []

for user_id in all_user_ids[:5]:  # 처음 5개만 테스트
    try:
        response = employees_table.get_item(Key={'user_id': user_id})
        if 'Item' in response:
            employee = response['Item']
            name = employee.get('basic_info', {}).get('name', 'Unknown')
            role = employee.get('basic_info', {}).get('role', 'Unknown')
            print(f"  ✓ {user_id}: {name} ({role})")
            found_count += 1
        else:
            print(f"  ✗ {user_id}: 직원 데이터 없음")
            not_found.append(user_id)
    except Exception as e:
        print(f"  ✗ {user_id}: 조회 실패 - {str(e)}")
        not_found.append(user_id)

print(f"\n  매칭 결과: {found_count}/{len(all_user_ids[:5])}개 성공")

if not_found:
    print(f"  ⚠️  매칭 실패: {not_found}")
else:
    print(f"  ✓ 모든 팀원 ID가 직원 데이터와 매칭됨")

# 3. Lambda 함수가 직원 이름을 조회하는지 확인
print("\n[3단계] Lambda 함수 응답 확인...")
lambda_client = boto3.client('lambda', region_name='us-east-2')

try:
    response = lambda_client.invoke(
        FunctionName='ProjectsList',
        InvocationType='RequestResponse',
        Payload=json.dumps({'httpMethod': 'GET', 'path': '/projects'})
    )
    
    payload = json.loads(response['Payload'].read())
    body = json.loads(payload.get('body', '{}'))
    projects = body.get('projects', [])
    
    if projects:
        sample = projects[0]
        team_members = sample.get('team_members', [])
        
        print(f"  프로젝트: {sample.get('project_name')}")
        print(f"  팀원 수: {len(team_members)}명")
        
        if team_members:
            first_member = team_members[0]
            print(f"\n  첫 번째 팀원 데이터:")
            print(f"    user_id: {first_member.get('user_id')}")
            print(f"    name: {first_member.get('name', '❌ 없음')}")
            print(f"    role: {first_member.get('role')}")
            
            if 'name' in first_member and first_member['name']:
                print(f"\n  ✓ Lambda 함수가 직원 이름을 조회하고 있음")
            else:
                print(f"\n  ✗ Lambda 함수가 직원 이름을 조회하지 않음")
                print(f"  → Lambda 함수 수정 필요")
        else:
            print(f"  ⚠️  팀원 데이터 없음")
    
except Exception as e:
    print(f"  ✗ Lambda 테스트 실패: {str(e)}")

print("\n" + "=" * 70)
