"""
Property-Based Test for Project Data Round Trip

**Feature: hr-resource-optimization, Property 5: Project Data Round Trip**
**Validates: Requirements 2.1**

Property: *For any* project data, storing it to DynamoDB and retrieving it 
          should return equivalent data

이 테스트는 프로젝트 데이터가 DynamoDB에 저장되고 조회될 때 
데이터 무결성이 유지되는지 검증합니다.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from moto import mock_aws
import boto3
from common.dynamodb_client import DynamoDBClient
from common.repositories import ProjectRepository
from common.models import Project, ProjectPeriod, TechStack


# Hypothesis 전략 정의

@st.composite
def tech_stack_strategy(draw):
    """TechStack 객체 생성 전략"""
    return TechStack(
        backend=draw(st.lists(
            st.text(min_size=1, max_size=20),
            min_size=0,
            max_size=5
        )),
        frontend=draw(st.lists(
            st.text(min_size=1, max_size=20),
            min_size=0,
            max_size=5
        )),
        data=draw(st.lists(
            st.text(min_size=1, max_size=20),
            min_size=0,
            max_size=5
        )),
        infra=draw(st.lists(
            st.text(min_size=1, max_size=20),
            min_size=0,
            max_size=5
        ))
    )


@st.composite
def project_period_strategy(draw):
    """ProjectPeriod 객체 생성 전략"""
    return ProjectPeriod(
        start=draw(st.text(min_size=10, max_size=10, alphabet='0123456789-')),
        end=draw(st.text(min_size=10, max_size=10, alphabet='0123456789-')),
        duration_months=draw(st.integers(min_value=1, max_value=60))
    )


@st.composite
def project_strategy(draw):
    """Project 객체 생성 전략"""
    project_id = draw(st.text(
        min_size=3,
        max_size=20,
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='_-'
        )
    ))
    
    return Project(
        project_id=project_id,
        project_name=draw(st.text(min_size=1, max_size=100)),
        client_industry=draw(st.text(min_size=1, max_size=50)),
        period=draw(project_period_strategy()),
        budget_scale=draw(st.one_of(st.none(), st.text(min_size=1, max_size=50))),
        description=draw(st.one_of(st.none(), st.text(min_size=0, max_size=500))),
        tech_stack=draw(tech_stack_strategy()),
        requirements=draw(st.lists(
            st.text(min_size=1, max_size=100),
            min_size=0,
            max_size=10
        )),
        team_composition=draw(st.one_of(
            st.none(),
            st.dictionaries(
                st.text(min_size=1, max_size=20),
                st.integers(min_value=1, max_value=10),
                min_size=0,
                max_size=5
            )
        ))
    )


@pytest.fixture
def dynamodb_client():
    """DynamoDB 클라이언트 픽스처 (moto 사용)"""
    with mock_aws():
        # DynamoDB 리소스 생성
        dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
        
        # Projects 테이블 생성
        table = dynamodb.create_table(
            TableName='Projects',
            KeySchema=[
                {'AttributeName': 'project_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'project_id', 'AttributeType': 'S'},
                {'AttributeName': 'industry', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'IndustryIndex',
                    'KeySchema': [
                        {'AttributeName': 'industry', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            BillingMode='PROVISIONED',
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        # 테이블이 활성화될 때까지 대기
        table.meta.client.get_waiter('table_exists').wait(TableName='Projects')
        
        # DynamoDBClient 생성
        client = DynamoDBClient(region_name='us-east-2')
        
        yield client


@pytest.fixture
def project_repository(dynamodb_client):
    """ProjectRepository 픽스처"""
    return ProjectRepository(dynamodb_client, table_name='Projects')


@pytest.mark.property
class TestProjectDataRoundTrip:
    """프로젝트 데이터 라운드 트립 Property 테스트"""
    
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @given(project=project_strategy())
    def test_project_data_round_trip(self, project_repository, project):
        """
        Property 5: Project Data Round Trip
        
        *For any* project data, storing it to DynamoDB and retrieving it 
        should return equivalent data
        
        이 테스트는 프로젝트 데이터를 저장하고 조회했을 때 
        동일한 데이터가 반환되는지 검증합니다.
        """
        # 프로젝트 저장
        created_project = project_repository.create(project)
        
        # 저장된 프로젝트 조회
        retrieved_project = project_repository.get(project.project_id)
        
        # 조회 결과가 None이 아닌지 확인
        assert retrieved_project is not None, \
            f"프로젝트가 조회되지 않았습니다 (project_id: {project.project_id})"
        
        # 모든 필드가 동일한지 검증
        assert retrieved_project.project_id == project.project_id, \
            "project_id가 일치하지 않습니다"
        
        assert retrieved_project.project_name == project.project_name, \
            "project_name이 일치하지 않습니다"
        
        assert retrieved_project.client_industry == project.client_industry, \
            "client_industry가 일치하지 않습니다"
        
        assert retrieved_project.period.start == project.period.start, \
            "period.start가 일치하지 않습니다"
        
        assert retrieved_project.period.end == project.period.end, \
            "period.end가 일치하지 않습니다"
        
        assert retrieved_project.period.duration_months == project.period.duration_months, \
            "period.duration_months가 일치하지 않습니다"
        
        assert retrieved_project.budget_scale == project.budget_scale, \
            "budget_scale이 일치하지 않습니다"
        
        assert retrieved_project.description == project.description, \
            "description이 일치하지 않습니다"
        
        assert retrieved_project.tech_stack.backend == project.tech_stack.backend, \
            "tech_stack.backend가 일치하지 않습니다"
        
        assert retrieved_project.tech_stack.frontend == project.tech_stack.frontend, \
            "tech_stack.frontend가 일치하지 않습니다"
        
        assert retrieved_project.requirements == project.requirements, \
            "requirements가 일치하지 않습니다"
        
        assert retrieved_project.team_composition == project.team_composition, \
            "team_composition이 일치하지 않습니다"
    
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @given(project=project_strategy())
    def test_project_update_round_trip(self, project_repository, project):
        """
        프로젝트 업데이트 후 라운드 트립 검증
        
        프로젝트를 업데이트한 후 조회했을 때 
        업데이트된 값이 반환되는지 검증합니다.
        """
        # 초기 프로젝트 저장
        project_repository.create(project)
        
        # 프로젝트 업데이트
        project.project_name = "Updated Project Name"
        project.budget_scale = "Large"
        
        # 업데이트 수행
        project_repository.update(project)
        
        # 업데이트된 프로젝트 조회
        retrieved_project = project_repository.get(project.project_id)
        
        # 업데이트된 값이 반영되었는지 확인
        assert retrieved_project is not None
        assert retrieved_project.project_name == "Updated Project Name", \
            "업데이트된 project_name이 반영되지 않았습니다"
        assert retrieved_project.budget_scale == "Large", \
            "업데이트된 budget_scale이 반영되지 않았습니다"
