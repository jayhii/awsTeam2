"""
Employees List Lambda Function
직원 목록 조회

Requirements: 직원 데이터 조회 및 목록 제공
"""

import json
import logging
import os
from typing import Dict, Any, List
from decimal import Decimal
import boto3

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS 클라이언트 초기화
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-2'))


def handler(event, context):
    """
    Lambda handler for API Gateway
    
    Args:
        event: API Gateway 이벤트
        context: Lambda 컨텍스트
        
    Returns:
        dict: API Gateway 응답
    """
    try:
        logger.info("직원 목록 조회 요청 수신")
        
        # 직원 목록 조회
        employees = fetch_all_employees()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'employees': employees,
                'count': len(employees)
            }, default=decimal_default)
        }
        
    except Exception as e:
        logger.error(f"직원 목록 조회 중 오류 발생: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({'error': str(e)})
        }


def fetch_all_employees() -> List[Dict[str, Any]]:
    """
    모든 직원 데이터 조회
    
    Returns:
        list: 직원 목록
    """
    try:
        table = dynamodb.Table('Employees')
        response = table.scan()
        
        employees = []
        for item in response.get('Items', []):
            # 필요한 정보만 추출
            employee = {
                'user_id': item.get('user_id'),
                'basic_info': {
                    'name': item.get('basic_info', {}).get('name', ''),
                    'role': item.get('basic_info', {}).get('role', ''),
                    'email': item.get('basic_info', {}).get('email', ''),
                    'years_of_experience': float(item.get('basic_info', {}).get('years_of_experience', 0))
                },
                'skills': [],
                'certifications': item.get('certifications', []),
                'work_experience': item.get('work_experience', [])
            }
            
            # 자기소개 추가 (있는 경우)
            if 'self_introduction' in item:
                employee['self_introduction'] = item['self_introduction']
            
            # 학력 정보 추가 (있는 경우)
            if 'education' in item:
                employee['education'] = item['education']
            
            # 스킬 정보 추출
            skills = item.get('skills', [])
            if isinstance(skills, list):
                for skill in skills:
                    if isinstance(skill, dict):
                        employee['skills'].append({
                            'name': skill.get('name', ''),
                            'level': skill.get('level', ''),
                            'years': float(skill.get('years', 0)) if skill.get('years') else 0
                        })
            
            employees.append(employee)
        
        logger.info(f"총 {len(employees)}명의 직원 조회 완료")
        return employees
        
    except Exception as e:
        logger.error(f"직원 데이터 조회 실패: {str(e)}")
        raise


def decimal_default(obj):
    """Decimal을 float로 변환"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError
