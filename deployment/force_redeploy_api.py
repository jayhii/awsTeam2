#!/usr/bin/env python3
"""
API를 강제로 재배포
"""

import boto3
import time

REGION = "us-east-2"
API_ID = "xoc7x1m6p8"

api_gateway = boto3.client('apigateway', region_name=REGION)

def main():
    print("=" * 60)
    print("API 강제 재배포")
    print("=" * 60)
    
    try:
        # 새 배포 생성
        print("\n새 배포 생성 중...")
        deployment = api_gateway.create_deployment(
            restApiId=API_ID,
            stageName='prod',
            description='Force redeploy to fix 403 errors',
            stageDescription='Updated deployment'
        )
        
        print(f"✓ 배포 생성 완료!")
        print(f"  Deployment ID: {deployment['id']}")
        print(f"  Created: {deployment.get('createdDate')}")
        
        # 잠시 대기
        print("\n배포 전파 대기 중 (10초)...")
        time.sleep(10)
        
        # Stage 확인
        stage = api_gateway.get_stage(
            restApiId=API_ID,
            stageName='prod'
        )
        
        print(f"\n✓ Stage 업데이트 확인:")
        print(f"  Current Deployment ID: {stage.get('deploymentId')}")
        print(f"  Last Updated: {stage.get('lastUpdatedDate')}")
        
        print("\n" + "=" * 60)
        print("API 엔드포인트:")
        print(f"https://{API_ID}.execute-api.{REGION}.amazonaws.com/prod")
        print("=" * 60)
        
        print("\n✓ 재배포 완료!")
        print("\n다음 명령어로 테스트하세요:")
        print("  python deployment/test_all_endpoints.py")
        
    except Exception as e:
        print(f"\n✗ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
