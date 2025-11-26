"""
Property-Based Test for Affinity Score Persistence

**Feature: hr-resource-optimization, Property 7: Affinity Score Persistence**
**Validates: Requirements 2.3**

Property: *For any* collaboration history between two employees, 
          calculating and storing the affinity score should allow retrieval 
          of the same score

이 테스트는 친밀도 점수가 DynamoDB에 저장되고 조회될 때 
데이터 무결성이 유지되는지 검증합니다.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from moto import mock_aws
import boto3
from typing import List
from common.dynamodb_client import DynamoDBClient
from common.repositories import AffinityRepository
from common.models import (
    Affinity,
    EmployeePair,
    ProjectCollaboration,
    SharedProject,
    MessengerCommunication,
    CompanyEvents,
    PersonalCloseness
)


# Hypothesis 전략 정의

@st.composite
def shared_project_strategy(draw):
    """SharedProject 객체 생성 전략"""
    return SharedProject(
        project_id=draw(st.text(min_size=1, max_size=20, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-'
        ))),
        overlap_period_months=draw(st.integers(min_value=0, max_value=60)),
        same_team=draw(st.booleans())
    )


@st.composite
def project_collaboration_strategy(draw):
    """ProjectCollaboration 객체 생성 전략"""
    return ProjectCollaboration(
        shared_projects=draw(st.lists(
            shared_project_strategy(),
            min_size=0,
            max_size=5
        )),
        collaboration_score=draw(st.floats(
            min_value=0,
            max_value=100,
            allow_nan=False,
            allow_infinity=False
        ).filter(lambda x: x == 0 or abs(x) >= 1e-100))
    )


@st.composite
def messenger_communication_strategy(draw):
    """MessengerCommunication 객체 생성 전략"""
    return MessengerCommunication(
        total_messages_exchanged=draw(st.integers(min_value=0, max_value=10000)),
        avg_response_time_minutes=draw(st.floats(
            min_value=0,
            max_value=1440,
            allow_nan=False,
            allow_infinity=False
        ).filter(lambda x: x == 0 or abs(x) >= 1e-100)),
        communication_score=draw(st.floats(
            min_value=0,
            max_value=100,
            allow_nan=False,
            allow_infinity=False
        ).filter(lambda x: x == 0 or abs(x) >= 1e-100))
    )


@st.composite
def company_events_strategy(draw):
    """CompanyEvents 객체 생성 전략"""
    return CompanyEvents(
        shared_events=draw(st.lists(
            st.text(min_size=1, max_size=20, alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-'
            )),
            min_size=0,
            max_size=10
        )),
        social_score=draw(st.floats(
            min_value=0,
            max_value=100,
            allow_nan=False,
            allow_infinity=False
        ).filter(lambda x: x == 0 or abs(x) >= 1e-100))
    )


@st.composite
def personal_closeness_strategy(draw):
    """PersonalCloseness 객체 생성 전략"""
    return PersonalCloseness(
        payday_contact_frequency=draw(st.integers(min_value=0, max_value=50)),
        vacation_day_contact_frequency=draw(st.integers(min_value=0, max_value=50)),
        personal_score=draw(st.floats(
            min_value=0,
            max_value=100,
            allow_nan=False,
            allow_infinity=False
        ).filter(lambda x: x == 0 or abs(x) >= 1e-100))
    )


@st.composite
def affinity_strategy(draw):
    """Affinity 객체 생성 전략"""
    # 직원 ID 생성
    employee_1 = draw(st.text(
        min_size=3,
        max_size=20,
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='_-'
        )
    ))
    employee_2 = draw(st.text(
        min_size=3,
        max_size=20,
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='_-'
        )
    ))
    
    # 두 직원 ID가 다른지 확인
    assume(employee_1 != employee_2)
    
    # affinity_id 생성
    affinity_id = f"AFF_{employee_1}_{employee_2}"
    
    return Affinity(
        affinity_id=affinity_id,
        employee_pair=EmployeePair(
            employee_1=employee_1,
            employee_2=employee_2
        ),
        project_collaboration=draw(project_collaboration_strategy()),
        messenger_communication=draw(messenger_communication_strategy()),
        company_events=draw(company_events_strategy()),
        personal_closeness=draw(personal_closeness_strategy()),
        overall_affinity_score=draw(st.floats(
            min_value=0,
            max_value=100,
            allow_nan=False,
            allow_infinity=False
        ).filter(lambda x: x == 0 or abs(x) >= 1e-100))
    )


@pytest.fixture
def dynamodb_client():
    """DynamoDB 클라이언트 픽스처 (moto 사용)"""
    with mock_aws():
        # DynamoDB 리소스 생성
        dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
        
        # EmployeeAffinity 테이블 생성
        table = dynamodb.create_table(
            TableName='EmployeeAffinity',
            KeySchema=[
                {'AttributeName': 'affinity_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'affinity_id', 'AttributeType': 'S'},
                {'AttributeName': 'employee_1', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'Employee1Index',
                    'KeySchema': [
                        {'AttributeName': 'employee_1', 'KeyType': 'HASH'}
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
        table.meta.client.get_waiter('table_exists').wait(
            TableName='EmployeeAffinity'
        )
        
        # DynamoDBClient 생성
        client = DynamoDBClient(region_name='us-east-2')
        
        yield client


@pytest.fixture
def affinity_repository(dynamodb_client):
    """AffinityRepository 픽스처"""
    return AffinityRepository(dynamodb_client, table_name='EmployeeAffinity')


@pytest.mark.property
class TestAffinityScorePersistence:
    """친밀도 점수 영속성 Property 테스트"""
    
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @given(affinity=affinity_strategy())
    def test_affinity_score_round_trip(self, affinity_repository, affinity):
        """
        Property 7: Affinity Score Persistence
        
        *For any* collaboration history between two employees, 
        calculating and storing the affinity score should allow retrieval 
        of the same score
        
        이 테스트는 친밀도 점수를 저장하고 조회했을 때 
        동일한 데이터가 반환되는지 검증합니다.
        """
        # 친밀도 점수 저장
        created_affinity = affinity_repository.create(affinity)
        
        # 저장된 친밀도 점수 조회
        retrieved_affinity = affinity_repository.get(affinity.affinity_id)
        
        # 조회 결과가 None이 아닌지 확인
        assert retrieved_affinity is not None, \
            f"친밀도 점수가 조회되지 않았습니다 (affinity_id: {affinity.affinity_id})"
        
        # 모든 필드가 동일한지 검증
        assert retrieved_affinity.affinity_id == affinity.affinity_id, \
            "affinity_id가 일치하지 않습니다"
        
        assert retrieved_affinity.employee_pair.employee_1 == affinity.employee_pair.employee_1, \
            "employee_1이 일치하지 않습니다"
        
        assert retrieved_affinity.employee_pair.employee_2 == affinity.employee_pair.employee_2, \
            "employee_2가 일치하지 않습니다"
        
        assert abs(retrieved_affinity.overall_affinity_score - affinity.overall_affinity_score) < 0.01, \
            f"overall_affinity_score가 일치하지 않습니다 " \
            f"(저장: {affinity.overall_affinity_score}, " \
            f"조회: {retrieved_affinity.overall_affinity_score})"
        
        # 프로젝트 협업 점수 검증
        assert abs(
            retrieved_affinity.project_collaboration.collaboration_score -
            affinity.project_collaboration.collaboration_score
        ) < 0.01, "collaboration_score가 일치하지 않습니다"
        
        # 메신저 커뮤니케이션 점수 검증
        assert abs(
            retrieved_affinity.messenger_communication.communication_score -
            affinity.messenger_communication.communication_score
        ) < 0.01, "communication_score가 일치하지 않습니다"
        
        # 회사 행사 점수 검증
        assert abs(
            retrieved_affinity.company_events.social_score -
            affinity.company_events.social_score
        ) < 0.01, "social_score가 일치하지 않습니다"
        
        # 개인적 친밀도 점수 검증
        assert abs(
            retrieved_affinity.personal_closeness.personal_score -
            affinity.personal_closeness.personal_score
        ) < 0.01, "personal_score가 일치하지 않습니다"
    
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @given(affinity=affinity_strategy())
    def test_affinity_score_update_persistence(self, affinity_repository, affinity):
        """
        친밀도 점수 업데이트 후 영속성 검증
        
        Requirements: 2-1.7 - 친밀도 점수 주기적 업데이트
        
        친밀도 점수를 업데이트한 후 조회했을 때 
        업데이트된 값이 반환되는지 검증합니다.
        """
        # 초기 친밀도 점수 저장
        affinity_repository.create(affinity)
        
        # 점수 업데이트
        updated_score = min(100.0, affinity.overall_affinity_score + 10.0)
        affinity.overall_affinity_score = updated_score
        
        # 업데이트 수행
        affinity_repository.update(affinity)
        
        # 업데이트된 친밀도 점수 조회
        retrieved_affinity = affinity_repository.get(affinity.affinity_id)
        
        # 업데이트된 점수가 반영되었는지 확인
        assert retrieved_affinity is not None
        assert abs(retrieved_affinity.overall_affinity_score - updated_score) < 0.01, \
            f"업데이트된 점수가 반영되지 않았습니다 " \
            f"(예상: {updated_score}, 실제: {retrieved_affinity.overall_affinity_score})"
    
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @given(
        affinity=affinity_strategy(),
        new_collaboration_score=st.floats(
            min_value=0,
            max_value=100,
            allow_nan=False,
            allow_infinity=False
        ).filter(lambda x: x == 0 or abs(x) >= 1e-100)
    )
    def test_component_score_persistence(
        self,
        affinity_repository,
        affinity,
        new_collaboration_score
    ):
        """
        개별 구성 요소 점수의 영속성 검증
        
        친밀도의 개별 구성 요소(협업, 커뮤니케이션 등)를 
        업데이트한 후 조회했을 때 올바르게 반영되는지 검증합니다.
        """
        # 초기 친밀도 점수 저장
        affinity_repository.create(affinity)
        
        # 협업 점수 업데이트
        affinity.project_collaboration.collaboration_score = new_collaboration_score
        affinity_repository.update(affinity)
        
        # 조회 및 검증
        retrieved_affinity = affinity_repository.get(affinity.affinity_id)
        
        assert retrieved_affinity is not None
        assert abs(
            retrieved_affinity.project_collaboration.collaboration_score -
            new_collaboration_score
        ) < 0.01, \
            f"협업 점수가 올바르게 업데이트되지 않았습니다 " \
            f"(예상: {new_collaboration_score}, " \
            f"실제: {retrieved_affinity.project_collaboration.collaboration_score})"
    
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @given(affinities=st.lists(affinity_strategy(), min_size=1, max_size=10))
    def test_multiple_affinity_scores_persistence(
        self,
        affinity_repository,
        affinities: List[Affinity]
    ):
        """
        여러 친밀도 점수의 동시 영속성 검증
        
        여러 직원 쌍의 친밀도 점수를 저장하고 조회했을 때 
        모두 올바르게 저장되고 조회되는지 검증합니다.
        """
        # 모든 affinity_id가 고유한지 확인
        affinity_ids = [a.affinity_id for a in affinities]
        assume(len(affinity_ids) == len(set(affinity_ids)))
        
        # 모든 친밀도 점수 저장
        for affinity in affinities:
            affinity_repository.create(affinity)
        
        # 모든 친밀도 점수 조회 및 검증
        for affinity in affinities:
            retrieved_affinity = affinity_repository.get(affinity.affinity_id)
            
            assert retrieved_affinity is not None, \
                f"친밀도 점수가 조회되지 않았습니다 (affinity_id: {affinity.affinity_id})"
            
            assert abs(
                retrieved_affinity.overall_affinity_score -
                affinity.overall_affinity_score
            ) < 0.01, \
                f"친밀도 점수가 일치하지 않습니다 " \
                f"(affinity_id: {affinity.affinity_id})"
    
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @given(affinity=affinity_strategy())
    def test_affinity_score_query_by_employee_pair(
        self,
        affinity_repository,
        affinity
    ):
        """
        직원 쌍으로 친밀도 점수 조회 검증
        
        Requirements: 2.3 - 직원 간 친밀도 점수 조회
        
        직원 쌍을 사용하여 친밀도 점수를 조회했을 때 
        올바른 점수가 반환되는지 검증합니다.
        """
        # 친밀도 점수 저장
        affinity_repository.create(affinity)
        
        # 직원 쌍으로 조회
        retrieved_affinity = affinity_repository.find_by_employee_pair(
            affinity.employee_pair.employee_1,
            affinity.employee_pair.employee_2
        )
        
        # 조회 결과 검증
        assert retrieved_affinity is not None, \
            f"직원 쌍으로 친밀도 점수를 조회할 수 없습니다 " \
            f"({affinity.employee_pair.employee_1} - {affinity.employee_pair.employee_2})"
        
        assert retrieved_affinity.affinity_id == affinity.affinity_id
        assert abs(
            retrieved_affinity.overall_affinity_score -
            affinity.overall_affinity_score
        ) < 0.01
    
    @settings(
        max_examples=30,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @given(affinity=affinity_strategy())
    def test_affinity_score_data_integrity(self, affinity_repository, affinity):
        """
        친밀도 점수 데이터 무결성 검증
        
        저장된 친밀도 점수의 모든 필드가 
        원본 데이터와 정확히 일치하는지 검증합니다.
        """
        # 친밀도 점수 저장
        affinity_repository.create(affinity)
        
        # 조회
        retrieved_affinity = affinity_repository.get(affinity.affinity_id)
        
        assert retrieved_affinity is not None
        
        # 프로젝트 협업 상세 정보 검증
        assert len(retrieved_affinity.project_collaboration.shared_projects) == \
               len(affinity.project_collaboration.shared_projects), \
            "공동 참여 프로젝트 수가 일치하지 않습니다"
        
        # 메신저 커뮤니케이션 상세 정보 검증
        assert retrieved_affinity.messenger_communication.total_messages_exchanged == \
               affinity.messenger_communication.total_messages_exchanged, \
            "총 메시지 교환 수가 일치하지 않습니다"
        
        assert abs(
            retrieved_affinity.messenger_communication.avg_response_time_minutes -
            affinity.messenger_communication.avg_response_time_minutes
        ) < 0.01, "평균 응답 시간이 일치하지 않습니다"
        
        # 회사 행사 상세 정보 검증
        assert len(retrieved_affinity.company_events.shared_events) == \
               len(affinity.company_events.shared_events), \
            "공동 참여 행사 수가 일치하지 않습니다"
        
        # 개인적 친밀도 상세 정보 검증
        assert retrieved_affinity.personal_closeness.payday_contact_frequency == \
               affinity.personal_closeness.payday_contact_frequency, \
            "월급일 연락 빈도가 일치하지 않습니다"
        
        assert retrieved_affinity.personal_closeness.vacation_day_contact_frequency == \
               affinity.personal_closeness.vacation_day_contact_frequency, \
            "연차일 연락 빈도가 일치하지 않습니다"
    
    def test_affinity_score_persistence_with_zero_scores(self, affinity_repository):
        """
        모든 점수가 0인 경우의 영속성 검증
        
        엣지 케이스: 모든 구성 요소 점수가 0일 때도 
        올바르게 저장되고 조회되는지 검증합니다.
        """
        affinity = Affinity(
            affinity_id="AFF_ZERO_TEST",
            employee_pair=EmployeePair(
                employee_1="EMP_001",
                employee_2="EMP_002"
            ),
            project_collaboration=ProjectCollaboration(
                shared_projects=[],
                collaboration_score=0.0
            ),
            messenger_communication=MessengerCommunication(
                total_messages_exchanged=0,
                avg_response_time_minutes=0.0,
                communication_score=0.0
            ),
            company_events=CompanyEvents(
                shared_events=[],
                social_score=0.0
            ),
            personal_closeness=PersonalCloseness(
                payday_contact_frequency=0,
                vacation_day_contact_frequency=0,
                personal_score=0.0
            ),
            overall_affinity_score=0.0
        )
        
        # 저장 및 조회
        affinity_repository.create(affinity)
        retrieved_affinity = affinity_repository.get(affinity.affinity_id)
        
        # 검증
        assert retrieved_affinity is not None
        assert retrieved_affinity.overall_affinity_score == 0.0
        assert retrieved_affinity.project_collaboration.collaboration_score == 0.0
        assert retrieved_affinity.messenger_communication.communication_score == 0.0
        assert retrieved_affinity.company_events.social_score == 0.0
        assert retrieved_affinity.personal_closeness.personal_score == 0.0
    
    def test_affinity_score_persistence_with_max_scores(self, affinity_repository):
        """
        모든 점수가 최대값(100)인 경우의 영속성 검증
        
        엣지 케이스: 모든 구성 요소 점수가 100일 때도 
        올바르게 저장되고 조회되는지 검증합니다.
        """
        affinity = Affinity(
            affinity_id="AFF_MAX_TEST",
            employee_pair=EmployeePair(
                employee_1="EMP_003",
                employee_2="EMP_004"
            ),
            project_collaboration=ProjectCollaboration(
                shared_projects=[
                    SharedProject(
                        project_id="P_001",
                        overlap_period_months=60,
                        same_team=True
                    )
                ],
                collaboration_score=100.0
            ),
            messenger_communication=MessengerCommunication(
                total_messages_exchanged=10000,
                avg_response_time_minutes=1.0,
                communication_score=100.0
            ),
            company_events=CompanyEvents(
                shared_events=["EVT_001", "EVT_002", "EVT_003"],
                social_score=100.0
            ),
            personal_closeness=PersonalCloseness(
                payday_contact_frequency=50,
                vacation_day_contact_frequency=50,
                personal_score=100.0
            ),
            overall_affinity_score=100.0
        )
        
        # 저장 및 조회
        affinity_repository.create(affinity)
        retrieved_affinity = affinity_repository.get(affinity.affinity_id)
        
        # 검증
        assert retrieved_affinity is not None
        assert retrieved_affinity.overall_affinity_score == 100.0
        assert retrieved_affinity.project_collaboration.collaboration_score == 100.0
        assert retrieved_affinity.messenger_communication.communication_score == 100.0
        assert retrieved_affinity.company_events.social_score == 100.0
        assert retrieved_affinity.personal_closeness.personal_score == 100.0
