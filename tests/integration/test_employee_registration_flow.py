"""
직원 등록 플로우 통합 테스트

Requirements: 1.1, 1.2
- 모달 열기 및 폼 유효성 검사 테스트
- API 통합 및 데이터 지속성 테스트
- 직원 목록 새로고침 검증
"""

import json
import pytest
import boto3
from moto import mock_aws
from decimal import Decimal
import sys
import os

# 공통 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from lambda_functions.employee_create.index import lambda_handler as create_employee_handler
from lambda_functions.employees_list.index import handler as list_employees_handler


@pytest.fixture
def aws_credentials():
    """AWS 자격 증명 설정"""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-2'


@pytest.fixture
def dynamodb_table(aws_credentials):
    """DynamoDB 테이블 생성"""
    with mock_aws():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
        
        # Employees 테이블 생성
        table = dynamodb.create_table(
            TableName='Employees',
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'role', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'RoleIndex',
                    'KeySchema': [
                        {'AttributeName': 'role', 'KeyType': 'HASH'}
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
        
        os.environ['EMPLOYEES_TABLE'] = 'Employees'
        
        yield table


class TestEmployeeRegistrationFlow:
    """직원 등록 플로우 통합 테스트"""
    
    def test_complete_employee_registration_flow(self, dynamodb_table):
        """
        완전한 직원 등록 플로우 테스트
        
        시나리오:
        1. 유효한 직원 데이터로 등록 요청
        2. Lambda 함수가 데이터를 DynamoDB에 저장
        3. 직원 목록 조회 시 새로운 직원이 포함됨
        """
        # 1. 직원 등록 요청 데이터
        employee_data = {
            'name': '김철수',
            'email': 'kim.cs@example.com',
            'role': 'Senior Software Engineer',
            'years_of_experience': 7,
            'department': '개발팀',
            'skills': [
                {'name': 'Python', 'level': 'Expert', 'years': 7},
                {'name': 'Java', 'level': 'Advanced', 'years': 5},
                {'name': 'AWS', 'level': 'Intermediate', 'years': 3}
            ],
            'self_introduction': '백엔드 개발 전문가입니다.',
            'degree': 'Computer Science, BS',
            'university': '서울대학교',
            'certifications': ['AWS SAA', 'CKAD']
        }
        
        # 2. 직원 생성 API 호출
        create_event = {
            'httpMethod': 'POST',
            'body': json.dumps(employee_data)
        }
        
        create_response = create_employee_handler(create_event, None)
        
        # 3. 응답 검증
        assert create_response['statusCode'] == 201
        response_body = json.loads(create_response['body'])
        assert 'employee' in response_body
        assert response_body['employee']['basic_info']['name'] == '김철수'
        assert response_body['employee']['basic_info']['email'] == 'kim.cs@example.com'
        
        # 생성된 user_id 저장
        created_user_id = response_body['employee']['user_id']
        assert created_user_id.startswith('U_')
        
        # 4. 직원 목록 조회
        list_event = {
            'httpMethod': 'GET',
            'queryStringParameters': None
        }
        
        list_response = list_employees_handler(list_event, None)
        
        # 5. 목록에 새 직원이 포함되어 있는지 확인
        assert list_response['statusCode'] == 200
        list_body = json.loads(list_response['body'])
        assert 'employees' in list_body
        assert len(list_body['employees']) == 1
        
        # 6. 생성된 직원 데이터 검증
        employee = list_body['employees'][0]
        assert employee['user_id'] == created_user_id
        assert employee['basic_info']['name'] == '김철수'
        assert employee['basic_info']['role'] == 'Senior Software Engineer'
        assert employee['basic_info']['years_of_experience'] == 7
        assert len(employee['skills']) == 3
        assert employee['skills'][0]['name'] == 'Python'
        assert employee['skills'][0]['level'] == 'Expert'
        assert len(employee['certifications']) == 2
    
    def test_form_validation_required_fields(self, dynamodb_table):
        """
        폼 유효성 검사 - 필수 필드 누락
        
        시나리오:
        1. 필수 필드가 누락된 데이터로 등록 시도
        2. 400 Bad Request 응답 확인
        3. 적절한 에러 메시지 확인
        """
        # 필수 필드 누락 (email 없음)
        invalid_data = {
            'name': '이영희',
            'role': 'Junior Developer',
            'years_of_experience': 2
        }
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps(invalid_data)
        }
        
        response = create_employee_handler(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'email' in body['message'].lower()
    
    def test_form_validation_invalid_email(self, dynamodb_table):
        """
        폼 유효성 검사 - 잘못된 이메일 형식
        
        시나리오:
        1. 잘못된 이메일 형식으로 등록 시도
        2. 400 Bad Request 응답 확인
        """
        invalid_data = {
            'name': '박민수',
            'email': 'invalid-email',  # 잘못된 형식
            'role': 'Developer',
            'years_of_experience': 3,
            'skills': [{'name': 'JavaScript', 'level': 'Intermediate', 'years': 2}]
        }
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps(invalid_data)
        }
        
        response = create_employee_handler(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert '이메일' in body['message'] or 'email' in body['message'].lower()
    
    def test_form_validation_negative_experience(self, dynamodb_table):
        """
        폼 유효성 검사 - 음수 경력 연수
        
        시나리오:
        1. 음수 경력 연수로 등록 시도
        2. 400 Bad Request 응답 확인
        """
        invalid_data = {
            'name': '최지훈',
            'email': 'choi@example.com',
            'role': 'Developer',
            'years_of_experience': -1,  # 음수
            'skills': [{'name': 'Python', 'level': 'Beginner', 'years': 0}]
        }
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps(invalid_data)
        }
        
        response = create_employee_handler(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert '경력' in body['message'] or 'experience' in body['message'].lower()
    
    def test_form_validation_invalid_skill_level(self, dynamodb_table):
        """
        폼 유효성 검사 - 잘못된 기술 숙련도
        
        시나리오:
        1. 잘못된 숙련도 값으로 등록 시도
        2. 400 Bad Request 응답 확인
        """
        invalid_data = {
            'name': '정수진',
            'email': 'jung@example.com',
            'role': 'Developer',
            'years_of_experience': 4,
            'skills': [
                {'name': 'Java', 'level': 'InvalidLevel', 'years': 3}  # 잘못된 숙련도
            ]
        }
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps(invalid_data)
        }
        
        response = create_employee_handler(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert '숙련도' in body['message'] or 'level' in body['message'].lower()
    
    def test_multiple_employees_registration(self, dynamodb_table):
        """
        여러 직원 등록 및 목록 조회
        
        시나리오:
        1. 3명의 직원을 순차적으로 등록
        2. 직원 목록 조회 시 3명 모두 포함됨
        3. 각 직원의 데이터가 정확히 저장됨
        """
        employees_data = [
            {
                'name': '홍길동',
                'email': 'hong@example.com',
                'role': 'Tech Lead',
                'years_of_experience': 10,
                'skills': [{'name': 'Java', 'level': 'Expert', 'years': 10}]
            },
            {
                'name': '김영희',
                'email': 'kim@example.com',
                'role': 'Senior Developer',
                'years_of_experience': 6,
                'skills': [{'name': 'Python', 'level': 'Advanced', 'years': 6}]
            },
            {
                'name': '이철수',
                'email': 'lee@example.com',
                'role': 'Junior Developer',
                'years_of_experience': 2,
                'skills': [{'name': 'JavaScript', 'level': 'Intermediate', 'years': 2}]
            }
        ]
        
        created_ids = []
        
        # 각 직원 등록
        for emp_data in employees_data:
            event = {
                'httpMethod': 'POST',
                'body': json.dumps(emp_data)
            }
            
            response = create_employee_handler(event, None)
            assert response['statusCode'] == 201
            
            body = json.loads(response['body'])
            created_ids.append(body['employee']['user_id'])
        
        # 전체 목록 조회
        list_event = {
            'httpMethod': 'GET',
            'queryStringParameters': None
        }
        
        list_response = list_employees_handler(list_event, None)
        assert list_response['statusCode'] == 200
        
        list_body = json.loads(list_response['body'])
        assert len(list_body['employees']) == 3
        
        # 모든 생성된 ID가 목록에 있는지 확인
        returned_ids = [emp['user_id'] for emp in list_body['employees']]
        for created_id in created_ids:
            assert created_id in returned_ids
    
    def test_employee_data_persistence(self, dynamodb_table):
        """
        데이터 지속성 테스트
        
        시나리오:
        1. 직원 등록
        2. DynamoDB에서 직접 조회
        3. 모든 필드가 정확히 저장되었는지 확인
        """
        employee_data = {
            'name': '강민지',
            'email': 'kang@example.com',
            'role': 'Data Scientist',
            'years_of_experience': 5,
            'skills': [
                {'name': 'Python', 'level': 'Expert', 'years': 5},
                {'name': 'TensorFlow', 'level': 'Advanced', 'years': 3}
            ],
            'self_introduction': '머신러닝 전문가입니다.',
            'degree': 'Statistics, MS',
            'university': '연세대학교',
            'certifications': ['TensorFlow Developer Certificate']
        }
        
        # 직원 등록
        event = {
            'httpMethod': 'POST',
            'body': json.dumps(employee_data)
        }
        
        response = create_employee_handler(event, None)
        assert response['statusCode'] == 201
        
        body = json.loads(response['body'])
        user_id = body['employee']['user_id']
        
        # DynamoDB에서 직접 조회
        dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
        table = dynamodb.Table('Employees')
        
        db_response = table.get_item(Key={'user_id': user_id})
        assert 'Item' in db_response
        
        item = db_response['Item']
        
        # 모든 필드 검증
        assert item['user_id'] == user_id
        assert item['basic_info']['name'] == '강민지'
        assert item['basic_info']['email'] == 'kang@example.com'
        assert item['basic_info']['role'] == 'Data Scientist'
        assert item['basic_info']['years_of_experience'] == 5
        assert len(item['skills']) == 2
        assert item['self_introduction'] == '머신러닝 전문가입니다.'
        assert item['education']['degree'] == 'Statistics, MS'
        assert item['education']['university'] == '연세대학교'
        assert len(item['certifications']) == 1
    
    def test_cors_headers(self, dynamodb_table):
        """
        CORS 헤더 검증
        
        시나리오:
        1. OPTIONS 요청 전송
        2. 적절한 CORS 헤더 확인
        """
        event = {
            'httpMethod': 'OPTIONS'
        }
        
        response = create_employee_handler(event, None)
        
        assert response['statusCode'] == 200
        assert 'headers' in response
        assert 'Access-Control-Allow-Origin' in response['headers']
        assert response['headers']['Access-Control-Allow-Origin'] == '*'
        assert 'Access-Control-Allow-Methods' in response['headers']
    
    def test_empty_optional_fields(self, dynamodb_table):
        """
        선택적 필드가 비어있을 때 처리
        
        시나리오:
        1. 필수 필드만 포함하여 등록
        2. 선택적 필드는 빈 배열이나 빈 문자열
        3. 정상적으로 등록되고 빈 값은 필터링됨
        """
        employee_data = {
            'name': '윤서연',
            'email': 'yoon@example.com',
            'role': 'Developer',
            'years_of_experience': 3,
            'skills': [
                {'name': 'JavaScript', 'level': 'Intermediate', 'years': 3},
                {'name': '', 'level': 'Beginner', 'years': 0}  # 빈 기술명
            ],
            'self_introduction': '',  # 빈 자기소개
            'certifications': ['', 'AWS SAA', '']  # 빈 자격증 포함
        }
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps(employee_data)
        }
        
        response = create_employee_handler(event, None)
        assert response['statusCode'] == 201
        
        body = json.loads(response['body'])
        employee = body['employee']
        
        # 빈 기술은 필터링되어야 함
        assert len(employee['skills']) == 1
        assert employee['skills'][0]['name'] == 'JavaScript'
        
        # 빈 자격증은 필터링되어야 함
        assert len(employee['certifications']) == 1
        assert employee['certifications'][0] == 'AWS SAA'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
