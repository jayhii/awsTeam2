import boto3
import zipfile
import os
from pathlib import Path

# AWS 클라이언트
lambda_client = boto3.client('lambda', region_name='us-east-2')

print("=" * 70)
print("Projects List Lambda 함수 업데이트")
print("=" * 70)

# 1. Lambda 함수 코드 패키징
print("\n[1단계] Lambda 함수 코드 패키징 중...")
lambda_dir = Path('lambda_functions/projects_list')
zip_path = Path('lambda_functions/projects_list.zip')

try:
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # index.py 추가
        index_file = lambda_dir / 'index.py'
        if index_file.exists():
            zipf.write(index_file, 'index.py')
            print(f"  ✓ {index_file} 추가됨")
        else:
            print(f"  ✗ {index_file} 파일을 찾을 수 없습니다")
            exit(1)
    
    print(f"  ✓ ZIP 파일 생성 완료: {zip_path}")
    print(f"  크기: {zip_path.stat().st_size / 1024:.2f} KB")
    
except Exception as e:
    print(f"  ✗ 패키징 실패: {str(e)}")
    exit(1)

# 2. Lambda 함수 업데이트
print("\n[2단계] Lambda 함수 코드 업데이트 중...")
function_name = 'ProjectsList'

try:
    with open(zip_path, 'rb') as f:
        zip_content = f.read()
    
    response = lambda_client.update_function_code(
        FunctionName=function_name,
        ZipFile=zip_content
    )
    
    print(f"  ✓ Lambda 함수 '{function_name}' 업데이트 완료")
    print(f"  함수 ARN: {response['FunctionArn']}")
    print(f"  런타임: {response['Runtime']}")
    print(f"  최종 수정: {response['LastModified']}")
    
except lambda_client.exceptions.ResourceNotFoundException:
    print(f"  ✗ Lambda 함수 '{function_name}'를 찾을 수 없습니다")
    print("  힌트: 함수 이름을 확인하거나 Terraform으로 먼저 생성하세요")
    exit(1)
    
except Exception as e:
    print(f"  ✗ 업데이트 실패: {str(e)}")
    exit(1)

# 3. 정리
print("\n[3단계] 임시 파일 정리 중...")
try:
    zip_path.unlink()
    print(f"  ✓ {zip_path} 삭제됨")
except Exception as e:
    print(f"  ⚠️  정리 실패: {str(e)}")

print("\n" + "=" * 70)
print("완료!")
print("=" * 70)
print("\n다음 단계:")
print("  1. 프론트엔드에서 프로젝트 목록 새로고침")
print("  2. 브라우저 콘솔에서 API 응답 확인")
print("  3. 팀원 정보가 포함되어 있는지 확인")
