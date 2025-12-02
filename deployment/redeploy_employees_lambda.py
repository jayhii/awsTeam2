"""
EmployeesList Lambda 함수 재배포
"""
import boto3
import zipfile
import os
import io
import json
import time

lambda_client = boto3.client('lambda', region_name='us-east-2')

print("=" * 80)
print("EmployeesList Lambda 함수 재배포")
print("=" * 80)

# 1. Lambda 함수 코드 압축
print("\n[1/3] Lambda 함수 코드 압축 중...")

zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
    lambda_path = '../lambda_functions/employees_list/index.py'
    zip_file.write(lambda_path, 'index.py')
    print("  ✓ index.py 추가")

zip_buffer.seek(0)
zip_content = zip_buffer.read()

print(f"  압축 파일 크기: {len(zip_content):,} bytes")

# 2. Lambda 함수 업데이트
print("\n[2/3] Lambda 함수 코드 업데이트 중...")

try:
    response = lambda_client.update_function_code(
        FunctionName='EmployeesList',
        ZipFile=zip_content
    )
    
    print(f"  ✓ 함수 업데이트 완료")
    print(f"  함수 ARN: {response['FunctionArn']}")
    print(f"  마지막 수정: {response['LastModified']}")
    
except Exception as e:
    print(f"  ✗ 업데이트 실패: {str(e)}")
    exit(1)

# 3. Lambda 함수 테스트
print("\n[3/3] Lambda 함수 테스트 중...")

time.sleep(2)

test_event = {
    'httpMethod': 'GET',
    'path': '/employees'
}

try:
    response = lambda_client.invoke(
        FunctionName='EmployeesList',
        InvocationType='RequestResponse',
        Payload=json.dumps(test_event)
    )
    
    payload = json.loads(response['Payload'].read())
    
    if payload.get('statusCode') == 200:
        body = json.loads(payload['body'])
        employees = body.get('employees', [])
        
        print(f"  ✓ 테스트 성공!")
        print(f"  직원 수: {len(employees)}명")
    else:
        print(f"  ✗ 테스트 실패")
        print(f"  응답: {json.dumps(payload, indent=2)[:500]}")
        
except Exception as e:
    print(f"  ✗ 테스트 실패: {str(e)}")

print("\n" + "=" * 80)
print("재배포 완료!")
print("=" * 80)
