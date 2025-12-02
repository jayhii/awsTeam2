#!/usr/bin/env python3
"""
올바른 API ID 찾기
"""

import boto3

REGION = "us-east-2"
api_gateway = boto3.client('apigateway', region_name=REGION)

def main():
    print("=" * 60)
    print("API Gateway 목록 조회")
    print("=" * 60)
    
    try:
        # 모든 API 가져오기
        response = api_gateway.get_rest_apis(limit=100)
        
        print(f"\n발견된 API: {len(response['items'])}개\n")
        
        for api in response['items']:
            api_id = api['id']
            api_name = api['name']
            created = api.get('createdDate', 'N/A')
            
            print(f"API: {api_name}")
            print(f"  ID: {api_id}")
            print(f"  Created: {created}")
            
            # 엔드포인트 URL
            endpoint = f"https://{api_id}.execute-api.{REGION}.amazonaws.com/prod"
            print(f"  Endpoint: {endpoint}")
            
            # 리소스 확인
            try:
                resources = api_gateway.get_resources(restApiId=api_id, limit=10)
                paths = [r['path'] for r in resources['items']]
                print(f"  Resources: {', '.join(paths[:5])}")
                
                # domain-analysis가 있는지 확인
                if any('/domain-analysis' in p for p in paths):
                    print(f"  ✓ /domain-analysis 발견!")
                    
            except Exception as e:
                print(f"  Error: {str(e)}")
            
            print()
        
    except Exception as e:
        print(f"\n✗ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
