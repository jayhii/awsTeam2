#!/usr/bin/env python3
"""
누락된 Lambda 함수들을 생성하는 스크립트
KMS 권한 문제를 우회하기 위해 환경 변수 없이 생성
"""

import boto3
import zipfile
import os
import io

REGION = "us-east-2"
ROLE_ARN = "arn:aws:iam::412677576136:role/LambdaExecutionRole-Team2"
LAYER_ARN = "arn:aws:lambda:us-east-2:412677576136:layer:boto3-layer-team2:1"

lambda_client = boto3.client('lambda', region_name=REGION)

def create_zip_from_file(file_path):
    """파일을 ZIP으로 압축"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write(file_path, 'index.py')
    return zip_buffer.getvalue()

def create_lambda_function(function_name, handler, code_path, memory=512, timeout=30, layers=None):
    """Lambda 함수 생성"""
    try:
        # 기존 함수 확인
        try:
            lambda_client.get_function(FunctionName=function_name)
            print(f"✓ {function_name} 이미 존재합니다.")
            return True
        except lambda_client.exceptions.ResourceNotFoundException:
            pass
        
        # ZIP 파일 생성
        print(f"  {function_name} ZIP 생성 중...")
        zip_content = create_zip_from_file(code_path)
        
        # Lambda 함수 생성 (환경 변수 없이)
        print(f"  {function_name} 생성 중...")
        params = {
            'FunctionName': function_name,
            'Runtime': 'python3.11',
            'Role': ROLE_ARN,
            'Handler': handler,
            'Code': {'ZipFile': zip_content},
            'Timeout': timeout,
            'MemorySize': memory,
            'Tags': {
                'Team': 'Team2',
                'EmployeeID': '524956',
                'Project': 'HR-Resource-Optimization',
                'Environment': 'prod'
            }
        }
        
        if layers:
            params['Layers'] = layers
        
        lambda_client.create_function(**params)
        print(f"✓ {function_name} 생성 완료!")
        return True
        
    except Exception as e:
        print(f"✗ {function_name} 생성 실패: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("누락된 Lambda 함수 생성 시작...")
    print("=" * 60)
    
    functions = [
        {
            'name': 'DashboardMetrics',
            'handler': 'index.lambda_handler',
            'code': '../lambda_functions/dashboard_metrics/index.py',
            'memory': 512,
            'timeout': 30,
            'layers': [LAYER_ARN]
        },
        {
            'name': 'EmployeeCreate',
            'handler': 'index.lambda_handler',
            'code': '../lambda_functions/employee_create/index.py',
            'memory': 512,
            'timeout': 30,
            'layers': [LAYER_ARN]
        },
        {
            'name': 'ProjectCreate',
            'handler': 'index.lambda_handler',
            'code': '../lambda_functions/project_create/index.py',
            'memory': 512,
            'timeout': 30,
            'layers': [LAYER_ARN]
        },
        {
            'name': 'ProjectAssignment',
            'handler': 'index.handler',
            'code': '../lambda_functions/project_assign/index.py',
            'memory': 512,
            'timeout': 60,
            'layers': [LAYER_ARN]
        },
        {
            'name': 'ResumeUploadURLGenerator',
            'handler': 'index.lambda_handler',
            'code': '../lambda_functions/resume_upload/index.py',
            'memory': 256,
            'timeout': 30,
            'layers': None
        }
    ]
    
    success_count = 0
    for func in functions:
        print(f"\n처리 중: {func['name']}")
        if create_lambda_function(
            func['name'],
            func['handler'],
            func['code'],
            func['memory'],
            func['timeout'],
            func['layers']
        ):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"완료! {success_count}/{len(functions)}개 함수 생성됨")
    print("=" * 60)

if __name__ == '__main__':
    main()
