#!/usr/bin/env python3
"""
Lambda 함수에 환경 변수 추가
"""

import boto3

REGION = "us-east-2"
lambda_client = boto3.client('lambda', region_name=REGION)

def update_env_vars(function_name, env_vars):
    """Lambda 함수 환경 변수 업데이트"""
    try:
        lambda_client.update_function_configuration(
            FunctionName=function_name,
            Environment={'Variables': env_vars}
        )
        print(f"✓ {function_name} 환경 변수 업데이트 완료")
        return True
    except Exception as e:
        print(f"✗ {function_name} 환경 변수 업데이트 실패: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("Lambda 환경 변수 업데이트 시작...")
    print("=" * 60)
    
    updates = [
        {
            'name': 'DashboardMetrics',
            'env': {
                'EMPLOYEES_TABLE': 'Employees',
                'PROJECTS_TABLE': 'Projects',
                'EVALUATIONS_TABLE': 'EmployeeEvaluations'
            }
        },
        {
            'name': 'EmployeeCreate',
            'env': {
                'EMPLOYEES_TABLE': 'Employees'
            }
        },
        {
            'name': 'ProjectCreate',
            'env': {
                'PROJECTS_TABLE': 'Projects'
            }
        },
        {
            'name': 'ProjectAssignment',
            'env': {
                'EMPLOYEES_TABLE': 'Employees',
                'PROJECTS_TABLE': 'Projects'
            }
        },
        {
            'name': 'ResumeUploadURLGenerator',
            'env': {
                'RESUMES_BUCKET': 'hr-resource-optimization-resumes-prod'
            }
        }
    ]
    
    success_count = 0
    for update in updates:
        print(f"\n처리 중: {update['name']}")
        if update_env_vars(update['name'], update['env']):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"완료! {success_count}/{len(updates)}개 함수 업데이트됨")
    print("=" * 60)

if __name__ == '__main__':
    main()
