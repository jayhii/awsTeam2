import boto3
import json
from decimal import Decimal

# AWS 클라이언트
lambda_client = boto3.client('lambda', region_name='us-east-2')

print("=" * 70)
print("Projects List API 테스트")
print("=" * 70)

# Lambda 함수 직접 호출
print("\n[테스트] Lambda 함수 직접 호출 중...")
function_name = 'ProjectsList'

try:
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        Payload=json.dumps({
            'httpMethod': 'GET',
            'path': '/projects',
            'headers': {}
        })
    )
    
    # 응답 파싱
    payload = json.loads(response['Payload'].read())
    
    print(f"\n응답 상태 코드: {payload.get('statusCode')}")
    
    if payload.get('statusCode') == 200:
        body = json.loads(payload.get('body', '{}'))
        projects = body.get('projects', [])
        count = body.get('count', 0)
        
        print(f"✓ 성공! 총 {count}개의 프로젝트 조회됨")
        
        # 상태별 통계
        status_count = {}
        for proj in projects:
            status = proj.get('status', 'unknown')
            status_count[status] = status_count.get(status, 0) + 1
        
        print(f"\n상태별 통계:")
        for status, cnt in status_count.items():
            print(f"  {status}: {cnt}개")
        
        # 샘플 프로젝트 출력 (진행중)
        ongoing_projects = [p for p in projects if p.get('status') == '진행중']
        
        if ongoing_projects:
            print(f"\n샘플 프로젝트 (진행중):")
            sample = ongoing_projects[0]
            print(f"  프로젝트 ID: {sample.get('project_id')}")
            print(f"  프로젝트명: {sample.get('project_name')}")
            print(f"  상태: {sample.get('status')}")
            print(f"  산업: {sample.get('client_industry')}")
            print(f"  시작일: {sample.get('start_date')}")
            print(f"  종료일: {sample.get('end_date')}")
            print(f"  필요 스킬: {', '.join(sample.get('required_skills', [])[:5])}...")
            
            team_members = sample.get('team_members', [])
            print(f"  팀 규모: {sample.get('team_size', 0)}명")
            
            if team_members:
                print(f"  팀원:")
                for member in team_members[:3]:
                    name = member.get('name', 'Unknown')
                    role = member.get('role', 'Unknown')
                    score = member.get('skill_match_score', 'N/A')
                    print(f"    - {name} ({role}) - 매칭점수: {score}")
                if len(team_members) > 3:
                    print(f"    ... 외 {len(team_members) - 3}명")
            else:
                print(f"  ⚠️  팀원 정보 없음")
        
        # 완료된 프로젝트 샘플
        completed_projects = [p for p in projects if p.get('status') == '완료']
        
        if completed_projects:
            print(f"\n샘플 프로젝트 (완료):")
            sample = completed_projects[0]
            print(f"  프로젝트 ID: {sample.get('project_id')}")
            print(f"  프로젝트명: {sample.get('project_name')}")
            print(f"  팀 규모: {sample.get('team_size', 0)}명")
            
            team_members = sample.get('team_members', [])
            if team_members:
                print(f"  팀원 수: {len(team_members)}명")
            else:
                print(f"  ⚠️  팀원 정보 없음")
        
    else:
        print(f"✗ 실패: {payload.get('body')}")
    
except Exception as e:
    print(f"✗ 테스트 실패: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
