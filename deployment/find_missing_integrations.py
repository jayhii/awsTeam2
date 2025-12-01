#!/usr/bin/env python3
"""
통합이 없는 메서드를 찾는 스크립트
"""

import boto3

REGION = "us-east-2"
API_ID = "xoc7x1m6p8"

api_gateway = boto3.client('apigateway', region_name=REGION)

def main():
    print("=" * 60)
    print("통합이 없는 메서드 찾기...")
    print("=" * 60)
    
    # 모든 리소스 가져오기
    response = api_gateway.get_resources(restApiId=API_ID, limit=500)
    resources = response['items']
    
    missing_integrations = []
    
    for resource in resources:
        path = resource['path']
        resource_id = resource['id']
        
        # 리소스에 정의된 메서드 확인
        if 'resourceMethods' in resource:
            for method in resource['resourceMethods'].keys():
                try:
                    # 통합 확인
                    api_gateway.get_integration(
                        restApiId=API_ID,
                        resourceId=resource_id,
                        httpMethod=method
                    )
                except api_gateway.exceptions.NotFoundException:
                    missing_integrations.append({
                        'path': path,
                        'resource_id': resource_id,
                        'method': method
                    })
                    print(f"✗ {method} {path} (ID: {resource_id}) - 통합 없음!")
    
    print("\n" + "=" * 60)
    if missing_integrations:
        print(f"총 {len(missing_integrations)}개의 메서드에 통합이 없습니다:")
        for item in missing_integrations:
            print(f"  - {item['method']} {item['path']}")
    else:
        print("모든 메서드에 통합이 있습니다!")
    print("=" * 60)

if __name__ == '__main__':
    main()
