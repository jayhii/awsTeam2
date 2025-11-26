"""
HR System 유틸리티 함수

기술 스택 정규화 및 기타 공통 유틸리티 함수를 제공합니다.
"""

from typing import Dict, List


# 기술 이름 정규화 매핑 딕셔너리
SKILL_NORMALIZATION_MAP: Dict[str, str] = {
    # Programming Languages
    "java": "Java",
    "python": "Python",
    "javascript": "JavaScript",
    "java script": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "go": "Go",
    "golang": "Go",
    "rust": "Rust",
    "kotlin": "Kotlin",
    "swift": "Swift",
    "ruby": "Ruby",
    "php": "PHP",
    "scala": "Scala",
    
    # Frameworks - Backend
    "spring": "Spring",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "fast api": "FastAPI",
    "express": "Express.js",
    "expressjs": "Express.js",
    "express.js": "Express.js",
    "nestjs": "NestJS",
    "nest.js": "NestJS",
    "laravel": "Laravel",
    "rails": "Ruby on Rails",
    "ruby on rails": "Ruby on Rails",
    
    # Frameworks - Frontend
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "svelte": "Svelte",
    "next": "Next.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "nuxt": "Nuxt.js",
    "nuxtjs": "Nuxt.js",
    "nuxt.js": "Nuxt.js",
    
    # Databases
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "oracle": "Oracle",
    "oracle db": "Oracle",
    "mssql": "Microsoft SQL Server",
    "sql server": "Microsoft SQL Server",
    "dynamodb": "DynamoDB",
    "cassandra": "Cassandra",
    "elasticsearch": "Elasticsearch",
    "elastic search": "Elasticsearch",
    
    # Cloud Platforms
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    
    # DevOps & Tools
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "jenkins": "Jenkins",
    "gitlab": "GitLab",
    "github": "GitHub",
    "git": "Git",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "circleci": "CircleCI",
    "travis": "Travis CI",
    "travis ci": "Travis CI",
    
    # Message Queues
    "kafka": "Kafka",
    "apache kafka": "Kafka",
    "rabbitmq": "RabbitMQ",
    "rabbit mq": "RabbitMQ",
    "activemq": "ActiveMQ",
    "sqs": "AWS SQS",
    "sns": "AWS SNS",
    
    # Testing
    "junit": "JUnit",
    "pytest": "pytest",
    "jest": "Jest",
    "mocha": "Mocha",
    "selenium": "Selenium",
    "cypress": "Cypress",
    
    # Others
    "graphql": "GraphQL",
    "rest": "REST",
    "rest api": "REST API",
    "restful": "REST API",
    "grpc": "gRPC",
    "websocket": "WebSocket",
    "web socket": "WebSocket",
}


def normalize_skill(skill_name: str) -> str:
    """
    기술 이름을 표준 형식으로 정규화합니다.
    
    이 함수는 다양한 형태로 입력된 기술 이름을 일관된 표준 형식으로 변환합니다.
    예: "javascript", "JAVASCRIPT", "Java Script" -> "JavaScript"
    
    Args:
        skill_name: 정규화할 기술 이름
        
    Returns:
        정규화된 기술 이름. 매핑에 없는 경우 원본을 title case로 반환
        
    Examples:
        >>> normalize_skill("javascript")
        'JavaScript'
        >>> normalize_skill("PYTHON")
        'Python'
        >>> normalize_skill("spring boot")
        'Spring Boot'
    """
    if not skill_name:
        return ""
    
    # 공백 제거
    cleaned = skill_name.strip()
    
    # 소문자 변환하여 매핑 딕셔너리에서 찾기
    normalized_key = cleaned.lower()
    
    if normalized_key in SKILL_NORMALIZATION_MAP:
        return SKILL_NORMALIZATION_MAP[normalized_key]
    
    # 매핑에 없는 경우: 이미 정규화된 값인지 확인 (멱등성 보장)
    # 정규화된 값들 중에 일치하는 것이 있으면 그대로 반환
    for normalized_value in SKILL_NORMALIZATION_MAP.values():
        if cleaned == normalized_value:
            return normalized_value
    
    # 완전히 새로운 스킬인 경우에만 title case 적용
    return cleaned.title()


def normalize_skills(skill_names: List[str]) -> List[str]:
    """
    여러 기술 이름을 한 번에 정규화합니다.
    
    Args:
        skill_names: 정규화할 기술 이름 리스트
        
    Returns:
        정규화된 기술 이름 리스트
        
    Examples:
        >>> normalize_skills(["python", "JAVA", "react"])
        ['Python', 'Java', 'React']
    """
    return [normalize_skill(skill) for skill in skill_names]


def get_unique_skills(skill_names: List[str]) -> List[str]:
    """
    기술 이름 리스트에서 중복을 제거하고 정규화합니다.
    
    Args:
        skill_names: 기술 이름 리스트
        
    Returns:
        중복이 제거되고 정규화된 기술 이름 리스트
        
    Examples:
        >>> get_unique_skills(["python", "PYTHON", "java", "Python"])
        ['Python', 'Java']
    """
    normalized = normalize_skills(skill_names)
    # 순서를 유지하면서 중복 제거
    seen = set()
    result = []
    for skill in normalized:
        if skill not in seen:
            seen.add(skill)
            result.append(skill)
    return result
