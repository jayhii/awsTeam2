import json
import random
from datetime import datetime, timedelta
from collections import defaultdict

# 직원 데이터 로드
with open('test_data/employees_extended.json', 'r', encoding='utf-8') as f:
    employees = json.load(f)

print(f"직원 데이터 로드: {len(employees)}명")

# 직원 스킬 인덱스 생성
employee_skills_map = {}
for emp in employees:
    user_id = emp['user_id']
    skills = set()
    for skill in emp.get('skills', []):
        skills.add(skill['name'])
    employee_skills_map[user_id] = {
        'name': emp['basic_info']['name'],
        'role': emp['basic_info']['role'],
        'years_exp': emp['basic_info']['years_of_experience'],
        'skills': skills,
        'employee': emp
    }

# 직원들의 기존 프로젝트 정보 수집
existing_projects = {}
project_members = defaultdict(list)

for emp in employees:
    user_id = emp['user_id']
    name = emp['basic_info']['name']
    role = emp['basic_info']['role']
    
    for exp in emp.get('work_experience', []):
        project_id = exp['project_id']
        
        if project_id not in existing_projects:
            existing_projects[project_id] = {
                'project_id': project_id,
                'project_name': exp['project_name'],
                'members': []
            }
        
        project_members[project_id].append({
            'user_id': user_id,
            'name': name,
            'role': exp['role'],
            'period': exp['period']
        })

print(f"기존 프로젝트 수집: {len(existing_projects)}개 (완료된 프로젝트)")

# 산업 분야 및 기술 스택 매핑
industry_tech_map = {
    "Finance": {
        "industries": ["금융", "은행", "증권", "보험"],
        "techs": ["Java", "Spring Framework", "Oracle", "MSA", "Kubernetes", "Redis", "Kafka"],
        "domains": ["코어뱅킹", "거래시스템", "결제시스템", "리스크관리"],
        "roles": ["System Architect", "Backend Developer", "Data Engineer", "Security Engineer"]
    },
    "Manufacturing": {
        "industries": ["제조", "자동차", "전자", "화학"],
        "techs": ["Python", "TensorFlow", "IoT", "Computer Vision", "MES", "Edge Computing"],
        "domains": ["스마트팩토리", "품질관리", "생산최적화", "예지보전"],
        "roles": ["AI/ML Engineer", "Data Engineer", "Backend Developer", "IoT Engineer"]
    },
    "E-commerce": {
        "industries": ["이커머스", "유통", "리테일"],
        "techs": ["React", "Node.js", "MongoDB", "Redis", "Elasticsearch", "Kafka", "MSA"],
        "domains": ["커머스플랫폼", "추천시스템", "재고관리", "주문관리"],
        "roles": ["Frontend Developer", "Backend Developer", "Full Stack Developer", "DevOps Engineer"]
    },
    "Healthcare": {
        "industries": ["헬스케어", "의료", "제약", "바이오"],
        "techs": ["Python", "TensorFlow", "PostgreSQL", "FHIR", "HL7"],
        "domains": ["EMR", "진단보조", "환자관리", "임상데이터분석"],
        "roles": ["AI/ML Engineer", "Backend Developer", "Data Scientist", "Security Engineer"]
    },
    "Logistics": {
        "industries": ["물류", "운송", "배송"],
        "techs": ["Java", "Spring Boot", "PostgreSQL", "Redis", "Kafka", "GPS"],
        "domains": ["배송관리", "경로최적화", "재고관리", "WMS"],
        "roles": ["Backend Developer", "Full Stack Developer", "Data Engineer", "Mobile Developer"]
    },
    "Telecom": {
        "industries": ["통신", "5G", "네트워크"],
        "techs": ["Java", "C++", "Kubernetes", "Kafka", "Prometheus"],
        "domains": ["네트워크관리", "과금시스템", "고객관리", "IoT플랫폼"],
        "roles": ["System Architect", "Backend Developer", "DevOps Engineer", "Network Engineer"]
    },
    "Energy": {
        "industries": ["에너지", "전력", "신재생"],
        "techs": ["Python", "IoT", "Time Series DB", "Grafana", "Edge Computing"],
        "domains": ["스마트그리드", "에너지관리", "발전소운영", "ESS"],
        "roles": ["Data Engineer", "IoT Engineer", "Backend Developer", "DevOps Engineer"]
    },
    "Education": {
        "industries": ["교육", "에듀테크", "이러닝"],
        "techs": ["React", "Node.js", "MongoDB", "WebRTC", "LMS"],
        "domains": ["LMS", "화상교육", "학습분석", "콘텐츠관리"],
        "roles": ["Frontend Developer", "Backend Developer", "Full Stack Developer", "UI/UX Designer"]
    }
}

project_statuses = ["진행중", "완료", "계획중"]
project_priorities = ["높음", "중간", "낮음"]

def calculate_skill_match_score(employee_skills, required_skills):
    """직원 스킬과 프로젝트 필요 스킬 매칭 점수 계산"""
    if not required_skills:
        return 0
    
    matched = len(employee_skills.intersection(set(required_skills)))
    return matched / len(required_skills) * 100

def find_best_employees_for_project(required_skills, required_roles, num_needed, exclude_ids=set()):
    """프로젝트에 가장 적합한 직원 찾기"""
    candidates = []
    
    for user_id, emp_info in employee_skills_map.items():
        if user_id in exclude_ids:
            continue
        
        # 스킬 매칭 점수
        skill_score = calculate_skill_match_score(emp_info['skills'], required_skills)
        
        # 역할 매칭 보너스
        role_bonus = 20 if any(role in emp_info['role'] for role in required_roles) else 0
        
        # 경력 점수 (5년 이상이면 보너스)
        exp_bonus = min(emp_info['years_exp'] * 2, 20)
        
        total_score = skill_score + role_bonus + exp_bonus
        
        candidates.append({
            'user_id': user_id,
            'info': emp_info,
            'score': total_score
        })
    
    # 점수 순으로 정렬
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    return candidates[:num_needed]

def generate_project_details(project_name, industry_key, is_ongoing=False):
    """프로젝트 상세 정보 생성"""
    industry_info = industry_tech_map[industry_key]
    
    # 프로젝트 기간
    if is_ongoing:
        # 진행중 프로젝트: 최근 시작, 미래 종료
        start_year = random.choice([2024, 2024, 2024, 2023])  # 대부분 2024년
        start_month = random.randint(1, 11)
        duration_months = random.randint(12, 24)
        start_date = f"{start_year}-{start_month:02d}-01"
        
        end_datetime = datetime(start_year, start_month, 1) + timedelta(days=duration_months*30)
        end_date = end_datetime.strftime("%Y-%m-%d")
        status = "진행중"
    else:
        # 완료된 프로젝트
        start_year = random.randint(2022, 2023)
        start_month = random.randint(1, 12)
        duration_months = random.randint(6, 18)
        start_date = f"{start_year}-{start_month:02d}-01"
        
        end_datetime = datetime(start_year, start_month, 1) + timedelta(days=duration_months*30)
        end_date = end_datetime.strftime("%Y-%m-%d")
        status = "완료"
    
    # 예산 (억원)
    budget = random.randint(10, 500)
    
    # 필요 기술
    num_skills = min(random.randint(5, 8), len(industry_info['techs']))
    required_skills = random.sample(industry_info['techs'], num_skills)
    
    # 클라이언트 정보
    client_name = f"{random.choice(industry_info['industries'])} {random.choice(['A', 'B', 'C', 'D', 'E'])}사"
    
    return {
        'client_name': client_name,
        'client_industry': random.choice(industry_info['industries']),
        'start_date': start_date,
        'end_date': end_date,
        'status': status,
        'budget': budget,
        'priority': random.choice(project_priorities) if is_ongoing else "낮음",
        'required_skills': required_skills,
        'required_roles': industry_info['roles'],
        'description': f"{client_name}의 {random.choice(industry_info['domains'])} 구축 프로젝트",
        'objectives': [
            f"{random.choice(industry_info['domains'])} 시스템 구축",
            "업무 효율성 향상",
            "디지털 전환 가속화"
        ]
    }

# 1. 기존 프로젝트 데이터 완성 (완료된 프로젝트)
projects = []

for project_id, proj_info in existing_projects.items():
    members = project_members[project_id]
    
    # 랜덤 산업 선택
    industry_key = random.choice(list(industry_tech_map.keys()))
    
    project = {
        'project_id': project_id,
        'project_name': proj_info['project_name'],
        **generate_project_details(proj_info['project_name'], industry_key, is_ongoing=False),
        'team_members': members,
        'team_size': len(members)
    }
    
    projects.append(project)

print(f"기존 프로젝트 생성 완료: {len(projects)}개 (모두 완료 상태)")

# 2. 신규 프로젝트 생성 (진행중 프로젝트, 스킬 매칭)
new_project_templates = [
    ("AI 기반 고객 서비스 챗봇 구축", "E-commerce"),
    ("클라우드 네이티브 마이크로서비스 전환", "Finance"),
    ("빅데이터 분석 플랫폼 구축", "E-commerce"),
    ("모바일 뱅킹 앱 리뉴얼", "Finance"),
    ("레거시 시스템 현대화", "Finance"),
    ("실시간 데이터 파이프라인 구축", "E-commerce"),
    ("보안 강화 및 컴플라이언스 대응", "Finance"),
    ("DevOps 자동화 구축", "Telecom"),
    ("고객 데이터 플랫폼(CDP) 구축", "E-commerce"),
    ("옴니채널 커머스 플랫폼", "E-commerce"),
    ("IoT 디바이스 관리 플랫폼", "Manufacturing"),
    ("블록체인 기반 인증 시스템", "Finance"),
    ("AI 추천 엔진 고도화", "E-commerce"),
    ("실시간 모니터링 대시보드", "Telecom"),
    ("API Gateway 및 통합 플랫폼", "Finance"),
    ("데이터 웨어하우스 구축", "Healthcare"),
    ("머신러닝 파이프라인 자동화", "Manufacturing"),
    ("고가용성 인프라 구축", "Finance"),
    ("서버리스 아키텍처 전환", "E-commerce"),
    ("컨테이너 오케스트레이션 플랫폼", "Telecom"),
    ("스마트 팩토리 MES 구축", "Manufacturing"),
    ("전자의무기록(EMR) 시스템", "Healthcare"),
    ("물류 최적화 플랫폼", "Logistics"),
    ("스마트 그리드 관리 시스템", "Energy"),
    ("온라인 교육 플랫폼", "Education"),
    ("5G 네트워크 관리 시스템", "Telecom"),
    ("AI 기반 품질 검사 시스템", "Manufacturing"),
    ("환자 데이터 분석 플랫폼", "Healthcare"),
    ("배송 경로 최적화 시스템", "Logistics"),
    ("신재생 에너지 모니터링", "Energy"),
    ("학습 분석 대시보드", "Education"),
    ("증권 거래 시스템 고도화", "Finance"),
    ("이커머스 추천 시스템", "E-commerce"),
    ("예지 보전 AI 시스템", "Manufacturing"),
    ("원격 진료 플랫폼", "Healthcare"),
    ("창고 관리 시스템(WMS)", "Logistics"),
    ("ESS 통합 관리 플랫폼", "Energy"),
    ("화상 교육 솔루션", "Education"),
    ("네트워크 자동화 플랫폼", "Telecom"),
    ("디지털 트윈 구축", "Manufacturing"),
    ("의료 영상 AI 분석", "Healthcare"),
    ("라스트마일 배송 시스템", "Logistics"),
    ("전력 수요 예측 시스템", "Energy"),
    ("학습 콘텐츠 관리 시스템", "Education"),
    ("모바일 결제 시스템", "Finance"),
    ("소셜 커머스 플랫폼", "E-commerce"),
    ("생산 스케줄링 최적화", "Manufacturing"),
    ("임상 데이터 분석 플랫폼", "Healthcare"),
    ("실시간 배송 추적 시스템", "Logistics"),
    ("에너지 거래 플랫폼", "Energy")
]

current_max_id = max([int(p['project_id'].split('_')[1]) for p in projects])
used_employees = set()  # 이미 배정된 직원 추적

for i, (project_name, industry_key) in enumerate(new_project_templates):
    project_id = f"P_{current_max_id + i + 1:03d}"
    
    # 프로젝트 상세 정보 생성
    project_details = generate_project_details(project_name, industry_key, is_ongoing=True)
    
    # 필요한 팀원 수 (3-8명)
    team_size = random.randint(3, 8)
    
    # 스킬 매칭으로 최적의 직원 찾기
    best_candidates = find_best_employees_for_project(
        project_details['required_skills'],
        project_details['required_roles'],
        team_size,
        exclude_ids=used_employees
    )
    
    # 팀원 정보 생성
    members = []
    for candidate in best_candidates:
        emp_info = candidate['info']
        user_id = candidate['user_id']
        
        # 프로젝트 기간 (진행중이므로 현재 참여중)
        start_date = project_details['start_date']
        end_date = project_details['end_date']
        
        members.append({
            'user_id': user_id,
            'name': emp_info['name'],
            'role': emp_info['role'],
            'period': f"{start_date[:7]} ~ {end_date[:7]}",
            'skill_match_score': round(candidate['score'], 1)
        })
        
        used_employees.add(user_id)
    
    project = {
        'project_id': project_id,
        'project_name': project_name,
        **project_details,
        'team_members': members,
        'team_size': len(members)
    }
    
    # required_roles는 내부 처리용이므로 제거
    del project['required_roles']
    
    projects.append(project)

print(f"신규 프로젝트 생성 완료: {len(new_project_templates)}개 (모두 진행중 상태)")
print(f"총 프로젝트 수: {len(projects)}개")
print(f"프로젝트에 배정된 직원: {len(used_employees)}명 / {len(employees)}명")

# 프로젝트 데이터 저장
with open('test_data/projects_data.json', 'w', encoding='utf-8') as f:
    json.dump(projects, f, ensure_ascii=False, indent=2)

print("\n프로젝트 데이터 저장 완료: test_data/projects_data.json")

# 통계 출력
status_count = defaultdict(int)
industry_count = defaultdict(int)
priority_count = defaultdict(int)

for proj in projects:
    status_count[proj['status']] += 1
    industry_count[proj['client_industry']] += 1
    priority_count[proj['priority']] += 1

print("\n" + "=" * 60)
print("프로젝트 통계")
print("=" * 60)
print(f"총 프로젝트: {len(projects)}개")
print(f"\n상태별:")
for status, count in sorted(status_count.items()):
    print(f"  {status}: {count}개")
print(f"\n우선순위별:")
for priority, count in sorted(priority_count.items()):
    print(f"  {priority}: {count}개")
print(f"\n산업별 (Top 5):")
for industry, count in sorted(industry_count.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {industry}: {count}개")

# 스킬 매칭 통계
print(f"\n스킬 매칭 통계:")
ongoing_projects = [p for p in projects if p['status'] == '진행중']
if ongoing_projects:
    avg_match_scores = []
    for proj in ongoing_projects:
        if proj['team_members']:
            scores = [m.get('skill_match_score', 0) for m in proj['team_members']]
            avg_match_scores.append(sum(scores) / len(scores))
    
    if avg_match_scores:
        print(f"  평균 스킬 매칭 점수: {sum(avg_match_scores) / len(avg_match_scores):.1f}점")
        print(f"  최고 매칭 점수: {max(avg_match_scores):.1f}점")
        print(f"  최저 매칭 점수: {min(avg_match_scores):.1f}점")
