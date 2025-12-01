import boto3
import json
import time
from decimal import Decimal

# AWS 클라이언트
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
dynamodb_client = boto3.client('dynamodb', region_name='us-east-2')

print("=" * 70)
print("프로젝트 테이블 초기화 및 재생성")
print("=" * 70)

table_name = 'Projects'

# 1. 기존 데이터 모두 삭제
print(f"\n[1단계] 기존 프로젝트 데이터 삭제 중...")
try:
    table = dynamodb.Table(table_name)
    
    # 모든 아이템 스캔
    response = table.scan()
    items = response.get('Items', [])
    
    # 페이지네이션 처리
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))
    
    print(f"  삭제할 아이템: {len(items)}개")
    
    # 배치 삭제
    deleted_count = 0
    with table.batch_writer() as batch:
        for item in items:
            batch.delete_item(Key={'project_id': item['project_id']})
            deleted_count += 1
            if deleted_count % 50 == 0:
                print(f"  진행: {deleted_count}/{len(items)} 삭제됨")
    
    print(f"  ✓ {deleted_count}개 아이템 삭제 완료")
    
except Exception as e:
    print(f"  ✗ 삭제 실패: {str(e)}")
    exit(1)

# 2. 로컬 프로젝트 데이터 로드
print(f"\n[2단계] 로컬 프로젝트 데이터 로드 중...")
try:
    with open('test_data/projects_data.json', 'r', encoding='utf-8') as f:
        projects = json.load(f)
    
    print(f"  ✓ {len(projects)}개의 프로젝트 데이터 로드됨")
    
except FileNotFoundError:
    print(f"  ✗ test_data/projects_data.json 파일을 찾을 수 없습니다")
    exit(1)
except Exception as e:
    print(f"  ✗ 파일 로드 실패: {str(e)}")
    exit(1)

# 3. Decimal 변환 함수
def convert_to_decimal(obj):
    """float를 Decimal로 변환 (DynamoDB 호환)"""
    if isinstance(obj, list):
        return [convert_to_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    return obj

# 4. 새 데이터 삽입
print(f"\n[3단계] 새 프로젝트 데이터 삽입 중...")
try:
    inserted_count = 0
    batch_size = 25
    
    for i in range(0, len(projects), batch_size):
        batch = projects[i:i + batch_size]
        
        with table.batch_writer() as writer:
            for project in batch:
                converted_project = convert_to_decimal(project)
                writer.put_item(Item=converted_project)
                inserted_count += 1
        
        print(f"  진행: {inserted_count}/{len(projects)} ({inserted_count*100//len(projects)}%)")
    
    print(f"  ✓ {inserted_count}개 프로젝트 삽입 완료")
    
except Exception as e:
    print(f"  ✗ 삽입 실패: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)

# 5. 검증
print(f"\n[4단계] 데이터 검증 중...")
try:
    response = table.scan(Select='COUNT')
    final_count = response['Count']
    
    print(f"  최종 프로젝트 수: {final_count}개")
    
    if final_count == len(projects):
        print(f"  ✓ 데이터 검증 성공!")
    else:
        print(f"  ⚠️  데이터 불일치: 예상 {len(projects)}개, 실제 {final_count}개")
    
except Exception as e:
    print(f"  ✗ 검증 실패: {str(e)}")

# 6. 샘플 데이터 확인
print(f"\n[5단계] 샘플 데이터 확인...")
try:
    response = table.scan(Limit=1)
    
    if response['Items']:
        sample = response['Items'][0]
        print(f"\n  샘플 프로젝트:")
        print(f"    ID: {sample.get('project_id')}")
        print(f"    이름: {sample.get('project_name')}")
        print(f"    산업: {sample.get('client_industry')}")
        print(f"    예산: {sample.get('budget_scale')}")
        
        # period 확인
        period = sample.get('period', {})
        if period:
            print(f"    기간: {period.get('start')} ~ {period.get('end')}")
        
        # team_composition 확인
        team_comp = sample.get('team_composition', {})
        if team_comp:
            total_members = sum(len(members) if isinstance(members, list) else members 
                              for members in team_comp.values())
            print(f"    팀 규모: {total_members}명")
            print(f"    팀 구성:")
            for role, members in list(team_comp.items())[:3]:
                if isinstance(members, list):
                    print(f"      {role}: {len(members)}명")
                else:
                    print(f"      {role}: {members}명")
        
        # tech_stack 확인
        tech_stack = sample.get('tech_stack', {})
        if tech_stack:
            print(f"    기술 스택:")
            for category, techs in list(tech_stack.items())[:2]:
                if techs:
                    print(f"      {category}: {', '.join(techs[:3])}...")
    
except Exception as e:
    print(f"  ✗ 샘플 조회 실패: {str(e)}")

print("\n" + "=" * 70)
print("완료!")
print("=" * 70)
print(f"\n✅ 프로젝트 테이블이 성공적으로 초기화되었습니다.")
print(f"   총 {len(projects)}개의 프로젝트가 로드되었습니다.")
print(f"\n다음 단계:")
print(f"  1. Lambda 함수 테스트")
print(f"     python deployment/test_projects_api.py")
print(f"  2. API Gateway 배포 (AWS Console)")
print(f"  3. 프론트엔드 재시작")
