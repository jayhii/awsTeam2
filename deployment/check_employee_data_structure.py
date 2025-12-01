"""
DynamoDB에 저장된 직원 데이터 구조 확인
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
table = dynamodb.Table('Employees')

# 테스트할 직원 ID
test_ids = ['U_003', 'U_004', 'U_005']

print("=" * 80)
print("DynamoDB 직원 데이터 구조 확인")
print("=" * 80)

for user_id in test_ids:
    print(f"\n[{user_id}] 데이터 조회 중...")
    
    try:
        response = table.get_item(Key={'user_id': user_id})
        
        if 'Item' in response:
            item = response['Item']
            print(f"\n✓ 데이터 발견")
            print(f"\n전체 키 목록:")
            for key in item.keys():
                print(f"  - {key}")
            
            print(f"\n주요 필드 값:")
            print(f"  - name: {item.get('name', 'N/A')}")
            print(f"  - basic_info: {item.get('basic_info', 'N/A')}")
            print(f"  - experienceYears: {item.get('experienceYears', 'N/A')}")
            print(f"  - experience_years: {item.get('experience_years', 'N/A')}")
            
            # skills 필드 확인
            skills = item.get('skills', [])
            print(f"  - skills 개수: {len(skills)}")
            if skills:
                print(f"    첫 번째 스킬: {skills[0]}")
            
            # projectHistory 필드 확인
            project_history = item.get('projectHistory', [])
            print(f"  - projectHistory 개수: {len(project_history)}")
            
            project_history2 = item.get('project_history', [])
            print(f"  - project_history 개수: {len(project_history2)}")
            
            work_experience = item.get('work_experience', [])
            print(f"  - work_experience 개수: {len(work_experience)}")
            
            if work_experience:
                print(f"    첫 번째 프로젝트: {work_experience[0].get('project_name', 'N/A')}")
            
            # 전체 데이터 출력 (디버깅용)
            print(f"\n전체 데이터:")
            print(json.dumps(item, indent=2, cls=DecimalEncoder))
        else:
            print(f"  ✗ 데이터 없음")
    
    except Exception as e:
        print(f"  ✗ 오류: {str(e)}")

print("\n" + "=" * 80)
