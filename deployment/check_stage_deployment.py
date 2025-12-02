#!/usr/bin/env python3
"""
Stage 배포 상태 확인
"""

import boto3
import json

REGION = "us-east-2"
API_ID = "xoc7x1m6p8"

api_gateway = boto3.client('apigateway', region_name=REGION)

def main():
    print("=" * 60)
    print("Stage 배포 상태 확인")
    print("=" * 60)
    
    try:
        # Stage 정보 가져오기
        stage = api_gateway.get_stage(
            restApiId=API_ID,
            stageName='prod'
        )
        
        print(f"\nStage: prod")
        print(f"Deployment ID: {stage.get('deploymentId')}")
        print(f"Created: {stage.get('createdDate')}")
        print(f"Last Updated: {stage.get('lastUpdatedDate')}")
        
        # 배포 정보 가져오기
        deployment = api_gateway.get_deployment(
            restApiId=API_ID,
            deploymentId=stage['deploymentId']
        )
        
        print(f"\nDeployment 정보:")
        print(f"  ID: {deployment.get('id')}")
        print(f"  Created: {deployment.get('createdDate')}")
        print(f"  Description: {deployment.get('description', 'N/A')}")
        
        # 리소스 확인
        print("\n리소스 확인:")
        resources = api_gateway.get_resources(restApiId=API_ID, limit=500)
        
        target_paths = ['/domain-analysis', '/recommendations', '/quantitative-analysis', '/qualitative-analysis']
        
        for resource in resources['items']:
            path = resource['path']
            if path in target_paths:
                print(f"\n  {path}:")
                methods = resource.get('resourceMethods', {})
                for method in methods:
                    if method != 'OPTIONS':
                        try:
                            integration = api_gateway.get_integration(
                                restApiId=API_ID,
                                resourceId=resource['id'],
                                httpMethod=method
                            )
                            uri = integration.get('uri', '')
                            lambda_name = uri.split('function:')[1].split('/')[0] if 'function:' in uri else 'N/A'
                            print(f"    {method}: {lambda_name}")
                        except:
                            print(f"    {method}: No integration")
        
        # 최근 배포 목록
        print("\n최근 배포 목록:")
        deployments = api_gateway.get_deployments(restApiId=API_ID, limit=5)
        for i, dep in enumerate(deployments['items']):
            marker = "← 현재" if dep['id'] == stage['deploymentId'] else ""
            print(f"  {i+1}. {dep['id']} - {dep.get('createdDate')} {marker}")
        
    except Exception as e:
        print(f"\n✗ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
