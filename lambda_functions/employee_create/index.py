"""
직원 생성 Lambda 함수

신규 직원을 DynamoDB Employees 테이블에 등록합니다.
"""

import json
import os
import sys
import uuid
from datetime import datetime
from typing import Dict, Any

# Lambda Layer에서 boto3 가져오기
import boto3
from botocore.exceptions import ClientError

# 공통 모듈 경로 추가
sys.path.append('/opt/python')
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from common.models import Employee, BasicInfo, Skill, Education
from common.utils import setup_logger, validate_email

# 로거 설정
logger = setup_logger(__name__)

# DynamoDB 클라이언트
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
employees_table = dynamodb.Table(os.environ.get('EMPLOYEES_TABLE', 'Employees'))


def validate_employee_data(data: Dict[str, Any]) -> tuple[bool, str]:
    """
    직원 데이터 유효성 검사
    
    Args:
        data: 직원 데이터
        
    Returns:
        (유효성 여부, 에러 메시지)
    """
    # 필수 필드 검증
    required_fields = ['name', 'email', 'role', 'years_of_experience']
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"필수 필드가 누락되었습니다: {field}"
    
    # 이메일 형식 검증
    if not validate_email(data['email']):
        return False, "올바른 이메일 형식이 아닙니다"
    
    # 경력 연수 검증
    try:
        years = int(data['years_of_experience'])
        if years < 0:
            return False, "경력 연수는 0 이상이어야 합니다"
    except (ValueError, TypeError):
        return False, "경력 연수는 숫자여야 합니다"
    
    # 기술 스택 검증
    if 'skills' in data and data['skills']:
        if not isinstance(data['skills'], list):
            return False, "기술 스택은 배열이어야 합니다"
        
        # 빈 기술 이름을 가진 항목은 필터링하고 유효한 기술만 검증
        valid_skills = [skill for skill in data['skills'] if isinstance(skill, dict) and skill.get('name', '').strip()]
        
        for skill in valid_skills:
            if not isinstance(skill, dict):
                return False, "각 기술은 객체여야 합니다"
            if 'level' not in skill:
                return False, "기술 숙련도는 필수입니다"
            if skill['level'] not in ['Beginner', 'Intermediate', 'Advanced', 'Expert']:
                return False, f"올바르지 않은 숙련도: {skill['level']}"
    
    return True, ""


def create_employee(event_body: Dict[str, Any]) -> Dict[str, Any]:
    """
    신규 직원 생성
    
    Args:
        event_body: 요청 본문
        
    Returns:
        생성된 직원 데이터
    """
    # 데이터 유효성 검사
    is_valid, error_message = validate_employee_data(event_body)
    if not is_valid:
        raise ValueError(error_message)
    
    # 고유 ID 생성
    user_id = f"U_{uuid.uuid4().hex[:8].upper()}"
    
    # 기본 정보 구성
    basic_info = {
        'name': event_body['name'],
        'role': event_body['role'],
        'years_of_experience': int(event_body['years_of_experience']),
        'email': event_body['email']
    }
    
    # 기술 스택 구성
    skills = []
    if 'skills' in event_body and event_body['skills']:
        for skill_data in event_body['skills']:
            if skill_data.get('name'):  # 빈 기술은 제외
                skills.append({
                    'name': skill_data['name'],
                    'level': skill_data.get('level', 'Intermediate'),
                    'years': int(skill_data.get('years', 0))
                })
    
    # 직원 객체 생성
    employee_data = {
        'user_id': user_id,
        'basic_info': basic_info,
        'skills': skills,
        'work_experience': [],
        'certifications': []
    }
    
    # 선택적 필드 추가
    if 'self_introduction' in event_body and event_body['self_introduction']:
        employee_data['self_introduction'] = event_body['self_introduction']
    
    if 'degree' in event_body and event_body['degree']:
        employee_data['education'] = {
            'degree': event_body['degree'],
            'university': event_body.get('university', '')
        }
    
    if 'certifications' in event_body and event_body['certifications']:
        # 빈 자격증 제외
        certs = [cert for cert in event_body['certifications'] if cert.strip()]
        if certs:
            employee_data['certifications'] = certs
    
    # Pydantic 모델로 검증
    try:
        employee = Employee(**employee_data)
    except Exception as e:
        logger.error(f"직원 데이터 검증 실패: {str(e)}")
        raise ValueError(f"데이터 형식이 올바르지 않습니다: {str(e)}")
    
    # DynamoDB에 저장
    try:
        employees_table.put_item(Item=employee.to_dynamodb())
        logger.info(f"직원 생성 완료: {user_id}")
    except ClientError as e:
        logger.error(f"DynamoDB 저장 실패: {str(e)}")
        raise Exception(f"데이터베이스 저장에 실패했습니다: {str(e)}")
    
    return employee.to_dynamodb()


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda 핸들러
    
    Args:
        event: API Gateway 이벤트
        context: Lambda 컨텍스트
        
    Returns:
        API Gateway 응답
    """
    logger.info(f"직원 생성 요청 수신: {json.dumps(event)}")
    
    try:
        # CORS 헤더
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        }
        
        # OPTIONS 요청 처리 (CORS preflight)
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'OK'})
            }
        
        # 요청 본문 파싱
        if 'body' not in event:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': '요청 본문이 없습니다',
                    'message': 'Request body is required'
                })
            }
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        # 직원 생성
        employee = create_employee(body)
        
        # 성공 응답
        return {
            'statusCode': 201,
            'headers': headers,
            'body': json.dumps({
                'message': '직원이 성공적으로 등록되었습니다',
                'employee': employee
            }, ensure_ascii=False)
        }
        
    except ValueError as e:
        # 유효성 검사 실패
        logger.warning(f"유효성 검사 실패: {str(e)}")
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({
                'error': 'Validation Error',
                'message': str(e)
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        # 서버 에러
        logger.error(f"직원 생성 실패: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': '직원 등록 중 오류가 발생했습니다'
            }, ensure_ascii=False)
        }
