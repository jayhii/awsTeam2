"""
Repository 유닛 테스트

DynamoDB Repository 클래스의 기본 기능을 테스트합니다.
moto를 사용하여 DynamoDB를 모킹합니다.
"""

import pytest
from moto import mock_aws
import boto3
from common.dynamodb_client import DynamoDBClient, DynamoDBClientError
from common.repositories import EmployeeRepository, ProjectRepository, AffinityRepository
from common.models import (
    Employee, Project, Affinity,
    BasicInfo, Skill, SkillLevel, Education, WorkExperience,
    ProjectPeriod, TechStack, EmployeePair,
    ProjectCollaboration, SharedProject,
    MessengerCommunication, CompanyEvents, PersonalCloseness
)


@pytest.fixture
def aws_credentials(monkeypatch):
    """AWS 자격 증명 모킹"""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-2")


@pytest.fixture
def dynamodb_client(aws_credentials):
    """DynamoDB 클라이언트 픽스처"""
    with mock_aws():
        client = DynamoDBClient(region_name='us-east-2')
        yield client


@pytest.fixture
def employees_table(dynamodb_client):
    """Employees 테이블 생성 픽스처"""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    
    table = dynamodb.create_table(
        TableName='Employees',
        KeySchema=[
            {'AttributeName': 'user_id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'user_id', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    
    table.wait_until_exists()
    yield table


@pytest.fixture
def projects_table(dynamodb_client):
    """Projects 테이블 생성 픽스처"""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    
    table = dynamodb.create_table(
        TableName='Projects',
        KeySchema=[
            {'AttributeName': 'project_id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'project_id', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    
    table.wait_until_exists()
    yield table


@pytest.fixture
def affinity_table(dynamodb_client):
    """EmployeeAffinity 테이블 생성 픽스처"""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    
    table = dynamodb.create_table(
        TableName='EmployeeAffinity',
        KeySchema=[
            {'AttributeName': 'affinity_id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'affinity_id', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    
    table.wait_until_exists()
    yield table


class TestEmployeeRepository:
    """EmployeeRepository 테스트"""

    def test_create_employee(self, dynamodb_client, employees_table):
        """직원 생성 테스트"""
        repo = EmployeeRepository(dynamodb_client)
        
        employee = Employee(
            user_id="U_001",
            basic_info=BasicInfo(
                name="홍길동",
                role="Software Engineer",
                years_of_experience=5,
                email="hong@example.com"
            ),
            skills=[
                Skill(name="Python", level=SkillLevel.EXPERT, years=5)
            ]
        )
        
        result = repo.create(employee)
        
        assert result.user_id == "U_001"
        assert result.basic_info.name == "홍길동"

    def test_get_employee(self, dynamodb_client, employees_table):
        """직원 조회 테스트"""
        repo = EmployeeRepository(dynamodb_client)
        
        # 직원 생성
        employee = Employee(
            user_id="U_002",
            basic_info=BasicInfo(
                name="김철수",
                role="Senior Developer",
                years_of_experience=10,
                email="kim@example.com"
            )
        )
        repo.create(employee)
        
        # 조회
        retrieved = repo.get("U_002")
        
        assert retrieved is not None
        assert retrieved.user_id == "U_002"
        assert retrieved.basic_info.name == "김철수"

    def test_get_nonexistent_employee(self, dynamodb_client, employees_table):
        """존재하지 않는 직원 조회 테스트"""
        repo = EmployeeRepository(dynamodb_client)
        
        result = repo.get("U_999")
        
        assert result is None

    def test_update_employee(self, dynamodb_client, employees_table):
        """직원 업데이트 테스트"""
        repo = EmployeeRepository(dynamodb_client)
        
        # 직원 생성
        employee = Employee(
            user_id="U_003",
            basic_info=BasicInfo(
                name="이영희",
                role="Data Scientist",
                years_of_experience=3,
                email="lee@example.com"
            )
        )
        repo.create(employee)
        
        # 업데이트
        employee.basic_info.years_of_experience = 4
        employee.skills.append(Skill(name="TensorFlow", level=SkillLevel.ADVANCED, years=2))
        repo.update(employee)
        
        # 확인
        updated = repo.get("U_003")
        assert updated.basic_info.years_of_experience == 4
        assert len(updated.skills) == 1

    def test_delete_employee(self, dynamodb_client, employees_table):
        """직원 삭제 테스트"""
        repo = EmployeeRepository(dynamodb_client)
        
        # 직원 생성
        employee = Employee(
            user_id="U_004",
            basic_info=BasicInfo(
                name="박민수",
                role="DevOps Engineer",
                years_of_experience=6,
                email="park@example.com"
            )
        )
        repo.create(employee)
        
        # 삭제
        result = repo.delete("U_004")
        assert result is True
        
        # 확인
        deleted = repo.get("U_004")
        assert deleted is None

    def test_list_all_employees(self, dynamodb_client, employees_table):
        """전체 직원 조회 테스트"""
        repo = EmployeeRepository(dynamodb_client)
        
        # 여러 직원 생성
        for i in range(3):
            employee = Employee(
                user_id=f"U_{i:03d}",
                basic_info=BasicInfo(
                    name=f"직원{i}",
                    role="Developer",
                    years_of_experience=i + 1,
                    email=f"emp{i}@example.com"
                )
            )
            repo.create(employee)
        
        # 전체 조회
        all_employees = repo.list_all()
        
        assert len(all_employees) == 3

    def test_find_by_skills(self, dynamodb_client, employees_table):
        """기술 기반 직원 조회 테스트"""
        repo = EmployeeRepository(dynamodb_client)
        
        # Python 보유 직원
        employee1 = Employee(
            user_id="U_010",
            basic_info=BasicInfo(
                name="Python 개발자",
                role="Backend Developer",
                years_of_experience=5,
                email="python@example.com"
            ),
            skills=[
                Skill(name="Python", level=SkillLevel.EXPERT, years=5),
                Skill(name="Django", level=SkillLevel.ADVANCED, years=3)
            ]
        )
        repo.create(employee1)
        
        # Java 보유 직원
        employee2 = Employee(
            user_id="U_011",
            basic_info=BasicInfo(
                name="Java 개발자",
                role="Backend Developer",
                years_of_experience=7,
                email="java@example.com"
            ),
            skills=[
                Skill(name="Java", level=SkillLevel.EXPERT, years=7),
                Skill(name="Spring Boot", level=SkillLevel.ADVANCED, years=5)
            ]
        )
        repo.create(employee2)
        
        # Python과 Django 모두 보유한 직원 조회
        results = repo.find_by_skills(["Python", "Django"])
        
        assert len(results) == 1
        assert results[0].user_id == "U_010"


class TestProjectRepository:
    """ProjectRepository 테스트"""

    def test_create_project(self, dynamodb_client, projects_table):
        """프로젝트 생성 테스트"""
        repo = ProjectRepository(dynamodb_client)
        
        project = Project(
            project_id="P_001",
            project_name="차세대 시스템",
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
            )
        )
        
        result = repo.create(project)
        
        assert result.project_id == "P_001"
        assert result.project_name == "차세대 시스템"

    def test_get_project(self, dynamodb_client, projects_table):
        """프로젝트 조회 테스트"""
        repo = ProjectRepository(dynamodb_client)
        
        # 프로젝트 생성
        project = Project(
            project_id="P_002",
            project_name="모바일 앱",
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
        repo.create(project)
        
        # 조회
        retrieved = repo.get("P_002")
        
        assert retrieved is not None
        assert retrieved.project_id == "P_002"
        assert retrieved.client_industry == "Retail"

    def test_update_project(self, dynamodb_client, projects_table):
        """프로젝트 업데이트 테스트"""
        repo = ProjectRepository(dynamodb_client)
        
        # 프로젝트 생성
        project = Project(
            project_id="P_003",
            project_name="AI 챗봇",
            client_industry="Healthcare",
            period=ProjectPeriod(
                start="2024-03-01",
                end="2024-09-30",
                duration_months=7
            ),
            tech_stack=TechStack(
                backend=["Python"],
                frontend=["Vue.js"],
                data=["Redis"],
                infra=["Azure"]
            )
        )
        repo.create(project)
        
        # 업데이트
        project.budget_scale = "5억 원"
        repo.update(project)
        
        # 확인
        updated = repo.get("P_003")
        assert updated.budget_scale == "5억 원"

    def test_delete_project(self, dynamodb_client, projects_table):
        """프로젝트 삭제 테스트"""
        repo = ProjectRepository(dynamodb_client)
        
        # 프로젝트 생성
        project = Project(
            project_id="P_004",
            project_name="테스트 프로젝트",
            client_industry="IT",
            period=ProjectPeriod(
                start="2024-01-01",
                end="2024-06-30",
                duration_months=6
            ),
            tech_stack=TechStack(
                backend=["Go"],
                frontend=["Angular"],
                data=["MySQL"],
                infra=["AWS"]
            )
        )
        repo.create(project)
        
        # 삭제
        result = repo.delete("P_004")
        assert result is True
        
        # 확인
        deleted = repo.get("P_004")
        assert deleted is None

    def test_list_all_projects(self, dynamodb_client, projects_table):
        """전체 프로젝트 조회 테스트"""
        repo = ProjectRepository(dynamodb_client)
        
        # 여러 프로젝트 생성
        for i in range(3):
            project = Project(
                project_id=f"P_{i:03d}",
                project_name=f"프로젝트{i}",
                client_industry="IT",
                period=ProjectPeriod(
                    start="2024-01-01",
                    end="2024-12-31",
                    duration_months=12
                ),
                tech_stack=TechStack(
                    backend=["Python"],
                    frontend=["React"],
                    data=["PostgreSQL"],
                    infra=["AWS"]
                )
            )
            repo.create(project)
        
        # 전체 조회
        all_projects = repo.list_all()
        
        assert len(all_projects) == 3


class TestAffinityRepository:
    """AffinityRepository 테스트"""

    def test_create_affinity(self, dynamodb_client, affinity_table):
        """친밀도 생성 테스트"""
        repo = AffinityRepository(dynamodb_client)
        
        affinity = Affinity(
            affinity_id="AFF_001",
            employee_pair=EmployeePair(
                employee_1="U_001",
                employee_2="U_002"
            ),
            project_collaboration=ProjectCollaboration(
                shared_projects=[],
                collaboration_score=70.0
            ),
            messenger_communication=MessengerCommunication(
                total_messages_exchanged=100,
                avg_response_time_minutes=15.0,
                communication_score=65.0
            ),
            company_events=CompanyEvents(
                shared_events=["EVT_001"],
                social_score=60.0
            ),
            personal_closeness=PersonalCloseness(
                payday_contact_frequency=2,
                vacation_day_contact_frequency=1,
                personal_score=55.0
            ),
            overall_affinity_score=62.5
        )
        
        result = repo.create(affinity)
        
        assert result.affinity_id == "AFF_001"
        assert result.overall_affinity_score == 62.5

    def test_get_affinity(self, dynamodb_client, affinity_table):
        """친밀도 조회 테스트"""
        repo = AffinityRepository(dynamodb_client)
        
        # 친밀도 생성
        affinity = Affinity(
            affinity_id="AFF_002",
            employee_pair=EmployeePair(
                employee_1="U_003",
                employee_2="U_004"
            ),
            project_collaboration=ProjectCollaboration(
                shared_projects=[],
                collaboration_score=80.0
            ),
            messenger_communication=MessengerCommunication(
                total_messages_exchanged=200,
                avg_response_time_minutes=10.0,
                communication_score=75.0
            ),
            company_events=CompanyEvents(
                shared_events=["EVT_002", "EVT_003"],
                social_score=70.0
            ),
            personal_closeness=PersonalCloseness(
                payday_contact_frequency=3,
                vacation_day_contact_frequency=2,
                personal_score=65.0
            ),
            overall_affinity_score=72.5
        )
        repo.create(affinity)
        
        # 조회
        retrieved = repo.get("AFF_002")
        
        assert retrieved is not None
        assert retrieved.affinity_id == "AFF_002"
        assert retrieved.overall_affinity_score == 72.5

    def test_update_affinity(self, dynamodb_client, affinity_table):
        """친밀도 업데이트 테스트"""
        repo = AffinityRepository(dynamodb_client)
        
        # 친밀도 생성
        affinity = Affinity(
            affinity_id="AFF_003",
            employee_pair=EmployeePair(
                employee_1="U_005",
                employee_2="U_006"
            ),
            project_collaboration=ProjectCollaboration(
                shared_projects=[],
                collaboration_score=60.0
            ),
            messenger_communication=MessengerCommunication(
                total_messages_exchanged=50,
                avg_response_time_minutes=20.0,
                communication_score=55.0
            ),
            company_events=CompanyEvents(
                shared_events=[],
                social_score=50.0
            ),
            personal_closeness=PersonalCloseness(
                payday_contact_frequency=1,
                vacation_day_contact_frequency=1,
                personal_score=45.0
            ),
            overall_affinity_score=52.5
        )
        repo.create(affinity)
        
        # 업데이트
        affinity.overall_affinity_score = 60.0
        repo.update(affinity)
        
        # 확인
        updated = repo.get("AFF_003")
        assert updated.overall_affinity_score == 60.0

    def test_delete_affinity(self, dynamodb_client, affinity_table):
        """친밀도 삭제 테스트"""
        repo = AffinityRepository(dynamodb_client)
        
        # 친밀도 생성
        affinity = Affinity(
            affinity_id="AFF_004",
            employee_pair=EmployeePair(
                employee_1="U_007",
                employee_2="U_008"
            ),
            project_collaboration=ProjectCollaboration(
                shared_projects=[],
                collaboration_score=50.0
            ),
            messenger_communication=MessengerCommunication(
                total_messages_exchanged=30,
                avg_response_time_minutes=25.0,
                communication_score=45.0
            ),
            company_events=CompanyEvents(
                shared_events=[],
                social_score=40.0
            ),
            personal_closeness=PersonalCloseness(
                payday_contact_frequency=0,
                vacation_day_contact_frequency=0,
                personal_score=35.0
            ),
            overall_affinity_score=42.5
        )
        repo.create(affinity)
        
        # 삭제
        result = repo.delete("AFF_004")
        assert result is True
        
        # 확인
        deleted = repo.get("AFF_004")
        assert deleted is None

    def test_list_all_affinities(self, dynamodb_client, affinity_table):
        """전체 친밀도 조회 테스트"""
        repo = AffinityRepository(dynamodb_client)
        
        # 여러 친밀도 생성
        for i in range(3):
            affinity = Affinity(
                affinity_id=f"AFF_{i:03d}",
                employee_pair=EmployeePair(
                    employee_1=f"U_{i:03d}",
                    employee_2=f"U_{i+1:03d}"
                ),
                project_collaboration=ProjectCollaboration(
                    shared_projects=[],
                    collaboration_score=50.0
                ),
                messenger_communication=MessengerCommunication(
                    total_messages_exchanged=50,
                    avg_response_time_minutes=15.0,
                    communication_score=50.0
                ),
                company_events=CompanyEvents(
                    shared_events=[],
                    social_score=50.0
                ),
                personal_closeness=PersonalCloseness(
                    payday_contact_frequency=1,
                    vacation_day_contact_frequency=1,
                    personal_score=50.0
                ),
                overall_affinity_score=50.0
            )
            repo.create(affinity)
        
        # 전체 조회
        all_affinities = repo.list_all()
        
        assert len(all_affinities) == 3
