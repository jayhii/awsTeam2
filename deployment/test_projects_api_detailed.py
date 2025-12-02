"""
프로젝트 API 상세 테스트
Lambda 함수가 반환하는 데이터 구조 확인
"""
import json
import boto3

# Lambda 함수 직접 호출
lambda_client = boto3.client('lambda', region_name='us-east-2')

print("=" * 80)
print("프로젝트 API 상세 테스트")
print("=" * 80)

# Lambda 함수 호출
response = lambda_client.invoke(
    FunctionName='ProjectsList',
    InvocationType='RequestResponse',
    Payload=json.dumps({
        'httpMethod': 'GET',
        'path': '/projects'
    })
)

# 응답 파싱
payload = json.loads(response['Payload'].read())
print(f"\nLambda 응답 상태 코드: {payload.get('statusCode')}")

if payload.get('statusCode') == 200:
    body = json.loads(payload['body'])
    projects = body.get('projects', [])
    
    print(f"\n총 프로젝트 수: {len(projects)}개")
    
    if projects:
        # 첫 번째 프로젝트 상세 정보
        first_project = projects[0]
        print("\n" + "=" * 80)
        print("첫 번째 프로젝트 상세 정보")
        print("=" * 80)
        print(json.dumps(first_project, indent=2, ensure_ascii=False))
        
        # 필드 체크
        print("\n" + "=" * 80)
        print("필드 존재 여부 체크")
        print("=" * 80)
        
        required_fields = [
            'project_id',
            'project_name',
            'status',
            'start_date',
            'end_date',
            'duration_months',
            'team_members',
            'team_size',
            'required_skills',
            'client_industry',
            'budget_scale',
            'description'
        ]
        
        for field in required_fields:
            exists = field in first_project
            value = first_project.get(field, 'N/A')
            status = "✅" if exists else "❌"
            
            # 값 미리보기
            if isinstance(value, list):
                preview = f"[{len(value)}개 항목]"
            elif isinstance(value, dict):
                preview = f"{{...}}"
            elif isinstance(value, str) and len(value) > 50:
                preview = value[:50] + "..."
            else:
                preview = value
            
            print(f"{status} {field:20s}: {preview}")
        
        # 팀원 정보 상세
        if 'team_members' in first_project and first_project['team_members']:
            print("\n" + "=" * 80)
            print("팀원 정보 샘플 (최대 3명)")
            print("=" * 80)
            for i, member in enumerate(first_project['team_members'][:3], 1):
                print(f"\n[{i}] {json.dumps(member, indent=2, ensure_ascii=False)}")
        
        # 날짜 정보 확인
        print("\n" + "=" * 80)
        print("날짜 정보 확인")
        print("=" * 80)
        print(f"시작일: {first_project.get('start_date', 'N/A')}")
        print(f"종료일: {first_project.get('end_date', 'N/A')}")
        print(f"기간: {first_project.get('duration_months', 'N/A')}개월")
        
        # 통계
        print("\n" + "=" * 80)
        print("전체 프로젝트 통계")
        print("=" * 80)
        
        # 날짜 정보가 있는 프로젝트 수
        with_start_date = sum(1 for p in projects if p.get('start_date') and p.get('start_date') != '')
        with_end_date = sum(1 for p in projects if p.get('end_date') and p.get('end_date') != '')
        with_team_members = sum(1 for p in projects if p.get('team_members') and len(p.get('team_members', [])) > 0)
        
        print(f"시작일 있음: {with_start_date}/{len(projects)}개 ({with_start_date*100//len(projects)}%)")
        print(f"종료일 있음: {with_end_date}/{len(projects)}개 ({with_end_date*100//len(projects)}%)")
        print(f"팀원 정보 있음: {with_team_members}/{len(projects)}개 ({with_team_members*100//len(projects)}%)")
        
        # 평균 팀 크기
        total_team_size = sum(p.get('team_size', 0) for p in projects)
        avg_team_size = total_team_size / len(projects) if projects else 0
        print(f"평균 팀 크기: {avg_team_size:.1f}명")
        
else:
    print(f"\n❌ 오류 발생:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

print("\n" + "=" * 80)
print("테스트 완료")
print("=" * 80)
