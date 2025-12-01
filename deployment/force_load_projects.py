import json
import boto3
from decimal import Decimal
from botocore.exceptions import ClientError

def convert_to_decimal(obj):
    """DynamoDB용 float를 Decimal로 변환"""
    if isinstance(obj, list):
        return [convert_to_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    return obj

# AWS 리전 설정
REGION = 'us-east-2'
dynamodb = boto3.resource('dynamodb', region_name=REGION)

print("=" * 70)
print("DynamoDB 프로젝트 데이터 강제 업데이트")
print("=" * 70)

# 1. DynamoDB 테이블 확인
print("\n[1단계] DynamoDB 테이블 확인 중...")
try:
    table = dynamodb.Table('Projects')
    table_info = table.table_status
    print(f"  ✓ 'Projects' 테이블 존재 (상태: {table_info})")
except ClientError as e:
    print(f"  ✗ 'Projects' 테이블을 찾을 수 없습니다.")
    print(f"  오류: {e.response['Error']['Message']}")
    exit(1)

# 2. 현재 저장된 프로젝트 수 확인
print("\n[2단계] 현재 저장된 프로젝트 수 확인 중...")
try:
    response = table.scan(Select='COUNT')
    current_count = response['Count']
    print(f"  현재 DynamoDB에 저장된 프로젝트: {current_count}개")
except ClientError as e:
    print(f"  ✗ 데이터 조회 실패: {e.response['Error']['Message']}")
    current_count = 0

# 3. 로컬 프로젝트 데이터 로드
print("\n[3단계] 로컬 프로젝트 데이터 로드 중...")
try:
    with open('test_data/projects_data.json', 'r', encoding='utf-8') as f:
        projects = json.load(f)
    print(f"  로컬 파일에 {len(projects)}개의 프로젝트 데이터 존재")
    
    # 팀원 통계 (team_composition 형식)
    total_members = 0
    for p in projects:
        team_comp = p.get('team_composition', {})
        if isinstance(team_comp, dict):
            for role, members in team_comp.items():
                if isinstance(members, list):
                    total_members += len(members)
                elif isinstance(members, int):
                    total_members += members
    
    print(f"    - 총 배정 인원: {total_members}명")
    print(f"    - 프로젝트당 평균: {total_members / len(projects):.1f}명")
    
except FileNotFoundError:
    print("  ✗ test_data/projects_data.json 파일을 찾을 수 없습니다.")
    exit(1)

# 4. 배치 쓰기 함수
def batch_write_items(table, items, batch_size=25):
    """배치로 아이템 쓰기 (DynamoDB 제한: 25개)"""
    total = len(items)
    success_count = 0
    
    for i in range(0, total, batch_size):
        batch = items[i:i + batch_size]
        
        try:
            with table.batch_writer() as writer:
                for item in batch:
                    writer.put_item(Item=convert_to_decimal(item))
                    success_count += 1
            
            print(f"  진행: {success_count}/{total} ({success_count*100//total}%)")
        
        except ClientError as e:
            print(f"  ✗ 배치 쓰기 실패: {e.response['Error']['Message']}")
            # 실패한 경우 개별 아이템으로 재시도
            for item in batch:
                try:
                    table.put_item(Item=convert_to_decimal(item))
                    success_count += 1
                except ClientError as e2:
                    print(f"  ✗ 아이템 쓰기 실패 ({item.get('project_id', 'Unknown')}): {e2.response['Error']['Message']}")
    
    return success_count

# 5. 데이터 로드
print("\n[4단계] 프로젝트 데이터 업데이트 중...")
print("  (기존 데이터를 덮어씁니다)")
try:
    success = batch_write_items(table, projects)
    print(f"\n  ✓ {success}개의 프로젝트 데이터 DynamoDB에 저장 완료!")
    
except Exception as e:
    print(f"\n  ✗ 예상치 못한 오류: {str(e)}")
    exit(1)

# 6. 검증
print("\n[5단계] 데이터 로드 검증 중...")
try:
    response = table.scan(Select='COUNT')
    final_count = response['Count']
    print(f"  최종 DynamoDB 프로젝트 수: {final_count}개")
    
    if final_count >= len(projects):
        print(f"  ✓ 데이터 로드 성공!")
    else:
        print(f"  ⚠️  일부 데이터가 누락되었을 수 있습니다.")
        print(f"  예상: {len(projects)}개, 실제: {final_count}개")
    
except ClientError as e:
    print(f"  ✗ 검증 실패: {e.response['Error']['Message']}")

# 7. 상태별 통계
print("\n[6단계] 상태별 통계 확인 중...")
try:
    # 진행중 프로젝트 수
    response_ongoing = table.scan(
        FilterExpression='#status = :status',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={':status': '진행중'},
        Select='COUNT'
    )
    ongoing_count = response_ongoing['Count']
    
    # 완료 프로젝트 수
    response_completed = table.scan(
        FilterExpression='#status = :status',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={':status': '완료'},
        Select='COUNT'
    )
    completed_count = response_completed['Count']
    
    print(f"  진행중 프로젝트: {ongoing_count}개")
    print(f"  완료 프로젝트: {completed_count}개")
    
except ClientError as e:
    print(f"  ✗ 통계 조회 실패: {e.response['Error']['Message']}")

# 8. 샘플 데이터 조회
print("\n[7단계] 샘플 데이터 조회...")
try:
    # 진행중인 프로젝트 하나 조회
    response = table.scan(
        FilterExpression='#status = :status',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={':status': '진행중'},
        Limit=1
    )
    
    if response['Items']:
        sample = response['Items'][0]
        print(f"\n  샘플 프로젝트 (진행중):")
        print(f"    프로젝트 ID: {sample.get('project_id')}")
        print(f"    프로젝트명: {sample.get('project_name')}")
        print(f"    상태: {sample.get('status')}")
        print(f"    팀 규모: {sample.get('team_size')}명")
        print(f"    산업: {sample.get('client_industry')}")
        print(f"    우선순위: {sample.get('priority')}")
        
        team_members = sample.get('team_members', [])
        if team_members:
            print(f"    팀원 ({len(team_members)}명):")
            for member in team_members[:3]:
                score = member.get('skill_match_score', 'N/A')
                print(f"      - {member.get('name')} ({member.get('role')}) - 매칭점수: {score}")
            if len(team_members) > 3:
                print(f"      ... 외 {len(team_members) - 3}명")
        else:
            print(f"    ⚠️  팀원 정보 없음")
    else:
        print("  ℹ️  진행중인 프로젝트를 찾을 수 없습니다.")
        
except ClientError as e:
    print(f"  ✗ 샘플 조회 실패: {e.response['Error']['Message']}")

print("\n" + "=" * 70)
print("완료!")
print("=" * 70)
print("\n✅ 프로젝트 데이터가 DynamoDB에 성공적으로 로드되었습니다.")
print("\n주요 특징:")
print("  - 완료된 프로젝트: 기존 직원 경력 기반")
print("  - 진행중 프로젝트: 스킬 매칭 알고리즘 적용")
print("  - 모든 프로젝트에 팀원 배정 완료")
print("\n다음 단계:")
print("  1. AWS Console에서 DynamoDB 'Projects' 테이블 확인")
print("  2. API를 통해 프로젝트 조회 테스트")
print("  3. 직원-프로젝트 매칭 기능 테스트")
