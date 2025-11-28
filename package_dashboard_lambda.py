#!/usr/bin/env python3
"""
Dashboard Metrics Lambda 패키징 스크립트
"""
import zipfile
import os

def package_lambda():
    """Lambda 함수를 ZIP 파일로 패키징"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(base_dir, 'lambda_functions', 'dashboard_metrics')
    output_zip = os.path.join(base_dir, 'lambda_functions', 'dashboard_metrics.zip')
    
    # 기존 ZIP 파일 삭제
    if os.path.exists(output_zip):
        os.remove(output_zip)
        print(f"기존 ZIP 파일 삭제: {output_zip}")
    
    # ZIP 파일 생성
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)
                print(f"추가됨: {arcname}")
    
    print(f"\n✓ 패키징 완료: {output_zip}")
    print(f"파일 크기: {os.path.getsize(output_zip)} bytes")

if __name__ == '__main__':
    package_lambda()
