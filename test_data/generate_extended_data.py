import json
import random
from datetime import datetime, timedelta

# 한국 이름 생성용 데이터
last_names = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임", "한", "오", "서", "신", "권", "황", "안", "송", "류", "홍"]
first_names_male = ["민준", "서준", "예준", "도윤", "시우", "주원", "하준", "지호", "준서", "건우", "우진", "현우", "선우", "연우", "유준", "정우", "승우", "승현", "시윤", "준혁"]
first_names_female = ["서연", "서윤", "지우", "서현", "민서", "하은", "하윤", "윤서", "지유", "채원", "지민", "수아", "소율", "예은", "예린", "다은", "은서", "가은", "나은", "채은"]

roles = [
    "Senior System Architect", "System Architect", "Backend Developer", "Frontend Developer",
    "Full Stack Developer", "DevOps Engineer", "AI/ML Engineer", "Data Engineer",
    "Data Scientist", "Security Engineer", "QA Engineer", "Mobile Developer",
    "Cloud Architect", "Database Administrator", "UI/UX Designer", "Product Manager",
    "Scrum Master", "Technical Lead", "Software Engineer", "Solutions Architect"
]

skills_pool = {
    "Backend": [
        {"name": "Java", "categories": ["Backend", "Enterprise"]},
        {"name": "Spring Framework", "categories": ["Backend", "Enterprise"]},
        {"name": "Python", "categories": ["Backend", "AI", "Data"]},
        {"name": "Node.js", "categories": ["Backend", "JavaScript"]},
        {"name": "Go", "categories": ["Backend", "Cloud"]},
        {"name": "C#", "categories": ["Backend", "Enterprise"]},
        {"name": ".NET Core", "categories": ["Backend", "Enterprise"]},
        {"name": "Django", "categories": ["Backend", "Python"]},
        {"name": "FastAPI", "categories": ["Backend", "Python"]},
        {"name": "Express.js", "categories": ["Backend", "JavaScript"]}
    ],
    "Frontend": [
        {"name": "React", "categories": ["Frontend", "JavaScript"]},
        {"name": "Vue.js", "categories": ["Frontend", "JavaScript"]},
        {"name": "Angular", "categories": ["Frontend", "JavaScript"]},
        {"name": "Next.js", "categories": ["Frontend", "JavaScript"]},
        {"name": "TypeScript", "categories": ["Frontend", "JavaScript"]},
        {"name": "JavaScript", "categories": ["Frontend"]},
        {"name": "HTML/CSS", "categories": ["Frontend"]},
        {"name": "Tailwind CSS", "categories": ["Frontend"]},
        {"name": "Redux", "categories": ["Frontend", "JavaScript"]},
        {"name": "Webpack", "categories": ["Frontend", "Build"]}
    ],
    "Cloud": [
        {"name": "AWS", "categories": ["Cloud", "DevOps"]},
        {"name": "Azure", "categories": ["Cloud", "DevOps"]},
        {"name": "GCP", "categories": ["Cloud", "DevOps"]},
        {"name": "Kubernetes", "categories": ["Cloud", "DevOps"]},
        {"name": "Docker", "categories": ["Cloud", "DevOps"]},
        {"name": "Terraform", "categories": ["Cloud", "IaC"]},
        {"name": "CloudFormation", "categories": ["Cloud", "IaC"]},
        {"name": "Ansible", "categories": ["DevOps", "IaC"]},
        {"name": "Jenkins", "categories": ["DevOps", "CI/CD"]},
        {"name": "GitLab CI", "categories": ["DevOps", "CI/CD"]}
    ],
    "Data": [
        {"name": "Apache Spark", "categories": ["Data", "BigData"]},
        {"name": "Apache Kafka", "categories": ["Data", "Streaming"]},
        {"name": "Hadoop", "categories": ["Data", "BigData"]},
        {"name": "Elasticsearch", "categories": ["Data", "Search"]},
        {"name": "MongoDB", "categories": ["Database", "NoSQL"]},
        {"name": "PostgreSQL", "categories": ["Database", "SQL"]},
        {"name": "MySQL", "categories": ["Database", "SQL"]},
        {"name": "Oracle", "categories": ["Database", "SQL"]},
        {"name": "Redis", "categories": ["Database", "Cache"]},
        {"name": "Cassandra", "categories": ["Database", "NoSQL"]}
    ],
    "AI": [
        {"name": "TensorFlow", "categories": ["AI", "ML"]},
        {"name": "PyTorch", "categories": ["AI", "ML"]},
        {"name": "Scikit-learn", "categories": ["AI", "ML"]},
        {"name": "Keras", "categories": ["AI", "ML"]},
        {"name": "Computer Vision", "categories": ["AI", "CV"]},
        {"name": "NLP", "categories": ["AI", "NLP"]},
        {"name": "Deep Learning", "categories": ["AI", "ML"]},
        {"name": "MLOps", "categories": ["AI", "DevOps"]},
        {"name": "Pandas", "categories": ["Data", "Python"]},
        {"name": "NumPy", "categories": ["Data", "Python"]}
    ]
}

universities = [
    "Seoul National University", "KAIST", "POSTECH", "Yonsei University", "Korea University",
    "Hanyang University", "Sungkyunkwan University", "Ewha Womans University",
    "Sogang University", "Chung-Ang University", "Kyung Hee University"
]

degrees = ["BS", "MS", "PhD"]
majors = [
    "Computer Science", "Computer Engineering", "Software Engineering", "Information Systems",
    "Artificial Intelligence", "Data Science", "Statistics", "Mathematics",
    "Electrical Engineering", "Industrial Engineering", "Design & Technology"
]

certifications_pool = [
    "AWS Solutions Architect Professional", "AWS Solutions Architect Associate",
    "AWS DevOps Engineer Professional", "AWS Certified Data Analytics",
    "CKA", "CKAD", "CKS", "Google Cloud Professional",
    "Azure Solutions Architect", "PMP", "Scrum Master",
    "TensorFlow Developer Certificate", "OCP", "OCPJP"
]

project_templates = [
    {
        "name": "차세대 금융 코어 뱅킹 시스템 구축",
        "industry": "Finance",
        "roles": ["System Architect", "Backend Developer", "Data Engineer"]
    },
    {
        "name": "전기차 배터리 생산 공장 MES 고도화",
        "industry": "Manufacturing",
        "roles": ["AI Engineer", "Backend Developer", "DevOps Engineer"]
    },
    {
        "name": "대형 유통사 온/오프라인 통합 옴니채널 커머스 플랫폼",
        "industry": "Retail",
        "roles": ["Frontend Developer", "Backend Developer", "DevOps Engineer"]
    },
    {
        "name": "이커머스 플랫폼 MSA 전환",
        "industry": "E-commerce",
        "roles": ["System Architect", "Backend Developer", "DevOps Engineer"]
    },
    {
        "name": "증권사 실시간 거래 시스템",
        "industry": "Finance",
        "roles": ["System Architect", "Backend Developer", "Data Engineer"]
    },
    {
        "name": "스마트 팩토리 IoT 플랫폼",
        "industry": "Manufacturing",
        "roles": ["Backend Developer", "Data Engineer", "DevOps Engineer"]
    },
    {
        "name": "헬스케어 데이터 분석 플랫폼",
        "industry": "Healthcare",
        "roles": ["Data Scientist", "AI Engineer", "Backend Developer"]
    },
    {
        "name": "모바일 뱅킹 앱 리뉴얼",
        "industry": "Finance",
        "roles": ["Mobile Developer", "Frontend Developer", "Backend Developer"]
    },
    {
        "name": "클라우드 마이그레이션 프로젝트",
        "industry": "Enterprise",
        "roles": ["Cloud Architect", "DevOps Engineer", "Backend Developer"]
    },
    {
        "name": "AI 기반 고객 추천 시스템",
        "industry": "E-commerce",
        "roles": ["AI Engineer", "Data Scientist", "Backend Developer"]
    }
]

def generate_name(gender="random"):
    last = random.choice(last_names)
    if gender == "random":
        gender = random.choice(["male", "female"])
    first = random.choice(first_names_male if gender == "male" else first_names_female)
    return last + first

def generate_email(name, user_id):
    domains = ["tech-resume.com", "dev-career.com", "tech-ops.com", "ai-lab.com", 
               "data-eng.com", "architect.com", "systems.com", "cloud-tech.com"]
    # 이름을 영문으로 변환 (간단한 방식)
    email_prefix = f"user{user_id.split('_')[1]}"
    return f"{email_prefix}@{random.choice(domains)}"

def select_skills_for_role(role, years_exp):
    selected_skills = []
    
    # 역할에 따라 스킬 카테고리 선택
    if "Architect" in role or "Lead" in role:
        categories = ["Backend", "Cloud", "Data"]
        num_skills = random.randint(7, 10)
    elif "Backend" in role:
        categories = ["Backend", "Data", "Cloud"]
        num_skills = random.randint(5, 8)
    elif "Frontend" in role or "UI/UX" in role:
        categories = ["Frontend"]
        num_skills = random.randint(5, 7)
    elif "DevOps" in role or "Cloud" in role:
        categories = ["Cloud", "Backend"]
        num_skills = random.randint(6, 9)
    elif "AI" in role or "ML" in role or "Data Scientist" in role:
        categories = ["AI", "Data"]
        num_skills = random.randint(6, 9)
    elif "Data Engineer" in role:
        categories = ["Data", "Cloud"]
        num_skills = random.randint(6, 8)
    elif "Mobile" in role:
        categories = ["Frontend"]
        num_skills = random.randint(5, 7)
    else:
        categories = ["Backend", "Frontend"]
        num_skills = random.randint(5, 7)
    
    # 스킬 선택
    available_skills = []
    for cat in categories:
        if cat in skills_pool:
            available_skills.extend(skills_pool[cat])
    
    selected = random.sample(available_skills, min(num_skills, len(available_skills)))
    
    for skill in selected:
        skill_years = min(random.randint(1, years_exp), years_exp)
        levels = ["Beginner", "Intermediate", "Advanced", "Expert"]
        
        if skill_years >= 7:
            level = random.choice(["Advanced", "Expert"])
        elif skill_years >= 4:
            level = random.choice(["Intermediate", "Advanced"])
        elif skill_years >= 2:
            level = random.choice(["Beginner", "Intermediate"])
        else:
            level = "Beginner"
        
        selected_skills.append({
            "name": skill["name"],
            "level": level,
            "years": skill_years
        })
    
    return selected_skills

def generate_self_introduction(role, years_exp):
    intros = [
        f"{years_exp}년 경력의 {role}입니다. 다양한 프로젝트 경험을 통해 실무 역량을 쌓아왔습니다.",
        f"기술적 전문성과 팀워크를 중시하는 {role}입니다. {years_exp}년간 다양한 도메인에서 프로젝트를 수행했습니다.",
        f"문제 해결 능력과 커뮤니케이션 스킬을 갖춘 {role}입니다. {years_exp}년의 실무 경험이 있습니다.",
        f"최신 기술 트렌드를 빠르게 습득하고 적용하는 {role}입니다. {years_exp}년간 업계에서 활동해왔습니다.",
        f"효율적인 시스템 설계와 구현에 강점이 있는 {role}입니다. {years_exp}년의 개발 경력을 보유하고 있습니다."
    ]
    return random.choice(intros)

def generate_work_experience(user_id, role, years_exp):
    num_projects = min(random.randint(1, 3), max(1, years_exp // 2))
    experiences = []
    
    for i in range(num_projects):
        project = random.choice(project_templates)
        project_role = random.choice(project["roles"]) if role not in project["roles"] else role
        
        # 프로젝트 기간 생성
        end_year = 2024 - i * 2
        start_year = end_year - random.randint(1, 2)
        start_month = random.randint(1, 12)
        end_month = random.randint(1, 12)
        
        experiences.append({
            "project_id": f"P_{random.randint(1, 100):03d}",
            "project_name": project["name"],
            "role": project_role,
            "period": f"{start_year}-{start_month:02d} ~ {end_year}-{end_month:02d}",
            "main_tasks": [
                "시스템 설계 및 구현",
                "성능 최적화 및 튜닝",
                "팀 협업 및 코드 리뷰"
            ],
            "performance_result": "프로젝트 성공적 완료 및 고객 만족도 향상"
        })
    
    return experiences

def generate_employee(user_id):
    gender = random.choice(["male", "female"])
    name = generate_name(gender)
    role = random.choice(roles)
    years_exp = random.randint(2, 15)
    
    employee = {
        "user_id": user_id,
        "basic_info": {
            "name": name,
            "role": role,
            "years_of_experience": years_exp,
            "email": generate_email(name, user_id)
        },
        "self_introduction": generate_self_introduction(role, years_exp),
        "skills": select_skills_for_role(role, years_exp),
        "work_experience": generate_work_experience(user_id, role, years_exp),
        "education": {
            "degree": f"{random.choice(majors)}, {random.choice(degrees)}",
            "university": random.choice(universities)
        },
        "certifications": random.sample(certifications_pool, random.randint(0, 3))
    }
    
    return employee

def generate_messenger_logs(employees, num_logs=2000):
    logs = []
    user_ids = [emp["user_id"] for emp in employees]
    
    # 급여일 및 휴가 정보
    paydays = ["2024-11-25", "2024-10-25", "2024-09-25"]
    vacation_days = {}
    for _ in range(50):
        user = random.choice(user_ids)
        vacation_day = datetime(2024, random.randint(1, 11), random.randint(1, 28))
        vacation_days[vacation_day.strftime("%Y-%m-%d")] = user
    
    # 메신저 로그 생성
    for i in range(num_logs):
        sender = random.choice(user_ids)
        receiver = random.choice([uid for uid in user_ids if uid != sender])
        
        # 타임스탬프 생성 (최근 1년)
        days_ago = random.randint(0, 365)
        timestamp = datetime.now() - timedelta(days=days_ago, 
                                               hours=random.randint(0, 23),
                                               minutes=random.randint(0, 59))
        
        log = {
            "log_id": f"MSG_{i+1:05d}",
            "sender_id": sender,
            "receiver_id": receiver,
            "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "message_content": "[ANONYMIZED]",
            "response_time_minutes": random.randint(1, 180),
            "conversation_thread_id": f"THREAD_{random.randint(1, 500):04d}"
        }
        
        # 급여일 체크
        date_str = timestamp.strftime("%Y-%m-%d")
        if date_str in paydays:
            log["is_payday"] = True
        
        # 휴가일 체크
        if date_str in vacation_days:
            log["is_vacation_day"] = True
            log["vacation_owner"] = vacation_days[date_str]
        
        logs.append(log)
    
    # 타임스탬프 기준 정렬
    logs.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return logs

# 기존 직원 데이터 로드
with open('test_data/employees_extended.json', 'r', encoding='utf-8') as f:
    existing_employees = json.load(f)

print(f"기존 직원 수: {len(existing_employees)}")

# 새로운 직원 생성 (300명까지)
target_count = 300
new_employees = existing_employees.copy()
current_max_id = max([int(emp["user_id"].split("_")[1]) for emp in existing_employees])

for i in range(len(existing_employees), target_count):
    user_id = f"U_{current_max_id + i - len(existing_employees) + 1:03d}"
    new_employee = generate_employee(user_id)
    new_employees.append(new_employee)
    
    if (i + 1) % 50 == 0:
        print(f"생성 중... {i + 1}/{target_count}")

print(f"총 직원 수: {len(new_employees)}")

# 직원 데이터 저장
with open('test_data/employees_extended.json', 'w', encoding='utf-8') as f:
    json.dump(new_employees, f, ensure_ascii=False, indent=2)

print("직원 데이터 저장 완료!")

# 메신저 로그 생성
print("메신저 로그 생성 중...")
messenger_logs = generate_messenger_logs(new_employees, num_logs=2000)

with open('test_data/messenger_logs_anonymized.json', 'w', encoding='utf-8') as f:
    json.dump(messenger_logs, f, ensure_ascii=False, indent=2)

print(f"메신저 로그 {len(messenger_logs)}개 생성 완료!")
print("\n생성 완료!")
print(f"- 직원 데이터: {len(new_employees)}명")
print(f"- 메신저 로그: {len(messenger_logs)}개")
