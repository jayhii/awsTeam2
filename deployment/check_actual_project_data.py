"""
DynamoDB에 실제 저장된 프로젝트 데이터 확인
"""
import boto3
import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

print("=" * 80)
print("DynamoDB 프로젝트 데이터 실제 구조 확인")
print("=" * 80)

table = dynamodb.Table('Projects')
response = table.scan(Limit=3)
projects = response['Items']

print(f"\n총 {len(projects)}개 프로젝트 샘플 조회\n")

for i, project in enumerate(projects, 1):
    print("=" * 80)
    print(f"프로젝트 {i}: {project.get('project_name', 'N/A')}")
    print("=" * 80)
    
    # 전체 구조 출력
    print(json.dumps(project, indent=2, ensure_ascii=False, cls=DecimalEncoder))
    
    # 주요 필드 확인
    print(f"\n주요 필드 체크:")
    print(f"  project_id: {project.get('project_id', 'N/A')}")
    print(f"  start_date: {project.get('start_date', 'N/A')}")
    print(f"  end_date: {project.get('end_date', 'N/A')}")
    
    # period 필드 확인
    if 'period' in project:
        print(f"  period: {project['period']}")
    
    # team_members 필드 확인
    if 'team_members' in project:
        print(f"  team_members (타입: {type(project['team_members']).__name__}):")
        if isinstance(project['team_members'], list):
            print(f"    길이: {len(project['team_members'])}")
            if project['team_members']:
                print(f"    첫 번째 항목: {project['team_members'][0]}")
    
    # team_composition 필드 확인
    if 'team_composition' in project:
        print(f"  team_composition (타입: {type(project['team_composition']).__name__}):")
        if isinstance(project['team_composition'], dict):
            print(f"    역할 수: {len(project['team_composition'])}")
            for role, members in list(project['team_composition'].items())[:2]:
                print(f"    {role}: {members}")
    
    print()

print("=" * 80)
print("분석 완료")
print("=" * 80)
