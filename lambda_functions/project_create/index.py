"""
프로젝트 생성 Lambda 함수

신규 프로젝트를 DynamoDB에 생성합니다.
Requirements: 2.1
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Lambda Layer의 common 모듈 경로 추가
sys.path.insert(0, '/opt/python')

import boto3
from common.dynamodb_client import DynamoDBClient
from common.repositories import ProjectRepository
from common.models import Project, ProjectPeriod, TechStack

# 로거 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB 클라이언트 초기화
dynamodb_client = DynamoDBClient()
project_repo = ProjectRepository(dynamodb_client)


def generate_project_id() -> str:
    """
    프로젝트 ID 생성
    
    Returns:
        생성된 프로젝트 ID (예: P_20250130_001)
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"P_{timestamp}"


def calculate_end_date(start_date: str, duration_months: int) -> str:
    """
    종료일 계산
    
    Args:
        start_date: 시작일 (YYYY-MM-DD)
        duration_months: 기간 (개월)
        
    Returns:
        종료일 (YYYY-MM-DD)
    """
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = start + relativedelta(months=duration_months)
    return end.strftime('%Y-%m-%d')


def validate_project_data(data: Dict[str, Any]) -> tuple[bool, str]:
    """
    프로젝트 데이터 유효성 검사
    
    Args:
        data: 프로젝트 데이터
        
    Returns:
        (유효성 여부, 에러 메시지)
    """
    required_fields = [
        'project_name',
        'client_industry',
        'required_skills',
        'duration_months',
        'team_size',
        'start_date'
    ]
    
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"필수 필드 누락: {field}"
    
    # 기간 검증
    if not isinstance(data['duration_months'], int) or data['duration_months'] <= 0:
        return False, "프로젝트 기간은 1개월 이상이어야 합니다"
    
    # 팀 규모 검증
    if not isinstance(data['team_size'], int) or data['team_size'] <= 0:
        return False, "팀 규모는 1명 이상이어야 합니다"
    
    # 기술 목록 검증
    if not isinstance(data['required_skills'], list) or len(data['required_skills']) == 0:
        return False, "최소 1개 이상의 기술이 필요합니다"
    
    # 날짜 형식 검증
    try:
        datetime.strptime(data['start_date'], '%Y-%m-%d')
    except ValueError:
        return False, "시작일 형식이 올바르지 않습니다 (YYYY-MM-DD)"
    
    return True, ""


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda 핸들러 함수
    
    Args:
        event: API Gateway 이벤트
        context: Lambda 컨텍스트
        
    Returns:
        API Gateway 응답
    """
    try:
        logger.info(f"프로젝트 생성 요청 수신: {json.dumps(event)}")
        
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
            logger.error("요청 본문 없음")
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': '요청 본문이 필요합니다',
                    'message': 'Request body is required'
                })
            }
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        logger.info(f"요청 데이터: {json.dumps(body)}")
        
        # 데이터 유효성 검사
        is_valid, error_message = validate_project_data(body)
        if not is_valid:
            logger.error(f"유효성 검사 실패: {error_message}")
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': error_message,
                    'message': 'Validation failed'
                })
            }
        
        # 프로젝트 ID 생성
        project_id = generate_project_id()
        
        # 종료일 계산
        end_date = calculate_end_date(body['start_date'], body['duration_months'])
        
        # 기술 스택 분류 (간단한 휴리스틱 사용)
        backend_techs = []
        frontend_techs = []
        data_techs = []
        infra_techs = []
        
        backend_keywords = ['java', 'spring', 'python', 'django', 'node', 'express', '.net', 'c#']
        frontend_keywords = ['react', 'vue', 'angular', 'javascript', 'typescript', 'html', 'css']
        data_keywords = ['mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'dynamodb', 'elasticsearch']
        infra_keywords = ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins']
        
        for skill in body['required_skills']:
            skill_lower = skill.lower()
            categorized = False
            
            if any(keyword in skill_lower for keyword in backend_keywords):
                backend_techs.append(skill)
                categorized = True
            if any(keyword in skill_lower for keyword in frontend_keywords):
                frontend_techs.append(skill)
                categorized = True
            if any(keyword in skill_lower for keyword in data_keywords):
                data_techs.append(skill)
                categorized = True
            if any(keyword in skill_lower for keyword in infra_keywords):
                infra_techs.append(skill)
                categorized = True
            
            # 분류되지 않은 기술은 백엔드로 기본 분류
            if not categorized:
                backend_techs.append(skill)
        
        # Project 객체 생성
        project = Project(
            project_id=project_id,
            project_name=body['project_name'],
            client_industry=body['client_industry'],
            period=ProjectPeriod(
                start=body['start_date'],
                end=end_date,
                duration_months=body['duration_months']
            ),
            budget_scale=body.get('budget_scale'),
            description=body.get('description'),
            tech_stack=TechStack(
                backend=backend_techs,
                frontend=frontend_techs,
                data=data_techs,
                infra=infra_techs
            ),
            requirements=body['required_skills'],
            team_composition={'required_members': body['team_size']}
        )
        
        # DynamoDB에 저장
        created_project = project_repo.create(project)
        logger.info(f"프로젝트 생성 완료: {project_id}")
        
        # 응답 데이터 생성
        response_data = {
            'project_id': created_project.project_id,
            'project_name': created_project.project_name,
            'client_industry': created_project.client_industry,
            'start_date': created_project.period.start,
            'end_date': created_project.period.end,
            'duration_months': created_project.period.duration_months,
            'required_skills': body['required_skills'],
            'team_size': body['team_size'],
            'budget_scale': created_project.budget_scale,
            'description': created_project.description,
            'status': 'planning',
            'message': '프로젝트가 성공적으로 등록되었습니다'
        }
        
        return {
            'statusCode': 201,
            'headers': headers,
            'body': json.dumps(response_data, ensure_ascii=False)
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON 파싱 오류: {str(e)}")
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({
                'error': 'JSON 형식이 올바르지 않습니다',
                'message': f'Invalid JSON format: {str(e)}'
            })
        }
    
    except Exception as e:
        logger.error(f"프로젝트 생성 실패: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': '프로젝트 생성 중 오류가 발생했습니다',
                'message': str(e)
            })
        }
