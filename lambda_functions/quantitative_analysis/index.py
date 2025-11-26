"""
Quantitative Analysis Lambda Function
정량적 인력 평가

Requirements: 3.2, 3.3
"""

import json
import logging
import os
from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime
import boto3

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS 클라이언트 초기화
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-2'))


def handler(event, context):
    """
    Lambda handler for API Gateway
    
    Requirements: 3.2 - 정량적 인력 평가
    
    Args:
        event: API Gateway 이벤트
        context: Lambda 컨텍스트
        
    Returns:
        dict: API Gateway 응답
    """
    try:
        logger.info(f"정량적 분석 요청 수신: {json.dumps(event)}")
        
        # 요청 본문 파싱
        body = json.loads(event.get('body', '{}'))
        
        # 입력 검증
        if not body.get('user_id'):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'user_id가 필요합니다'})
            }
        
        user_id = body['user_id']
        
        logger.info(f"직원 {user_id}에 대한 정량적 분석 시작")
        
        # 직원 데이터 조회
        employee = fetch_employee_data(user_id)
        
        if not employee:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': '직원을 찾을 수 없습니다'})
            }
        
        # 정량적 분석 수행
        analysis_result = perform_quantitative_analysis(employee)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(analysis_result, default=decimal_default)
        }
        
    except Exception as e:
        logger.error(f"정량적 분석 중 오류 발생: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }


def fetch_employee_data(user_id: str) -> Dict[str, Any]:
    """
    직원 데이터 조회
    
    Args:
        user_id: 직원 ID
        
    Returns:
        dict: 직원 데이터
    """
    try:
        table = dynamodb.Table('Employees')
        response = table.get_item(Key={'user_id': user_id})
        
        return response.get('Item')
        
    except Exception as e:
        logger.error(f"직원 데이터 조회 실패: {str(e)}")
        return None


def perform_quantitative_analysis(employee: Dict[str, Any]) -> Dict[str, Any]:
    """
    정량적 분석 수행
    
    Requirements: 3.2, 3.3
    
    Args:
        employee: 직원 데이터
        
    Returns:
        dict: 분석 결과
    """
    user_id = employee.get('user_id')
    
    # 1. 경력 지표 계산 (Requirements: 3.2)
    experience_metrics = calculate_experience_metrics(employee)
    
    # 2. 기술 트렌드 데이터 통합 (Requirements: 3.2, 12.3)
    tech_evaluation = evaluate_tech_stack(employee)
    
    # 3. 프로젝트 경험 점수 계산 (Requirements: 3.3)
    project_scores = calculate_project_experience_scores(employee)
    
    # 4. 종합 점수 계산
    overall_score = calculate_overall_quantitative_score(
        experience_metrics,
        tech_evaluation,
        project_scores
    )
    
    return {
        'user_id': user_id,
        'name': employee.get('basic_info', {}).get('name', ''),
        'experience_metrics': experience_metrics,
        'tech_evaluation': tech_evaluation,
        'project_scores': project_scores,
        'overall_score': overall_score
    }


def calculate_experience_metrics(employee: Dict[str, Any]) -> Dict[str, Any]:
    """
    경력 지표 계산
    
    Requirements: 3.2 - 경력 연수, 프로젝트 수, 기술 다양성
    
    Args:
        employee: 직원 데이터
        
    Returns:
        dict: 경력 지표
    """
    basic_info = employee.get('basic_info', {})
    
    # 경력 연수
    years_of_experience = basic_info.get('years_of_experience', 0)
    if isinstance(years_of_experience, Decimal):
        years_of_experience = float(years_of_experience)
    
    # 프로젝트 수
    work_experience = employee.get('work_experience', [])
    project_count = len(work_experience) if isinstance(work_experience, list) else 0
    
    # 기술 다양성
    skills = employee.get('skills', [])
    skill_diversity = len(skills) if isinstance(skills, list) else 0
    
    # 기술 레벨 분포
    skill_levels = {}
    for skill in skills:
        if isinstance(skill, dict):
            level = skill.get('level', 'Unknown')
            skill_levels[level] = skill_levels.get(level, 0) + 1
    
    # 경력 점수 계산 (0-100)
    experience_score = min(100, (years_of_experience / 20) * 100)  # 20년 = 100점
    project_score = min(100, (project_count / 10) * 100)  # 10개 프로젝트 = 100점
    diversity_score = min(100, (skill_diversity / 15) * 100)  # 15개 기술 = 100점
    
    return {
        'years_of_experience': years_of_experience,
        'project_count': project_count,
        'skill_diversity': skill_diversity,
        'skill_levels': skill_levels,
        'experience_score': round(experience_score, 2),
        'project_score': round(project_score, 2),
        'diversity_score': round(diversity_score, 2)
    }


def evaluate_tech_stack(employee: Dict[str, Any]) -> Dict[str, Any]:
    """
    기술 스택 평가
    
    Requirements: 3.2, 12.3 - 기술 최신성 및 시장 수요 평가
    
    Args:
        employee: 직원 데이터
        
    Returns:
        dict: 기술 스택 평가 결과
    """
    skills = employee.get('skills', [])
    
    # 기술 트렌드 데이터 조회
    tech_trends = fetch_tech_trends()
    
    # 각 기술 평가
    skill_evaluations = []
    total_trend_score = 0
    total_demand_score = 0
    
    for skill in skills:
        if not isinstance(skill, dict):
            continue
        
        skill_name = skill.get('name', '')
        skill_years = skill.get('years', 0)
        if isinstance(skill_years, Decimal):
            skill_years = float(skill_years)
        
        # 트렌드 데이터 조회
        trend_data = tech_trends.get(skill_name, {})
        trend_score = trend_data.get('trend_score', 50)
        market_demand = trend_data.get('market_demand', 50)
        
        # 최신성 점수 (경험 연수가 적을수록 최신)
        recency_score = max(0, 100 - (skill_years * 10))
        
        skill_evaluations.append({
            'skill_name': skill_name,
            'years': skill_years,
            'trend_score': trend_score,
            'market_demand': market_demand,
            'recency_score': recency_score
        })
        
        total_trend_score += trend_score
        total_demand_score += market_demand
    
    # 평균 점수 계산
    num_skills = len(skill_evaluations)
    avg_trend_score = total_trend_score / num_skills if num_skills > 0 else 0
    avg_demand_score = total_demand_score / num_skills if num_skills > 0 else 0
    
    # 종합 기술 스택 점수
    tech_stack_score = (avg_trend_score * 0.5 + avg_demand_score * 0.5)
    
    return {
        'skill_evaluations': skill_evaluations,
        'avg_trend_score': round(avg_trend_score, 2),
        'avg_demand_score': round(avg_demand_score, 2),
        'tech_stack_score': round(tech_stack_score, 2)
    }


def fetch_tech_trends() -> Dict[str, Dict[str, float]]:
    """
    기술 트렌드 데이터 조회
    
    Returns:
        dict: 기술별 트렌드 데이터
    """
    try:
        table = dynamodb.Table('TechTrends')
        response = table.scan()
        
        trends = {}
        for item in response.get('Items', []):
            tech_name = item.get('tech_name')
            if tech_name:
                trends[tech_name] = {
                    'trend_score': float(item.get('trend_score', 50)),
                    'market_demand': float(item.get('market_demand', 50))
                }
        
        return trends
        
    except Exception as e:
        logger.error(f"기술 트렌드 조회 실패: {str(e)}")
        return {}


def calculate_project_experience_scores(employee: Dict[str, Any]) -> Dict[str, Any]:
    """
    프로젝트 경험 점수 계산
    
    Requirements: 3.3 - 프로젝트 규모, 역할, 성과 평가
    
    Args:
        employee: 직원 데이터
        
    Returns:
        dict: 프로젝트 경험 점수
    """
    work_experience = employee.get('work_experience', [])
    
    if not isinstance(work_experience, list) or len(work_experience) == 0:
        return {
            'project_evaluations': [],
            'avg_scale_score': 0,
            'avg_role_score': 0,
            'avg_performance_score': 0,
            'project_experience_score': 0
        }
    
    project_evaluations = []
    total_scale_score = 0
    total_role_score = 0
    total_performance_score = 0
    
    for project in work_experience:
        if not isinstance(project, dict):
            continue
        
        # 프로젝트 규모 평가
        scale_score = evaluate_project_scale(project)
        
        # 역할 평가
        role_score = evaluate_project_role(project)
        
        # 성과 평가
        performance_score = evaluate_project_performance(project)
        
        project_evaluations.append({
            'project_name': project.get('project_name', ''),
            'role': project.get('role', ''),
            'scale_score': scale_score,
            'role_score': role_score,
            'performance_score': performance_score
        })
        
        total_scale_score += scale_score
        total_role_score += role_score
        total_performance_score += performance_score
    
    # 평균 점수 계산
    num_projects = len(project_evaluations)
    avg_scale_score = total_scale_score / num_projects
    avg_role_score = total_role_score / num_projects
    avg_performance_score = total_performance_score / num_projects
    
    # 종합 프로젝트 경험 점수
    project_experience_score = (
        avg_scale_score * 0.3 +
        avg_role_score * 0.4 +
        avg_performance_score * 0.3
    )
    
    return {
        'project_evaluations': project_evaluations,
        'avg_scale_score': round(avg_scale_score, 2),
        'avg_role_score': round(avg_role_score, 2),
        'avg_performance_score': round(avg_performance_score, 2),
        'project_experience_score': round(project_experience_score, 2)
    }


def evaluate_project_scale(project: Dict[str, Any]) -> float:
    """
    프로젝트 규모 평가
    
    Args:
        project: 프로젝트 데이터
        
    Returns:
        float: 규모 점수 (0-100)
    """
    # 간단한 구현: 프로젝트 기간과 팀 크기로 평가
    duration = project.get('duration', '')
    
    # 기간에서 개월 수 추출 (간단한 구현)
    if '~' in duration:
        # 예: "2023-01 ~ 2023-12" -> 12개월
        months = 12  # 기본값
    else:
        months = 6  # 기본값
    
    # 규모 점수 (최대 24개월 = 100점)
    scale_score = min(100, (months / 24) * 100)
    
    return scale_score


def evaluate_project_role(project: Dict[str, Any]) -> float:
    """
    프로젝트 역할 평가
    
    Args:
        project: 프로젝트 데이터
        
    Returns:
        float: 역할 점수 (0-100)
    """
    role = project.get('role', '').lower()
    
    # 역할별 점수
    role_scores = {
        'lead': 100,
        'architect': 95,
        'principal': 90,
        'senior': 80,
        'manager': 85,
        'developer': 70,
        'engineer': 70,
        'junior': 50
    }
    
    # 역할 키워드 매칭
    for keyword, score in role_scores.items():
        if keyword in role:
            return score
    
    return 60  # 기본 점수


def evaluate_project_performance(project: Dict[str, Any]) -> float:
    """
    프로젝트 성과 평가
    
    Args:
        project: 프로젝트 데이터
        
    Returns:
        float: 성과 점수 (0-100)
    """
    performance_result = project.get('performance_result', '')
    
    # 성과 키워드 기반 점수
    positive_keywords = ['성공', '완료', '달성', '개선', '증가', '향상', '우수']
    negative_keywords = ['지연', '실패', '문제', '감소']
    
    score = 70  # 기본 점수
    
    for keyword in positive_keywords:
        if keyword in performance_result:
            score += 5
    
    for keyword in negative_keywords:
        if keyword in performance_result:
            score -= 10
    
    return max(0, min(100, score))


def calculate_overall_quantitative_score(
    experience_metrics: Dict[str, Any],
    tech_evaluation: Dict[str, Any],
    project_scores: Dict[str, Any]
) -> float:
    """
    종합 정량적 점수 계산
    
    Args:
        experience_metrics: 경력 지표
        tech_evaluation: 기술 스택 평가
        project_scores: 프로젝트 경험 점수
        
    Returns:
        float: 종합 점수 (0-100)
    """
    # 가중 평균
    overall_score = (
        experience_metrics['experience_score'] * 0.2 +
        experience_metrics['project_score'] * 0.15 +
        experience_metrics['diversity_score'] * 0.15 +
        tech_evaluation['tech_stack_score'] * 0.25 +
        project_scores['project_experience_score'] * 0.25
    )
    
    return round(overall_score, 2)


def decimal_default(obj):
    """Decimal을 float로 변환"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError
