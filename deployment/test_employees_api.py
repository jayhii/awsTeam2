"""
직원 목록 API 테스트 스크립트
"""

import requests
import json

# API Gateway URL (실제 URL로 변경 필요)
API_BASE_URL = "https://your-api-gateway-url.execute-api.us-east-2.amazonaws.com/prod"

def test_employees_list():
    """직원 목록 조회 테스트"""
    print("=" * 60)
    print("직원 목록 조회 API 테스트")
    print("=" * 60)
    
    url = f"{API_BASE_URL}/employees"
    
    try:
        response = requests.get(url)
        
        print(f"\n상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            employees = data.get('employees', [])
            
            print(f"총 직원 수: {len(employees)}")
            print("\n직원 목록:")
            print("-" * 60)
            
            for emp in employees:
                # 다양한 필드명 지원
                name = emp.get('name') or emp.get('basic_info', {}).get('name', '이름 없음')
                position = emp.get('position') or emp.get('role') or emp.get('basic_info', {}).get('role', '직책 미정')
                experience = emp.get('experienceYears') or emp.get('experience_years') or emp.get('basic_info', {}).get('years_of_experience', 0)
                
                print(f"이름: {name}")
                print(f"직책: {position}")
                print(f"경력: {experience}년")
                print(f"user_id: {emp.get('user_id', 'N/A')}")
                print("-" * 60)
            
            # 첫 번째 직원의 전체 데이터 출력
            if employees:
                print("\n첫 번째 직원 전체 데이터:")
                print(json.dumps(employees[0], indent=2, ensure_ascii=False))
        else:
            print(f"오류: {response.text}")
            
    except Exception as e:
        print(f"테스트 실패: {str(e)}")

def test_direct_lambda():
    """Lambda 함수 직접 호출 테스트"""
    print("\n" + "=" * 60)
    print("Lambda 함수 직접 호출 테스트")
    print("=" * 60)
    
    import boto3
    
    lambda_client = boto3.client('lambda', region_name='us-east-2')
    
    try:
        response = lambda_client.invoke(
            FunctionName='EmployeesList',
            InvocationType='RequestResponse'
        )
        
        payload = json.loads(response['Payload'].read())
        
        print(f"\n상태 코드: {payload.get('statusCode')}")
        
        if payload.get('statusCode') == 200:
            body = json.loads(payload.get('body', '{}'))
            employees = body.get('employees', [])
            
            print(f"총 직원 수: {len(employees)}")
            print("\n직원 목록:")
            print("-" * 60)
            
            for emp in employees:
                name = emp.get('name') or emp.get('basic_info', {}).get('name', '이름 없음')
                position = emp.get('position') or emp.get('role') or emp.get('basic_info', {}).get('role', '직책 미정')
                experience = emp.get('experienceYears') or emp.get('experience_years') or emp.get('basic_info', {}).get('years_of_experience', 0)
                
                print(f"이름: {name} | 직책: {position} | 경력: {experience}년")
            
            # 첫 번째 직원의 전체 데이터 출력
            if employees:
                print("\n첫 번째 직원 전체 데이터:")
                print(json.dumps(employees[0], indent=2, ensure_ascii=False))
        else:
            print(f"오류: {payload}")
            
    except Exception as e:
        print(f"테스트 실패: {str(e)}")

if __name__ == '__main__':
    # Lambda 직접 호출 테스트
    test_direct_lambda()
    
    # API Gateway 테스트 (URL이 설정된 경우)
    # test_employees_list()
