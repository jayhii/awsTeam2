#!/usr/bin/env python3
"""
도메인 분석 엔드포인트 상태 확인
"""

import boto3
import json

REGION = "us-east-2"
API_ID = "xoc7x1m6p8"

api_gateway = boto3.client('apigateway', region_name=REGION)

def main():
    print("=" * 60)
    print("도메인 분석 엔드포인트 확인")
    print("=" * 60)
    
    try:
        # 모든 리소스 가져오기
        response = api_gateway.get_resources(restApiId=API_ID, limit=500)
        resources = response['items']
        
        # /domain-analysis 리소스 찾기
        domain_resource = None
        for resource in resources:
            if resource['path'] == '/domain-analysis':
                domain_resource = resource
                break
        
        if not domain_resource:
            print("✗ /domain-analysis 리소스를 찾을 수 없습니다!")
            print("\n사용 가능한 리소스:")
            for resource in resources:
                print(f"  - {resource['path']}")
            return
        
        print(f"✓ /domain-analysis 리소스 발견")
        print(f"  Resource ID: {domain_resource['id']}")
        
        # POST 메서드 확인
        resource_methods = domain_resource.get('resourceMethods', {})
        print(f"\n사용 가능한 메서드: {list(resource_methods.keys())}")
        
        if 'POST' not in resource_methods:
            print("✗ POST 메서드가 없습니다!")
            return
        
        # POST 메서드 상세 정보
        method = api_gateway.get_method(
            restApiId=API_ID,
            resourceId=domain_resource['id'],
            httpMethod='POST'
        )
        
        print("\n✓ POST 메서드 존재")
        print(f"  Authorization: {method.get('authorizationType', 'NONE')}")
        
        # 통합 확인
        try:
            integration = api_gateway.get_integration(
                restApiId=API_ID,
                resourceId=domain_resource['id'],
                httpMethod='POST'
            )
            
            print("\n✓ Lambda 통합 존재")
            print(f"  Type: {integration.get('type')}")
            print(f"  URI: {integration.get('uri')}")
            print(f"  Integration Method: {integration.get('httpMethod')}")
            
            # Lambda 함수 이름 추출
            uri = integration.get('uri', '')
            if 'function:' in uri:
                lambda_name = uri.split('function:')[1].split('/')[0]
                print(f"  Lambda 함수: {lambda_name}")
            
        except api_gateway.exceptions.NotFoundException:
            print("\n✗ Lambda 통합이 없습니다!")
            print("  fix_all_integrations.py를 실행하여 통합을 생성하세요.")
        
        # CORS 설정 확인
        if 'OPTIONS' in resource_methods:
            print("\n✓ OPTIONS 메서드 존재 (CORS 설정됨)")
        else:
            print("\n⚠ OPTIONS 메서드 없음 (CORS 미설정)")
        
        # 배포 상태 확인
        print("\n배포 상태 확인:")
        deployments = api_gateway.get_deployments(restApiId=API_ID, limit=1)
        if deployments['items']:
            latest = deployments['items'][0]
            print(f"  최근 배포: {latest['id']}")
            print(f"  생성 시간: {latest.get('createdDate')}")
        
        # Stage 확인
        stages = api_gateway.get_stages(restApiId=API_ID)
        print("\n사용 가능한 Stage:")
        for stage in stages['item']:
            print(f"  - {stage['stageName']}: {stage.get('deploymentId')}")
        
        print("\n" + "=" * 60)
        print("API 엔드포인트:")
        print(f"https://{API_ID}.execute-api.{REGION}.amazonaws.com/prod/domain-analysis")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
