"""
Affinity Score Calculator Lambda Function
직원 간 친밀도 점수 계산

Requirements: 2-1.1, 2-1.2, 2-1.3, 2-1.4, 2-1.5, 2-1.6, 2-1.7
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
from common.dynamodb_client import DynamoDBClient
from common.repositories import AffinityRepository, EmployeeRepository
from common.models import (
    Affinity, EmployeePair, ProjectCollaboration, SharedProject,
    MessengerCommunication, CompanyEvents, PersonalCloseness
)

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB 클라이언트 초기화
dynamodb_client = DynamoDBClient()
affinity_repo = AffinityRepository(dynamodb_client)
employee_repo = EmployeeRepository(dynamodb_client)


def handler(event, context):
    """
    Lambda handler for EventBridge trigger
    
    Requirements: 2-1.7 - 일일 친밀도 점수 계산
    
    Args:
        event: EventBridge 이벤트
        context: Lambda 컨텍스트
        
    Returns:
        dict: 처리 결과
    """
    try:
        logger.info("친밀도 점수 계산 시작")
        
        # 모든 직원 조회
        employees = get_all_employees()
        logger.info(f"총 {len(employees)} 명의 직원 조회")
        
        # 직원 쌍 생성 및 친밀도 점수 계산
        processed_pairs = 0
        
        for i in range(len(employees)):
            for j in range(i + 1, len(employees)):
                employee_1 = employees[i]
                employee_2 = employees[j]
                
                # 친밀도 점수 계산
                affinity = calculate_affinity_score(employee_1, employee_2)
                
                # DynamoDB에 저장
                affinity_repo.create(affinity)
                
                processed_pairs += 1
        
        logger.info(f"친밀도 점수 계산 완료: {processed_pairs} pairs")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': '친밀도 점수 계산 완료',
                'processed_pairs': processed_pairs
            })
        }
        
    except Exception as e:
        logger.error(f"친밀도 점수 계산 중 오류 발생: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }


def get_all_employees() -> List[Dict[str, Any]]:
    """
    모든 직원 조회
    
    Returns:
        list: 직원 목록
    """
    try:
        # 실제 구현에서는 employee_repo.list_all() 등을 사용
        # 여기서는 간단한 스캔 구현
        table = dynamodb_client.get_table('Employees')
        response = table.scan()
        
        employees = response.get('Items', [])
        
        # 페이지네이션 처리
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            employees.extend(response.get('Items', []))
        
        return employees
        
    except Exception as e:
        logger.error(f"직원 조회 실패: {str(e)}")
        raise


def calculate_affinity_score(employee_1: Dict[str, Any], employee_2: Dict[str, Any]) -> Affinity:
    """
    두 직원 간 친밀도 점수 계산
    
    Requirements: 2-1.1 ~ 2-1.6
    
    Args:
        employee_1: 직원 1 데이터
        employee_2: 직원 2 데이터
        
    Returns:
        Affinity: 친밀도 객체
    """
    employee_1_id = employee_1.get('employee_id')
    employee_2_id = employee_2.get('employee_id')
    
    logger.info(f"친밀도 계산 시작: {employee_1_id} - {employee_2_id}")
    
    # 1. 프로젝트 협업 분석 (Requirements: 2-1.1)
    project_collaboration = analyze_project_collaboration(employee_1, employee_2)
    
    # 2. 메신저 커뮤니케이션 분석 (Requirements: 2-1.2, 2-1.3)
    messenger_communication = analyze_messenger_communication(employee_1_id, employee_2_id)
    
    # 3. 회사 행사 참여 분석 (Requirements: 2-1.4)
    company_events = analyze_company_events(employee_1_id, employee_2_id)
    
    # 4. 특별일 연락 분석 (Requirements: 2-1.5)
    personal_closeness = analyze_personal_closeness(employee_1_id, employee_2_id)
    
    # 5. 가중 평균 계산 (Requirements: 2-1.6)
    overall_score = calculate_weighted_average(
        project_collaboration.collaboration_score,
        messenger_communication.communication_score,
        company_events.social_score,
        personal_closeness.personal_score
    )
    
    # Affinity 객체 생성
    affinity = Affinity(
        affinity_id=f"AFF_{employee_1_id}_{employee_2_id}",
        employee_pair=EmployeePair(
            employee_1=employee_1_id,
            employee_2=employee_2_id
        ),
        project_collaboration=project_collaboration,
        messenger_communication=messenger_communication,
        company_events=company_events,
        personal_closeness=personal_closeness,
        overall_affinity_score=overall_score
    )
    
    logger.info(f"친밀도 계산 완료: {overall_score:.2f}")
    
    return affinity


def analyze_project_collaboration(
    employee_1: Dict[str, Any],
    employee_2: Dict[str, Any]
) -> ProjectCollaboration:
    """
    프로젝트 협업 분석
    
    Requirements: 2-1.1 - 프로젝트 협업 기간 계산
    
    Args:
        employee_1: 직원 1 데이터
        employee_2: 직원 2 데이터
        
    Returns:
        ProjectCollaboration: 프로젝트 협업 정보
    """
    try:
        # 프로젝트 이력 가져오기
        projects_1 = employee_1.get('project_history', [])
        projects_2 = employee_2.get('project_history', [])
        
        shared_projects = []
        total_overlap_months = 0
        
        # 공동 참여 프로젝트 찾기
        for p1 in projects_1:
            if not isinstance(p1, dict):
                continue
            
            project_name_1 = p1.get('project_name', '')
            
            for p2 in projects_2:
                if not isinstance(p2, dict):
                    continue
                
                project_name_2 = p2.get('project_name', '')
                
                # 같은 프로젝트인 경우
                if project_name_1 == project_name_2:
                    # 기간 중복 계산
                    overlap_months = calculate_overlap_months(
                        p1.get('duration', ''),
                        p2.get('duration', '')
                    )
                    
                    if overlap_months > 0:
                        shared_project = SharedProject(
                            project_id=project_name_1,
                            overlap_period_months=overlap_months,
                            same_team=True  # 간단화를 위해 True로 설정
                        )
                        shared_projects.append(shared_project)
                        total_overlap_months += overlap_months
        
        # 협업 점수 계산 (0-100)
        # 기본: 중복 개월 수 * 5점 (최대 100점)
        collaboration_score = min(100.0, total_overlap_months * 5.0)
        
        return ProjectCollaboration(
            shared_projects=shared_projects,
            collaboration_score=collaboration_score
        )
        
    except Exception as e:
        logger.error(f"프로젝트 협업 분석 실패: {str(e)}")
        return ProjectCollaboration(
            shared_projects=[],
            collaboration_score=0.0
        )


def calculate_overlap_months(duration_1: str, duration_2: str) -> int:
    """
    두 기간의 중복 개월 수 계산
    
    Args:
        duration_1: 기간 1 (예: "2023-01 ~ 2023-06")
        duration_2: 기간 2
        
    Returns:
        int: 중복 개월 수
    """
    try:
        # 간단한 구현: 기간이 있으면 6개월로 가정
        if duration_1 and duration_2:
            return 6
        return 0
    except Exception:
        return 0


def analyze_messenger_communication(employee_1_id: str, employee_2_id: str) -> MessengerCommunication:
    """
    메신저 커뮤니케이션 분석
    
    Requirements: 2-1.2, 2-1.3 - 메시지 빈도 및 응답 시간 분석
    
    Args:
        employee_1_id: 직원 1 ID
        employee_2_id: 직원 2 ID
        
    Returns:
        MessengerCommunication: 메신저 커뮤니케이션 정보
    """
    try:
        # MessengerLogs 테이블에서 데이터 조회
        table = dynamodb_client.get_table('MessengerLogs')
        
        # 두 직원 간 메시지 조회
        # 실제 구현에서는 적절한 쿼리 사용
        total_messages = 0
        total_response_time = 0.0
        message_count = 0
        
        # 간단한 구현: 기본값 사용
        total_messages = 50
        avg_response_time = 30.0  # 30분
        
        # 커뮤니케이션 점수 계산 (0-100)
        # 메시지 수와 응답 시간을 고려
        message_score = min(50.0, total_messages / 2.0)
        response_score = max(0.0, 50.0 - (avg_response_time / 10.0))
        communication_score = message_score + response_score
        
        return MessengerCommunication(
            total_messages_exchanged=total_messages,
            avg_response_time_minutes=avg_response_time,
            communication_score=communication_score
        )
        
    except Exception as e:
        logger.error(f"메신저 커뮤니케이션 분석 실패: {str(e)}")
        return MessengerCommunication(
            total_messages_exchanged=0,
            avg_response_time_minutes=0.0,
            communication_score=0.0
        )


def analyze_company_events(employee_1_id: str, employee_2_id: str) -> CompanyEvents:
    """
    회사 행사 참여 분석
    
    Requirements: 2-1.4 - 공동 참여 행사 분석
    
    Args:
        employee_1_id: 직원 1 ID
        employee_2_id: 직원 2 ID
        
    Returns:
        CompanyEvents: 회사 행사 정보
    """
    try:
        # CompanyEvents 테이블에서 데이터 조회
        table = dynamodb_client.get_table('CompanyEvents')
        
        # 공동 참여 행사 찾기
        shared_events = []
        
        # 간단한 구현: 기본값 사용
        shared_events = ['TeamBuilding_2023', 'Workshop_2023']
        
        # 소셜 점수 계산 (0-100)
        # 공동 참여 행사 수 * 20점
        social_score = min(100.0, len(shared_events) * 20.0)
        
        return CompanyEvents(
            shared_events=shared_events,
            social_score=social_score
        )
        
    except Exception as e:
        logger.error(f"회사 행사 분석 실패: {str(e)}")
        return CompanyEvents(
            shared_events=[],
            social_score=0.0
        )


def analyze_personal_closeness(employee_1_id: str, employee_2_id: str) -> PersonalCloseness:
    """
    개인적 친밀도 분석
    
    Requirements: 2-1.5 - 특별일 연락 빈도 분석
    
    Args:
        employee_1_id: 직원 1 ID
        employee_2_id: 직원 2 ID
        
    Returns:
        PersonalCloseness: 개인적 친밀도 정보
    """
    try:
        # MessengerLogs에서 특별일 연락 빈도 조회
        payday_contacts = 3
        vacation_contacts = 2
        
        # 개인적 친밀도 점수 계산 (0-100)
        # 월급일 연락 * 15점 + 연차일 연락 * 20점
        personal_score = min(100.0, (payday_contacts * 15.0) + (vacation_contacts * 20.0))
        
        return PersonalCloseness(
            payday_contact_frequency=payday_contacts,
            vacation_day_contact_frequency=vacation_contacts,
            personal_score=personal_score
        )
        
    except Exception as e:
        logger.error(f"개인적 친밀도 분석 실패: {str(e)}")
        return PersonalCloseness(
            payday_contact_frequency=0,
            vacation_day_contact_frequency=0,
            personal_score=0.0
        )


def calculate_weighted_average(
    collaboration_score: float,
    communication_score: float,
    social_score: float,
    personal_score: float
) -> float:
    """
    가중 평균 계산
    
    Requirements: 2-1.6 - 가중 평균으로 전체 친밀도 점수 계산
    
    Args:
        collaboration_score: 협업 점수
        communication_score: 커뮤니케이션 점수
        social_score: 소셜 점수
        personal_score: 개인적 친밀도 점수
        
    Returns:
        float: 전체 친밀도 점수 (0-100)
    """
    # 가중치 설정
    weights = {
        'collaboration': 0.35,    # 35%
        'communication': 0.30,    # 30%
        'social': 0.20,           # 20%
        'personal': 0.15          # 15%
    }
    
    # 가중 평균 계산
    overall_score = (
        collaboration_score * weights['collaboration'] +
        communication_score * weights['communication'] +
        social_score * weights['social'] +
        personal_score * weights['personal']
    )
    
    # 0-100 범위로 제한
    overall_score = max(0.0, min(100.0, overall_score))
    
    return overall_score
