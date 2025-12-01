"""
직원 평가 Lambda 함수
DB에 등록된 직원을 기준으로 상대 평가 수행

평가 기준:
1. 기술역량 (30%): skills의 name, level, years 기반 평가
2. 프로젝트 경험 (30%): work_experience 기반 평가
3. 이력 신뢰도 (20%): 경력과 프로젝트의 일관성 평가
4. 문화 적합성 (20%): self_introduction, role, education 기반 평가

상대 평가: 각 항목별로 최고점자를 100점으로 하고 나머지는 비율로 환산
"""

import json
import os
import boto3
from decimal import Decimal
from typing import Dict, List, Any, Tuple
from datetime import datetime

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-2')

EMPLOYEES_TABLE = os.environ.get('EMPLOYEES_TABLE', 'Employees')
PROJECTS_TABLE = os.environ.get('PROJECTS_TABLE', 'Projects')

# 기술 난이도 가중치
TECH_DIFFICULTY_WEIGHTS = {
    'kubernetes': 1.5, 'k8s': 1.5, 'msa': 1.5, 'microservices': 1.5,
    'aws': 1.3, 'azure': 1.3, 'gcp': 1.3,
    'java': 1.2, 'spring': 1.2, 'spring boot': 1.2,
    'react': 1.2, 'vue': 1.2, 'angular': 1.2,
    'python': 1.1, 'node.js': 1.1, 'typescript': 1.1,
    'ai': 1.5, 'ml': 1.5, 'machine learning': 1.5, 'deep learning': 1.5,
    'terraform': 1.3, 'docker': 1.2, 'jenkins': 1.1
}

# 역할 레벨 가중치
ROLE_LEVEL_WEIGHTS = {
    'architect': 1.5, 'lead': 1.3, 'senior': 1.2, 
    'principal': 1.5, 'staff': 1.4
}


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


def get_experience_years(emp_data: Dict) -> float:
    """경력 년수 추출"""
    return float(
        emp_data.get('basic_info', {}).get('years_of_experience') or
        emp_data.get('experienceYears') or
        emp_data.get('experience_years') or
        0
    )


def get_project_history(emp_data: Dict) -> List[Dict]:
    """프로젝트 이력 추출"""
    return (
        emp_data.get('work_experience') or
        emp_data.get('projectHistory') or
        emp_data.get('project_history') or
        []
    )


def calculate_tech_skill_raw_score(employee_data: Dict) -> float:
    """기술역량 임시 점수 계산 (0~100)"""
    skills = employee_data.get('skills', [])
    role = employee_data.get('basic_info', {}).get('role', employee_data.get('role', ''))
    experience_years = get_experience_years(employee_data)
    
    if not skills:
        return 30.0
    
    total_score = 0.0
    
    for skill in skills:
        if not isinstance(skill, dict):
            continue
        
        skill_name = skill.get('name', '').lower()
        skill_level = skill.get('level', 'Beginner').lower()
        skill_years = float(skill.get('years', 0))
        
        # 기본 점수 (숙련도 기반)
        level_score = {
            'expert': 10, 'advanced': 7, 
            'intermediate': 5, 'beginner': 3
        }.get(skill_level, 5)
        
        # 난이도 가중치 적용
        difficulty_weight = TECH_DIFFICULTY_WEIGHTS.get(skill_name, 1.0)
        
        # 경험 년수 보너스
        years_bonus = min(skill_years * 0.5, 5)
        
        skill_score = (level_score + years_bonus) * difficulty_weight
        total_score += skill_score
    
    # 역할 레벨 가중치
    role_lower = role.lower()
    role_weight = 1.0
    for key, weight in ROLE_LEVEL_WEIGHTS.items():
        if key in role_lower:
            role_weight = weight
            break
    
    # 경력 년수 보너스
    experience_bonus = min(experience_years * 2, 20)
    
    raw_score = (total_score * role_weight + experience_bonus) / 2
    return min(100.0, raw_score)


def calculate_project_experience_raw_score(employee_data: Dict, all_projects: List[Dict]) -> float:
    """프로젝트 경험 임시 점수 계산 (0~100)"""
    projects = get_project_history(employee_data)
    employee_skills = set([
        s.get('name', '').lower() if isinstance(s, dict) else str(s).lower()
        for s in employee_data.get('skills', [])
    ])
    
    if not projects:
        return 20.0
    
    total_score = 0.0
    
    for proj in projects:
        if not isinstance(proj, dict):
            continue
        
        # 기본 점수
        base_score = 15
        
        # 역할 가중치
        role = proj.get('role', '').lower()
        role_weight = 1.0
        for key, weight in ROLE_LEVEL_WEIGHTS.items():
            if key in role:
                role_weight = weight
                break
        
        # 프로젝트 기간 계산 (대략적)
        period = proj.get('period', '')
        duration_months = 6  # 기본값
        if '~' in period:
            duration_months = 12  # 장기 프로젝트 가정
        
        duration_bonus = min(duration_months / 2, 10)
        
        # 프로젝트 매칭 점수
        matching_score = 0
        for project in all_projects[:10]:
            required_skills = project.get('required_skills', [])
            if isinstance(required_skills, list):
                required_set = set([str(s).lower() for s in required_skills])
                match_count = len(employee_skills & required_set)
                if match_count > 0:
                    matching_score += match_count * 2
        
        proj_score = (base_score + duration_bonus) * role_weight + min(matching_score, 15)
        total_score += proj_score
    
    # 프로젝트 개수 보너스
    project_count_bonus = min(len(projects) * 5, 15)
    
    raw_score = total_score + project_count_bonus
    return min(100.0, raw_score)


def calculate_career_reliability_raw_score(employee_data: Dict) -> float:
    """이력 신뢰도 임시 점수 계산 (0~100)"""
    experience_years = get_experience_years(employee_data)
    skills = employee_data.get('skills', [])
    projects = get_project_history(employee_data)
    
    if experience_years == 0:
        return 50.0
    
    # 1. 기술 숙련도 일관성 (40점)
    total_skill_years = 0
    for skill in skills:
        if isinstance(skill, dict):
            total_skill_years += float(skill.get('years', 0))
    
    avg_skill_years = total_skill_years / len(skills) if skills else 0
    skill_consistency = min(40, (avg_skill_years / experience_years) * 40) if experience_years > 0 else 20
    
    # 2. 프로젝트 개수 적정성 (30점)
    expected_projects = experience_years * 0.4  # 1년당 0.4개
    actual_projects = len(projects)
    
    if actual_projects == 0:
        project_consistency = 10
    elif actual_projects < expected_projects * 0.5:
        project_consistency = 15  # 너무 적음
    elif actual_projects > expected_projects * 3:
        project_consistency = 20  # 과장 의심
    else:
        project_consistency = 30  # 적정
    
    # 3. 역할과 기술의 연관성 (30점)
    role = employee_data.get('basic_info', {}).get('role', employee_data.get('role', '')).lower()
    skill_names = [s.get('name', '').lower() if isinstance(s, dict) else str(s).lower() for s in skills]
    
    role_skill_match = 30
    if 'frontend' in role or 'front-end' in role:
        if not any(s in skill_names for s in ['react', 'vue', 'angular', 'javascript', 'typescript']):
            role_skill_match = 15
    elif 'backend' in role or 'back-end' in role:
        if not any(s in skill_names for s in ['java', 'python', 'node', 'spring', 'django']):
            role_skill_match = 15
    elif 'devops' in role:
        if not any(s in skill_names for s in ['aws', 'kubernetes', 'docker', 'terraform', 'jenkins']):
            role_skill_match = 15
    
    raw_score = skill_consistency + project_consistency + role_skill_match
    return min(100.0, raw_score)


def calculate_culture_fit_raw_score(employee_data: Dict) -> float:
    """문화 적합성 임시 점수 계산 (0~100)"""
    self_intro = employee_data.get('self_introduction', '')
    education = employee_data.get('education', {})
    certifications = employee_data.get('certifications', [])
    
    base_score = 70.0  # 기본 점수
    
    # 자기소개 키워드 분석
    positive_keywords = ['협업', '소통', '성장', '책임', '열정', '전문가', '리더십', '팀워크']
    keyword_bonus = sum(3 for keyword in positive_keywords if keyword in self_intro)
    
    # 학위 보너스
    education_bonus = 0
    if isinstance(education, dict):
        degree = education.get('degree', '').lower()
        if 'phd' in degree or 'ph.d' in degree or '박사' in degree:
            education_bonus = 10
        elif 'ms' in degree or 'master' in degree or '석사' in degree:
            education_bonus = 5
    
    # 자격증 보너스
    cert_bonus = min(len(certifications) * 3, 15)
    
    raw_score = base_score + keyword_bonus + education_bonus + cert_bonus
    return min(100.0, raw_score)


def calculate_relative_scores(employee_data: Dict, all_employees: List[Dict], all_projects: List[Dict]) -> Dict[str, float]:
    """
    상대 평가 점수 계산
    1. 모든 직원의 임시 점수(raw_score) 계산
    2. 각 항목별 최고점을 100점으로 환산
    """
    
    # 1. 모든 직원의 임시 점수 계산
    all_raw_scores = []
    for emp in all_employees:
        raw_scores = {
            'tech_skill': calculate_tech_skill_raw_score(emp),
            'project_experience': calculate_project_experience_raw_score(emp, all_projects),
            'career_reliability': calculate_career_reliability_raw_score(emp),
            'culture_fit': calculate_culture_fit_raw_score(emp)
        }
        all_raw_scores.append(raw_scores)
    
    # 2. 각 항목별 최대값 찾기
    max_tech = max([s['tech_skill'] for s in all_raw_scores]) if all_raw_scores else 1
    max_project = max([s['project_experience'] for s in all_raw_scores]) if all_raw_scores else 1
    max_reliability = max([s['career_reliability'] for s in all_raw_scores]) if all_raw_scores else 1
    max_culture = max([s['culture_fit'] for s in all_raw_scores]) if all_raw_scores else 1
    
    # 3. 현재 직원의 임시 점수 계산
    employee_raw = {
        'tech_skill': calculate_tech_skill_raw_score(employee_data),
        'project_experience': calculate_project_experience_raw_score(employee_data, all_projects),
        'career_reliability': calculate_career_reliability_raw_score(employee_data),
        'culture_fit': calculate_culture_fit_raw_score(employee_data)
    }
    
    # 4. 상대 평가로 환산 (최고점자 = 100점)
    technical_skills_score = round((employee_raw['tech_skill'] / max_tech) * 100, 1) if max_tech > 0 else 50.0
    project_experience_score = round((employee_raw['project_experience'] / max_project) * 100, 1) if max_project > 0 else 50.0
    career_reliability_score = round((employee_raw['career_reliability'] / max_reliability) * 100, 1) if max_reliability > 0 else 50.0
    cultural_fit_score = round((employee_raw['culture_fit'] / max_culture) * 100, 1) if max_culture > 0 else 50.0
    
    # 5. 종합 점수 계산 (가중 평균: 기술 30%, 프로젝트 30%, 신뢰도 20%, 문화 20%)
    overall_score = round(
        technical_skills_score * 0.3 +
        project_experience_score * 0.3 +
        career_reliability_score * 0.2 +
        cultural_fit_score * 0.2,
        1
    )
    
    return {
        'technical_skills': technical_skills_score,
        'project_experience': project_experience_score,
        'resume_credibility': career_reliability_score,
        'cultural_fit': cultural_fit_score,
        'overall_score': overall_score
    }


def get_all_projects():
    """모든 프로젝트 데이터 조회"""
    try:
        table = dynamodb.Table(PROJECTS_TABLE)
        response = table.scan()
        return response.get('Items', [])
    except:
        return []


def generate_project_recommendations(employee_data: Dict, all_projects: List[Dict], scores: Dict) -> List[Dict]:
    """프로젝트 매칭 추천"""
    employee_skills = set([
        s.get('name', '').lower() if isinstance(s, dict) else str(s).lower()
        for s in employee_data.get('skills', [])
    ])
    
    role = employee_data.get('basic_info', {}).get('role', employee_data.get('role', '')).lower()
    
    recommendations = []
    
    for proj in all_projects[:20]:
        required_skills = proj.get('required_skills', [])
        if not isinstance(required_skills, list):
            continue
        
        required_set = set([str(s).lower() for s in required_skills])
        match_count = len(employee_skills & required_set)
        
        if match_count == 0:
            continue
        
        # 적합도 점수 계산
        skill_match_score = (match_count / len(required_set)) * 60 if required_set else 0
        role_match_score = 20 if any(r in role for r in ['architect', 'lead', 'senior']) else 10
        experience_score = min(scores.get('overall_score', 0) * 0.2, 20)
        
        fit_score = round(skill_match_score + role_match_score + experience_score, 1)
        
        reason = f"{match_count}개 기술 매칭, "
        if fit_score >= 80:
            reason += "즉시 투입 가능"
        elif fit_score >= 60:
            reason += "조건부 투입 가능"
        else:
            reason += "추가 학습 후 고려"
        
        recommendations.append({
            'project_id': proj.get('project_id', ''),
            'project_name': proj.get('project_name', ''),
            'fit_score': fit_score,
            'reason': reason
        })
    
    # 적합도 순으로 정렬하여 상위 3개 반환
    recommendations.sort(key=lambda x: x['fit_score'], reverse=True)
    return recommendations[:3]


def analyze_skill_gaps(employee_data: Dict, all_employees: List[Dict]) -> Dict[str, Any]:
    """같은 직책의 비슷한 경력자들과 비교하여 부족한 기술 분석"""
    experience_years = get_experience_years(employee_data)
    role = employee_data.get('basic_info', {}).get('role', employee_data.get('role', '')).lower()
    employee_skills = set([
        s.get('name', '').lower() if isinstance(s, dict) else str(s).lower()
        for s in employee_data.get('skills', [])
    ])
    
    # 같은 직책 또는 유사 직책 찾기
    similar_employees = []
    for emp in all_employees:
        emp_role = emp.get('basic_info', {}).get('role', emp.get('role', '')).lower()
        emp_exp = get_experience_years(emp)
        
        # 같은 직책이거나 유사 직책 (예: Senior, Lead 등)
        role_match = False
        if role == emp_role:
            role_match = True
        else:
            # 핵심 키워드 매칭
            role_keywords = ['architect', 'developer', 'engineer', 'frontend', 'backend', 'devops', 'fullstack', 'ai', 'ml', 'data']
            for keyword in role_keywords:
                if keyword in role and keyword in emp_role:
                    role_match = True
                    break
        
        # 경력 ±3년 범위
        if role_match and abs(emp_exp - experience_years) <= 3:
            similar_employees.append(emp)
    
    if len(similar_employees) < 2:
        return {
            'missing_skills': [],
            'recommended_skills': [],
            'peer_comparison': f"비교 가능한 동료 데이터가 부족합니다 (현재 {len(similar_employees)}명)"
        }
    
    # 동료들이 가진 기술 통계
    skill_frequency = {}
    for emp in similar_employees:
        emp_skills = emp.get('skills', [])
        for skill in emp_skills:
            if isinstance(skill, dict):
                skill_name = skill.get('name', '').lower()
                if skill_name and skill_name not in employee_skills:
                    skill_frequency[skill_name] = skill_frequency.get(skill_name, 0) + 1
    
    # 빈도순으로 정렬
    sorted_skills = sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True)
    
    # 50% 이상의 동료가 가진 기술 = 필수 기술
    threshold = len(similar_employees) * 0.5
    missing_skills = []
    recommended_skills = []
    
    for skill_name, count in sorted_skills:
        percentage = (count / len(similar_employees)) * 100
        skill_info = {
            'name': skill_name.title(),
            'percentage': round(percentage, 1),
            'count': count,
            'total': len(similar_employees)
        }
        
        if count >= threshold:
            missing_skills.append(skill_info)
        elif count >= len(similar_employees) * 0.3:  # 30% 이상
            recommended_skills.append(skill_info)
    
    # 비교 메시지 생성
    peer_comparison = f"같은 직책의 비슷한 경력자 {len(similar_employees)}명과 비교한 결과입니다."
    
    return {
        'missing_skills': missing_skills[:5],  # 상위 5개
        'recommended_skills': recommended_skills[:5],  # 상위 5개
        'peer_comparison': peer_comparison,
        'peer_count': len(similar_employees)
    }


def generate_ai_analysis(employee_data: Dict, scores: Dict, project_recommendations: List[Dict], all_employees: List[Dict]) -> Dict[str, Any]:
    """AI 분석 결과 생성 (규칙 기반)"""
    experience_years = get_experience_years(employee_data)
    skills = employee_data.get('skills', [])
    project_history = get_project_history(employee_data)
    role = employee_data.get('basic_info', {}).get('role', employee_data.get('role', ''))
    
    # 기술 격차 분석
    skill_gap_analysis = analyze_skill_gaps(employee_data, all_employees)
    
    # 강점 분석
    strengths = []
    if experience_years >= 10:
        strengths.append(f"{int(experience_years)}년의 풍부한 실무 경력")
    elif experience_years >= 5:
        strengths.append(f"{int(experience_years)}년의 충분한 실무 경험")
    else:
        strengths.append(f"{int(experience_years)}년의 실무 경험")
    
    if len(skills) >= 5:
        strengths.append(f"다양한 기술 스택 보유 ({len(skills)}개 기술)")
    
    if scores.get('technical_skills', 0) >= 80:
        strengths.append("우수한 기술 역량")
    
    if len(project_history) >= 3:
        strengths.append(f"풍부한 프로젝트 경험 ({len(project_history)}개)")
    
    # 개선 필요 사항 (기술 격차 포함)
    weaknesses = []
    
    # 기술 격차 기반 개선 사항
    missing_skills = skill_gap_analysis.get('missing_skills', [])
    if missing_skills:
        skill_names = ', '.join([s['name'] for s in missing_skills[:3]])
        weaknesses.append(f"동료 대비 부족한 필수 기술: {skill_names}")
    
    if scores.get('technical_skills', 0) < 70:
        weaknesses.append("기술 역량 강화 필요")
    
    if scores.get('project_experience', 0) < 70:
        weaknesses.append("프로젝트 경험 확대 필요")
    
    if scores.get('resume_credibility', 0) < 70:
        weaknesses.append("경력 이력 보완 필요")
    
    # 추천 기술 추가
    recommended_skills = skill_gap_analysis.get('recommended_skills', [])
    if recommended_skills and len(weaknesses) < 3:
        skill_names = ', '.join([s['name'] for s in recommended_skills[:2]])
        weaknesses.append(f"경쟁력 향상을 위한 추천 기술: {skill_names}")
    
    if not weaknesses:
        weaknesses.append("지속적인 최신 기술 트렌드 학습 권장")
    
    # 상세 분석
    tech_stack_analysis = f"{len(skills)}개의 기술을 보유하고 있으며, {role} 역할에 적합한 기술 스택입니다."
    if scores.get('technical_skills', 0) >= 80:
        tech_stack_analysis += " 시장에서 수요가 높은 기술들을 다수 보유하고 있습니다."
    
    project_similarity = f"{len(project_history)}개의 프로젝트 경험이 있어 실무 적응력이 우수합니다."
    if len(project_history) >= 3:
        project_similarity += " 다양한 프로젝트 경험으로 빠른 업무 파악이 가능합니다."
    
    credibility_check = "경력과 기술 수준이 일관성 있게 구성되어 있습니다."
    if scores.get('resume_credibility', 0) >= 80:
        credibility_check = "제출된 이력이 검증 가능하며 신뢰도가 높습니다."
    elif scores.get('resume_credibility', 0) < 70:
        credibility_check = "일부 경력 정보에 대한 추가 검증이 필요합니다."
    
    market_comparison = f"{int(experience_years)}년 경력 대비 적절한 기술 역량을 보유하고 있습니다."
    if scores.get('overall_score', 0) >= 85:
        market_comparison = f"{int(experience_years)}년 경력 대비 우수한 역량을 보유하고 있습니다."
    
    # 요약 코멘트 (3줄)
    summary_lines = []
    summary_lines.append(f"{role}로서 {int(experience_years)}년의 경력과 {len(skills)}개 기술을 보유하여 즉시 활용 가능합니다.")
    
    if weaknesses:
        summary_lines.append(weaknesses[0] + ".")
    
    summary_lines.append("클라우드 네이티브 아키텍처나 최신 프레임워크 관련 교육 프로그램 참여를 추천합니다.")
    
    summary_comment = " ".join(summary_lines)
    
    return {
        'strengths': strengths[:4],
        'weaknesses': weaknesses[:3],
        'tech_stack_analysis': tech_stack_analysis,
        'project_similarity': project_similarity,
        'credibility_check': credibility_check,
        'market_comparison': market_comparison,
        'summary_comment': summary_comment
    }


def analyze_with_ai(employee_data: Dict, all_projects: List[Dict], scores: Dict, all_employees: List[Dict]) -> Dict[str, Any]:
    """AI를 사용한 상세 분석 및 추천"""
    
    # 직원 정보 추출
    name = employee_data.get('basic_info', {}).get('name', employee_data.get('name', 'Unknown'))
    experience_years = get_experience_years(employee_data)
    role = employee_data.get('basic_info', {}).get('role', employee_data.get('role', ''))
    
    skills = employee_data.get('skills', [])
    project_history = get_project_history(employee_data)
    
    # 프로젝트 추천
    project_recommendations = generate_project_recommendations(employee_data, all_projects, scores)
    
    # 투입 가능 여부 판단
    overall_score = scores.get('overall_score', 0)
    tech_score = scores.get('technical_skills', 0)
    reliability_score = scores.get('resume_credibility', 0)
    
    if overall_score >= 80 and tech_score >= 75 and reliability_score >= 70:
        deployable = "즉시 투입 가능"
    elif overall_score >= 65 and tech_score >= 60:
        deployable = "조건부 투입 가능"
    elif overall_score >= 50:
        deployable = "추가 학습 후 고려"
    else:
        deployable = "부적합"
    
    # 추천 역할
    recommended_roles = []
    role_lower = role.lower()
    if 'architect' in role_lower:
        recommended_roles.append("시스템 아키텍트")
    if 'senior' in role_lower or 'lead' in role_lower:
        recommended_roles.append(f"{role} (리드 역할)")
    if 'frontend' in role_lower or 'front-end' in role_lower:
        recommended_roles.append("프론트엔드 개발자")
    if 'backend' in role_lower or 'back-end' in role_lower:
        recommended_roles.append("백엔드 개발자")
    if 'devops' in role_lower:
        recommended_roles.append("DevOps 엔지니어")
    if 'fullstack' in role_lower or 'full-stack' in role_lower:
        recommended_roles.append("풀스택 개발자")
    
    if not recommended_roles:
        recommended_roles.append(role if role else "개발자")
    
    # 규칙 기반 AI 분석 생성
    analysis = generate_ai_analysis(employee_data, scores, project_recommendations, all_employees)
    
    # 기술 격차 분석
    skill_gap_analysis = analyze_skill_gaps(employee_data, all_employees)
    
    # 추가 정보 포함
    analysis['deployable'] = deployable
    analysis['recommended_roles'] = recommended_roles
    analysis['recommended_projects'] = project_recommendations
    analysis['skill_gap_analysis'] = skill_gap_analysis
    
    return analysis


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
        scores = calculate_relative_scores(employee_data, all_employees, all_projects)
        
        # AI 분석 수행
        ai_analysis = analyze_with_ai(employee_data, all_projects, scores, all_employees)
        
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
            'ai_recommendation': ai_analysis.get('summary_comment', ''),
            'deployable': ai_analysis.get('deployable', '추가 검토 필요'),
            'recommended_roles': ai_analysis.get('recommended_roles', []),
            'recommended_projects': ai_analysis.get('recommended_projects', []),
            'skill_gap_analysis': ai_analysis.get('skill_gap_analysis', {}),
            'project_history': get_project_history(employee_data),
            'skills': employee_data.get('skills', []),
            'experience_years': get_experience_years(employee_data),
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
