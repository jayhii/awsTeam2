"""
Domain Analysis Engine Lambda Function
신규 도메인 확장 분석

Requirements: 4.1, 4.2, 4.3, 4.4
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
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-2'))


def handler(event, context):
    """
    Lambda handler for API Gateway
    
    Requirements: 4.1 - 도메인 분석 수행
    
    Args:
        event: API Gateway 이벤트
        context: Lambda 컨텍스트
        
    Returns:
        dict: API Gateway 응답
    """
    try:
        logger.info(f"도메인 분석 요청 수신: {json.dumps(event)}")
        
        # 요청 본문 파싱
        body = json.loads(event.get('body', '{}'))
        analysis_type = body.get('analysis_type', 'new_domains')
        
        # 전체 프로젝트 이력 수집
        projects = fetch_all_projects()
        employees = fetch_all_employees()
        
        logger.info(f"프로젝트 {len(projects)}개, 직원 {len(employees)}명 조회")
        
        # 도메인 분석 수행
        if analysis_type == 'new_domains':
            result = analyze_new_domains(projects, employees)
        elif analysis_type == 'expansion_strategy':
            result = analyze_expansion_strategy(projects, employees)
        else:
            result = analyze_new_domains(projects, employees)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(result, default=decimal_default)
        }
        
    except Exception as e:
        logger.error(f"도메인 분석 중 오류 발생: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }


def fetch_all_projects() -> List[Dict[str, Any]]:
    """
    모든 프로젝트 조회
    
    Returns:
        list: 프로젝트 목록
    """
    try:
        table = dynamodb.Table('Projects')
        response = table.scan()
        
        projects = response.get('Items', [])
        
        # 페이지네이션 처리
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            projects.extend(response.get('Items', []))
        
        return projects
        
    except Exception as e:
        logger.error(f"프로젝트 조회 실패: {str(e)}")
        return []


def fetch_all_employees() -> List[Dict[str, Any]]:
    """
    모든 직원 조회
    
    Returns:
        list: 직원 목록
    """
    try:
        table = dynamodb.Table('Employees')
        response = table.scan()
        
        employees = response.get('Items', [])
        
        # 페이지네이션 처리
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            employees.extend(response.get('Items', []))
        
        return employees
        
    except Exception as e:
        logger.error(f"직원 조회 실패: {str(e)}")
        return []


def analyze_new_domains(
    projects: List[Dict[str, Any]],
    employees: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    신규 도메인 분석
    
    Requirements: 4.1, 4.2, 4.3
    
    Args:
        projects: 프로젝트 목록
        employees: 직원 목록
        
    Returns:
        dict: 도메인 분석 결과
    """
    # 1. 프로젝트 도메인 분류 (Requirements: 4.1)
    domain_classification = classify_project_domains(projects)
    
    # 2. 신규 도메인 식별 (Requirements: 4.2)
    potential_domains = identify_potential_domains(domain_classification)
    
    # 3. 도메인 진입 분석 (Requirements: 4.3)
    domain_analysis = []
    for domain in potential_domains:
        analysis = analyze_domain_entry(domain, employees)
        domain_analysis.append(analysis)
    
    return {
        'current_domains': domain_classification['current_domains'],
        'identified_domains': domain_analysis,
        'total_projects_analyzed': len(projects),
        'total_employees': len(employees)
    }


def classify_project_domains(projects: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    프로젝트 도메인 분류
    
    Requirements: 4.1 - Claude를 사용한 도메인 분류
    
    Args:
        projects: 프로젝트 목록
        
    Returns:
        dict: 도메인 분류 결과
    """
    try:
        # 프로젝트 정보 요약
        project_summaries = []
        for project in projects[:20]:  # 최대 20개 프로젝트 분석
            summary = {
                'name': project.get('project_name', ''),
                'industry': project.get('client_industry', ''),
                'tech_stack': project.get('tech_stack', {})
            }
            project_summaries.append(summary)
        
        # Claude를 사용한 도메인 분류
        prompt = f"""다음 프로젝트들을 분석하여 도메인을 분류해주세요:

프로젝트 목록:
{json.dumps(project_summaries, ensure_ascii=False, indent=2)}

다음 형식으로 응답해주세요:
1. 현재 보유 도메인 목록 (예: Finance, Healthcare, E-commerce)
2. 각 도메인별 주요 기술 스택
3. 각 도메인별 프로젝트 수

JSON 형식으로 응답해주세요."""

        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-v2',
            body=json.dumps({
                'prompt': f"\n\nHuman: {prompt}\n\nAssistant:",
                'max_tokens_to_sample': 1000,
                'temperature': 0.5
            })
        )
        
        response_body = json.loads(response['body'].read())
        classification_text = response_body.get('completion', '').strip()
        
        # 간단한 파싱 (실제로는 더 정교한 파싱 필요)
        current_domains = extract_domains_from_text(classification_text)
        
        return {
            'current_domains': current_domains,
            'classification_text': classification_text
        }
        
    except Exception as e:
        logger.error(f"도메인 분류 실패: {str(e)}")
        # 기본 도메인 반환
        return {
            'current_domains': ['Finance', 'Healthcare', 'E-commerce'],
            'classification_text': ''
        }


def extract_domains_from_text(text: str) -> List[str]:
    """
    텍스트에서 도메인 추출
    
    Args:
        text: 분류 텍스트
        
    Returns:
        list: 도메인 목록
    """
    # 간단한 구현: 일반적인 도메인 키워드 찾기
    common_domains = [
        'Finance', 'Banking', 'Healthcare', 'E-commerce', 'Retail',
        'Manufacturing', 'Logistics', 'Education', 'Government',
        'Telecommunications', 'Media', 'Entertainment', 'Insurance'
    ]
    
    found_domains = []
    for domain in common_domains:
        if domain.lower() in text.lower():
            found_domains.append(domain)
    
    return found_domains if found_domains else ['General']


def identify_potential_domains(classification: Dict[str, Any]) -> List[str]:
    """
    잠재적 신규 도메인 식별
    
    Requirements: 4.2 - 현재 보유하지 않은 도메인 식별
    
    Args:
        classification: 도메인 분류 결과
        
    Returns:
        list: 잠재적 신규 도메인 목록
    """
    current_domains = set(classification.get('current_domains', []))
    
    # 모든 가능한 도메인
    all_domains = {
        'Finance', 'Banking', 'Healthcare', 'E-commerce', 'Retail',
        'Manufacturing', 'Logistics', 'Education', 'Government',
        'Telecommunications', 'Media', 'Entertainment', 'Insurance',
        'Real Estate', 'Energy', 'Transportation', 'Hospitality'
    }
    
    # 현재 보유하지 않은 도메인
    potential_domains = list(all_domains - current_domains)
    
    # 상위 5개만 반환
    return potential_domains[:5]


def analyze_domain_entry(
    domain: str,
    employees: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    도메인 진입 분석
    
    Requirements: 4.3 - 기술 갭 및 전환 가능성 분석
    
    Args:
        domain: 도메인 이름
        employees: 직원 목록
        
    Returns:
        dict: 도메인 진입 분석 결과
    """
    try:
        # 도메인별 필요 기술 정의
        required_skills = get_required_skills_for_domain(domain)
        
        # 현재 보유 기술 분석
        current_skills = set()
        for employee in employees:
            skills = employee.get('skills', [])
            for skill in skills:
                if isinstance(skill, dict):
                    current_skills.add(skill.get('name', ''))
        
        # 기술 갭 계산
        skill_gap = list(set(required_skills) - current_skills)
        
        # 전환 가능한 직원 찾기
        transferable_employees = find_transferable_employees(
            employees,
            required_skills
        )
        
        # 실현 가능성 점수 계산
        feasibility_score = calculate_feasibility_score(
            required_skills,
            current_skills,
            transferable_employees
        )
        
        return {
            'domain_name': domain,
            'feasibility_score': feasibility_score,
            'required_skills': required_skills,
            'skill_gap': skill_gap,
            'transferable_employees': len(transferable_employees),
            'recommended_team': [emp.get('user_id') for emp in transferable_employees[:5]]
        }
        
    except Exception as e:
        logger.error(f"도메인 진입 분석 실패: {str(e)}")
        return {
            'domain_name': domain,
            'feasibility_score': 0,
            'required_skills': [],
            'skill_gap': [],
            'transferable_employees': 0,
            'recommended_team': []
        }


def get_required_skills_for_domain(domain: str) -> List[str]:
    """
    도메인별 필요 기술 반환
    
    Args:
        domain: 도메인 이름
        
    Returns:
        list: 필요 기술 목록
    """
    domain_skills = {
        'Finance': ['Java', 'Spring', 'Oracle', 'Security', 'Compliance'],
        'Healthcare': ['Python', 'HIPAA', 'HL7', 'FHIR', 'Data Privacy'],
        'E-commerce': ['Node.js', 'React', 'MongoDB', 'Payment Gateway', 'AWS'],
        'Manufacturing': ['IoT', 'Python', 'Data Analytics', 'ERP', 'MES'],
        'Logistics': ['GPS', 'Route Optimization', 'Mobile', 'Real-time Tracking'],
        'Education': ['LMS', 'Video Streaming', 'Mobile', 'Gamification'],
        'Government': ['Security', 'Compliance', 'Java', 'Legacy Systems'],
        'Telecommunications': ['5G', 'Network', 'Real-time', 'High Availability'],
        'Insurance': ['Actuarial', 'Risk Assessment', 'Java', 'Compliance'],
        'Real Estate': ['GIS', 'Mobile', 'Payment', 'CRM'],
        'Energy': ['IoT', 'SCADA', 'Real-time Monitoring', 'Data Analytics'],
        'Transportation': ['GPS', 'Route Planning', 'Mobile', 'Real-time'],
        'Hospitality': ['Booking System', 'Payment', 'Mobile', 'CRM']
    }
    
    return domain_skills.get(domain, ['General Programming', 'Database', 'Web Development'])


def find_transferable_employees(
    employees: List[Dict[str, Any]],
    required_skills: List[str]
) -> List[Dict[str, Any]]:
    """
    전환 가능한 직원 찾기
    
    Args:
        employees: 직원 목록
        required_skills: 필요 기술 목록
        
    Returns:
        list: 전환 가능한 직원 목록
    """
    transferable = []
    
    for employee in employees:
        employee_skills = set()
        skills = employee.get('skills', [])
        for skill in skills:
            if isinstance(skill, dict):
                employee_skills.add(skill.get('name', ''))
        
        # 필요 기술 중 일부를 보유한 직원
        matched_skills = employee_skills.intersection(set(required_skills))
        if len(matched_skills) >= len(required_skills) * 0.3:  # 30% 이상 매칭
            transferable.append(employee)
    
    return transferable


def calculate_feasibility_score(
    required_skills: List[str],
    current_skills: Set[str],
    transferable_employees: List[Dict[str, Any]]
) -> float:
    """
    실현 가능성 점수 계산
    
    Args:
        required_skills: 필요 기술 목록
        current_skills: 현재 보유 기술
        transferable_employees: 전환 가능한 직원 목록
        
    Returns:
        float: 실현 가능성 점수 (0-100)
    """
    # 기술 보유율
    skill_coverage = len(current_skills.intersection(set(required_skills))) / len(required_skills)
    
    # 인력 가용성
    employee_availability = min(1.0, len(transferable_employees) / 5.0)  # 최소 5명 필요
    
    # 종합 점수
    feasibility = (skill_coverage * 0.6 + employee_availability * 0.4) * 100
    
    return round(feasibility, 2)


def analyze_expansion_strategy(
    projects: List[Dict[str, Any]],
    employees: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    확장 전략 분석
    
    Args:
        projects: 프로젝트 목록
        employees: 직원 목록
        
    Returns:
        dict: 확장 전략 분석 결과
    """
    # 신규 도메인 분석 재사용
    new_domains_result = analyze_new_domains(projects, employees)
    
    # 우선순위 정렬 (실현 가능성 기준)
    sorted_domains = sorted(
        new_domains_result['identified_domains'],
        key=lambda x: x['feasibility_score'],
        reverse=True
    )
    
    return {
        'recommended_domains': sorted_domains[:3],
        'expansion_strategy': 'Focus on high-feasibility domains first',
        'total_analysis': new_domains_result
    }


def update_domain_portfolio_on_new_hire(employee_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    신규 채용 시 도메인 포트폴리오 업데이트
    
    Requirements: 4.4 - 신규 직원의 기술로 진입 가능한 도메인 추가
    
    Args:
        employee_data: 신규 직원 데이터
        
    Returns:
        dict: 업데이트된 도메인 포트폴리오
    """
    try:
        # 신규 직원의 기술 추출
        employee_skills = set()
        skills = employee_data.get('skills', [])
        for skill in skills:
            if isinstance(skill, dict):
                employee_skills.add(skill.get('name', ''))
        
        logger.info(f"신규 직원 기술: {employee_skills}")
        
        # 모든 도메인에 대해 진입 가능성 확인
        all_domains = [
            'Finance', 'Banking', 'Healthcare', 'E-commerce', 'Retail',
            'Manufacturing', 'Logistics', 'Education', 'Government',
            'Telecommunications', 'Media', 'Entertainment', 'Insurance',
            'Real Estate', 'Energy', 'Transportation', 'Hospitality'
        ]
        
        new_accessible_domains = []
        
        for domain in all_domains:
            required_skills = set(get_required_skills_for_domain(domain))
            
            # 신규 직원의 기술이 도메인 필요 기술의 30% 이상을 충족하는지 확인
            matched_skills = employee_skills.intersection(required_skills)
            match_rate = len(matched_skills) / len(required_skills) if required_skills else 0
            
            if match_rate >= 0.3:
                new_accessible_domains.append({
                    'domain': domain,
                    'match_rate': round(match_rate * 100, 2),
                    'matched_skills': list(matched_skills)
                })
        
        # DomainPortfolio 테이블에 저장 (테이블이 있다면)
        if new_accessible_domains:
            try:
                table = dynamodb.Table('DomainPortfolio')
                for domain_info in new_accessible_domains:
                    table.put_item(Item={
                        'domain_name': domain_info['domain'],
                        'employee_id': employee_data.get('user_id'),
                        'match_rate': Decimal(str(domain_info['match_rate'])),
                        'matched_skills': domain_info['matched_skills'],
                        'added_date': employee_data.get('hire_date', 'unknown')
                    })
                logger.info(f"도메인 포트폴리오 업데이트 완료: {len(new_accessible_domains)}개 도메인")
            except Exception as e:
                logger.warning(f"DomainPortfolio 테이블 업데이트 실패 (테이블이 없을 수 있음): {str(e)}")
        
        return {
            'employee_id': employee_data.get('user_id'),
            'new_accessible_domains': new_accessible_domains,
            'total_domains_added': len(new_accessible_domains)
        }
        
    except Exception as e:
        logger.error(f"도메인 포트폴리오 업데이트 실패: {str(e)}")
        return {
            'employee_id': employee_data.get('user_id'),
            'new_accessible_domains': [],
            'total_domains_added': 0,
            'error': str(e)
        }


def decimal_default(obj):
    """Decimal을 float로 변환"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError
