"""
최근 Lambda 로그에서 에러만 확인
"""

import boto3
from datetime import datetime, timedelta

logs_client = boto3.client('logs', region_name='us-east-2')

log_group_name = '/aws/lambda/EmployeeEvaluation'

print("=" * 80)
print("최근 Lambda 에러 로그")
print("=" * 80)

try:
    start_time = int((datetime.now() - timedelta(minutes=5)).timestamp() * 1000)
    end_time = int(datetime.now().timestamp() * 1000)
    
    response = logs_client.filter_log_events(
        logGroupName=log_group_name,
        startTime=start_time,
        endTime=end_time,
        limit=100
    )
    
    events = response.get('events', [])
    print(f"\n최근 5분간 로그 ({len(events)}개):\n")
    
    for event in events[-30:]:
        timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
        message = event['message'].strip()
        print(f"[{timestamp.strftime('%H:%M:%S')}] {message}")
    
    print("\n" + "=" * 80)

except Exception as e:
    print(f"✗ 오류: {str(e)}")
