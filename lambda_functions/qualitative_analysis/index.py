"""
Qualitative Analysis Lambda Function
정성적 인력 평가

Requirements: 3.1, 3.4, 3.5
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
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-2'))


def handler(event, context):
    """
    Lambda handler for API Gateway
    
    Requirements: 3.1 - 정성적 인력 평가
    
    Args:
        event: API Gateway 이벤트
        context: Lambda 컨텍스트
        
    Returns:
        dict: API Gateway 응답
    """
    try:
        logger.info(f"정성적 분석 요청 수신: {json.dumps(event)}")
        
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
        
        logger.info(f"직원 {user_id}에 대한 정성적 분석 시작")
        
        # 직원 프로필 조회
        employee = fetch_employee_profile(user_id)
        
        if not employee:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': '직원을 찾을 수 없습니다'})
            }
        
        # 정성적 분석 수행
        analysis_result = perform_qualitative_analysis(employee)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(analysis_result, default=decimal_default)
        }
        
    except Exception as e:
        logger.error(f"정성적 분석 중 오류 발생: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }


def fetch_employee_profile(user_id: str) -> Dict[str, Any]:
    """
    직원 프로필 조회
    
    Args:
        user_id: 직원 ID
        
    Returns:
        dict: 직원 프로필
    """
    try:
        table = dynamodb.Table('Employees')
        response = table.get_item(Key={'user_id': user_id})
        
        return response.get('Item')
        
    except Exception as e:
        logger.error(f"직원 프로필 조회 실패: {str(e)}")
        return None


def perform_qualitative_analysis(employee: Dict[str, Any]) -> Dict[str, Any]:
    """
    정성적 분석 수행
    
    Requirements: 3.1, 3.4, 3.5
    
    Args:
        employee: 직원 데이터
        
    Returns:
        dict: 분석 결과
    """
    user_id = employee.get('user_id')
    name = employee.get('basic_info', {}).get('name', '')
    
    # 1. 이력서 분석 (Requirements: 3.1, 3.4)
    resume_analysis = analyze_resume_with_claude(employee)
    
    # 2. 의심스러운 내용 감지 (Requirements: 3.5)
    suspicious_content = detect_suspicious_content(employee)
    
    return {
        'user_id': user_id,
        'name': name,
        'strengths': resume_analysis.get('strengths', []),
        'weaknesses': resume_analysis.get('weaknesses', []),
        'suitable_projects': resume_analysis.get('suitable_projects', []),
        'development_areas': resume_analysis.get('development_areas', []),
        'suspicious_flags': suspicious_content,
        'overall_assessment': resume_analysis.get('overall_assessment', '')
    }


def analyze_resume_with_claude(employee: Dict[str, Any]) -> Dict[str, Any]:
    """
    Claude를 사용한 이력서 분석
    
    Requirements: 3.1, 3.4 - 강점, 약점, 추천 프로젝트 도출
    
    Args:
        employee: 직원 데이터
        
    Returns:
        dict: 분석 결과
    """
    try:
        # 직원 정보 요약
        basic_info = employee.get('basic_info', {})
        self_introduction = employee.get('self_introduction', '')
        skills = employee.get('skills', [])
        work_experience = employee.get('work_experience', [])
        
        # 프롬프트 생성
        prompt = f"""다음 직원의 이력서를 분석하여 평가해주세요:

이름: {basic_info.get('name', '')}
역할: {basic_info.get('role', '')}
경력: {basic_info.get('years_of_experience', 0)}년

자기소개:
{self_introduction}

보유 기술:
{json.dumps([s.get('name', '') for s in skills if isinstance(s, dict)], ensure_ascii=False)}

프로젝트 경험:
{json.dumps([{{
    'project': p.get('project_name', ''),
    'role': p.get('role', ''),
    'duration': p.get('duration', '')
}} for p in work_experience[:5] if isinstance(p, dict)], ensure_ascii=False, indent=2)}

다음 형식으로 JSON 응답을 작성해주세요:
{{
  "strengths": ["강점1", "강점2", "강점3"],
  "weaknesses": ["약점1", "약점2"],
  "suitable_projects": ["적합한 프로젝트 유형1", "적합한 프로젝트 유형2"],
  "development_areas": ["개발 필요 영역1", "개발 필요 영역2"],
  "overall_assessment": "종합 평가 (2-3문장)"
}}"""

        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-v2',
            body=json.dumps({
                'prompt': f"\n\nHuman: {prompt}\n\nAssistant:",
                'max_tokens_to_sample': 1000,
                'temperature': 0.7
            })
        )
        
        response_body = json.loads(response['body'].read())
        completion = response_body.get('completion', '').strip()
        
        # JSON 파싱 시도
        try:
            # JSON 부분만 추출
            json_start = completion.find('{')
            json_end = completion.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = completion[json_start:json_end]
                analysis = json.loads(json_str)
                return analysis
        except:
            pass
        
        # 파싱 실패 시 기본 응답
        return {
            'strengths': ['경력이 풍부함', '다양한 프로젝트 경험'],
            'weaknesses': ['추가 분석 필요'],
            'suitable_projects': ['기존 경험과 유사한 프로젝트'],
            'development_areas': ['신기술 학습'],
            'overall_assessment': completion[:200] if completion else '추가 분석이 필요합니다.'
        }
        
    except Exception as e:
        logger.error(f"이력서 분석 실패: {str(e)}")
        return {
            'strengths': [],
            'weaknesses': [],
            'suitable_projects': [],
            'development_areas': [],
            'overall_assessment': '분석 중 오류가 발생했습니다.'
        }


def detect_suspicious_content(employee: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    의심스러운 내용 감지
    
    Requirements: 3.5 - 검증이 필요한 정보 플래그
    
    Args:
        employee: 직원 데이터
        
    Returns:
        list: 의심스러운 항목 목록
    """
    suspicious_flags = []
    
    # 1. 경력 연수와 프로젝트 수 불일치
    basic_info = employee.get('basic_info', {})
    years_of_experience = basic_info.get('years_of_experience', 0)
    if isinstance(years_of_experience, Decimal):
        years_of_experience = float(years_of_experience)
    
    work_experience = employee.get('work_experience', [])
    project_count = len(work_experience) if isinstance(work_experience, list) else 0
    
    # 경력 대비 프로젝트 수가 너무 많거나 적음
    expected_projects = years_of_experience / 2  # 평균 2년에 1개 프로젝트
    if project_count > expected_projects * 3:
        suspicious_flags.append({
            'type': 'project_count_mismatch',
            'description': f'경력 {years_of_experience}년 대비 프로젝트 수({project_count})가 과도하게 많습니다.',
            'severity': 'medium'
        })
    elif project_count < expected_projects * 0.3 and years_of_experience > 3:
        suspicious_flags.append({
            'type': 'project_count_mismatch',
            'description': f'경력 {years_of_experience}년 대비 프로젝트 수({project_count})가 너무 적습니다.',
            'severity': 'low'
        })
    
    # 2. 기술 레벨과 경력 불일치
    skills = employee.get('skills', [])
    for skill in skills:
        if not isinstance(skill, dict):
            continue
        
        skill_name = skill.get('name', '')
        skill_level = skill.get('level', '')
        skill_years = skill.get('years', 0)
        if isinstance(skill_years, Decimal):
            skill_years = float(skill_years)
        
        # Expert 레벨인데 경험이 3년 미만
        if skill_level == 'Expert' and skill_years < 3:
            suspicious_flags.append({
                'type': 'skill_level_mismatch',
                'description': f'{skill_name} 기술이 Expert 레벨이지만 경험이 {skill_years}년으로 짧습니다.',
                'severity': 'high'
            })
        
        # 기술 경험이 전체 경력보다 긴 경우
        if skill_years > years_of_experience + 1:
            suspicious_flags.append({
                'type': 'skill_years_exceed_experience',
                'description': f'{skill_name} 기술 경험({skill_years}년)이 전체 경력({years_of_experience}년)보다 깁니다.',
                'severity': 'high'
            })
    
    # 3. 자기소개 내용 검증
    self_introduction = employee.get('self_introduction', '')
    
    # 과장된 표현 감지
    exaggerated_keywords = ['최고', '최상', '완벽', '절대', '항상', '모든', '전부']
    for keyword in exaggerated_keywords:
        if keyword in self_introduction:
            suspicious_flags.append({
                'type': 'exaggerated_claims',
                'description': f'자기소개에 과장된 표현("{keyword}")이 포함되어 있습니다.',
                'severity': 'low'
            })
            break
    
    # 4. 프로젝트 성과 검증
    for project in work_experience:
        if not isinstance(project, dict):
            continue
        
        performance = project.get('performance_result', '')
        
        # 구체적인 수치 없이 성과만 강조
        if any(word in performance for word in ['성공', '달성', '완료']) and not any(char.isdigit() for char in performance):
            suspicious_flags.append({
                'type': 'vague_performance',
                'description': f'프로젝트 "{project.get("project_name", "")}"의 성과가 구체적인 수치 없이 기술되어 있습니다.',
                'severity': 'medium'
            })
            break
    
    return suspicious_flags


def decimal_default(obj):
    """Decimal을 float로 변환"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError
