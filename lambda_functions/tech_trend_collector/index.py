"""
Tech Trend Collector Lambda Function
외부 API 및 크롤링을 통한 기술 트렌드 수집 및 업데이트

Requirements: 자동화된 기술 트렌드 데이터 수집
"""

import json
import logging
import os
from typing import Dict, Any, List
from decimal import Decimal
import boto3
from datetime import datetime, timedelta
import requests

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS 클라이언트 초기화
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-2'))
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-2'))

# GitHub API (공개 데이터)
GITHUB_API_BASE = "https://api.github.com"

def handler(event, context):
    """
    Lambda handler for scheduled tech trend collection
    
    Args:
        event: EventBridge 이벤트
        context: Lambda 컨텍스트
        
    Returns:
        dict: 실행 결과
    """
    try:
        logger.info("기술 트렌드 수집 시작")
        
        # 1. GitHub 트렌드 수집
        github_trends = collect_github_trends()
        
        # 2. Stack Overflow 트렌드 분석 (Claude 활용)
        stackoverflow_trends = analyze_stackoverflow_trends()
        
        # 3. 기존 TechTrends 데이터 업데이트
        updated_count = update_tech_trends(github_trends, stackoverflow_trends)
        
        # 4. 신규 기술 발견 및 추가
        new_count = discover_new_technologies()
        
        result = {
            'status': 'success',
            'updated_trends': updated_count,
            'new_technologies': new_count,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"기술 트렌드 수집 완료: {json.dumps(result)}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"기술 트렌드 수집 실패: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def collect_github_trends() -> Dict[str, Any]:
    """
    GitHub API를 통한 기술 트렌드 수집
    
    Returns:
        dict: 기술별 트렌드 데이터
    """
    trends = {}
    
    # 주요 기술 리포지토리 목록
    tech_repos = {
        'React': 'facebook/react',
        'Vue.js': 'vuejs/vue',
        'Angular': 'angular/angular',
        'Python': 'python/cpython',
        'Node.js': 'nodejs/node',
        'Kubernetes': 'kubernetes/kubernetes',
        'TensorFlow': 'tensorflow/tensorflow',
        'PyTorch': 'pytorch/pytorch'
    }
    
    for tech_name, repo in tech_repos.items():
        try:
            # GitHub API 호출 (인증 없이 공개 데이터만)
            response = requests.get(
                f"{GITHUB_API_BASE}/repos/{repo}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # 스타 수, 포크 수, 이슈 수 등으로 트렌드 계산
                stars = data.get('stargazers_count', 0)
                forks = data.get('forks_count', 0)
                open_issues = data.get('open_issues_count', 0)
                
                # 간단한 트렌드 점수 계산
                trend_score = min(100, (stars / 1000) + (forks / 100))
                
                trends[tech_name] = {
                    'stars': stars,
                    'forks': forks,
                    'open_issues': open_issues,
                    'trend_score': trend_score,
                    'last_updated': data.get('updated_at')
                }
                
                logger.info(f"GitHub 트렌드 수집: {tech_name} - Stars: {stars}")
                
        except Exception as e:
            logger.warning(f"GitHub 트렌드 수집 실패: {tech_name} - {str(e)}")
    
    return trends


def analyze_stackoverflow_trends() -> Dict[str, Any]:
    """
    Stack Overflow 트렌드 분석 (Claude 활용)
    
    Returns:
        dict: 기술별 트렌드 분석
    """
    try:
        # Claude를 사용한 트렌드 분석
        prompt = """다음 기술들의 최근 트렌드를 분석해주세요:

기술 목록:
- Python
- JavaScript/Node.js
- React
- Vue.js
- Angular
- Kubernetes
- Docker
- AWS
- TensorFlow
- PyTorch

각 기술에 대해 다음 정보를 JSON 형식으로 제공해주세요:
1. 현재 인기도 (0-100)
2. 성장 추세 (증가/유지/감소)
3. 주요 사용 분야
4. 2024년 전망

JSON 형식으로만 응답해주세요."""

        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-v2',
            body=json.dumps({
                'prompt': f"\n\nHuman: {prompt}\n\nAssistant:",
                'max_tokens_to_sample': 2000,
                'temperature': 0.3
            })
        )
        
        response_body = json.loads(response['body'].read())
        analysis_text = response_body.get('completion', '').strip()
        
        # JSON 파싱 시도
        try:
            trends = json.loads(analysis_text)
            return trends
        except:
            logger.warning("Claude 응답 파싱 실패, 기본값 반환")
            return {}
            
    except Exception as e:
        logger.error(f"Stack Overflow 트렌드 분석 실패: {str(e)}")
        return {}


def update_tech_trends(github_trends: Dict, stackoverflow_trends: Dict) -> int:
    """
    TechTrends 테이블 업데이트
    
    Args:
        github_trends: GitHub 트렌드 데이터
        stackoverflow_trends: Stack Overflow 트렌드 데이터
        
    Returns:
        int: 업데이트된 항목 수
    """
    trends_table = dynamodb.Table('TechTrends')
    updated_count = 0
    
    for tech_name, github_data in github_trends.items():
        try:
            # 기존 데이터 조회
            response = trends_table.get_item(Key={'tech_name': tech_name})
            
            if 'Item' in response:
                item = response['Item']
                
                # GitHub 데이터로 업데이트
                old_trend = float(item.get('trend_score', 0))
                new_trend = github_data.get('trend_score', old_trend)
                
                # 성장률 계산
                if old_trend > 0:
                    growth_rate = ((new_trend - old_trend) / old_trend) * 100
                else:
                    growth_rate = 0
                
                # 업데이트
                item['trend_score'] = Decimal(str(new_trend))
                item['growth_rate'] = Decimal(str(round(growth_rate, 2)))
                item['github_stars'] = github_data.get('stars', 0)
                item['last_updated'] = datetime.now().isoformat()
                
                trends_table.put_item(Item=item)
                updated_count += 1
                
                logger.info(f"업데이트: {tech_name} - 트렌드: {new_trend:.1f}")
                
        except Exception as e:
            logger.error(f"업데이트 실패: {tech_name} - {str(e)}")
    
    return updated_count


def discover_new_technologies() -> int:
    """
    신규 기술 발견 및 추가
    
    Returns:
        int: 추가된 신규 기술 수
    """
    trends_table = dynamodb.Table('TechTrends')
    new_count = 0
    
    # 신규 주목받는 기술 목록 (예시)
    emerging_techs = [
        {
            'tech_name': 'Rust',
            'category': 'Backend',
            'trend_score': Decimal('85'),
            'demand_score': Decimal('75'),
            'growth_rate': Decimal('25.5'),
            'market_share': Decimal('5.2'),
            'related_domains': ['Systems Programming', 'WebAssembly'],
            'skill_level_required': 'Advanced',
            'description': '안전하고 빠른 시스템 프로그래밍 언어'
        },
        {
            'tech_name': 'Svelte',
            'category': 'Frontend',
            'trend_score': Decimal('82'),
            'demand_score': Decimal('70'),
            'growth_rate': Decimal('28.3'),
            'market_share': Decimal('3.8'),
            'related_domains': ['Web Development'],
            'skill_level_required': 'Intermediate',
            'description': '컴파일 타임 프레임워크'
        }
    ]
    
    for tech in emerging_techs:
        try:
            # 이미 존재하는지 확인
            response = trends_table.get_item(Key={'tech_name': tech['tech_name']})
            
            if 'Item' not in response:
                # 신규 추가
                tech['last_updated'] = datetime.now().isoformat()
                trends_table.put_item(Item=tech)
                new_count += 1
                logger.info(f"신규 기술 추가: {tech['tech_name']}")
                
        except Exception as e:
            logger.error(f"신규 기술 추가 실패: {tech['tech_name']} - {str(e)}")
    
    return new_count


def decimal_default(obj):
    """Decimal을 float로 변환"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError
