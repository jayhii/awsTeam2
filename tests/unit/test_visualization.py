"""
시각화 및 보고 기능 단위 테스트

Requirements: 8.1, 8.2, 8.3, 8.4
"""

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from collections import Counter

# 테스트 대상 모듈 임포트
import sys
sys.path.insert(0, 'lambda_functions/visualization')
sys.path.insert(0, 'common')

from lambda_functions.visualization.index import (
    aggregate_skill_distribution,
    calculate_domain_coverage,
    summarize_team_composition,
    get_dashboard_metrics,
    filter_by_date_range,
    export_report
)
from lambda_functions.visualization.report_generator import (
    generate_pdf_report,
    generate_excel_report
)


class TestDataAggregation:
    """데이터 집계 함수 테스트"""
    
    @patch('lambda_functions.visualization.index.employee_repo')
    def test_aggregate_skill_distribution(self, mock_repo):
        """기술 분포 집계 테스트"""
        # Mock 직원 데이터
        from common.models import Employee, BasicInfo, Skill, SkillLevel
        
        mock_employees = [
            Employee(
                user_id='U_001',
                basic_info=BasicInfo(
                    name='테스트1',
                    role='Engineer',
                    years_of_experience=5,
                    email='test1@test.com'
                ),
                skills=[
                    Skill(name='Python', level=SkillLevel.EXPERT, years=5),
                    Skill(name='Java', level=SkillLevel.ADVANCED, years=3)
                ]
            ),
            Employee(
                user_id='U_002',
                basic_info=BasicInfo(
                    name='테스트2',
                    role='Engineer',
                    years_of_experience=3,
                    email='test2@test.com'
                ),
                skills=[
                    Skill(name='Python', level=SkillLevel.INTERMEDIATE, years=2)
                ]
            )
        ]
        
        mock_repo.get_all_employees.return_value = mock_employees
        
        # 실행
        result = aggregate_skill_distribution()
        
        # 검증
        assert result['total_employees'] == 2
        assert result['total_skills'] == 2
        assert len(result['skills']) == 2
        
        # Python이 가장 많은 직원을 보유
        python_skill = next(s for s in result['skills'] if s['skill_name'] == 'Python')
        assert python_skill['employee_count'] == 2
        assert python_skill['average_years'] == 3.5
    
    @patch('lambda_functions.visualization.index.project_repo')
    def test_calculate_domain_coverage(self, mock_repo):
        """도메인 커버리지 계산 테스트"""
        from common.models import Project, ProjectPeriod, TechStack
        
        mock_projects = [
            Project(
                project_id='P_001',
                project_name='프로젝트1',
                client_industry='Finance',
                period=ProjectPeriod(start='2024-01-01', end='2024-12-31', duration_months=12),
                tech_stack=TechStack(
                    backend=['Java', 'Spring'],
                    frontend=['React'],
                    data=['PostgreSQL'],
                    infra=['AWS']
                )
            ),
            Project(
                project_id='P_002',
                project_name='프로젝트2',
                client_industry='Finance',
                period=ProjectPeriod(start='2024-06-01', end='2024-12-31', duration_months=7),
                tech_stack=TechStack(
                    backend=['Python', 'Django'],
                    frontend=['Vue.js'],
                    data=['MongoDB'],
                    infra=['GCP']
                )
            )
        ]
        
        mock_repo.get_all_projects.return_value = mock_projects
        
        # 실행
        result = calculate_domain_coverage()
        
        # 검증
        assert result['total_domains'] == 1
        assert result['total_projects'] == 2
        
        finance_domain = result['domains'][0]
        assert finance_domain['domain'] == 'Finance'
        assert finance_domain['project_count'] == 2
        assert finance_domain['unique_tech_count'] > 0
    
    @patch('lambda_functions.visualization.index.employee_repo')
    def test_summarize_team_composition(self, mock_repo):
        """팀 구성 요약 테스트"""
        from common.models import Employee, BasicInfo
        
        mock_employees = [
            Employee(
                user_id='U_001',
                basic_info=BasicInfo(
                    name='테스트1',
                    role='Senior Engineer',
                    years_of_experience=8,
                    email='test1@test.com'
                ),
                skills=[]
            ),
            Employee(
                user_id='U_002',
                basic_info=BasicInfo(
                    name='테스트2',
                    role='Junior Engineer',
                    years_of_experience=2,
                    email='test2@test.com'
                ),
                skills=[]
            ),
            Employee(
                user_id='U_003',
                basic_info=BasicInfo(
                    name='테스트3',
                    role='Senior Engineer',
                    years_of_experience=12,
                    email='test3@test.com'
                ),
                skills=[]
            )
        ]
        
        mock_repo.get_all_employees.return_value = mock_employees
        
        # 실행
        result = summarize_team_composition()
        
        # 검증
        assert result['total_employees'] == 3
        assert 'role_distribution' in result
        assert result['role_distribution']['Senior Engineer'] == 2
        assert result['role_distribution']['Junior Engineer'] == 1
        
        # 경력 분포 확인
        exp_dist = result['experience_distribution']
        assert exp_dist['0-2년'] == 1
        assert exp_dist['6-10년'] == 1
        assert exp_dist['11년 이상'] == 1


class TestDashboardMetrics:
    """대시보드 메트릭 테스트"""
    
    @patch('lambda_functions.visualization.index.project_repo')
    @patch('lambda_functions.visualization.index.employee_repo')
    def test_get_dashboard_metrics(self, mock_emp_repo, mock_proj_repo):
        """대시보드 메트릭 조회 테스트"""
        from common.models import Employee, BasicInfo, Project, ProjectPeriod, TechStack
        
        # Mock 데이터
        mock_emp_repo.get_all_employees.return_value = [
            Employee(
                user_id='U_001',
                basic_info=BasicInfo(
                    name='테스트',
                    role='Engineer',
                    years_of_experience=5,
                    email='test@test.com'
                ),
                skills=[]
            )
        ]
        
        today = datetime.now()
        mock_proj_repo.get_all_projects.return_value = [
            Project(
                project_id='P_001',
                project_name='진행중 프로젝트',
                client_industry='IT',
                period=ProjectPeriod(
                    start='2024-01-01',
                    end='2025-12-31',
                    duration_months=24
                ),
                tech_stack=TechStack()
            )
        ]
        
        # 실행
        result = get_dashboard_metrics()
        
        # 검증
        assert 'employee_metrics' in result
        assert 'project_metrics' in result
        assert 'recommendation_metrics' in result
        
        assert result['employee_metrics']['total_employees'] == 1
        assert result['project_metrics']['total_projects'] == 1


class TestDateRangeFiltering:
    """날짜 범위 필터링 테스트"""
    
    @patch('lambda_functions.visualization.index.project_repo')
    def test_filter_projects_by_date_range(self, mock_repo):
        """프로젝트 날짜 범위 필터링 테스트"""
        from common.models import Project, ProjectPeriod, TechStack
        
        mock_projects = [
            Project(
                project_id='P_001',
                project_name='2024 프로젝트',
                client_industry='IT',
                period=ProjectPeriod(
                    start='2024-01-01',
                    end='2024-06-30',
                    duration_months=6
                ),
                tech_stack=TechStack()
            ),
            Project(
                project_id='P_002',
                project_name='2025 프로젝트',
                client_industry='Finance',
                period=ProjectPeriod(
                    start='2025-01-01',
                    end='2025-12-31',
                    duration_months=12
                ),
                tech_stack=TechStack()
            )
        ]
        
        mock_repo.get_all_projects.return_value = mock_projects
        
        # 2024년 프로젝트만 필터링
        result = filter_by_date_range('2024-01-01', '2024-12-31', 'projects')
        
        # 검증
        assert result['data_type'] == 'projects'
        assert result['count'] == 1
        assert result['data'][0]['project_id'] == 'P_001'
    
    def test_filter_invalid_date_format(self):
        """잘못된 날짜 형식 테스트"""
        result = filter_by_date_range('invalid-date', '2024-12-31', 'projects')
        
        assert 'error' in result
        assert '잘못된 날짜 형식' in result['error']


class TestReportGeneration:
    """보고서 생성 테스트"""
    
    def test_generate_pdf_report_skills(self):
        """기술 분포 PDF 보고서 생성 테스트"""
        data = {
            'total_skills': 10,
            'total_employees': 50,
            'skills': [
                {
                    'skill_name': 'Python',
                    'employee_count': 30,
                    'average_years': 5.5
                }
            ]
        }
        
        result = generate_pdf_report(data, 'skills')
        
        assert isinstance(result, bytes)
        assert len(result) > 0
        assert b'Python' in result
    
    def test_generate_excel_report_domains(self):
        """도메인 커버리지 Excel 보고서 생성 테스트"""
        data = {
            'total_domains': 5,
            'total_projects': 20,
            'domains': [
                {
                    'domain': 'Finance',
                    'project_count': 10,
                    'unique_tech_count': 15
                }
            ]
        }
        
        result = generate_excel_report(data, 'domains')
        
        assert isinstance(result, bytes)
        assert len(result) > 0
        # CSV 형식이므로 쉼표가 포함되어야 함
        assert b',' in result


class TestLambdaHandler:
    """Lambda 핸들러 테스트"""
    
    @patch('lambda_functions.visualization.index.aggregate_skill_distribution')
    def test_lambda_handler_aggregate_skills(self, mock_aggregate):
        """기술 집계 액션 테스트"""
        from lambda_functions.visualization.index import lambda_handler
        
        mock_aggregate.return_value = {
            'total_skills': 10,
            'total_employees': 50
        }
        
        event = {
            'body': json.dumps({
                'action': 'aggregate_skills'
            })
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['total_skills'] == 10
    
    def test_lambda_handler_invalid_action(self):
        """잘못된 액션 테스트"""
        from lambda_functions.visualization.index import lambda_handler
        
        event = {
            'body': json.dumps({
                'action': 'invalid_action'
            })
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
    
    def test_lambda_handler_missing_date_params(self):
        """날짜 파라미터 누락 테스트"""
        from lambda_functions.visualization.index import lambda_handler
        
        event = {
            'body': json.dumps({
                'action': 'filter_by_date'
            })
        }
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
