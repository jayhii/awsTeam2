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

# 산업 분야 및 기술 스택 매핑
industry_tech_map = {
    "Finance": {
        "techs": {
            "backend": ["Java", "Spring Boot", "Oracle", "MSA"],
            "frontend": ["React", "TypeScript", "Angular"],
            "data": ["Oracle", "Redis", "PostgreSQL"],
            "infra": ["AWS", "Docker", "Kubernetes", "Terraform"]
        },
        "requirements": ["보안", "고가용성", "확장성", "컴플라이언스"],
        "roles": ["Backend Developer", "System Architect", "Security Engineer", "DevOps Engineer"]
    },
    "E-commerce": {
        "techs": {
            "backend": ["Node.js", "Express", "Java", "Spring Boot"],
            "frontend": ["React", "Vue.js", "Next.js"],
            "data": ["MongoDB", "Redis", "Elasticsearch"],
            "infra": ["AWS", "Docker", "Kubernetes"]
        },
        "requirements": ["결제 시스템", "재고 관리", "추천 시스템", "실시간 처리"],
        "roles": ["Full Stack Developer", "Backend Developer", "Frontend Developer", "DevOps Engineer"]
    },
    "Manufacturing": {
        "techs": {
            "backend": ["Python", "Django", "FastAPI"],
            "frontend": ["React", "Vue.js"],
            "data": ["PostgreSQL", "MongoDB", "Time Series DB"],
            "infra": ["AWS", "Docker", "Edge Computing"]
        },
        "requirements": ["IoT 연동", "실시간 모니터링", "예지 보전", "품질 관리"],
        "roles": ["AI/ML Engineer", "Backend Developer", "Data Engineer", "IoT Engineer"]
    },
    "Healthcare": {
        "techs": {
            "backend": ["Python", "Java", "Spring Boot"],
            "frontend": ["React", "Angular"],
            "data": ["PostgreSQL", "MongoDB"],
            "infra": ["AWS", "Docker"]
        },
        "requirements": ["HIPAA 준수", "데이터 보안", "실시간 분석", "EMR 연동"],
        "roles": ["Backend Developer", "Security Engineer", "Data Scientist", "Full Stack Developer"]
    }
}

budget_scales = ["Small", "Medium", "Large", "Enterprise"]

def calculate_skill_match_score(employee_skills, required_techs):
    """스킬 매칭 점수 계산"""
    all_required = []
    for category, techs in required_techs.items():
        all_required.extend(techs)
    
    if not all_required:
        return 0
    
    matched = len(employee_skills.intersection(set(all_required)))
    return (matched / len(all_required)) * 100

def find_best_employees_for_project(required_techs, required_roles, num_needed, exclude_ids=set()):
    """프로젝트에 가장 적합한 직원 찾기"""
    candidates = []
    
    for user_id, emp_info in employee_skills_map.items():
        if user_id in exclude_ids:
            continue
        
        # 스킬 매칭 점수
        skill_score = calculate_skill_match_score(emp_info['skills'], required_techs)
        
        # 역할 매칭 보너스
        role_bonus = 20 if any(role in emp_info['role'] for role in required_roles) else 0
        
        # 경력 점수
        exp_bonus = min(emp_info['years_exp'] * 2, 20)
        
        total_score = skill_score + role_bonus + exp_bonus
        
        candidates.append({
            'user_id': user_id,
            'info': emp_info,
            'score': total_score
        })
    
    candidates.sort(key=lambda x: x['score'], reverse=True)
    return candidates[:num_needed]

def generate_project(project_id, project_name, industry_key, is_ongoing=False):
    """프로젝트 생성 (load_test_data.py 형식)"""
    industry_info = industry_tech_map[industry_key]
    
    # 프로젝트 기간
    if is_ongoing:
        start_year = random.choice([2024, 2024, 2024, 2023])
        start_month = random.randint(1, 11)
        duration_months = random.randint(12, 24)
    else:
        start_year = random.randint(2022, 2023)
        start_month = random.randint(1, 12)
        duration_months = random.randint(6, 18)
    
    start_date = f"{start_year}-{start_month:02d}-01"
    end_datetime = datetime(start_year, start_month, 1) + timedelta(days=duration_months*30)
    end_date = end_datetime.strftime("%Y-%m-%d")
    
    # 팀 구성 (역할별 필요 인원)
    team_composition = {}
    total_needed = random.randint(3, 8)
    roles = industry_info['roles']
    
    for i, role in enumerate(roles):
        if i < len(roles) - 1:
            count = random.randint(1, max(1, total_needed // len(roles)))
            team_composition[role] = count
            total_needed -= count
        else:
            team_composition[role] = max(1, total_needed)
    
    # 최적의 직원 찾기
    best_candidates = find_best_employees_for_project(
        industry_info['techs'],
        roles,
        sum(team_composition.values()),
        set()
    )
    
    # 실제 배정된 팀원 (역할별로 분류)
    assigned_team = {}
    candidate_idx = 0
    
    for role, count in team_composition.items():
        assigned_team[role] = []
        for _ in range(count):
            if candidate_idx < len(best_candidates):
                candidate = best_candidates[candidate_idx]
                assigned_team[role].append(candidate['user_id'])
                candidate_idx += 1
    
    # load_test_data.py 형식에 맞춘 프로젝트 객체
    project = {
        "project_id": project_id,
        "project_name": project_name,
        "client_industry": industry_key,
        "period": {
            "start": start_date,
            "end": end_date,
            "duration_months": duration_months
        },
        "budget_scale": random.choice(budget_scales),
        "description": f"{industry_key} 분야 {project_name}",
        "tech_stack": industry_info['techs'],
        "requirements": industry_info['requirements'],
        "team_composition": assigned_team  # 역할별 배정된 직원 ID 목록
    }
    
    return project

# 프로젝트 템플릿
project_templates = [
    ("금융 플랫폼 구축", "Finance"),
    ("차세대 코어뱅킹 시스템", "Finance"),
    ("증권 거래 시스템", "Finance"),
    ("모바일 뱅킹 앱", "Finance"),
    ("E-commerce 플랫폼", "E-commerce"),
    ("온라인 쇼핑몰 구축", "E-commerce"),
    ("옴니채널 커머스", "E-commerce"),
    ("AI 추천 시스템", "E-commerce"),
    ("스마트 팩토리 MES", "Manufacturing"),
    ("IoT 플랫폼 구축", "Manufacturing"),
    ("예지 보전 시스템", "Manufacturing"),
    ("품질 관리 시스템", "Manufacturing"),
    ("EMR 시스템 구축", "Healthcare"),
    ("원격 진료 플랫폼", "Healthcare"),
    ("의료 데이터 분석", "Healthcare"),
    ("환자 관리 시스템", "Healthcare"),
]

# 프로젝트 생성
projects = []

# 완료된 프로젝트 (50개)
print("\n완료된 프로젝트 생성 중...")
for i in range(50):
    project_name, industry = random.choice(project_templates)
    project_id = f"PRJ{i+1:03d}"
    project = generate_project(project_id, project_name, industry, is_ongoing=False)
    projects.append(project)
    
    if (i + 1) % 10 == 0:
        print(f"  {i + 1}/50 완료")

# 진행중 프로젝트 (50개)
print("\n진행중 프로젝트 생성 중...")
for i in range(50):
    project_name, industry = random.choice(project_templates)
    project_id = f"PRJ{i+51:03d}"
    project = generate_project(project_id, project_name, industry, is_ongoing=True)
    projects.append(project)
    
    if (i + 1) % 10 == 0:
        print(f"  {i + 1}/50 완료")

print(f"\n총 프로젝트 수: {len(projects)}개")

# 프로젝트 데이터 저장
with open('test_data/projects_data.json', 'w', encoding='utf-8') as f:
    json.dump(projects, f, ensure_ascii=False, indent=2)

print("프로젝트 데이터 저장 완료: test_data/projects_data.json")

# 통계 출력
print("\n=== 프로젝트 통계 ===")
print(f"총 프로젝트: {len(projects)}개")

# 산업별 통계
industry_count = defaultdict(int)
for proj in projects:
    industry_count[proj['client_industry']] += 1

print("\n산업별:")
for industry, count in sorted(industry_count.items()):
    print(f"  {industry}: {count}개")

# 예산 규모별 통계
budget_count = defaultdict(int)
for proj in projects:
    budget_count[proj['budget_scale']] += 1

print("\n예산 규모별:")
for budget, count in sorted(budget_count.items()):
    print(f"  {budget}: {count}개")

# 팀 구성 통계
total_members = 0
for proj in projects:
    for role, members in proj['team_composition'].items():
        total_members += len(members) if isinstance(members, list) else members

print(f"\n총 배정 인원: {total_members}명")
print(f"프로젝트당 평균 인원: {total_members / len(projects):.1f}명")
