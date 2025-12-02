#!/usr/bin/env python3
"""
모든 API Gateway 통합을 확인하고 수정하는 스크립트
"""

import boto3
import json

REGION = "us-east-2"
API_ID = "ifeniowvpb"
ACCOUNT_ID = "412677576136"

api_gateway = boto3.client('apigateway', region_name=REGION)

def check_and_fix_integration(resource_id, path, http_method, lambda_function_name):
    """통합 확인 및 수정"""
    try:
        # 통합 확인
        try:
            integration = api_gateway.get_integration(
                restApiId=API_ID,
                resourceId=resource_id,
                httpMethod=http_method
            )
            print(f"  ✓ {http_method} {path} - 통합 존재")
            return True
        except api_gateway.exceptions.NotFoundException:
            print(f"  ✗ {http_method} {path} - 통합 없음, 생성 중...")
            
            # 통합 생성
            lambda_arn = f"arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:{lambda_function_name}"
            uri = f"arn:aws:apigateway:{REGION}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
            
            api_gateway.put_integration(
                restApiId=API_ID,
                resourceId=resource_id,
                httpMethod=http_method,
                type='AWS_PROXY',
                integrationHttpMethod='POST',
                uri=uri
            )
            
            # Lambda 권한 추가
            lambda_client = boto3.client('lambda', region_name=REGION)
            try:
                lambda_client.add_permission(
                    FunctionName=lambda_function_name,
                    StatementId=f'AllowAPIGateway{resource_id}{http_method}',
                    Action='lambda:InvokeFunction',
                    Principal='apigateway.amazonaws.com',
                    SourceArn=f"arn:aws:execute-api:{REGION}:{ACCOUNT_ID}:{API_ID}/*/*"
                )
            except lambda_client.exceptions.ResourceConflictException:
                pass
            
            print(f"  ✓ {http_method} {path} - 통합 생성 완료")
            return True
            
    except Exception as e:
        print(f"  ✗ {http_method} {path} - 오류: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("API Gateway 통합 확인 및 수정...")
    print("=" * 60)
    
    # 모든 리소스 가져오기
    response = api_gateway.get_resources(restApiId=API_ID, limit=500)
    resources = response['items']
    
    # Lambda 함수 매핑
    lambda_mapping = {
        '/dashboard/metrics': {'GET': 'DashboardMetrics'},
        '/employees': {'GET': 'EmployeesList', 'POST': 'EmployeeCreate'},
        '/projects': {'GET': 'ProjectsList', 'POST': 'ProjectCreate'},
        '/projects/{projectId}/assign': {'POST': 'ProjectAssignment'},
        '/resume/upload-url': {'POST': 'ResumeUploadURLGenerator'},
        '/evaluations': {'GET': 'EvaluationsList'},
        '/evaluations/{evaluationId}/approve': {'PUT': 'EvaluationStatusUpdate'},
        '/evaluations/{evaluationId}/review': {'PUT': 'EvaluationStatusUpdate'},
        '/evaluations/{evaluationId}/reject': {'PUT': 'EvaluationStatusUpdate'},
        '/recommendations': {'POST': 'ProjectRecommendationEngine'},
        '/domain-analysis': {'POST': 'DomainAnalysisEngine'},
        '/quantitative-analysis': {'POST': 'QuantitativeAnalysis'},
        '/qualitative-analysis': {'POST': 'QualitativeAnalysis'}
    }
    
    success_count = 0
    total_count = 0
    
    for resource in resources:
        path = resource['path']
        resource_id = resource['id']
        
        if path in lambda_mapping:
            print(f"\n처리 중: {path}")
            for method, lambda_func in lambda_mapping[path].items():
                total_count += 1
                if check_and_fix_integration(resource_id, path, method, lambda_func):
                    success_count += 1
    
    print("\n" + "=" * 60)
    print(f"완료! {success_count}/{total_count}개 통합 확인/수정됨")
    print("=" * 60)
    
    # API 배포 시도
    print("\nAPI 배포 시도 중...")
    try:
        api_gateway.create_deployment(
            restApiId=API_ID,
            stageName='prod',
            description='통합 수정 후 재배포'
        )
        print("✓ API 배포 성공!")
    except Exception as e:
        print(f"✗ API 배포 실패: {str(e)}")
        print("일부 메서드에 여전히 통합이 없을 수 있습니다.")

if __name__ == '__main__':
    main()
