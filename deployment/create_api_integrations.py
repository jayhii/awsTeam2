#!/usr/bin/env python3
"""
API Gateway 통합을 직접 생성하는 스크립트
Terraform 없이 AWS CLI로 직접 통합 생성
"""

import boto3
import json

REGION = "us-east-2"
API_ID = "xoc7x1m6p8"
ACCOUNT_ID = "412677576136"

api_gateway = boto3.client('apigateway', region_name=REGION)

def create_integration(resource_id, http_method, lambda_function_name):
    """API Gateway 통합 생성"""
    try:
        lambda_arn = f"arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:{lambda_function_name}"
        uri = f"arn:aws:apigateway:{REGION}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
        
        # 통합 생성
        api_gateway.put_integration(
            restApiId=API_ID,
            resourceId=resource_id,
            httpMethod=http_method,
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=uri
        )
        print(f"  ✓ 통합 생성 완료")
        return True
    except Exception as e:
        print(f"  ✗ 통합 생성 실패: {str(e)}")
        return False

def add_lambda_permission(lambda_function_name, statement_id):
    """Lambda 함수에 API Gateway 호출 권한 추가"""
    try:
        lambda_client = boto3.client('lambda', region_name=REGION)
        source_arn = f"arn:aws:execute-api:{REGION}:{ACCOUNT_ID}:{API_ID}/*/*"
        
        lambda_client.add_permission(
            FunctionName=lambda_function_name,
            StatementId=statement_id,
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=source_arn
        )
        print(f"  ✓ Lambda 권한 추가 완료")
        return True
    except lambda_client.exceptions.ResourceConflictException:
        print(f"  ✓ Lambda 권한 이미 존재")
        return True
    except Exception as e:
        print(f"  ✗ Lambda 권한 추가 실패: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("API Gateway 통합 생성 시작...")
    print("=" * 60)
    
    integrations = [
        {
            'resource_id': '8nheik',
            'path': '/dashboard/metrics',
            'http_method': 'GET',
            'lambda_function': 'DashboardMetrics',
            'statement_id': 'AllowAPIGatewayInvokeDashboard'
        },
        {
            'resource_id': 'rlybgd',
            'path': '/employees',
            'http_method': 'POST',
            'lambda_function': 'EmployeeCreate',
            'statement_id': 'AllowAPIGatewayInvokeEmployeePost'
        },
        {
            'resource_id': 'kikxhv',
            'path': '/projects',
            'http_method': 'POST',
            'lambda_function': 'ProjectCreate',
            'statement_id': 'AllowAPIGatewayInvokeProjectPost'
        },
        {
            'resource_id': '5kskx7',
            'path': '/projects/{projectId}/assign',
            'http_method': 'POST',
            'lambda_function': 'ProjectAssignment',
            'statement_id': 'AllowAPIGatewayInvokeProjectAssign'
        },
        {
            'resource_id': 'vq9ljm',
            'path': '/resume/upload-url',
            'http_method': 'POST',
            'lambda_function': 'ResumeUploadURLGenerator',
            'statement_id': 'AllowAPIGatewayInvokeResumeUpload'
        }
    ]
    
    success_count = 0
    for integration in integrations:
        print(f"\n처리 중: {integration['http_method']} {integration['path']}")
        print(f"  Lambda: {integration['lambda_function']}")
        
        # 통합 생성
        if create_integration(
            integration['resource_id'],
            integration['http_method'],
            integration['lambda_function']
        ):
            # Lambda 권한 추가
            if add_lambda_permission(
                integration['lambda_function'],
                integration['statement_id']
            ):
                success_count += 1
    
    # API 배포
    print("\n" + "=" * 60)
    print("API 배포 중...")
    try:
        api_gateway.create_deployment(
            restApiId=API_ID,
            stageName='prod',
            description='통합 생성 후 배포'
        )
        print("✓ API 배포 완료!")
    except Exception as e:
        print(f"✗ API 배포 실패: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"완료! {success_count}/{len(integrations)}개 통합 생성됨")
    print("=" * 60)
    print(f"\nAPI URL: https://{API_ID}.execute-api.{REGION}.amazonaws.com/prod")

if __name__ == '__main__':
    main()
