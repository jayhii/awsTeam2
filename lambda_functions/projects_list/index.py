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
        items = response.get('Items', [])
        
        # 페이지네이션 처리
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
        
        for item in items:
            # period 객체에서 날짜 추출
            period = item.get('period', {})
            if isinstance(period, dict):
                start_date = period.get('start', '')
                end_date = period.get('end', '')
                duration_months = period.get('duration_months', 0)
            else:
                start_date = item.get('start_date', '')
                end_date = item.get('end_date', '')
                duration_months = 0
            
            # tech_stack에서 required_skills 추출
            required_skills = []
            tech_stack = item.get('tech_stack', {})
            if isinstance(tech_stack, dict):
                for category, skills in tech_stack.items():
                    if isinstance(skills, list):
                        required_skills.extend([str(skill) for skill in skills])
            
            # requirements도 추가
            requirements = item.get('requirements', [])
            if isinstance(requirements, list):
                required_skills.extend([str(req) for req in requirements])
            
            # 팀원 정보 추출 (두 가지 형식 지원)
            team_members = []
            team_size = 0
            
            # 형식 1: team_members (이전 형식 - 상세 정보 포함)
            if 'team_members' in item and item['team_members']:
                team_members = item['team_members']
                team_size = len(team_members) if isinstance(team_members, list) else 0
            
            # 형식 2: team_composition (새 형식 - user_id만 포함)
            elif 'team_composition' in item:
                team_composition = item.get('team_composition', {})
                if isinstance(team_composition, dict):
                    for role, members in team_composition.items():
                        if isinstance(members, list):
                            team_size += len(members)
                            # 각 멤버 ID를 팀원 정보로 변환
                            for member_id in members:
                                team_members.append({
                                    'user_id': member_id,
                                    'role': role
                                })
                        elif isinstance(members, int):
                            team_size += members
            
            # 프로젝트 객체 생성
            project = {
                'project_id': item.get('project_id'),
                'project_name': item.get('project_name', ''),
                'status': item.get('status', 'active'),
                'start_date': start_date,
                'end_date': end_date,
                'duration_months': duration_months,
                'required_skills': list(set(required_skills)),  # 중복 제거
                'description': item.get('description', ''),
                'client_industry': item.get('client_industry', ''),
                'budget_scale': item.get('budget_scale', ''),
                'team_members': team_members,
                'team_size': team_size,
                'tech_stack': tech_stack,
                'requirements': requirements
            }
            
            projects.append(project)
        
        logger.info(f"총 {len(projects)}개의 프로젝트 조회 완료")
        
        return projects
        
    except Exception as e:
        logger.error(f"프로젝트 데이터 조회 실패: {str(e)}", exc_info=True)
        raise


def decimal_default(obj):
    """Decimal을 float로 변환"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError
