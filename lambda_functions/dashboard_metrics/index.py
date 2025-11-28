"""
대시보드 메트릭 집계 Lambda 함수
전체 직원 수, 활성 프로젝트 수, 대기 중인 평가 등의 통계를 집계하여 반환
"""

import json
import os
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Attr
from typing import Dict, List, Any

# DynamoDB 클라이언트 초기화
dynamodb = boto3.resource('dynamodb')

# 테이블 이름 환경 변수에서 가져오기
EMPLOYEES_TABLE = os.environ.get('EMPLOYEES_TABLE', 'Employees')
PROJECTS_TABLE = os.environ.get('PROJECTS_TABLE', 'Projects')
EVALUATIONS_TABLE = os.environ.get('EVALUATIONS_TABLE', 'EmployeeEvaluations')


class DecimalEncoder(json.JSONEncoder):
    """DynamoDB Decimal 타입을 JSON으로 변환하기 위한 인코더"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def get_total_employees() -> int:
    """전체 직원 수 조회"""
    try:
        table = dynamodb.Table(EMPLOYEES_TABLE)
        response = table.scan(Select='COUNT')
        return response.get('Count', 0)
    except Exception as e:
        print(f"Error getting total employees: {str(e)}")
        return 0


def get_active_projects() -> int:
    """진행 중인 프로젝트 수 조회"""
    try:
        table = dynamodb.Table(PROJECTS_TABLE)
        # 프로젝트 상태가 'in-progress'인 것만 카운트
        response = table.scan(
            FilterExpression=Attr('status').eq('in-progress'),
            Select='COUNT'
        )
        return response.get('Count', 0)
    except Exception as e:
        print(f"Error getting active projects: {str(e)}")
        # 상태 필드가 없는 경우 전체 프로젝트 수 반환
        try:
            response = table.scan(Select='COUNT')
            return response.get('Count', 0)
        except:
            return 0


def get_available_employees() -> int:
    """투입 대기 인력 수 조회 (현재 프로젝트에 배정되지 않은 직원)"""
    try:
        table = dynamodb.Table(EMPLOYEES_TABLE)
        response = table.scan(
            FilterExpression=Attr('availability').eq('available')
        )
        return len(response.get('Items', []))
    except Exception as e:
        print(f"Error getting available employees: {str(e)}")
        # availability 필드가 없는 경우 currentProject가 null인 직원 카운트
        try:
            response = table.scan(
                FilterExpression=Attr('currentProject').not_exists() | Attr('currentProject').eq(None)
            )
            return len(response.get('Items', []))
        except:
            return 0


def get_pending_reviews() -> int:
    """검토 필요한 평가 수 조회"""
    try:
        table = dynamodb.Table(EVALUATIONS_TABLE)
        response = table.scan(
            FilterExpression=Attr('status').eq('pending'),
            Select='COUNT'
        )
        return response.get('Count', 0)
    except Exception as e:
        print(f"Error getting pending reviews: {str(e)}")
        return 0


def get_recent_recommendations() -> List[Dict[str, Any]]:
    """최근 인력 추천 목록 조회"""
    # 실제 구현에서는 추천 이력 테이블에서 조회
    # 현재는 샘플 데이터 반환
    return [
        {
            "project": "금융 플랫폼 구축",
            "recommended": 3,
            "match_rate": 95,
            "status": "승인 대기"
        },
        {
            "project": "AI 챗봇 개발",
            "recommended": 2,
            "match_rate": 88,
            "status": "검토 중"
        },
        {
            "project": "물류 시스템 개선",
            "recommended": 4,
            "match_rate": 92,
            "status": "승인됨"
        }
    ]


def get_top_skills() -> List[Dict[str, Any]]:
    """주요 기술 스택 분포 조회"""
    try:
        table = dynamodb.Table(EMPLOYEES_TABLE)
        response = table.scan()
        items = response.get('Items', [])
        
        # 모든 직원의 기술 스택 집계
        skill_counts = {}
        total_employees = len(items)
        
        for employee in items:
            skills = employee.get('skills', [])
            for skill in skills:
                skill_name = skill.get('name', '') if isinstance(skill, dict) else str(skill)
                if skill_name:
                    skill_counts[skill_name] = skill_counts.get(skill_name, 0) + 1
        
        # 상위 5개 기술 추출
        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        top_skills = []
        for skill_name, count in sorted_skills:
            percentage = int((count / total_employees) * 100) if total_employees > 0 else 0
            top_skills.append({
                "name": skill_name,
                "count": count,
                "percentage": percentage
            })
        
        return top_skills
    except Exception as e:
        print(f"Error getting top skills: {str(e)}")
        return []


def lambda_handler(event, context):
    """
    Lambda 핸들러 함수
    대시보드 메트릭을 집계하여 반환
    """
    try:
        # CORS 헤더 설정
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,OPTIONS'
        }
        
        # OPTIONS 요청 처리 (CORS preflight)
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'OK'})
            }
        
        # 메트릭 집계
        total_employees = get_total_employees()
        active_projects = get_active_projects()
        available_employees = get_available_employees()
        pending_reviews = get_pending_reviews()
        recent_recommendations = get_recent_recommendations()
        top_skills = get_top_skills()
        
        # 응답 데이터 구성
        metrics = {
            'total_employees': total_employees,
            'active_projects': active_projects,
            'available_employees': available_employees,
            'pending_reviews': pending_reviews,
            'recent_recommendations': recent_recommendations,
            'top_skills': top_skills
        }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(metrics, cls=DecimalEncoder)
        }
        
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
