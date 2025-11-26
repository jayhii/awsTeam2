"""
Project Recommendation Engine Lambda Function
프로젝트 투입 인력 추천

Requirements: 2.2, 2.4, 2.5, 1.3, 1.4, 11.3, 11.4
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
from decimal import Decimal
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS 클라이언트 초기화
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-2'))
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-2'))

# OpenSearch 클라이언트 초기화
def get_opensearch_client():
    """OpenSearch 클라이언트 생성"""
    endpoint = os.environ.get('OPENSEARCH_ENDPOINT')
    if not endpoint:
        raise ValueError("OPENSEARCH_ENDPOINT 환경 변수가 설정되지 않았습니다")
    
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        os.environ.get('AWS_REGION', 'us-east-2'),
        'es',
        session_token=credentials.token
    )
    
    return OpenSearch(
        hosts=[{'host': endpoint, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )


def handler(event, context):
    """
    Lambda handler for API Gateway
    
    Requirements: 2.2 - 프로젝트 투입 인력 추천
    
    Args:
        event: API Gateway 이벤트
        context: Lambda 컨텍스트
        
    Returns:
        dict: API Gateway 응답
    """
    try:
        logger.info(f"추천 요청 수신: {json.dumps(event)}")
        
        # 요청 본문 파싱 (Requirements: 2.2)
        body = json.loads(event.get('body', '{}'))
        
        # 입력 검증
        if not body.get('project_id'):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'project_id가 필요합니다'})
            }
        
        project_id = body['project_id']
        required_skills = body.get('required_skills', [])
        team_size = body.get('team_size', 5)
        priority = body.get('priority', 'balanced')  # skill, affinity, balanced
        
        logger.info(f"프로젝트 {project_id}에 대한 추천 시작")
        
        # 추천 생성
        recommendations = generate_recommendations(
            project_id=project_id,
            required_skills=required_skills,
            team_size=team_size,
            priority=priority
        )
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'project_id': project_id,
                'recommendations': recommendations
            }, default=decimal_default)
        }
        
    except Exception as e:
        logger.error(f"추천 생성 중 오류 발생: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }


def generate_recommendations(
    project_id: str,
    required_skills: List[str],
    team_size: int,
    priority: str
) -> List[Dict[str, Any]]:
    """
    프로젝트 투입 인력 추천 생성
    
    Requirements: 2.2, 2.4 - 다중 요소 점수 계산 및 추천
    
    Args:
        project_id: 프로젝트 ID
        required_skills: 요구 기술 목록
        team_size: 팀 크기
        priority: 우선순위 (skill, affinity, balanced)
        
    Returns:
        list: 추천 후보자 목록
    """
    # 1. 기술 매칭 알고리즘 (Requirements: 1.3, 2.2)
    skill_matches = find_employees_by_skills(required_skills)
    logger.info(f"기술 매칭 결과: {len(skill_matches)} 명")
    
    # 2. 벡터 유사도 검색 (Requirements: 11.3, 11.4)
    vector_matches = search_similar_employees(project_id, required_skills)
    logger.info(f"벡터 검색 결과: {len(vector_matches)} 명")
    
    # 3. 친밀도 점수 조회 (Requirements: 2.2)
    affinity_scores = get_affinity_scores()
    
    # 4. 후보자 통합 및 점수 계산
    candidates = merge_and_score_candidates(
        skill_matches=skill_matches,
        vector_matches=vector_matches,
        affinity_scores=affinity_scores,
        priority=priority
    )
    
    # 5. 가용성 확인 (Requirements: 2.5)
    candidates = check_availability(candidates)
    
    # 6. 상위 후보자 선택
    top_candidates = sorted(
        candidates,
        key=lambda x: x['overall_score'],
        reverse=True
    )[:team_size]
    
    # 7. 추천 근거 생성 (Requirements: 2.4)
    for candidate in top_candidates:
        candidate['reasoning'] = generate_reasoning(candidate)
    
    return top_candidates


def find_employees_by_skills(required_skills: List[str]) -> List[Dict[str, Any]]:
    """
    기술 스택으로 직원 검색
    
    Requirements: 1.3 - 기술 매칭 알고리즘
    
    Args:
        required_skills: 요구 기술 목록
        
    Returns:
        list: 매칭된 직원 목록
    """
    try:
        table = dynamodb.Table('Employees')
        
        # 모든 직원 조회 (실제로는 GSI 사용)
        response = table.scan()
        employees = response.get('Items', [])
        
        # 페이지네이션 처리
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            employees.extend(response.get('Items', []))
        
        # 기술 매칭 점수 계산
        matches = []
        for employee in employees:
            employee_skills = [
                skill.get('name', '') 
                for skill in employee.get('skills', [])
            ]
            
            # 매칭된 기술 수 계산
            matched_skills = [
                skill for skill in required_skills 
                if skill in employee_skills
            ]
            
            if matched_skills:
                match_score = (len(matched_skills) / len(required_skills)) * 100
                
                matches.append({
                    'user_id': employee.get('user_id'),
                    'name': employee.get('basic_info', {}).get('name', ''),
                    'role': employee.get('basic_info', {}).get('role', ''),
                    'matched_skills': matched_skills,
                    'skill_match_score': match_score,
                    'years_of_experience': employee.get('basic_info', {}).get('years_of_experience', 0)
                })
        
        return matches
        
    except Exception as e:
        logger.error(f"기술 검색 실패: {str(e)}")
        return []


def search_similar_employees(
    project_id: str,
    required_skills: List[str]
) -> List[Dict[str, Any]]:
    """
    벡터 유사도 검색
    
    Requirements: 11.3, 11.4 - OpenSearch 벡터 검색
    
    Args:
        project_id: 프로젝트 ID
        required_skills: 요구 기술 목록
        
    Returns:
        list: 유사한 직원 목록
    """
    try:
        # 프로젝트 요구사항 벡터 생성
        requirement_text = f"프로젝트 요구 기술: {', '.join(required_skills)}"
        requirement_vector = generate_embedding(requirement_text)
        
        # OpenSearch k-NN 검색
        opensearch_client = get_opensearch_client()
        
        query = {
            "size": 20,
            "query": {
                "knn": {
                    "profile_vector": {
                        "vector": requirement_vector,
                        "k": 20
                    }
                }
            }
        }
        
        response = opensearch_client.search(
            index='employee_profiles',
            body=query
        )
        
        matches = []
        for hit in response['hits']['hits']:
            source = hit['_source']
            similarity_score = hit['_score']
            
            matches.append({
                'user_id': source.get('user_id'),
                'name': source.get('name'),
                'role': source.get('role'),
                'similarity_score': similarity_score,
                'vector_match': True
            })
        
        return matches
        
    except Exception as e:
        logger.error(f"벡터 검색 실패: {str(e)}")
        return []


def generate_embedding(text: str) -> List[float]:
    """
    텍스트를 벡터 임베딩으로 변환
    
    Args:
        text: 입력 텍스트
        
    Returns:
        list: 벡터 임베딩
    """
    try:
        response = bedrock_runtime.invoke_model(
            modelId='amazon.titan-embed-text-v1',
            body=json.dumps({'inputText': text})
        )
        
        response_body = json.loads(response['body'].read())
        return response_body.get('embedding', [])
        
    except Exception as e:
        logger.error(f"임베딩 생성 실패: {str(e)}")
        return [0.0] * 1536  # 기본 벡터


def get_affinity_scores() -> Dict[str, float]:
    """
    친밀도 점수 조회
    
    Requirements: 2.2 - 친밀도 점수 반영
    
    Returns:
        dict: 직원 쌍별 친밀도 점수
    """
    try:
        table = dynamodb.Table('EmployeeAffinity')
        response = table.scan()
        
        affinity_map = {}
        for item in response.get('Items', []):
            employee_pair = item.get('employee_pair', {})
            emp1 = employee_pair.get('employee_1')
            emp2 = employee_pair.get('employee_2')
            score = float(item.get('overall_affinity_score', 0))
            
            if emp1 and emp2:
                key = f"{emp1}_{emp2}"
                affinity_map[key] = score
                # 양방향 저장
                key_reverse = f"{emp2}_{emp1}"
                affinity_map[key_reverse] = score
        
        return affinity_map
        
    except Exception as e:
        logger.error(f"친밀도 점수 조회 실패: {str(e)}")
        return {}


def merge_and_score_candidates(
    skill_matches: List[Dict[str, Any]],
    vector_matches: List[Dict[str, Any]],
    affinity_scores: Dict[str, float],
    priority: str
) -> List[Dict[str, Any]]:
    """
    후보자 통합 및 종합 점수 계산
    
    Requirements: 2.2, 2.4 - 다중 요소 점수 계산
    
    Args:
        skill_matches: 기술 매칭 결과
        vector_matches: 벡터 검색 결과
        affinity_scores: 친밀도 점수
        priority: 우선순위
        
    Returns:
        list: 통합된 후보자 목록
    """
    # 후보자 통합
    candidates_map = {}
    
    # 기술 매칭 결과 추가
    for match in skill_matches:
        user_id = match['user_id']
        candidates_map[user_id] = {
            'user_id': user_id,
            'name': match.get('name', ''),
            'role': match.get('role', ''),
            'skill_match_score': match.get('skill_match_score', 0),
            'similarity_score': 0,
            'affinity_score': 0,
            'matched_skills': match.get('matched_skills', []),
            'years_of_experience': match.get('years_of_experience', 0)
        }
    
    # 벡터 검색 결과 추가
    for match in vector_matches:
        user_id = match['user_id']
        if user_id in candidates_map:
            candidates_map[user_id]['similarity_score'] = match.get('similarity_score', 0)
        else:
            candidates_map[user_id] = {
                'user_id': user_id,
                'name': match.get('name', ''),
                'role': match.get('role', ''),
                'skill_match_score': 0,
                'similarity_score': match.get('similarity_score', 0),
                'affinity_score': 0,
                'matched_skills': [],
                'years_of_experience': 0
            }
    
    # 친밀도 점수 추가 (평균)
    for user_id in candidates_map:
        related_scores = [
            score for key, score in affinity_scores.items()
            if user_id in key
        ]
        if related_scores:
            candidates_map[user_id]['affinity_score'] = sum(related_scores) / len(related_scores)
    
    # 종합 점수 계산
    for candidate in candidates_map.values():
        if priority == 'skill':
            weights = {'skill': 0.6, 'similarity': 0.3, 'affinity': 0.1}
        elif priority == 'affinity':
            weights = {'skill': 0.3, 'similarity': 0.2, 'affinity': 0.5}
        else:  # balanced
            weights = {'skill': 0.4, 'similarity': 0.3, 'affinity': 0.3}
        
        overall_score = (
            candidate['skill_match_score'] * weights['skill'] +
            candidate['similarity_score'] * weights['similarity'] +
            candidate['affinity_score'] * weights['affinity']
        )
        
        candidate['overall_score'] = overall_score
    
    return list(candidates_map.values())


def check_availability(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    직원 가용성 확인
    
    Requirements: 2.5 - 가용성 정보 포함
    
    Args:
        candidates: 후보자 목록
        
    Returns:
        list: 가용성 정보가 추가된 후보자 목록
    """
    try:
        # 현재 프로젝트 배정 확인
        table = dynamodb.Table('Projects')
        response = table.scan()
        
        # 진행 중인 프로젝트 찾기
        active_projects = {}
        for project in response.get('Items', []):
            team = project.get('team_composition', {})
            for role, members in team.items():
                if isinstance(members, list):
                    for member_id in members:
                        active_projects[member_id] = project.get('project_name', '')
        
        # 가용성 정보 추가
        for candidate in candidates:
            user_id = candidate['user_id']
            if user_id in active_projects:
                candidate['availability'] = 'Busy'
                candidate['current_project'] = active_projects[user_id]
            else:
                candidate['availability'] = 'Available'
                candidate['current_project'] = None
        
        return candidates
        
    except Exception as e:
        logger.error(f"가용성 확인 실패: {str(e)}")
        # 오류 시 모두 Available로 설정
        for candidate in candidates:
            candidate['availability'] = 'Unknown'
            candidate['current_project'] = None
        return candidates


def generate_reasoning(candidate: Dict[str, Any]) -> str:
    """
    추천 근거 생성
    
    Requirements: 2.4 - Claude를 사용한 추천 근거 생성
    
    Args:
        candidate: 후보자 정보
        
    Returns:
        str: 추천 근거
    """
    try:
        prompt = f"""다음 후보자에 대한 프로젝트 투입 추천 근거를 간결하게 작성해주세요:

이름: {candidate.get('name')}
역할: {candidate.get('role')}
경력: {candidate.get('years_of_experience')}년
기술 매칭 점수: {candidate.get('skill_match_score', 0):.1f}
유사도 점수: {candidate.get('similarity_score', 0):.1f}
친밀도 점수: {candidate.get('affinity_score', 0):.1f}
종합 점수: {candidate.get('overall_score', 0):.1f}
매칭된 기술: {', '.join(candidate.get('matched_skills', []))}
가용성: {candidate.get('availability', 'Unknown')}

2-3문장으로 추천 이유를 설명해주세요."""

        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-v2',
            body=json.dumps({
                'prompt': f"\n\nHuman: {prompt}\n\nAssistant:",
                'max_tokens_to_sample': 200,
                'temperature': 0.7
            })
        )
        
        response_body = json.loads(response['body'].read())
        reasoning = response_body.get('completion', '').strip()
        
        return reasoning
        
    except Exception as e:
        logger.error(f"추천 근거 생성 실패: {str(e)}")
        return f"기술 매칭 {candidate.get('skill_match_score', 0):.1f}점, 종합 점수 {candidate.get('overall_score', 0):.1f}점으로 추천됩니다."


def decimal_default(obj):
    """Decimal을 float로 변환"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError
