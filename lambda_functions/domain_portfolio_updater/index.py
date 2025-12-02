"""
Domain Portfolio Updater Lambda Function
신규 프로젝트/직원 추가 시 도메인 포트폴리오 자동 업데이트

Requirements: 실시간 도메인 분석 업데이트
"""

import json
import logging
import os
from typing import Dict, Any, List, Set
from decimal import Decimal
import boto3

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS 클라이언트 초기화
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-2'))


def handler(event, context):
    """
    Lambda handler for DynamoDB Stream events
    
    Args:
        event: DynamoDB Stream 이벤트
        context: Lambda 컨텍스트
        
    Returns:
        dict: 처리 결과
    """
    try:
        logger.info(f"도메인 포트폴리오 업데이트 시작: {len(event.get('Records', []))}개 레코드")
        
        processed_count = 0
        
        for record in event.get('Records', []):
            event_name = record.get('eventName')
            
            # INSERT 또는 MODIFY 이벤트만 처리
            if event_name in ['INSERT', 'MODIFY']:
                table_name = record['eventSourceARN'].split('/')[1]
                
                if table_name == 'Projects':
                    process_project_change(record)
                    processed_count += 1
                elif table_name == 'Employees':
                    process_employee_change(record)
                    processed_count += 1
        
        logger.info(f"도메인 포트폴리오 업데이트 완료: {processed_count}개 처리")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'processed': processed_count
            })
        }
        
    except Exception as e:
        logger.error(f"도메인 포트폴리오 업데이트 실패: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def process_project_change(record: Dict[str, Any]):
    """
    프로젝트 변경 처리
    
    Args:
        record: DynamoDB Stream 레코드
    """
    try:
        new_image = record['dynamodb'].get('NewImage', {})
        
        # DynamoDB 형식에서 Python 객체로 변환
        project = deserialize_dynamodb_item(new_image)
        
        project_id = project.get('project_id')
        knowledge_domain = project.get('knowledge_domain')
        tech_domains = project.get('tech_domains', [])
        
        logger.info(f"프로젝트 변경 감지: {project_id} - {knowledge_domain}")
        
        # 1. 지식 도메인 통계 업데이트
        if knowledge_domain:
            update_knowledge_domain_stats(knowledge_domain, 'project_added')
        
        # 2. 기술 도메인 통계 업데이트
        for tech_domain in tech_domains:
            update_tech_domain_stats(tech_domain, 'project_added')
        
        # 3. 도메인 간 연관성 분석
        analyze_domain_relationships(knowledge_domain, tech_domains)
        
    except Exception as e:
        logger.error(f"프로젝트 변경 처리 실패: {str(e)}")


def process_employee_change(record: Dict[str, Any]):
    """
    직원 변경 처리
    
    Args:
        record: DynamoDB Stream 레코드
    """
    try:
        new_image = record['dynamodb'].get('NewImage', {})
        
        # DynamoDB 형식에서 Python 객체로 변환
        employee = deserialize_dynamodb_item(new_image)
        
        user_id = employee.get('user_id')
        skills = employee.get('skills', [])
        domain_experience = employee.get('domain_experience', {})
        
        logger.info(f"직원 변경 감지: {user_id}")
        
        # 1. 보유 기술 분석
        tech_skills = extract_tech_skills(skills)
        
        # 2. 진입 가능한 도메인 분석
        accessible_domains = analyze_accessible_domains(tech_skills, domain_experience)
        
        # 3. 도메인별 인력 통계 업데이트
        for domain in accessible_domains:
            update_domain_workforce(domain, user_id)
        
    except Exception as e:
        logger.error(f"직원 변경 처리 실패: {str(e)}")


def update_knowledge_domain_stats(domain: str, action: str):
    """
    지식 도메인 통계 업데이트
    
    Args:
        domain: 도메인 이름
        action: 액션 (project_added, project_removed)
    """
    try:
        # Projects 테이블에서 해당 도메인 프로젝트 수 계산
        projects_table = dynamodb.Table('Projects')
        
        response = projects_table.scan(
            FilterExpression='knowledge_domain = :domain',
            ExpressionAttributeValues={':domain': domain}
        )
        
        project_count = len(response.get('Items', []))
        
        # Employees 테이블에서 해당 도메인 경험 보유 인력 수 계산
        employees_table = dynamodb.Table('Employees')
        
        response = employees_table.scan()
        employees = response.get('Items', [])
        
        expert_count = 0
        for emp in employees:
            domain_exp = emp.get('domain_experience', {})
            knowledge_domains = domain_exp.get('knowledge_domains', [])
            
            for kd in knowledge_domains:
                if isinstance(kd, dict) and kd.get('domain') == domain:
                    expert_count += 1
                    break
        
        # 도메인 포트폴리오 업데이트 (테이블이 있다면)
        try:
            portfolio_table = dynamodb.Table('DomainPortfolio')
            portfolio_id = f'KD_{domain}'
            
            portfolio_table.update_item(
                Key={'portfolio_id': portfolio_id},
                UpdateExpression='SET current_projects = :projects, available_experts = :experts, last_updated = :timestamp',
                ExpressionAttributeValues={
                    ':projects': Decimal(str(project_count)),
                    ':experts': Decimal(str(expert_count)),
                    ':timestamp': datetime.now().isoformat()
                }
            )
            
            logger.info(f"지식 도메인 통계 업데이트: {domain} - 프로젝트: {project_count}, 전문가: {expert_count}")
            
        except Exception as e:
            logger.warning(f"DomainPortfolio 테이블 업데이트 실패: {str(e)}")
            
    except Exception as e:
        logger.error(f"지식 도메인 통계 업데이트 실패: {str(e)}")


def update_tech_domain_stats(tech_domain: str, action: str):
    """
    기술 도메인 통계 업데이트
    
    Args:
        tech_domain: 기술 도메인 이름
        action: 액션
    """
    try:
        # Projects 테이블에서 해당 기술 도메인 사용 프로젝트 수 계산
        projects_table = dynamodb.Table('Projects')
        
        response = projects_table.scan()
        projects = response.get('Items', [])
        
        project_count = 0
        for project in projects:
            tech_domains = project.get('tech_domains', [])
            if tech_domain in tech_domains:
                project_count += 1
        
        logger.info(f"기술 도메인 통계: {tech_domain} - 프로젝트: {project_count}")
        
    except Exception as e:
        logger.error(f"기술 도메인 통계 업데이트 실패: {str(e)}")


def analyze_domain_relationships(knowledge_domain: str, tech_domains: List[str]):
    """
    도메인 간 연관성 분석
    
    Args:
        knowledge_domain: 지식 도메인
        tech_domains: 기술 도메인 목록
    """
    try:
        # 도메인 조합 패턴 저장 (향후 추천에 활용)
        logger.info(f"도메인 연관성: {knowledge_domain} <-> {tech_domains}")
        
    except Exception as e:
        logger.error(f"도메인 연관성 분석 실패: {str(e)}")


def extract_tech_skills(skills: List[Dict]) -> Set[str]:
    """
    직원 기술에서 기술 이름 추출
    
    Args:
        skills: 기술 목록
        
    Returns:
        set: 기술 이름 집합
    """
    tech_skills = set()
    
    for skill in skills:
        if isinstance(skill, dict):
            skill_name = skill.get('name', '')
            if skill_name:
                tech_skills.add(skill_name)
    
    return tech_skills


def analyze_accessible_domains(tech_skills: Set[str], domain_experience: Dict) -> List[str]:
    """
    진입 가능한 도메인 분석
    
    Args:
        tech_skills: 보유 기술
        domain_experience: 도메인 경험
        
    Returns:
        list: 진입 가능한 도메인 목록
    """
    accessible = []
    
    # 기존 도메인 경험
    knowledge_domains = domain_experience.get('knowledge_domains', [])
    for kd in knowledge_domains:
        if isinstance(kd, dict):
            accessible.append(kd.get('domain'))
    
    # 기술 기반 도메인 매칭 (간단한 규칙)
    if 'Java' in tech_skills or 'Spring' in tech_skills:
        if 'Finance' not in accessible:
            accessible.append('Finance')
    
    if 'Python' in tech_skills or 'TensorFlow' in tech_skills:
        if 'Healthcare' not in accessible:
            accessible.append('Healthcare')
    
    return accessible


def update_domain_workforce(domain: str, user_id: str):
    """
    도메인별 인력 통계 업데이트
    
    Args:
        domain: 도메인 이름
        user_id: 직원 ID
    """
    try:
        logger.info(f"도메인 인력 업데이트: {domain} - {user_id}")
        
    except Exception as e:
        logger.error(f"도메인 인력 업데이트 실패: {str(e)}")


def deserialize_dynamodb_item(item: Dict) -> Dict:
    """
    DynamoDB 형식을 Python 객체로 변환
    
    Args:
        item: DynamoDB 형식 아이템
        
    Returns:
        dict: Python 객체
    """
    result = {}
    
    for key, value in item.items():
        if 'S' in value:
            result[key] = value['S']
        elif 'N' in value:
            result[key] = Decimal(value['N'])
        elif 'L' in value:
            result[key] = [deserialize_value(v) for v in value['L']]
        elif 'M' in value:
            result[key] = deserialize_dynamodb_item(value['M'])
        elif 'BOOL' in value:
            result[key] = value['BOOL']
    
    return result


def deserialize_value(value: Dict) -> Any:
    """DynamoDB 값 변환"""
    if 'S' in value:
        return value['S']
    elif 'N' in value:
        return Decimal(value['N'])
    elif 'M' in value:
        return deserialize_dynamodb_item(value['M'])
    elif 'L' in value:
        return [deserialize_value(v) for v in value['L']]
    return None


from datetime import datetime
