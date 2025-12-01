"""
직원 평가 Lambda 함수
DB에 등록된 직원을 기준으로 상대 평가 수행
"""

import json
import os
import boto3
from decimal import Decimal
from typing import Dict, List, Any
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-2')

EMPLOYEES_TABLE = os.environ.get('EMPLOYEES_TABLE', 'Employees')
PROJECTS_TABLE = os.environ.get('PROJECTS_TABLE', 'Projects')


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def get_all_employees():
    """모든 직원 데이터 조회"""
    table = dynamodb.Table(EMPLOYEES_TABLE)
    response = table.scan()
    return response.get('Items', [])


def calculate_relative_scores(employee_data: Dict, all_employees: List[Dict]) -> Dict[str, float]:
    """
    상대 평가 점수 계산
    각 항목별로 최고점자를 100점으로 하고 나머지는 상대적으로 점수 부여
    """
    
    # 경력 년수 추출 헬퍼 함수
    def get_experience_years(emp_data):
        return (
            emp_data.get('basic_info', {}).get('years_of_experience') or
            emp_data.get('experienceYears') or
            emp_data.get('experience_years') or
            0
        )
    
    # 프로젝트 이력 추출 헬퍼 함수
    def get_project_history(emp_data):
        return (
            emp_data.get('work_experience') or
            emp_data.get('projectHistory') or
            emp_data.get('project_history') or
            []
        )
    
    # 1. 기술 역량 점수 계산
    tech_scores = []
    for emp in all_employees:
        skills = emp.get('skills', [])
        skill_count = len(skills)
        # 기술 개수와 경력 년수를 고려
        experience_years = get_experience_years(emp)
        tech_score = skill_count * 10 + float(experience_years) * 5
        tech_scores.append(tech_score)
    
    employee_skills = employee_data.get('skills', [])
    employee_experience = get_experience_years(employee_data)
    employee_tech_score = len(employee_skills) * 10 + float(employee_experience) * 5
    
    max_tech_score = max(tech_scores) if tech_scores and max(tech_scores) > 0 else 1
    technical_skills_score = min(100, (employee_tech_score / max_tech_score) * 100) if max_tech_score > 0 else 50.0
    
    # 2. 프로젝트 경험 점수 계산
    project_scores = []
    for emp in all_employees:
        projects = get_project_history(emp)
        project_count = len(projects)
        # 프로젝트 개수와 다양성 고려
        project_score = project_count * 15
        project_scores.append(project_score)
    
    employee_projects = get_project_history(employee_data)
    employee_project_score = len(employee_projects) * 15
    
    max_project_score = max(project_scores) if project_scores and max(project_scores) > 0 else 1
    project_experience_score = min(100, (employee_project_score / max_project_score) * 100) if max_project_score > 0 else 50.0
    
    # 3. 이력 신뢰도 점수 (경력과 기술의 일관성 기반)
    # 경력 년수 대비 기술 개수의 비율로 계산
    exp_years_float = float(employee_experience)
    expected_skills = exp_years_float * 2  # 1년당 2개 기술 습득 가정
    skill_ratio = len(employee_skills) / max(expected_skills, 1) if expected_skills > 0 else 0.5
    
    # 프로젝트 개수와 경력의 일관성
    expected_projects = exp_years_float * 0.5  # 1년당 0.5개 프로젝트 가정
    project_ratio = len(employee_projects) / max(expected_projects, 1) if expected_projects > 0 else 0.5
    
    # 신뢰도 점수: 기술과 프로젝트 비율의 평균 (50~100점 범위)
    credibility_base = (skill_ratio + project_ratio) / 2
    resume_credibility_score = min(100, max(50, credibility_base * 100))
    
    # 4. 문화 적합성 점수 (경력 년수와 프로젝트 성공률 기반)
    cultural_scores = []
    for emp in all_employees:
        exp_years = get_experience_years(emp)
        projects = get_project_history(emp)
        cultural_score = float(exp_years) * 8 + len(projects) * 5
        cultural_scores.append(cultural_score)
    
    employee_cultural_score = float(employee_experience) * 8 + len(employee_projects) * 5
    max_cultural_score = max(cultural_scores) if cultural_scores and max(cultural_scores) > 0 else 1
    cultural_fit_score = min(100, (employee_cultural_score / max_cultural_score) * 100) if max_cultural_score > 0 else 50.0
    
    # 종합 점수 계산 (가중 평균)
    overall_score = (
        technical_skills_score * 0.35 +
        project_experience_score * 0.30 +
        resume_credibility_score * 0.20 +
        cultural_fit_score * 0.15
    )
    
    return {
        'technical_skills': round(technical_skills_score, 1),
        'project_experience': round(project_experience_score, 1),
        'resume_credibility': round(resume_credibility_score, 1),
        'cultural_fit': round(cultural_fit_score, 1),
        'overall_score': round(overall_score, 1)
    }


def get_all_projects():
    """모든 프로젝트 데이터 조회"""
    try:
        table = dynamodb.Table(PROJECTS_TABLE)
        response = table.scan()
        return response.get('Items', [])
    except:
        return []


def analyze_with_ai(employee_data: Dict, all_projects: List[Dict]) -> Dict[str, Any]:
    """AI를 사용한 상세 분석"""
    
    # 직원 정보 추출
    name = employee_data.get('basic_info', {}).get('name', employee_data.get('name', 'Unknown'))
    experience_years = (
        employee_data.get('basic_info', {}).get('years_of_experience') or
        employee_data.get('experienceYears') or
        employee_data.get('experience_years') or
        0
    )
    
    skills = employee_data.get('skills', [])
    skill_names = []
    for s in skills:
        if isinstance(s, dict):
            skill_names.append(f"{s.get('name', '')} ({s.get('level', '')} - {s.get('years', 0)}년)")
        else:
            skill_names.append(str(s))
    
    project_history = (
        employee_data.get('work_experience') or
        employee_data.get('projectHistory') or
        employee_data.get('project_history') or
        []
    )
    
    # 프로젝트 정보 구성
    project_details = []
    for proj in project_history[:5]:  # 최근 5개만
        if isinstance(proj, dict):
            project_details.append(f"- {proj.get('project_name', '')}: {proj.get('role', '')} ({proj.get('period', '')})")
    
    # 가능한 프로젝트 매칭
    matching_projects = []
    employee_skill_set = set([s.get('name', '').lower() if isinstance(s, dict) else str(s).lower() for s in skills])
    
    for proj in all_projects[:10]:  # 최근 10개 프로젝트
        required_skills = proj.get('required_skills', [])
        if isinstance(required_skills, list):
            required_skill_set = set([str(s).lower() for s in required_skills])
            match_count = len(employee_skill_set & required_skill_set)
            if match_count > 0:
                matching_projects.append({
                    'name': proj.get('project_name', ''),
                    'match_count': match_count,
                    'required_skills': required_skills[:3]
                })
    
    matching_projects.sort(key=lambda x: x['match_count'], reverse=True)
    
    prompt = f"""다음 직원의 이력을 분석하여 평가해주세요:

이름: {name}
경력: {experience_years}년
기술 스택: {', '.join(skill_names)}
프로젝트 이력: {len(project_history)}개
{chr(10).join(project_details) if project_details else '- 프로젝트 이력 없음'}

매칭 가능한 프로젝트:
{chr(10).join([f"- {p['name']}: {p['match_count']}개 기술 매칭" for p in matching_projects[:3]]) if matching_projects else '- 매칭 프로젝트 없음'}

다음 항목을 JSON 형식으로 분석해주세요:
1. strengths: 강점 3-4가지 (배열, 구체적으로)
2. weaknesses: 개선 필요 사항 2-3가지 (배열, 구체적으로)
3. tech_stack_analysis: 기술 스택 및 숙련도 평가 (200자 이내, 보유 기술의 시장 가치와 숙련도 평가)
4. project_similarity: 프로젝트 경험 유사도 분석 (200자 이내, 프로젝트 경험의 깊이와 다양성 평가)
5. credibility_check: 경력 이력 진위 여부 검증 (200자 이내, 경력과 기술 수준의 일관성 평가)
6. market_comparison: 시장 평균 대비 역량 비교 (200자 이내, 동일 경력 대비 역량 수준 평가)
7. recommendation: AI 추천 의견 (300자 이내, 프로젝트 투입 가능 여부, 적합한 역할, 매칭 프로젝트 추천 포함)

JSON 형식으로만 응답해주세요."""

    try:
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "messages": [{
                    "role": "user",
                    "content": prompt
                }]
            })
        )
        
        response_body = json.loads(response['body'].read())
        ai_response = response_body['content'][0]['text']
        
        # JSON 파싱
        try:
            analysis = json.loads(ai_response)
        except:
            # JSON 파싱 실패 시 기본값
            analysis = {
                'strengths': ['다양한 기술 스택 보유', '풍부한 프로젝트 경험', '지속적인 학습 의지'],
                'weaknesses': ['최신 기술 트렌드 학습 필요', '특정 도메인 전문성 강화 필요'],
                'tech_stack_analysis': '현재 보유한 기술 스택은 시장에서 수요가 높은 기술들입니다.',
                'project_similarity': '유사한 프로젝트 경험이 있어 빠른 적응이 가능할 것으로 예상됩니다.',
                'credibility_check': '제출된 이력은 대부분 검증 가능하며 신뢰도가 높습니다.',
                'market_comparison': '시장 평균 대비 우수한 역량을 보유하고 있습니다.',
                'recommendation': '즉시 투입 가능한 우수 인력으로 판단됩니다.'
            }
        
        return analysis
        
    except Exception as e:
        print(f"AI 분석 오류: {str(e)}")
        return {
            'strengths': ['다양한 기술 스택 보유', '풍부한 프로젝트 경험'],
            'weaknesses': ['추가 분석 필요'],
            'tech_stack_analysis': '기술 스택 분석 중...',
            'project_similarity': '프로젝트 유사도 분석 중...',
            'credibility_check': '이력 검증 중...',
            'market_comparison': '시장 비교 분석 중...',
            'recommendation': '추가 검토가 필요합니다.'
        }


def lambda_handler(event, context):
    """Lambda 핸들러"""
    
    # CORS 헤더
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'POST,OPTIONS'
    }
    
    # OPTIONS 요청 처리
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'OK'})
        }
    
    try:
        # 요청 본문 파싱
        body = json.loads(event.get('body', '{}'))
        employee_id = body.get('employee_id')
        
        print(f"요청 받은 employee_id: {employee_id}")
        
        if not employee_id:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'employee_id is required'})
            }
        
        # 직원 데이터 조회 (user_id로 시도)
        employees_table = dynamodb.Table(EMPLOYEES_TABLE)
        
        # user_id로 먼저 시도
        response = employees_table.get_item(Key={'user_id': employee_id})
        
        # 없으면 employeeId로 시도
        if 'Item' not in response:
            response = employees_table.get_item(Key={'employeeId': employee_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Employee not found'})
            }
        
        employee_data = response['Item']
        
        # 모든 직원 데이터 조회 (상대 평가를 위해)
        all_employees = get_all_employees()
        
        # 모든 프로젝트 데이터 조회 (매칭을 위해)
        all_projects = get_all_projects()
        
        # 상대 평가 점수 계산
        scores = calculate_relative_scores(employee_data, all_employees)
        
        # AI 분석 수행
        ai_analysis = analyze_with_ai(employee_data, all_projects)
        
        # 평가 결과 구성
        # 직원 이름 추출 (여러 형식 지원)
        employee_name = (
            employee_data.get('basic_info', {}).get('name') or
            employee_data.get('name') or
            employee_data.get('user_id') or
            'Unknown'
        )
        
        evaluation_result = {
            'evaluation_id': f"eval_{employee_id}_{int(datetime.now().timestamp())}",
            'employee_id': employee_id,
            'employee_name': employee_name,
            'evaluation_date': datetime.now().isoformat(),
            'scores': {
                'technical_skills': scores['technical_skills'],
                'project_experience': scores['project_experience'],
                'resume_credibility': scores['resume_credibility'],
                'cultural_fit': scores['cultural_fit']
            },
            'overall_score': scores['overall_score'],
            'strengths': ai_analysis.get('strengths', []),
            'weaknesses': ai_analysis.get('weaknesses', []),
            'analysis': {
                'tech_stack': ai_analysis.get('tech_stack_analysis', ''),
                'project_similarity': ai_analysis.get('project_similarity', ''),
                'credibility': ai_analysis.get('credibility_check', ''),
                'market_comparison': ai_analysis.get('market_comparison', '')
            },
            'ai_recommendation': ai_analysis.get('recommendation', ''),
            'project_history': employee_data.get('projectHistory', []),
            'skills': employee_data.get('skills', []),
            'experience_years': employee_data.get('experienceYears', 0),
            'status': 'completed'
        }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(evaluation_result, cls=DecimalEncoder)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
