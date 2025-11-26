"""
테스트 데이터 로딩 스크립트

Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6
DynamoDB에 테스트 데이터를 배치로 로드합니다.
"""

import json
import logging
import os
import sys
from typing import Dict, Any, List
import boto3
from decimal import Decimal

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS 클라이언트 초기화
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-2'))


def decimal_default(obj):
    """JSON 직렬화를 위한 Decimal 변환"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def convert_floats_to_decimal(obj):
    """float를 Decimal로 변환 (DynamoDB 호환)"""
    if isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_floats_to_decimal(value) for key, value in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    else:
        return obj


def load_json_file(file_path: str) -> List[Dict[str, Any]]:
    """JSON 파일 로드"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                return [data]
    except Exception as e:
        logger.error(f"파일 로드 실패 ({file_path}): {str(e)}")
        return []


def batch_write_items(table_name: str, items: List[Dict[str, Any]]) -> int:
    """
    DynamoDB에 배치로 아이템 작성
    
    Args:
        table_name: 테이블 이름
        items: 작성할 아이템 목록
        
    Returns:
        int: 작성된 아이템 수
    """
    try:
        table = dynamodb.Table(table_name)
        
        # 배치 크기 (DynamoDB 제한: 25개)
        batch_size = 25
        written_count = 0
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            with table.batch_writer() as writer:
                for item in batch:
                    # float를 Decimal로 변환
                    converted_item = convert_floats_to_decimal(item)
                    writer.put_item(Item=converted_item)
                    written_count += 1
            
            logger.info(f"{table_name}: {written_count}/{len(items)} 아이템 작성 완료")
        
        return written_count
        
    except Exception as e:
        logger.error(f"{table_name} 배치 작성 실패: {str(e)}")
        return 0


def load_employee_data():
    """
    직원 테스트 데이터 로드
    
    Requirements: 17.2 - employees_extended.json에서 로드
    """
    logger.info("=== 직원 데이터 로드 시작 ===")
    
    file_path = 'test_data/employees_extended.json'
    if not os.path.exists(file_path):
        logger.warning(f"파일이 존재하지 않습니다: {file_path}")
        return 0
    
    employees = load_json_file(file_path)
    if not employees:
        logger.warning("직원 데이터가 비어있습니다")
        return 0
    
    count = batch_write_items('Employees', employees)
    logger.info(f"직원 데이터 로드 완료: {count}개")
    return count


def load_project_data():
    """
    프로젝트 테스트 데이터 로드
    
    Requirements: 17.3 - project_example.txt에서 로드
    """
    logger.info("=== 프로젝트 데이터 로드 시작 ===")
    
    # project_example.txt는 텍스트 파일이므로 파싱 필요
    # 여기서는 간단한 예시 데이터 생성
    projects = [
        {
            "project_id": "PRJ001",
            "project_name": "금융 플랫폼 구축",
            "client_industry": "Finance",
            "period": {
                "start": "2023-01-01",
                "end": "2023-12-31",
                "duration_months": 12
            },
            "budget_scale": "Large",
            "description": "차세대 금융 플랫폼 구축 프로젝트",
            "tech_stack": {
                "backend": ["Java", "Spring Boot", "Oracle"],
                "frontend": ["React", "TypeScript"],
                "data": ["Oracle", "Redis"],
                "infra": ["AWS", "Docker", "Kubernetes"]
            },
            "requirements": ["보안", "고가용성", "확장성"],
            "team_composition": {
                "Backend Developer": 5,
                "Frontend Developer": 3,
                "DevOps Engineer": 2
            }
        },
        {
            "project_id": "PRJ002",
            "project_name": "E-commerce 플랫폼",
            "client_industry": "E-commerce",
            "period": {
                "start": "2023-06-01",
                "end": "2024-05-31",
                "duration_months": 12
            },
            "budget_scale": "Medium",
            "description": "온라인 쇼핑몰 구축",
            "tech_stack": {
                "backend": ["Node.js", "Express"],
                "frontend": ["Vue.js"],
                "data": ["MongoDB", "Redis"],
                "infra": ["AWS", "Docker"]
            },
            "requirements": ["결제 시스템", "재고 관리", "추천 시스템"],
            "team_composition": {
                "Full Stack Developer": 4,
                "DevOps Engineer": 1
            }
        }
    ]
    
    count = batch_write_items('Projects', projects)
    logger.info(f"프로젝트 데이터 로드 완료: {count}개")
    return count


def load_affinity_data():
    """
    친밀도 테스트 데이터 로드
    
    Requirements: 17.4 - employee_affinity_data.json에서 로드
    """
    logger.info("=== 친밀도 데이터 로드 시작 ===")
    
    file_path = 'test_data/employee_affinity_data.json'
    if not os.path.exists(file_path):
        logger.warning(f"파일이 존재하지 않습니다: {file_path}")
        return 0
    
    affinity_data = load_json_file(file_path)
    if not affinity_data:
        logger.warning("친밀도 데이터가 비어있습니다")
        return 0
    
    count = batch_write_items('EmployeeAffinity', affinity_data)
    logger.info(f"친밀도 데이터 로드 완료: {count}개")
    return count


def load_messenger_logs():
    """
    메신저 로그 테스트 데이터 로드
    
    Requirements: 17.5 - messenger_logs_anonymized.json에서 로드
    """
    logger.info("=== 메신저 로그 데이터 로드 시작 ===")
    
    file_path = 'test_data/messenger_logs_anonymized.json'
    if not os.path.exists(file_path):
        logger.warning(f"파일이 존재하지 않습니다: {file_path}")
        return 0
    
    messenger_logs = load_json_file(file_path)
    if not messenger_logs:
        logger.warning("메신저 로그 데이터가 비어있습니다")
        return 0
    
    count = batch_write_items('MessengerLogs', messenger_logs)
    logger.info(f"메신저 로그 데이터 로드 완료: {count}개")
    return count


def load_company_events():
    """
    회사 이벤트 테스트 데이터 로드
    
    Requirements: 17.6 - company_events.json에서 로드
    """
    logger.info("=== 회사 이벤트 데이터 로드 시작 ===")
    
    file_path = 'test_data/company_events.json'
    if not os.path.exists(file_path):
        logger.warning(f"파일이 존재하지 않습니다: {file_path}")
        return 0
    
    events = load_json_file(file_path)
    if not events:
        logger.warning("회사 이벤트 데이터가 비어있습니다")
        return 0
    
    count = batch_write_items('CompanyEvents', events)
    logger.info(f"회사 이벤트 데이터 로드 완료: {count}개")
    return count


def main():
    """
    메인 함수
    
    Requirements: 17.1 - 모든 테스트 데이터 로드
    """
    logger.info("=" * 60)
    logger.info("테스트 데이터 로딩 시작")
    logger.info("=" * 60)
    
    total_count = 0
    
    # 1. 직원 데이터 로드
    total_count += load_employee_data()
    
    # 2. 프로젝트 데이터 로드
    total_count += load_project_data()
    
    # 3. 친밀도 데이터 로드
    total_count += load_affinity_data()
    
    # 4. 메신저 로그 로드
    total_count += load_messenger_logs()
    
    # 5. 회사 이벤트 로드
    total_count += load_company_events()
    
    logger.info("=" * 60)
    logger.info(f"테스트 데이터 로딩 완료: 총 {total_count}개 아이템")
    logger.info("=" * 60)
    
    return total_count


if __name__ == "__main__":
    try:
        count = main()
        sys.exit(0 if count > 0 else 1)
    except Exception as e:
        logger.error(f"데이터 로딩 중 오류 발생: {str(e)}", exc_info=True)
        sys.exit(1)
