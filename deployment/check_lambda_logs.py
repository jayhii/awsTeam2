"""
Lambda 함수 로그 확인
"""

import boto3
from datetime import datetime, timedelta

logs_client = boto3.client('logs', region_name='us-east-2')

log_group_name = '/aws/lambda/employee-evaluation'

print("=" * 80)
print("Lambda 함수 로그 확인")
print("=" * 80)

try:
    # 최근 10분간의 로그 조회
    start_time = int((datetime.now() - timedelta(minutes=10)).timestamp() * 1000)
    end_time = int(datetime.now().timestamp() * 1000)
    
    response = logs_client.filter_log_events(
        logGroupName=log_group_name,
        startTime=start_time,
        endTime=end_time,
        limit=50
    )
    
    print(f"\n최근 로그 이벤트 ({len(response.get('events', []))}개):\n")
    
    for event in response.get('events', []):
        timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
        message = event['message'].strip()
        
        # 에러나 중요한 메시지만 출력
        if any(keyword in message.lower() for keyword in ['error', 'exception', 'ai 분석', 'json 파싱', 'bedrock']):
            print(f"[{timestamp.strftime('%H:%M:%S')}] {message}")
    
    print("\n" + "=" * 80)

except Exception as e:
    print(f"✗ 로그 조회 오류: {str(e)}")
