"""
데이터 모델 유닛 테스트

Employee, Project, Affinity 모델의 기본 기능을 테스트합니다.
"""

import pytest
from common.models import (
    Employee, Project, Affinity,
    BasicInfo, Skill, SkillLevel, Education, WorkExperience,
    ProjectPeriod, TechStack, EmployeePair,
    ProjectCollaboration, SharedProject,
    MessengerCommunication, CompanyEvents, PersonalCloseness
)


class TestEmployeeModel:
    """Employee 모델 테스트"""

    def test_create_employee_with_minimal_data(self):
        """최소 데이터로 Employee 생성 테스트"""
        employee = Employee(
            user_id="U_001",
            basic_info=BasicInfo(
                name="홍길동",
                role="Software Engineer",
                years_of_experience=5,
                email="hong@example.com"
            )
        )
        
        assert employee.user_id == "U_001"
        assert employee.basic_info.name == "홍길동"
        assert employee.skills == []
        assert employee.work_experience == []

    def test_create_employee_with_full_data(self):
        """전체 데이터로 Employee 생성 테스트"""
        employee = Employee(
            user_id="U_002",
            basic_info=BasicInfo(
                name="김철수",
                role="Senior Developer",
                years_of_experience=10,
                email="kim@example.com"
            ),
            self_introduction="백엔드 개발 전문가",
            skills=[
                Skill(name="Python", level=SkillLevel.EXPERT, years=10),
                Skill(name="Java", level=SkillLevel.ADVANCED, years=7)
            ],
            work_experience=[
                WorkExperience(
                    project_id="P_001",
                    project_name="테스트 프로젝트",
                    role="Lead Developer",
                    period="2023-01 ~ 2024-01",
                    main_tasks=["설계", "개발"],
                    performance_result="성공적 완료"
                )
            ],
            education=Education(
                degree="Computer Science, BS",
                university="서울대학교"
            ),
            certifications=["AWS SAA", "PMP"]
        )
        
        assert employee.user_id == "U_002"
        assert len(employee.skills) == 2
        assert employee.skills[0].name == "Python"
        assert employee.skills[0].level == SkillLevel.EXPERT
        assert len(employee.work_experience) == 1
        assert len(employee.certifications) == 2

    def test_employee_to_dynamodb(self):
        """Employee를 DynamoDB 형식으로 변환 테스트"""
        employee = Employee(
            user_id="U_003",
            basic_info=BasicInfo(
                name="이영희",
                role="Data Scientist",
                years_of_experience=3,
                email="lee@example.com"
            ),
            skills=[
                Skill(name="Python", level=SkillLevel.ADVANCED, years=3)
            ]
        )
        
        dynamodb_data = employee.to_dynamodb()
        
        assert isinstance(dynamodb_data, dict)
        assert dynamodb_data["user_id"] == "U_003"
        assert "basic_info" in dynamodb_data
        assert "skills" in dynamodb_data

    def test_employee_from_dynamodb(self):
        """DynamoDB 데이터에서 Employee 생성 테스트"""
        dynamodb_data = {
            "user_id": "U_004",
            "basic_info": {
                "name": "박민수",
                "role": "DevOps Engineer",
                "years_of_experience": 6,
                "email": "park@example.com"
            },
            "skills": [
                {
                    "name": "Docker",
                    "level": "Expert",
                    "years": 5
                }
            ]
        }
        
        employee = Employee.from_dynamodb(dynamodb_data)
        
        assert employee.user_id == "U_004"
        assert employee.basic_info.name == "박민수"
        assert len(employee.skills) == 1
        assert employee.skills[0].name == "Docker"


class TestProjectModel:
    """Project 모델 테스트"""

    def test_create_project(self):
        """Project 생성 테스트"""
        project = Project(
            project_id="P_001",
            project_name="차세대 시스템 구축",
            client_industry="Finance",
            period=ProjectPeriod(
                start="2024-01-01",
                end="2024-12-31",
                duration_months=12
            ),
            tech_stack=TechStack(
                backend=["Java", "Spring Boot"],
                frontend=["React"],
                data=["PostgreSQL"],
                infra=["AWS"]
            ),
            requirements=["고가용성", "보안"]
        )
        
        assert project.project_id == "P_001"
        assert project.period.duration_months == 12
        assert len(project.tech_stack.backend) == 2
        assert len(project.requirements) == 2

    def test_project_to_dynamodb(self):
        """Project를 DynamoDB 형식으로 변환 테스트"""
        project = Project(
            project_id="P_002",
            project_name="모바일 앱 개발",
            client_industry="Retail",
            period=ProjectPeriod(
                start="2024-06-01",
                end="2024-12-31",
                duration_months=7
            ),
            tech_stack=TechStack(
                backend=["Node.js"],
                frontend=["React Native"],
                data=["MongoDB"],
                infra=["GCP"]
            )
        )
        
        dynamodb_data = project.to_dynamodb()
        
        assert isinstance(dynamodb_data, dict)
        assert dynamodb_data["project_id"] == "P_002"
        assert "period" in dynamodb_data
        assert "tech_stack" in dynamodb_data

    def test_project_from_dynamodb(self):
        """DynamoDB 데이터에서 Project 생성 테스트"""
        dynamodb_data = {
            "project_id": "P_003",
            "project_name": "AI 챗봇 개발",
            "client_industry": "Healthcare",
            "period": {
                "start": "2024-03-01",
                "end": "2024-09-30",
                "duration_months": 7
            },
            "tech_stack": {
                "backend": ["Python", "FastAPI"],
                "frontend": ["Vue.js"],
                "data": ["Redis"],
                "infra": ["Azure"]
            }
        }
        
        project = Project.from_dynamodb(dynamodb_data)
        
        assert project.project_id == "P_003"
        assert project.client_industry == "Healthcare"
        assert project.period.duration_months == 7


class TestAffinityModel:
    """Affinity 모델 테스트"""

    def test_create_affinity(self):
        """Affinity 생성 테스트"""
        affinity = Affinity(
            affinity_id="AFF_001",
            employee_pair=EmployeePair(
                employee_1="U_001",
                employee_2="U_002"
            ),
            project_collaboration=ProjectCollaboration(
                shared_projects=[
                    SharedProject(
                        project_id="P_001",
                        overlap_period_months=6,
                        same_team=True
                    )
                ],
                collaboration_score=80.0
            ),
            messenger_communication=MessengerCommunication(
                total_messages_exchanged=150,
                avg_response_time_minutes=10.5,
                communication_score=75.0
            ),
            company_events=CompanyEvents(
                shared_events=["EVT_001", "EVT_002"],
                social_score=70.0
            ),
            personal_closeness=PersonalCloseness(
                payday_contact_frequency=2,
                vacation_day_contact_frequency=3,
                personal_score=65.0
            ),
            overall_affinity_score=72.5
        )
        
        assert affinity.affinity_id == "AFF_001"
        assert affinity.employee_pair.employee_1 == "U_001"
        assert affinity.overall_affinity_score == 72.5
        assert len(affinity.project_collaboration.shared_projects) == 1
        assert affinity.messenger_communication.total_messages_exchanged == 150

    def test_affinity_score_validation(self):
        """Affinity 점수 유효성 검사 테스트"""
        # 유효한 점수 (0-100)
        affinity = Affinity(
            affinity_id="AFF_002",
            employee_pair=EmployeePair(employee_1="U_003", employee_2="U_004"),
            project_collaboration=ProjectCollaboration(
                shared_projects=[],
                collaboration_score=50.0
            ),
            messenger_communication=MessengerCommunication(
                total_messages_exchanged=0,
                avg_response_time_minutes=0.0,
                communication_score=50.0
            ),
            company_events=CompanyEvents(
                shared_events=[],
                social_score=50.0
            ),
            personal_closeness=PersonalCloseness(
                payday_contact_frequency=0,
                vacation_day_contact_frequency=0,
                personal_score=50.0
            ),
            overall_affinity_score=50.0
        )
        
        assert affinity.overall_affinity_score == 50.0

    def test_affinity_to_dynamodb(self):
        """Affinity를 DynamoDB 형식으로 변환 테스트"""
        affinity = Affinity(
            affinity_id="AFF_003",
            employee_pair=EmployeePair(employee_1="U_005", employee_2="U_006"),
            project_collaboration=ProjectCollaboration(
                shared_projects=[],
                collaboration_score=60.0
            ),
            messenger_communication=MessengerCommunication(
                total_messages_exchanged=50,
                avg_response_time_minutes=15.0,
                communication_score=55.0
            ),
            company_events=CompanyEvents(
                shared_events=["EVT_003"],
                social_score=50.0
            ),
            personal_closeness=PersonalCloseness(
                payday_contact_frequency=1,
                vacation_day_contact_frequency=1,
                personal_score=45.0
            ),
            overall_affinity_score=52.5
        )
        
        dynamodb_data = affinity.to_dynamodb()
        
        assert isinstance(dynamodb_data, dict)
        assert dynamodb_data["affinity_id"] == "AFF_003"
        assert "employee_pair" in dynamodb_data
        assert "overall_affinity_score" in dynamodb_data


class TestSkillLevel:
    """SkillLevel Enum 테스트"""

    def test_skill_levels(self):
        """모든 스킬 레벨 테스트"""
        assert SkillLevel.BEGINNER == "Beginner"
        assert SkillLevel.INTERMEDIATE == "Intermediate"
        assert SkillLevel.ADVANCED == "Advanced"
        assert SkillLevel.EXPERT == "Expert"

    def test_skill_with_enum(self):
        """Skill 모델에서 Enum 사용 테스트"""
        skill = Skill(
            name="JavaScript",
            level=SkillLevel.INTERMEDIATE,
            years=3
        )
        
        # use_enum_values=True 설정으로 인해 문자열로 저장됨
        assert skill.level == "Intermediate"
