"""
ProjectsList Lambda 함수 재배포
"""
import boto3
import zipfile
import os
import io

lambda_client = boto3.client('lambda', region_name='us-east-2')

print("=" * 80)
print("ProjectsList Lambda 함수 재배포")
print("=" * 80)

# 1. Lambda 함수 코드 압축
print("\n[1/3] Lambda 함수 코드 압축 중...")

zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
    # index.py 추가
    lambda_path = '../lambda_functions/projects_list/index.py'
    if not os.path.exists(lambda_path):
        lambda_path = 'lambda_functions/projects_list/index.py'
    
    zip_file.write(lambda_path, 'index.py')
    print("  ✓ index.py 추가")

zip_buffer.seek(0)
zip_content = zip_buffer.read()

print(f"  압축 파일 크기: {len(zip_content):,} bytes")

# 2. Lambda 함수 업데이트
print("\n[2/3] Lambda 함수 코드 업데이트 중...")

try:
    response = lambda_client.update_function_code(
        FunctionName='ProjectsList',
        ZipFile=zip_content
    )
    
    print(f"  ✓ 함수 업데이트 완료")
    print(f"  함수 ARN: {response['FunctionArn']}")
    print(f"  마지막 수정: {response['LastModified']}")
    print(f"  코드 크기: {response['CodeSize']:,} bytes")
    
except Exception as e:
    print(f"  ✗ 업데이트 실패: {str(e)}")
    exit(1)

# 3. Lambda 함수 테스트
print("\n[3/3] Lambda 함수 테스트 중...")

import json
import time

# 함수가 업데이트될 때까지 잠시 대기
time.sleep(2)

test_event = {
    'httpMethod': 'GET',
    'path': '/projects'
}

try:
    response = lambda_client.invoke(
        FunctionName='ProjectsList',
        InvocationType='RequestResponse',
        Payload=json.dumps(test_event)
    )
    
    payload = json.loads(response['Payload'].read())
    
    if payload.get('statusCode') == 200:
        body = json.loads(payload['body'])
        projects = body.get('projects', [])
        
        print(f"  ✓ 테스트 성공!")
        print(f"  프로젝트 수: {len(projects)}개")
        
        if projects:
            first_project = projects[0]
            print(f"\n  첫 번째 프로젝트 필드 체크:")
            
            required_fields = ['project_id', 'project_name', 'start_date', 'end_date', 'team_members', 'team_size']
            for field in required_fields:
                exists = field in first_project
                value = first_project.get(field, 'N/A')
                status = "✓" if exists else "✗"
                
                if isinstance(value, list):
                    preview = f"[{len(value)}개]"
                    if value and field == 'team_members':
                        # 첫 번째 팀원 구조 확인
                        first_member = value[0]
                        if 'user_id' in first_member:
                            preview += " ✓ user_id 포함"
                        else:
                            preview += " ✗ user_id 없음"
                elif isinstance(value, str) and len(value) > 30:
                    preview = value[:30] + "..."
                else:
                    preview = value
                
                print(f"    {status} {field:20s}: {preview}")
    else:
        print(f"  ✗ 테스트 실패")
        print(f"  응답: {json.dumps(payload, indent=2, ensure_ascii=False)[:500]}")
        
except Exception as e:
    print(f"  ✗ 테스트 실패: {str(e)}")

print("\n" + "=" * 80)
print("재배포 완료!")
print("=" * 80)
print("\n다음 단계:")
print("1. API Gateway 테스트: python deployment/test_frontend_api_connection.py")
print("2. 프론트엔드 재배포 (필요시)")
