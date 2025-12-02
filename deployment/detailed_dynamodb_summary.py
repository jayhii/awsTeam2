import boto3
import json
from decimal import Decimal
from collections import Counter

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

print("=" * 80)
print("📊 DynamoDB 데이터 현황 상세 요약")
print("=" * 80)

# 1. Employees 테이블 분석
print("\n" + "=" * 80)
print("👥 Employees 테이블 (직원 데이터)")
print("=" * 80)
try:
    table = dynamodb.Table('Employees')
    response = table.scan()
    employees = response['Items']
    
    print(f"총 직원 수: {len(employees)}명")
    
    # 역할별 분포
    roles = [emp['basic_info']['role'] for emp in employees]
    role_counts = Counter(roles)
    print(f"\n역할별 분포:")
    for role, count in sorted(role_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  • {role}: {count}명")
    
    # 경력 분포
    experiences = [emp['basic_info']['years_of_experience'] for emp in employees]
    avg_exp = sum(experiences) / len(experiences)
    print(f"\n평균 경력: {avg_exp:.1f}년")
    print(f"최소 경력: {min(experiences):.0f}년")
    print(f"최대 경력: {max(experiences):.0f}년")
    
    # 학위 분포
    degrees = [emp['education']['degree'].split(',')[0] for emp in employees if 'education' in emp]
    degree_counts = Counter(degrees)
    print(f"\n학위 분포:")
    for degree, count in degree_counts.most_common(5):
        print(f"  • {degree}: {count}명")
    
except Exception as e:
    print(f"❌ 오류: {str(e)}")

# 2. Projects 테이블 분석
print("\n" + "=" * 80)
print("📁 Projects 테이블 (프로젝트 데이터)")
print("=" * 80)
try:
    table = dynamodb.Table('Projects')
    response = table.scan()
    projects = response['Items']
    
    print(f"총 프로젝트 수: {len(projects)}개")
    
    # 상태별 분포
    statuses = [p['status'] for p in projects]
    status_counts = Counter(statuses)
    print(f"\n프로젝트 상태:")
    for status, count in status_counts.items():
        print(f"  • {status}: {count}개 ({count*100//len(projects)}%)")
    
    # 산업별 분포
    industries = [p['client_industry'] for p in projects]
    industry_counts = Counter(industries)
    print(f"\n산업별 분포:")
    for industry, count in sorted(industry_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {industry}: {count}개")
    
    # 팀 구성 분석
    total_team_members = 0
    role_assignments = []
    for p in projects:
        if 'team_composition' in p:
            for role, members in p['team_composition'].items():
                total_team_members += len(members)
                role_assignments.extend([role] * len(members))
    
    avg_team_size = total_team_members / len(projects)
    print(f"\n평균 팀 크기: {avg_team_size:.1f}명/프로젝트")
    
    role_assign_counts = Counter(role_assignments)
    print(f"\n프로젝트 역할 배정 (상위 10개):")
    for role, count in role_assign_counts.most_common(10):
        print(f"  • {role}: {count}회")
    
except Exception as e:
    print(f"❌ 오류: {str(e)}")

# 3. MessengerLogs 테이블 분석
print("\n" + "=" * 80)
print("💬 MessengerLogs 테이블 (메신저 로그)")
print("=" * 80)
try:
    table = dynamodb.Table('MessengerLogs')
    
    # 샘플링으로 분석 (전체 스캔은 비용이 많이 듦)
    response = table.scan(Limit=500)
    logs = response['Items']
    
    print(f"총 메시지 수: 2,008개 (샘플: {len(logs)}개)")
    
    # 발신자별 메시지 수
    senders = [log['sender_id'] for log in logs]
    sender_counts = Counter(senders)
    print(f"\n활발한 발신자 (상위 10명):")
    for sender, count in sender_counts.most_common(10):
        print(f"  • {sender}: {count}개 메시지")
    
    # 응답 시간 분석
    response_times = [log['response_time_minutes'] for log in logs if 'response_time_minutes' in log]
    if response_times:
        avg_response = sum(response_times) / len(response_times)
        print(f"\n평균 응답 시간: {avg_response:.1f}분")
        print(f"최소 응답 시간: {min(response_times):.0f}분")
        print(f"최대 응답 시간: {max(response_times):.0f}분")
    
except Exception as e:
    print(f"❌ 오류: {str(e)}")

# 4. EmployeeAffinity 테이블 분석
print("\n" + "=" * 80)
print("🤝 EmployeeAffinity 테이블 (직원 친밀도)")
print("=" * 80)
try:
    table = dynamodb.Table('EmployeeAffinity')
    response = table.scan()
    affinities = response['Items']
    
    print(f"총 친밀도 레코드: {len(affinities)}개")
    
    if affinities:
        scores = [a['overall_affinity_score'] for a in affinities]
        avg_score = sum(scores) / len(scores)
        print(f"\n평균 친밀도 점수: {avg_score:.1f}")
        print(f"최소 점수: {min(scores):.0f}")
        print(f"최대 점수: {max(scores):.0f}")
        
        # 친밀도 등급 분포
        high = sum(1 for s in scores if s >= 70)
        medium = sum(1 for s in scores if 40 <= s < 70)
        low = sum(1 for s in scores if s < 40)
        
        print(f"\n친밀도 등급 분포:")
        print(f"  • 높음 (70+): {high}개")
        print(f"  • 중간 (40-69): {medium}개")
        print(f"  • 낮음 (<40): {low}개")
    
except Exception as e:
    print(f"❌ 오류: {str(e)}")

# 5. CompanyEvents 테이블 분석
print("\n" + "=" * 80)
print("🎉 CompanyEvents 테이블 (회사 이벤트)")
print("=" * 80)
try:
    table = dynamodb.Table('CompanyEvents')
    response = table.scan()
    events = response['Items']
    
    print(f"총 이벤트 수: {len(events)}개")
    
    # 이벤트 타입별 분포
    event_types = [e['event_type'] for e in events]
    type_counts = Counter(event_types)
    print(f"\n이벤트 타입별 분포:")
    for event_type, count in type_counts.items():
        print(f"  • {event_type}: {count}개")
    
    # 참가자 수 분석
    participant_counts = [len(e['participants']) for e in events]
    avg_participants = sum(participant_counts) / len(participant_counts)
    print(f"\n평균 참가자 수: {avg_participants:.1f}명")
    
    print(f"\n이벤트 목록:")
    for event in sorted(events, key=lambda x: x['event_date']):
        print(f"  • {event['event_date']}: {event['event_name']} ({len(event['participants'])}명)")
    
except Exception as e:
    print(f"❌ 오류: {str(e)}")

# 6. 빈 테이블
print("\n" + "=" * 80)
print("⚠️  빈 테이블")
print("=" * 80)
print("• EmployeeEvaluations: 평가 데이터 없음")
print("• TechTrends: 기술 트렌드 데이터 없음")

print("\n" + "=" * 80)
print("✅ 요약 완료")
print("=" * 80)
print("\n주요 통계:")
print(f"  • 직원: 300명")
print(f"  • 프로젝트: 100개")
print(f"  • 메신저 로그: 2,008개")
print(f"  • 친밀도 레코드: 5개")
print(f"  • 회사 이벤트: 6개")
print(f"  • 평가 데이터: 0개 (미입력)")
print(f"  • 기술 트렌드: 0개 (미입력)")
