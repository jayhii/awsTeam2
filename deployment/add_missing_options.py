#!/usr/bin/env python3
"""
누락된 OPTIONS 메서드 통합 추가
"""

import boto3

REGION = "us-east-2"
API_ID = "xoc7x1m6p8"

api_gateway = boto3.client('apigateway', region_name=REGION)

def add_options_integration(resource_id, path):
    """OPTIONS 메서드 통합 추가"""
    try:
        # Mock 통합 생성
        api_gateway.put_integration(
            restApiId=API_ID,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            type='MOCK',
            requestTemplates={
                'application/json': '{"statusCode": 200}'
            }
        )
        
        # 통합 응답 생성
        api_gateway.put_integration_response(
            restApiId=API_ID,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': "'Content-Type,Authorization'",
                'method.response.header.Access-Control-Allow-Methods': "'GET,POST,PUT,DELETE,OPTIONS'",
                'method.response.header.Access-Control-Allow-Origin': "'*'"
            }
        )
        
        print(f"  ✓ OPTIONS {path} - 통합 추가 완료")
        return True
    except Exception as e:
        print(f"  ✗ OPTIONS {path} - 실패: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("누락된 OPTIONS 메서드 통합 추가...")
    print("=" * 60)
    
    missing_options = [
        {'resource_id': '0pafg8', 'path': '/resume'},
        {'resource_id': '5ci83v', 'path': '/evaluations/{evaluationId}'},
        {'resource_id': '7pmnj6', 'path': '/projects/{projectId}'},
        {'resource_id': 'xny1oa', 'path': '/dashboard'}
    ]
    
    success_count = 0
    for item in missing_options:
        print(f"\n처리 중: {item['path']}")
        if add_options_integration(item['resource_id'], item['path']):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"완료! {success_count}/{len(missing_options)}개 통합 추가됨")
    print("=" * 60)
    
    # API 배포
    print("\nAPI 배포 중...")
    try:
        api_gateway.create_deployment(
            restApiId=API_ID,
            stageName='prod',
            description='OPTIONS 통합 추가 후 배포'
        )
        print("✓ API 배포 성공!")
        print(f"\nAPI URL: https://{API_ID}.execute-api.{REGION}.amazonaws.com/prod")
        print("\n브라우저를 새로고침하세요!")
    except Exception as e:
        print(f"✗ API 배포 실패: {str(e)}")

if __name__ == '__main__':
    main()
