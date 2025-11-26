"""
시각화 및 보고 Lambda 함수

이 Lambda 함수는 HR 시스템의 시각화 및 보고 기능을 제공합니다.
- 데이터 집계 (기술 분포, 도메인 커버리지, 팀 구성)
- 대시보드 메트릭
- 날짜 범위 필터링
- 보고서 내보내기 (PDF, Excel)
"""

import json
import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import boto3
from boto3.dynamodb.conditions import Key, Attr

# Lambda Layer 경로 추가
sys.path.append('/opt/python')

# 공통 모듈 임포트
sys.path.insert(0, '/var/task')
sys.path.insert(0, '/var/task/common')

from common.dynamodb_client import DynamoDBClient
from common.repositories import EmployeeRepository, ProjectRepository, AffinityRepository
from common.models import Employee, Project

# 보고서 생성 모듈 임포트
try:
    from report_generator import generate_pdf_report, generate_excel_report, upload_report_to_s3
except ImportError:
    from lambda_functions.visualization.report_generator import (
        generate_pdf_report,
        generate_excel_report,
        upload_report_to_s3
    )


# 환경 변수
REGION = os.environ.get('AWS_REGION', 'us-east-2')

# DynamoDB 클라이언트 초기화
dynamodb_client = DynamoDBClient(region_name=REGION)
employee_repo = EmployeeRepository(dynamodb_client)
project_repo = ProjectRepository(dynamodb_client)
affinity_repo = AffinityRepository(dynamodb_client)


def aggregate_skill_distribution() -> Dict[str, Any]:
    """
    전체 직원의 기술 스택 분포를 집계합니다.
    
    Returns:
        기술별 직원 수, 숙련도 분포, 평균 경력 연수를 포함한 딕셔너리
    """
    try:
        # 모든 직원 조회
        employees = employee_repo.get_all_employees()
        
        # 기술별 통계 수집
        skill_stats = defaultdict(lambda: {
            'count': 0,
            'levels': Counter(),
            'total_years': 0,
            'employees': []
        })
        
        for employee in employees:
            for skill in employee.skills:
                skill_name = skill.name
                skill_stats[skill_name]['count'] += 1
                skill_stats[skill_name]['levels'][skill.level] += 1
                skill_stats[skill_name]['total_years'] += skill.years
                skill_stats[skill_name]['employees'].append(employee.user_id)
        
        # 결과 포맷팅
        result = []
        for skill_name, stats in skill_stats.items():
            result.append({
                'skill_name': skill_name,
                'employee_count': stats['count'],
                'level_distribution': dict(stats['levels']),
                'average_years': round(stats['total_years'] / stats['count'], 1) if stats['count'] > 0 else 0,
                'employees': stats['employees']
            })
        
        # 직원 수 기준 내림차순 정렬
        result.sort(key=lambda x: x['employee_count'], reverse=True)
        
        return {
            'total_skills': len(result),
            'total_employees': len(employees),
            'skills': result
        }
        
    except Exception as e:
        print(f"기술 분포 집계 오류: {str(e)}")
        raise


def calculate_domain_coverage() -> Dict[str, Any]:
    """
    프로젝트 도메인 커버리지를 계산합니다.
    
    Returns:
        도메인별 프로젝트 수, 기술 스택, 참여 인력을 포함한 딕셔너리
    """
    try:
        # 모든 프로젝트 조회
        projects = project_repo.get_all_projects()
        
        # 도메인별 통계 수집
        domain_stats = defaultdict(lambda: {
            'project_count': 0,
            'projects': [],
            'tech_stacks': set(),
            'total_budget': 0
        })
        
        for project in projects:
            domain = project.client_industry
            domain_stats[domain]['project_count'] += 1
            domain_stats[domain]['projects'].append({
                'project_id': project.project_id,
                'project_name': project.project_name,
                'period': project.period.model_dump()
            })
            
            # 기술 스택 수집
            tech_stack = project.tech_stack
            domain_stats[domain]['tech_stacks'].update(tech_stack.backend)
            domain_stats[domain]['tech_stacks'].update(tech_stack.frontend)
            domain_stats[domain]['tech_stacks'].update(tech_stack.data)
            domain_stats[domain]['tech_stacks'].update(tech_stack.infra)
        
        # 결과 포맷팅
        result = []
        for domain, stats in domain_stats.items():
            result.append({
                'domain': domain,
                'project_count': stats['project_count'],
                'projects': stats['projects'],
                'unique_tech_count': len(stats['tech_stacks']),
                'tech_stacks': list(stats['tech_stacks'])
            })
        
        # 프로젝트 수 기준 내림차순 정렬
        result.sort(key=lambda x: x['project_count'], reverse=True)
        
        return {
            'total_domains': len(result),
            'total_projects': len(projects),
            'domains': result
        }
        
    except Exception as e:
        print(f"도메인 커버리지 계산 오류: {str(e)}")
        raise


def summarize_team_composition() -> Dict[str, Any]:
    """
    팀 구성 현황을 요약합니다.
    
    Returns:
        역할별 인원 수, 경력 분포, 가용성을 포함한 딕셔너리
    """
    try:
        # 모든 직원 조회
        employees = employee_repo.get_all_employees()
        
        # 역할별 통계
        role_stats = Counter()
        experience_distribution = {
            '0-2년': 0,
            '3-5년': 0,
            '6-10년': 0,
            '11년 이상': 0
        }
        
        for employee in employees:
            role = employee.basic_info.role
            role_stats[role] += 1
            
            years = employee.basic_info.years_of_experience
            if years <= 2:
                experience_distribution['0-2년'] += 1
            elif years <= 5:
                experience_distribution['3-5년'] += 1
            elif years <= 10:
                experience_distribution['6-10년'] += 1
            else:
                experience_distribution['11년 이상'] += 1
        
        return {
            'total_employees': len(employees),
            'role_distribution': dict(role_stats),
            'experience_distribution': experience_distribution,
            'roles': [
                {
                    'role': role,
                    'count': count,
                    'percentage': round(count / len(employees) * 100, 1)
                }
                for role, count in role_stats.most_common()
            ]
        }
        
    except Exception as e:
        print(f"팀 구성 요약 오류: {str(e)}")
        raise


def get_dashboard_metrics() -> Dict[str, Any]:
    """
    대시보드 메트릭을 조회합니다.
    
    Returns:
        인력 가용성, 프로젝트 진행 현황, 추천 대기 건수를 포함한 딕셔너리
    """
    try:
        # 직원 및 프로젝트 조회
        employees = employee_repo.get_all_employees()
        projects = project_repo.get_all_projects()
        
        # 현재 날짜
        today = datetime.now()
        
        # 진행 중인 프로젝트 계산
        active_projects = []
        for project in projects:
            try:
                start_date = datetime.strptime(project.period.start, '%Y-%m-%d')
                end_date = datetime.strptime(project.period.end, '%Y-%m-%d')
                
                if start_date <= today <= end_date:
                    active_projects.append({
                        'project_id': project.project_id,
                        'project_name': project.project_name,
                        'client_industry': project.client_industry,
                        'end_date': project.period.end
                    })
            except ValueError:
                # 날짜 파싱 실패 시 무시
                continue
        
        # 가용 인력 계산 (간단한 버전 - 실제로는 프로젝트 배정 정보 필요)
        total_employees = len(employees)
        
        return {
            'timestamp': today.isoformat(),
            'employee_metrics': {
                'total_employees': total_employees,
                'available_employees': total_employees,  # 실제로는 프로젝트 배정 정보 필요
                'availability_rate': 100.0  # 실제로는 계산 필요
            },
            'project_metrics': {
                'total_projects': len(projects),
                'active_projects': len(active_projects),
                'active_project_list': active_projects
            },
            'recommendation_metrics': {
                'pending_recommendations': 0  # 실제로는 추천 요청 테이블 필요
            }
        }
        
    except Exception as e:
        print(f"대시보드 메트릭 조회 오류: {str(e)}")
        raise


def filter_by_date_range(
    start_date: str,
    end_date: str,
    data_type: str = 'projects'
) -> Dict[str, Any]:
    """
    날짜 범위로 데이터를 필터링합니다.
    
    Args:
        start_date: 시작 날짜 (YYYY-MM-DD)
        end_date: 종료 날짜 (YYYY-MM-DD)
        data_type: 데이터 타입 ('projects' 또는 'employees')
        
    Returns:
        필터링된 데이터
    """
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        if data_type == 'projects':
            projects = project_repo.get_all_projects()
            filtered = []
            
            for project in projects:
                try:
                    project_start = datetime.strptime(project.period.start, '%Y-%m-%d')
                    project_end = datetime.strptime(project.period.end, '%Y-%m-%d')
                    
                    # 프로젝트 기간이 필터 범위와 겹치는지 확인
                    if not (project_end < start or project_start > end):
                        filtered.append(project.to_dynamodb())
                except ValueError:
                    continue
            
            return {
                'data_type': 'projects',
                'start_date': start_date,
                'end_date': end_date,
                'count': len(filtered),
                'data': filtered
            }
        
        else:
            return {
                'error': f'지원하지 않는 데이터 타입: {data_type}'
            }
            
    except ValueError as e:
        return {
            'error': f'잘못된 날짜 형식: {str(e)}'
        }
    except Exception as e:
        print(f"날짜 범위 필터링 오류: {str(e)}")
        raise


def export_report(
    report_type: str,
    format: str = 'pdf'
) -> Dict[str, Any]:
    """
    보고서를 PDF 또는 Excel 형식으로 내보냅니다.
    
    Args:
        report_type: 보고서 유형 ('skills', 'domains', 'team', 'dashboard')
        format: 내보내기 형식 ('pdf' 또는 'excel')
        
    Returns:
        S3 URL과 메타데이터를 포함한 딕셔너리
    """
    try:
        # 보고서 데이터 수집
        if report_type == 'skills':
            data = aggregate_skill_distribution()
        elif report_type == 'domains':
            data = calculate_domain_coverage()
        elif report_type == 'team':
            data = summarize_team_composition()
        elif report_type == 'dashboard':
            data = get_dashboard_metrics()
        else:
            return {
                'error': f'지원하지 않는 보고서 유형: {report_type}'
            }
        
        # 보고서 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'pdf':
            report_data = generate_pdf_report(data, report_type)
            file_name = f"{report_type}_report_{timestamp}.pdf"
        elif format == 'excel':
            report_data = generate_excel_report(data, report_type)
            file_name = f"{report_type}_report_{timestamp}.csv"
        else:
            return {
                'error': f'지원하지 않는 형식: {format}'
            }
        
        # S3에 업로드
        s3_url = upload_report_to_s3(report_data, file_name)
        
        return {
            'report_type': report_type,
            'format': format,
            'file_name': file_name,
            's3_url': s3_url,
            'generated_at': timestamp,
            'size_bytes': len(report_data)
        }
        
    except Exception as e:
        print(f"보고서 내보내기 오류: {str(e)}")
        raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda 핸들러 함수
    
    API Gateway에서 호출되며 다양한 시각화 및 보고 기능을 제공합니다.
    
    Args:
        event: API Gateway 이벤트
        context: Lambda 컨텍스트
        
    Returns:
        API Gateway 응답
    """
    try:
        # 요청 파싱
        body = json.loads(event.get('body', '{}'))
        action = body.get('action')
        
        print(f"시각화 요청 수신: action={action}")
        
        # 액션별 처리
        if action == 'aggregate_skills':
            result = aggregate_skill_distribution()
            
        elif action == 'calculate_domains':
            result = calculate_domain_coverage()
            
        elif action == 'summarize_team':
            result = summarize_team_composition()
            
        elif action == 'dashboard_metrics':
            result = get_dashboard_metrics()
            
        elif action == 'filter_by_date':
            start_date = body.get('start_date')
            end_date = body.get('end_date')
            data_type = body.get('data_type', 'projects')
            
            if not start_date or not end_date:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'start_date와 end_date가 필요합니다'
                    }, ensure_ascii=False)
                }
            
            result = filter_by_date_range(start_date, end_date, data_type)
        
        elif action == 'export_report':
            report_type = body.get('report_type', 'dashboard')
            format = body.get('format', 'pdf')
            
            result = export_report(report_type, format)
            
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': f'지원하지 않는 액션: {action}'
                }, ensure_ascii=False)
            }
        
        # 성공 응답
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result, ensure_ascii=False, default=str)
        }
        
    except Exception as e:
        print(f"Lambda 실행 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': '내부 서버 오류',
                'message': str(e)
            }, ensure_ascii=False)
        }
