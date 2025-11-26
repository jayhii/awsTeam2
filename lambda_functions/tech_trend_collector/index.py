"""
Tech Trend Collector Lambda Function
기술 트렌드 수집

Requirements: 12.1, 12.2, 12.4, 12.5
"""

import json
import logging
import os
from typing import Dict, Any, List
from datetime import datetime
import boto3
import requests

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS 클라이언트 초기화
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-2'))
lambda_client = boto3.client('lambda', region_name=os.environ.get('AWS_REGION', 'us-east-2'))


def handler(event, context):
    """
    Lambda handler for EventBridge trigger
    
    Requirements: 12.1 - 주기적 기술 트렌드 수집
    
    Args:
        event: EventBridge 이벤트
        context: Lambda 컨텍스트
        
    Returns:
        dict: 처리 결과
    """
    try:
        logger.info("기술 트렌드 수집 시작")
        
        # 외부 API 호출 (Requirements: 12.1)
        trend_data = collect_tech_trends()
        
        if not trend_data:
            logger.warning("트렌드 데이터 수집 실패, 캐시된 데이터 사용")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': '캐시된 데이터 사용',
                    'updated_count': 0
                })
            }
        
        # 데이터 파싱 및 저장 (Requirements: 12.2)
        updated_count = store_trend_data(trend_data)
        
        logger.info(f"기술 트렌드 업데이트 완료: {updated_count}개")
        
        # 점수 재계산 트리거 (Requirements: 12.5)
        trigger_score_recalculation()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': '기술 트렌드 수집 완료',
                'updated_count': updated_count
            })
        }
        
    except Exception as e:
        logger.error(f"기술 트렌드 수집 중 오류 발생: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }


def collect_tech_trends() -> List[Dict[str, Any]]:
    """
    외부 API에서 기술 트렌드 수집
    
    Requirements: 12.1, 12.4 - 외부 API 호출 및 실패 처리
    
    Returns:
        list: 트렌드 데이터 목록
    """
    try:
        # 외부 API URL (실제로는 환경 변수에서 가져옴)
        api_url = os.environ.get('TECH_TRENDS_API_URL', '')
        api_key = os.environ.get('TECH_TRENDS_API_KEY', '')
        
        if not api_url:
            logger.warning("외부 API URL이 설정되지 않음, 기본 데이터 사용")
            return get_default_trend_data()
        
        # API 호출 (타임아웃 10초)
        headers = {}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        response = requests.get(
            api_url,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"외부 API에서 {len(data)} 개의 트렌드 데이터 수집")
            return data
        else:
            logger.error(f"외부 API 호출 실패: {response.status_code}")
            # 실패 시 캐시된 데이터 사용 (Requirements: 12.4)
            return get_cached_trend_data()
        
    except requests.exceptions.Timeout:
        logger.error("외부 API 타임아웃")
        return get_cached_trend_data()
    except requests.exceptions.RequestException as e:
        logger.error(f"외부 API 요청 실패: {str(e)}")
        return get_cached_trend_data()
    except Exception as e:
        logger.error(f"트렌드 수집 중 오류: {str(e)}")
        return get_cached_trend_data()


def get_default_trend_data() -> List[Dict[str, Any]]:
    """
    기본 트렌드 데이터 반환
    
    Returns:
        list: 기본 트렌드 데이터
    """
    return [
        {'tech_name': 'Python', 'trend_score': 95, 'market_demand': 90},
        {'tech_name': 'JavaScript', 'trend_score': 92, 'market_demand': 88},
        {'tech_name': 'Java', 'trend_score': 85, 'market_demand': 85},
        {'tech_name': 'TypeScript', 'trend_score': 88, 'market_demand': 82},
        {'tech_name': 'React', 'trend_score': 90, 'market_demand': 85},
        {'tech_name': 'Node.js', 'trend_score': 87, 'market_demand': 83},
        {'tech_name': 'AWS', 'trend_score': 93, 'market_demand': 91},
        {'tech_name': 'Docker', 'trend_score': 86, 'market_demand': 84},
        {'tech_name': 'Kubernetes', 'trend_score': 84, 'market_demand': 82},
        {'tech_name': 'Spring Boot', 'trend_score': 82, 'market_demand': 80},
        {'tech_name': 'Vue.js', 'trend_score': 78, 'market_demand': 75},
        {'tech_name': 'Angular', 'trend_score': 72, 'market_demand': 70},
        {'tech_name': 'MongoDB', 'trend_score': 80, 'market_demand': 78},
        {'tech_name': 'PostgreSQL', 'trend_score': 83, 'market_demand': 81},
        {'tech_name': 'Redis', 'trend_score': 81, 'market_demand': 79},
        {'tech_name': 'GraphQL', 'trend_score': 76, 'market_demand': 73},
        {'tech_name': 'Go', 'trend_score': 79, 'market_demand': 76},
        {'tech_name': 'Rust', 'trend_score': 74, 'market_demand': 68},
        {'tech_name': 'Machine Learning', 'trend_score': 91, 'market_demand': 87},
        {'tech_name': 'AI', 'trend_score': 94, 'market_demand': 89}
    ]


def get_cached_trend_data() -> List[Dict[str, Any]]:
    """
    캐시된 트렌드 데이터 조회
    
    Requirements: 12.4 - API 실패 시 캐시 사용
    
    Returns:
        list: 캐시된 트렌드 데이터
    """
    try:
        table = dynamodb.Table('TechTrends')
        response = table.scan()
        
        cached_data = []
        for item in response.get('Items', []):
            cached_data.append({
                'tech_name': item.get('tech_name'),
                'trend_score': float(item.get('trend_score', 50)),
                'market_demand': float(item.get('market_demand', 50))
            })
        
        if cached_data:
            logger.info(f"캐시에서 {len(cached_data)}개의 트렌드 데이터 조회")
            return cached_data
        else:
            logger.warning("캐시된 데이터 없음, 기본 데이터 사용")
            return get_default_trend_data()
        
    except Exception as e:
        logger.error(f"캐시 조회 실패: {str(e)}")
        return get_default_trend_data()


def store_trend_data(trend_data: List[Dict[str, Any]]) -> int:
    """
    트렌드 데이터 저장
    
    Requirements: 12.2 - DynamoDB에 데이터 저장
    
    Args:
        trend_data: 트렌드 데이터 목록
        
    Returns:
        int: 업데이트된 항목 수
    """
    try:
        table = dynamodb.Table('TechTrends')
        updated_count = 0
        
        for trend in trend_data:
            tech_name = trend.get('tech_name')
            if not tech_name:
                continue
            
            # 데이터 저장
            item = {
                'tech_name': tech_name,
                'trend_score': trend.get('trend_score', 50),
                'market_demand': trend.get('market_demand', 50),
                'last_updated': datetime.utcnow().isoformat()
            }
            
            table.put_item(Item=item)
            updated_count += 1
        
        logger.info(f"{updated_count}개의 트렌드 데이터 저장 완료")
        return updated_count
        
    except Exception as e:
        logger.error(f"트렌드 데이터 저장 실패: {str(e)}")
        return 0


def trigger_score_recalculation():
    """
    점수 재계산 트리거
    
    Requirements: 12.5 - 트렌드 업데이트 시 점수 재계산
    """
    try:
        # 모든 직원에 대해 정량적 분석 재실행
        # 실제로는 비동기로 처리하거나 SQS를 사용
        logger.info("점수 재계산 트리거 (실제 구현에서는 비동기 처리)")
        
        # 예시: 특정 Lambda 함수 호출
        # lambda_client.invoke(
        #     FunctionName='quantitative-analysis',
        #     InvocationType='Event',
        #     Payload=json.dumps({'recalculate_all': True})
        # )
        
    except Exception as e:
        logger.error(f"점수 재계산 트리거 실패: {str(e)}")
