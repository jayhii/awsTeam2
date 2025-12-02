#!/usr/bin/env python3
"""
도메인 분석 Lambda 함수 업데이트
"""

import boto3
import zipfile
import os
from pathlib import Path

REGION = "us-east-2"
FUNCTION_NAME = "DomainAnalysisEngine"

lambda_client = boto3.client('lambda', region_name=REGION)

def create_deployment_package():
    """배포 패키지 생성"""
    print("배포 패키지 생성 중...")
    
    lambda_dir = Path('lambda_functions/domain_analysis')
    zip_path = Path('lambda_functions/domain_analysis_deployment.zip')
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # index.py 추가
        index_file = lambda_dir / 'index.py'
        if index_file.exists():
            zipf.write(index_file, 'index.py')
            print(f"  ✓ {index_file}")
        
        # __init__.py 추가
        init_file = lambda_dir / '__init__.py'
        if init_file.exists():
            zipf.write(init_file, '__init__.py')
            print(f"  ✓ {init_file}")
    
    print(f"✓ 배포 패키지 생성 완료: {zip_path}")
    return zip_path

def update_lambda_function(zip_path):
    """Lambda 함수 업데이트"""
    print(f"\nLambda 함수 업데이트 중: {FUNCTION_NAME}")
    
    try:
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        response = lambda_client.update_function_code(
            FunctionName=FUNCTION_NAME,
            ZipFile=zip_content
        )
        
        print(f"✓ Lambda 함수 업데이트 완료!")
        print(f"  Function ARN: {response['FunctionArn']}")
        print(f"  Last Modified: {response['LastModified']}")
        print(f"  Code Size: {response['CodeSize']} bytes")
        
        return True
        
    except Exception as e:
        print(f"✗ Lambda 함수 업데이트 실패: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("도메인 분석 Lambda 함수 업데이트")
    print("=" * 60)
    
    # 1. 배포 패키지 생성
    zip_path = create_deployment_package()
    
    # 2. Lambda 함수 업데이트
    if update_lambda_function(zip_path):
        print("\n" + "=" * 60)
        print("✓ 업데이트 완료!")
        print("=" * 60)
        print("\n다음 명령어로 테스트하세요:")
        print("  python deployment/test_domain_analysis_api.py")
    else:
        print("\n✗ 업데이트 실패")
    
    # 3. 임시 파일 삭제
    if zip_path.exists():
        os.remove(zip_path)
        print(f"\n임시 파일 삭제: {zip_path}")

if __name__ == '__main__':
    main()
