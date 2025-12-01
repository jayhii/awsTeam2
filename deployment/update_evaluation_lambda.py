"""
employee_evaluation Lambda 함수 업데이트 스크립트
"""

import os
import zipfile
import boto3
from pathlib import Path

def create_lambda_zip():
    """Lambda 함수 ZIP 파일 생성"""
    # 프로젝트 루트 경로
    project_root = Path(__file__).parent.parent
    lambda_dir = project_root / 'lambda_functions' / 'employee_evaluation'
    zip_path = lambda_dir / 'employee_evaluation.zip'
    
    print(f"Lambda 디렉토리: {lambda_dir}")
    print(f"ZIP 파일 경로: {zip_path}")
    
    # 기존 ZIP 파일 삭제
    if zip_path.exists():
        zip_path.unlink()
        print("기존 ZIP 파일 삭제 완료")
    
    # ZIP 파일 생성
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # index.py 파일 추가
        index_file = lambda_dir / 'index.py'
        if index_file.exists():
            zipf.write(index_file, 'index.py')
            print(f"추가됨: index.py")
        else:
            print(f"경고: index.py 파일을 찾을 수 없습니다: {index_file}")
            return None
    
    print(f"ZIP 파일 생성 완료: {zip_path}")
    return zip_path

def update_lambda_function(zip_path):
    """Lambda 함수 코드 업데이트"""
    lambda_client = boto3.client('lambda', region_name='us-east-2')
    
    function_name = 'EmployeeEvaluation'
    
    print(f"\nLambda 함수 업데이트 중: {function_name}")
    
    with open(zip_path, 'rb') as f:
        zip_content = f.read()
    
    try:
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        
        print(f"✓ Lambda 함수 업데이트 완료!")
        print(f"  - 함수명: {response['FunctionName']}")
        print(f"  - 버전: {response['Version']}")
        print(f"  - 마지막 수정: {response['LastModified']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Lambda 함수 업데이트 실패: {str(e)}")
        return False

def main():
    """메인 함수"""
    print("=" * 60)
    print("employee_evaluation Lambda 함수 업데이트")
    print("=" * 60)
    
    # ZIP 파일 생성
    zip_path = create_lambda_zip()
    if not zip_path:
        print("\n✗ ZIP 파일 생성 실패")
        return
    
    # Lambda 함수 업데이트
    success = update_lambda_function(zip_path)
    
    if success:
        print("\n" + "=" * 60)
        print("✓ 모든 작업 완료!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✗ 작업 실패")
        print("=" * 60)

if __name__ == '__main__':
    main()
