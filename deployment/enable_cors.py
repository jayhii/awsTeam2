#!/usr/bin/env python3
"""
API Gateway CORS 활성화 스크립트
모든 리소스에 OPTIONS 메서드를 추가하여 CORS preflight 요청을 처리합니다.
"""

import boto3
import sys

API_ID = "xoc7x1m6p8"
REGION = "us-east-2"

def enable_cors_for_resource(api_gateway, api_id, resource_id, path):
    """특정 리소스에 CORS OPTIONS 메서드 추가"""
    try:
        # OPTIONS 메서드 생성
        print(f"  OPTIONS 메서드 생성 중...")
        api_gateway.put_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            authorizationType='NONE'
        )
        
        # Mock 통합 설정
        print(f"  Mock 통합 설정 중...")
        api_gateway.put_integration(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            type='MOCK',
            requestTemplates={
                'application/json': '{"statusCode": 200}'
            }
        )
        
        # 메서드 응답 설정
        print(f"  메서드 응답 설정 중...")
        api_gateway.put_method_response(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': True,
                'method.response.header.Access-Control-Allow-Methods': True,
                'method.response.header.Access-Control-Allow-Origin': True
            }
        )
        
        # 통합 응답 설정 (CORS 헤더 포함)
        print(f"  통합 응답 설정 중...")
        api_gateway.put_integration_response(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                'method.response.header.Access-Control-Allow-Methods': "'GET,POST,PUT,DELETE,OPTIONS'",
                'method.response.header.Access-Control-Allow-Origin': "'*'"
            }
        )
        
        print(f"  ✓ 완료")
        return True
        
    except api_gateway.exceptions.ConflictException:
        print(f"  OPTIONS 메서드가 이미 존재합니다. 건너뛰기...")
        return False
    except Exception as e:
        print(f"  ✗ 오류: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("API Gateway CORS 설정 시작...")
    print("=" * 60)
    print(f"API ID: {API_ID}")
    print(f"Region: {REGION}\n")
    
    # API Gateway 클라이언트 생성
    api_gateway = boto3.client('apigateway', region_name=REGION)
    
    # 모든 리소스 가져오기
    print("리소스 목록 조회 중...\n")
    response = api_gateway.get_resources(restApiId=API_ID, limit=500)
    resources = response['items']
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for resource in resources:
        resource_id = resource['id']
        path = resource['path']
        
        # 루트 경로는 건너뛰기
        if path == '/':
            continue
        
        print(f"\n처리 중: {path} (ID: {resource_id})")
        
        # OPTIONS 메서드가 이미 있는지 확인
        if 'resourceMethods' in resource and 'OPTIONS' in resource.get('resourceMethods', {}):
            print(f"  OPTIONS 메서드가 이미 존재합니다. 건너뛰기...")
            skip_count += 1
            continue
        
        result = enable_cors_for_resource(api_gateway, API_ID, resource_id, path)
        if result:
            success_count += 1
        else:
            error_count += 1
    
    # API 배포
    print("\n" + "=" * 60)
    print("API 배포 중...")
    try:
        api_gateway.create_deployment(
            restApiId=API_ID,
            stageName='prod',
            description='CORS 설정 업데이트'
        )
        print("✓ API 배포 완료!")
    except Exception as e:
        print(f"✗ API 배포 실패: {str(e)}")
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("CORS 설정 완료!")
    print("=" * 60)
    print(f"성공: {success_count}개")
    print(f"건너뛰기: {skip_count}개")
    print(f"오류: {error_count}개")
    print(f"\nAPI URL: https://{API_ID}.execute-api.{REGION}.amazonaws.com/prod")

if __name__ == '__main__':
    main()
