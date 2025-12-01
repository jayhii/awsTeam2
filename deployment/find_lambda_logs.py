"""
Lambda 로그 그룹 찾기 및 최근 로그 확인
"""

import boto3
from datetime import datetime, timedelta

logs_client = boto3.client('logs', region_name='us-east-2')
lambda_client = boto3.client('lambda', region_name='us-east-2')

print("=" * 80)
print("Lambda 함수 및 로그 확인")
print("=" * 80)

# Lambda 함수 목록 조회
try:
    response = lambda_client.list_functions()
    
    print("\n[Lambda 함수 목록]")
    evaluation_function = None
    for func in response.get('Functions', []):
        func_name = func['FunctionName']
        if 'employeeevaluation' in func_name.lower():
            print(f"  ✓ {func_name} (선택됨)")
            evaluation_function = func_name
        elif 'evaluation' in func_name.lower():
            print(f"  ✓ {func_name}")
        else:
            print(f"    {func_name}")
    
    if not evaluation_function:
        print("\n✗ EmployeeEvaluation Lambda 함수를 찾을 수 없습니다.")
        exit(1)
    
    print(f"\n[선택된 함수: {evaluation_function}]")
    log_group_name = f"/aws/lambda/{evaluation_function}"
    print(f"로그 그룹: {log_group_name}")
    
    # 최근 로그 조회
    start_time = int((datetime.now() - timedelta(minutes=10)).timestamp() * 1000)
    end_time = int(datetime.now().timestamp() * 1000)
    
    try:
        response = logs_client.filter_log_events(
            logGroupName=log_group_name,
            startTime=start_time,
            endTime=end_time,
            limit=100
        )
        
        events = response.get('events', [])
        print(f"\n최근 로그 이벤트 ({len(events)}개):\n")
        
        if not events:
            print("  (로그 없음)")
        else:
            for event in events[-20:]:  # 최근 20개만
                timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
                message = event['message'].strip()
                print(f"[{timestamp.strftime('%H:%M:%S')}] {message}")
        
    except Exception as log_error:
        print(f"\n✗ 로그 조회 오류: {str(log_error)}")
    
    print("\n" + "=" * 80)

except Exception as e:
    print(f"✗ 오류: {str(e)}")
