"""
Projects List Lambda Function
프로젝트 목록 조회

Requirements: 프로젝트 데이터 조회 및 목록 제공
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
    # CORS preflight 요청 처리
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': ''
        }
    
    try:
        logger.info("프로젝트 목록 조회 요청 수신")
        
        # 프로젝트 목록 조회
        projects = fetch_all_projects()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'projects': projects,
                'count': len(projects)
            }, default=decimal_default)
        }
        
    except Exception as e:
        logger.error(f"프로젝트 목록 조회 중 오류 발생: {str(e)}", exc_info=True)
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


def fetch_all_projects() -> List[Dict[str, Any]]:
    """
    모든 프로젝트 데이터 조회
    
    Returns:
        list: 프로젝트 목록
    """
    try:
        table = dynamodb.Table('Projects')
        response = table.scan()
        
        projects = []
        for item in response.get('Items', []):
            # period 정보 추출
            period = item.get('period', {})
            start_date = ''
            end_date = ''
            
            if isinstance(period, dict):
                start_date = period.get('start', '')
                end_date = period.get('end', '')
            
            # tech_stack에서 필요 스킬 추출
            required_skills = []
            tech_stack = item.get('tech_stack', {})
            if isinstance(tech_stack, dict):
                for category, skills in tech_stack.items():
                    if isinstance(skills, list):
                        required_skills.extend([str(skill) for skill in skills])
            
            # 필요한 정보만 추출
            project = {
                'project_id': item.get('project_id'),
                'project_name': item.get('project_name', ''),
                'status': 'active',  # 기본값
                'start_date': start_date,
                'end_date': end_date,
                'required_skills': required_skills,
                'description': item.get('description', ''),
                'client_industry': item.get('client_industry', '')
            }
            
            projects.append(project)
        
        logger.info(f"총 {len(projects)}개의 프로젝트 조회 완료")
        return projects
        
    except Exception as e:
        logger.error(f"프로젝트 데이터 조회 실패: {str(e)}")
        raise


def decimal_default(obj):
    """Decimal을 float로 변환"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError
