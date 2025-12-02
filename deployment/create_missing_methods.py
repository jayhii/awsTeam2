#!/usr/bin/env python3
"""
누락된 메서드 생성 및 통합 설정
"""

import boto3
import time

REGION = "us-east-2"
API_ID = "ifeniowvpb"
ACCOUNT_ID = "412677576136"

api_gateway = boto3.client('apigateway', region_name=REGION)
lambda_client = boto3.client('lambda', region_name=REGION)

# 엔드포인트 매핑
ENDPOINTS = {
    '/domain-analysis': {'POST': 'DomainAnalysisEngine'},
    '/recommendations': {'POST': 'ProjectRecommendationEngine'},
    '/quantitative-analysis': {'POST': 'QuantitativeAnalysis'},
    '/qualitative-analysis': {'POST': 'QualitativeAnalysis'},
}

def create_method_and_integration(resource_id, path, http_method, lambda_function_name):
    """메서드 생성 및 Lambda 통합 설정"""
    try:
        # 1. 메서드 생성
        print(f"  메서드 생성: {http_method} {path}")
        try:
            api_gateway.put_method(
                restApiId=API_ID,
                resourceId=resource_id,
                httpMethod=http_method,
                authorizationType='NONE',
                apiKeyRequired=False
            )
            print(f"    ✓ 메서드 생성 완료")
        except api_gateway.exceptions.ConflictException:
            print(f"    ✓ 메서드 이미 존재")
        
        # 2. Lambda 통합 설정
        print(f"  Lambda 통합 설정: {lambda_function_name}")
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
        print(f"    ✓ Lambda 통합 완료")
        
        # 3. Lambda 권한 추가
        print(f"  Lambda 권한 추가")
        try:
            lambda_client.add_permission(
                FunctionName=lambda_function_name,
                StatementId=f'AllowAPIGateway{resource_id}{http_method}',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f"arn:aws:execute-api:{REGION}:{ACCOUNT_ID}:{API_ID}/*/*"
            )
            print(f"    ✓ Lambda 권한 추가 완료")
        except lambda_client.exceptions.ResourceConflictException:
            print(f"    ✓ Lambda 권한 이미 존재")
        
        # 4. Method Response 설정
        try:
            api_gateway.put_method_response(
                restApiId=API_ID,
                resourceId=resource_id,
                httpMethod=http_method,
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Origin': False
                }
            )
        except:
            pass
        
        # 5. Integration Response 설정
        try:
            api_gateway.put_integration_response(
                restApiId=API_ID,
                resourceId=resource_id,
                httpMethod=http_method,
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Origin': "'*'"
                }
            )
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"    ✗ 오류: {str(e)}")
        return False

def enable_cors(resource_id, path):
    """CORS 활성화"""
    try:
        print(f"  CORS 설정: {path}")
        
        # OPTIONS 메서드 생성
        try:
            api_gateway.put_method(
                restApiId=API_ID,
                resourceId=resource_id,
                httpMethod='OPTIONS',
                authorizationType='NONE'
            )
        except:
            pass
        
        # Mock 통합
        api_gateway.put_integration(
            restApiId=API_ID,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            type='MOCK',
            requestTemplates={
                'application/json': '{"statusCode": 200}'
            }
        )
        
        # Method Response
        api_gateway.put_method_response(
            restApiId=API_ID,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': False,
                'method.response.header.Access-Control-Allow-Methods': False,
                'method.response.header.Access-Control-Allow-Origin': False
            }
        )
        
        # Integration Response
        api_gateway.put_integration_response(
            restApiId=API_ID,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                'method.response.header.Access-Control-Allow-Methods': "'GET,POST,PUT,DELETE,OPTIONS'",
                'method.response.header.Access-Control-Allow-Origin': "'*'"
            }
        )
        
        print(f"    ✓ CORS 설정 완료")
        return True
        
    except Exception as e:
        print(f"    ✗ CORS 설정 실패: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("누락된 메서드 생성 및 통합 설정")
    print("=" * 60)
    
    try:
        # 모든 리소스 가져오기
        response = api_gateway.get_resources(restApiId=API_ID, limit=500)
        resources = {r['path']: r['id'] for r in response['items']}
        
        success_count = 0
        total_count = 0
        
        for path, methods in ENDPOINTS.items():
            if path not in resources:
                print(f"\n✗ 리소스 없음: {path}")
                continue
            
            resource_id = resources[path]
            print(f"\n처리 중: {path} (ID: {resource_id})")
            
            for method, lambda_func in methods.items():
                total_count += 1
                if create_method_and_integration(resource_id, path, method, lambda_func):
                    success_count += 1
            
            # CORS 설정
            enable_cors(resource_id, path)
        
        print("\n" + "=" * 60)
        print(f"완료! {success_count}/{total_count}개 메서드 생성/통합됨")
        print("=" * 60)
        
        # API 배포
        print("\nAPI 배포 중...")
        deployment = api_gateway.create_deployment(
            restApiId=API_ID,
            stageName='prod',
            description='Create missing methods and integrations'
        )
        print(f"✓ API 배포 완료! (Deployment ID: {deployment['id']})")
        
        print("\n배포 전파 대기 중 (10초)...")
        time.sleep(10)
        
        print("\n✓ 모든 작업 완료!")
        print("\n다음 명령어로 테스트하세요:")
        print("  python deployment/test_all_endpoints.py")
        
    except Exception as e:
        print(f"\n✗ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
