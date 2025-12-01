import json
import random
from datetime import datetime, timedelta
from collections import defaultdict

# 직원 데이터 로드
with open('test_data/employees_extended.json', 'r', encoding='utf-8') as f:
    employees = json.load(f)

print(f"직원 데이터 로드: {len(employees)}명")

# 직원들의 프로젝트 정보 수집
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

print(f"기존 프로젝트 수집: {len(existing_projects)}개")

# 산업 분야 및 기술 스택 매핑
industry_tech_map = {
    "Finance": {
        "industries": ["금융", "은행", "증권", "보험"],
        "techs": ["Java", "Spring Framework", "Oracle", "MSA", "Kubernetes", "Redis", "Kafka"],
        "domains": ["코어뱅킹", "거래시스템", "결제시스템", "리스크관리"]
    },
    "Manufacturing": {
        "industries": ["제조", "자동차", "전자", "화학"],
        "techs": ["Python", "TensorFlow", "IoT", "Edge Computing", "Computer Vision", "MES"],
        "domains": ["스마트팩토리", "품질관리", "생산최적화", "예지보전"]
    },
    "E-commerce": {
        "industries": ["이커머스", "유통", "리테일"],
        "techs": ["React", "Node.js", "MongoDB", "Redis", "Elasticsearch", "Kafka", "MSA"],
        "domains": ["커머스플랫폼", "추천시스템", "재고관리", "주문관리"]
    },
    "Healthcare": {
        "industries": ["헬스케어", "의료", "제약", "바이오"],
        "techs": ["Python", "TensorFlow", "FHIR", "HL7", "PostgreSQL", "AI/ML"],
        "domains": ["EMR", "진단보조", "환자관리", "임상데이터분석"]
    },
    "Logistics": {
        "industries": ["물류", "운송", "배송"],
        "techs": ["Java", "Spring Boot", "PostgreSQL", "Redis", "Kafka", "GPS/GIS"],
        "domains": ["배송관리", "경로최적화", "재고관리", "WMS"]
    },
    "Telecom": {
        "industries": ["통신", "5G", "네트워크"],
        "techs": ["Java", "C++", "Kubernetes", "Kafka", "Prometheus", "5G Core"],
        "domains": ["네트워크관리", "과금시스템", "고객관리", "IoT플랫폼"]
    },
    "Energy": {
        "industries": ["에너지", "전력", "신재생"],
        "techs": ["Python", "IoT", "Time Series DB", "Grafana", "Edge Computing"],
        "domains": ["스마트그리드", "에너지관리", "발전소운영", "ESS"]
    },
    "Education": {
        "industries": ["교육", "에듀테크", "이러닝"],
        "techs": ["React", "Node.js", "MongoDB", "WebRTC", "AI/ML", "LMS"],
        "domains": ["LMS", "화상교육", "학습분석", "콘텐츠관리"]
    }
}

# 프로젝트 상태
project_statuses = ["진행중", "완료", "계획중"]
project_priorities = ["높음", "중간", "낮음"]

def generate_project_details(project_name, base_info=None):
    """프로젝트 상세 정보 생성"""
    
    # 산업 분야 결정
    industry_key = random.choice(list(industry_tech_map.keys()))
    industry_info = industry_tech_map[industry_key]
    
    # 프로젝트 기간
    if base_info and 'period' in base_info:
        period = base_info['period']
        start_date = period.split(' ~ ')[0] + "-01"  # YYYY-MM -> YYYY-MM-01
        end_part = period.split(' ~ ')[1] if ' ~ ' in period else None
        end_date = end_part + "-01" if end_part else None
    else:
        start_year = random.randint(2022, 2024)
        start_month = random.randint(1, 12)
        duration_months = random.randint(6, 24)
        start_date = f"{start_year}-{start_month:02d}-01"
        
        end_datetime = datetime(start_year, start_month, 1) + timedelta(days=duration_months*30)
        end_date = end_datetime.strftime("%Y-%m-%d")
    
    # 상태 결정
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            if end_dt < datetime.now():
                status = "완료"
            else:
                status = "진행중"
        except:
            status = "진행중"
    else:
        status = random.choice(["진행중", "계획중"])
    
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
        'priority': random.choice(project_priorities),
        'required_skills': required_skills,
        'description': f"{client_name}의 {random.choice(industry_info['domains'])} 구축 프로젝트",
        'objectives': [
            f"{random.choice(industry_info['domains'])} 시스템 구축",
            "업무 효율성 향상",
            "디지털 전환 가속화"
        ]
    }

# 기존 프로젝트 데이터 완성
projects = []

for project_id, proj_info in existing_projects.items():
    members = project_members[project_id]
    
    # 첫 번째 멤버의 기간 정보 사용
    base_period = members[0]['period'] if members else None
    
    project = {
        'project_id': project_id,
        'project_name': proj_info['project_name'],
        **generate_project_details(proj_info['project_name'], {'period': base_period}),
        'team_members': members,
        'team_size': len(members)
    }
    
    projects.append(project)

print(f"기존 프로젝트 생성 완료: {len(projects)}개")

# 신규 프로젝트 생성 (50개)
new_project_templates = [
    "AI 기반 고객 서비스 챗봇 구축",
    "클라우드 네이티브 마이크로서비스 전환",
    "빅데이터 분석 플랫폼 구축",
    "모바일 앱 리뉴얼 프로젝트",
    "레거시 시스템 현대화",
    "실시간 데이터 파이프라인 구축",
    "보안 강화 및 컴플라이언스 대응",
    "DevOps 자동화 구축",
    "고객 데이터 플랫폼(CDP) 구축",
    "옴니채널 커머스 플랫폼",
    "IoT 디바이스 관리 플랫폼",
    "블록체인 기반 인증 시스템",
    "AI 추천 엔진 고도화",
    "실시간 모니터링 대시보드",
    "API Gateway 및 통합 플랫폼",
    "데이터 웨어하우스 구축",
    "머신러닝 파이프라인 자동화",
    "고가용성 인프라 구축",
    "서버리스 아키텍처 전환",
    "컨테이너 오케스트레이션 플랫폼"
]

current_max_id = max([int(p['project_id'].split('_')[1]) for p in projects])

for i in range(50):
    project_id = f"P_{current_max_id + i + 1:03d}"
    project_name = random.choice(new_project_templates)
    
    # 랜덤하게 직원 배정 (3-8명)
    team_size = random.randint(3, 8)
    selected_employees = random.sample(employees, team_size)
    
    members = []
    for emp in selected_employees:
        # 프로젝트 기간 생성
        start_year = random.randint(2023, 2024)
        start_month = random.randint(1, 12)
        duration = random.randint(6, 18)
        end_year = start_year + (start_month + duration) // 12
        end_month = (start_month + duration) % 12 or 12
        
        members.append({
            'user_id': emp['user_id'],
            'name': emp['basic_info']['name'],
            'role': emp['basic_info']['role'],
            'period': f"{start_year}-{start_month:02d} ~ {end_year}-{end_month:02d}"
        })
    
    project = {
        'project_id': project_id,
        'project_name': project_name,
        **generate_project_details(project_name),
        'team_members': members,
        'team_size': len(members)
    }
    
    projects.append(project)

print(f"신규 프로젝트 생성 완료: 50개")
print(f"총 프로젝트 수: {len(projects)}개")

# 프로젝트 데이터 저장
with open('test_data/projects_data.json', 'w', encoding='utf-8') as f:
    json.dump(projects, f, ensure_ascii=False, indent=2)

print("\n프로젝트 데이터 저장 완료: test_data/projects_data.json")

# 통계 출력
status_count = defaultdict(int)
industry_count = defaultdict(int)

for proj in projects:
    status_count[proj['status']] += 1
    industry_count[proj['client_industry']] += 1

print("\n=== 프로젝트 통계 ===")
print(f"총 프로젝트: {len(projects)}개")
print("\n상태별:")
for status, count in sorted(status_count.items()):
    print(f"  {status}: {count}개")
print("\n산업별:")
for industry, count in sorted(industry_count.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {industry}: {count}개")
