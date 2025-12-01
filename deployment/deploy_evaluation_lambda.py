#!/usr/bin/env python3
"""
직원 평가 Lambda 함수 배포 스크립트
"""

import boto3
import zipfile
import io
import os

REGION = "us-east-2"
ROLE_ARN = "arn:aws:iam::412677576136:role/LambdaExecutionRole-Team2"
LAYER_ARN = "arn:aws:lambda:us-east-2:412677576136:layer:boto3-layer-team2:1"

lambda_client = boto3.client('lambda', region_name=REGION)
api_gateway = boto3.client('apigateway', region_name=REGION)

def create_zip():
    """Lambda 함수 ZIP 생성"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write('../lambda_functions/employee_evaluation/index.py', 'index.py')
    return zip_buffer.getvalue()

def create_lambda():
    """Lambda 함수 생성"""
    try:
        # 기존 함수 확인
        try:
            lambda_client.get_function(FunctionName='EmployeeEvaluation')
            print("✓ Lambda 함수가 이미 존재합니다. 코드 업데이트 중...")
            
            # 코드 업데이트
            zip_content = create_zip()
            lambda_client.update_function_code(
                FunctionName='EmployeeEvaluation',
                ZipFile=zip_content
            )
            print("✓ Lambda 함수 코드 업데이트 완료")
            return True
            
        except lambda_client.exceptions.ResourceNotFoundException:
            print("Lambda 함수 생성 중...")
            zip_content = create_zip()
            
            lambda_client.create_function(
                FunctionName='EmployeeEvaluation',
                Runtime='python3.11',
                Role=ROLE_ARN,
                Handler='index.lambda_handler',
                Code={'ZipFile': zip_content},
                Timeout=60,
                MemorySize=512,
                Layers=[LAYER_ARN],
                Tags={
                    'Team': 'Team2',
                    'EmployeeID': '524956',
                    'Project': 'HR-Resource-Optimization',
                    'Environment': 'prod'
                }
            )
            print("✓ Lambda 함수 생성 완료")
            return True
            
    except Exception as e:
        print(f"✗ Lambda 함수 생성/업데이트 실패: {str(e)}")
        return False

def create_api_integration():
    """API Gateway 통합 생성"""
    try:
        API_ID = "xoc7x1m6p8"
        ACCOUNT_ID = "412677576136"
        
        # /employee-evaluation 리소스 생성
        print("\nAPI Gateway 리소스 생성 중...")
        
        # 루트 리소스 ID 가져오기
        resources = api_gateway.get_resources(restApiId=API_ID)
        root_id = [r for r in resources['items'] if r['path'] == '/'][0]['id']
        
        # 리소스 생성
        try:
            resource = api_gateway.create_resource(
                restApiId=API_ID,
                parentId=root_id,
                pathPart='employee-evaluation'
            )
            resource_id = resource['id']
            print(f"✓ 리소스 생성 완료: {resource_id}")
        except api_gateway.exceptions.ConflictException:
            # 이미 존재하는 경우
            resource_id = [r for r in resources['items'] if r['path'] == '/employee-evaluation'][0]['id']
            print(f"✓ 리소스 이미 존재: {resource_id}")
        
        # POST 메서드 생성
        try:
            api_gateway.put_method(
                restApiId=API_ID,
                resourceId=resource_id,
                httpMethod='POST',
                authorizationType='NONE'
            )
            print("✓ POST 메서드 생성 완료")
        except api_gateway.exceptions.ConflictException:
            print("✓ POST 메서드 이미 존재")
        
        # Lambda 통합 생성
        lambda_arn = f"arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:EmployeeEvaluation"
        uri = f"arn:aws:apigateway:{REGION}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
        
        api_gateway.put_integration(
            restApiId=API_ID,
            resourceId=resource_id,
            httpMethod='POST',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=uri
        )
        print("✓ Lambda 통합 생성 완료")
        
        # OPTIONS 메서드 (CORS)
        try:
            api_gateway.put_method(
                restApiId=API_ID,
                resourceId=resource_id,
                httpMethod='OPTIONS',
                authorizationType='NONE'
            )
            
            api_gateway.put_integration(
                restApiId=API_ID,
                resourceId=resource_id,
                httpMethod='OPTIONS',
                type='MOCK',
                requestTemplates={'application/json': '{"statusCode": 200}'}
            )
            
            api_gateway.put_method_response(
                restApiId=API_ID,
                resourceId=resource_id,
                httpMethod='OPTIONS',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Headers': True,
                    'method.response.header.Access-Control-Allow-Methods': True,
                    'method.response.header.Access-Control-Allow-Origin': True
                }
            )
            
            api_gateway.put_integration_response(
                restApiId=API_ID,
                resourceId=resource_id,
                httpMethod='OPTIONS',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Headers': "'Content-Type,Authorization'",
                    'method.response.header.Access-Control-Allow-Methods': "'POST,OPTIONS'",
                    'method.response.header.Access-Control-Allow-Origin': "'*'"
                }
            )
            print("✓ CORS 설정 완료")
        except:
            print("✓ CORS 이미 설정됨")
        
        # Lambda 권한 추가
        try:
            lambda_client.add_permission(
                FunctionName='EmployeeEvaluation',
                StatementId='AllowAPIGatewayInvokeEvaluation',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f"arn:aws:execute-api:{REGION}:{ACCOUNT_ID}:{API_ID}/*/*"
            )
            print("✓ Lambda 권한 추가 완료")
        except lambda_client.exceptions.ResourceConflictException:
            print("✓ Lambda 권한 이미 존재")
        
        # API 배포
        api_gateway.create_deployment(
            restApiId=API_ID,
            stageName='prod',
            description='직원 평가 기능 추가'
        )
        print("✓ API 배포 완료")
        
        return True
        
    except Exception as e:
        print(f"✗ API Gateway 통합 실패: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("직원 평가 Lambda 함수 배포")
    print("=" * 60)
    
    if create_lambda():
        print("\n" + "=" * 60)
        if create_api_integration():
            print("\n✓ 배포 완료!")
            print("API URL: https://xoc7x1m6p8.execute-api.us-east-2.amazonaws.com/prod/employee-evaluation")
        else:
            print("\n✗ API Gateway 통합 실패")
    else:
        print("\n✗ Lambda 함수 배포 실패")

if __name__ == '__main__':
    main()
