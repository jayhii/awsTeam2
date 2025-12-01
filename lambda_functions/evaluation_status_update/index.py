"""
평가 상태 업데이트 Lambda 함수
평가 승인, 검토, 반려 처리를 담당합니다.

Requirements: 3.1
"""

import json
import boto3
import os
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

table = dynamodb.Table('EmployeeEvaluations')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')

def decimal_default(obj):
    """Decimal 타입을 JSON 직렬화 가능하도록 변환"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    """
    평가 상태 업데이트
    
    Path Parameters:
    - evaluationId: 평가 ID
    
    Request Body:
    {
        "status": "approved|review|rejected",
        "comments": "검토 의견 (review 시)",
        "reason": "반려 사유 (rejected 시)"
    }
    
    Response:
    {
        "evaluation": {...},
        "message": "상태가 업데이트되었습니다"
    }
    """
    try:
        # CORS 헤더
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'PUT,OPTIONS'
        }
        
        # OPTIONS 요청 처리 (CORS preflight)
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'OK'})
            }
        
        # Path parameters에서 evaluation_id 추출
        path_params = event.get('pathParameters', {})
        evaluation_id = path_params.get('evaluationId')
        
        if not evaluation_id:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Missing evaluation ID',
                    'message': '평가 ID가 필요합니다'
                })
            }
        
        # 요청 본문 파싱
        body = json.loads(event.get('body', '{}'))
        new_status = body.get('status')
        comments = body.get('comments', '')
        reason = body.get('reason', '')
        
        # 상태 검증
        valid_statuses = ['approved', 'review', 'rejected']
        if new_status not in valid_statuses:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Invalid status',
                    'message': f'유효한 상태: {", ".join(valid_statuses)}'
                })
            }
        
        # 현재 평가 조회
        response = table.get_item(Key={'evaluation_id': evaluation_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Evaluation not found',
                    'message': '평가를 찾을 수 없습니다'
                })
            }
        
        evaluation = response['Item']
        
        # 상태 업데이트
        update_expression = 'SET #status = :status, updated_at = :updated_at'
        expression_values = {
            ':status': new_status,
            ':updated_at': datetime.now().isoformat()
        }
        expression_names = {'#status': 'status'}
        
        # 상태별 추가 필드 업데이트
        if new_status == 'approved':
            update_expression += ', approved_at = :approved_at'
            expression_values[':approved_at'] = datetime.now().isoformat()
            message = '평가가 승인되었습니다'
            
        elif new_status == 'review':
            if comments:
                update_expression += ', review_comments = :comments'
                expression_values[':comments'] = comments
            update_expression += ', reviewed_at = :reviewed_at'
            expression_values[':reviewed_at'] = datetime.now().isoformat()
            message = '평가가 검토 상태로 변경되었습니다'
            
        elif new_status == 'rejected':
            if reason:
                update_expression += ', rejection_reason = :reason'
                expression_values[':reason'] = reason
            update_expression += ', rejected_at = :rejected_at'
            expression_values[':rejected_at'] = datetime.now().isoformat()
            message = '평가가 반려되었습니다'
        
        # DynamoDB 업데이트
        response = table.update_item(
            Key={'evaluation_id': evaluation_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames=expression_names,
            ReturnValues='ALL_NEW'
        )
        
        updated_evaluation = response['Attributes']
        
        # SNS 알림 전송
        try:
            if SNS_TOPIC_ARN:
                notification_message = {
                    'evaluation_id': evaluation_id,
                    'user_id': evaluation.get('user_id', 'Unknown'),
                    'name': evaluation.get('name', 'Unknown'),
                    'status': new_status,
                    'timestamp': datetime.now().isoformat()
                }
                
                sns.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Subject=f'평가 상태 변경: {message}',
                    Message=json.dumps(notification_message, ensure_ascii=False, indent=2)
                )
                print(f"SNS 알림 전송 완료: {evaluation_id}")
        except Exception as sns_error:
            # SNS 실패는 로그만 남기고 계속 진행
            print(f"SNS 알림 전송 실패: {str(sns_error)}")
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'evaluation': updated_evaluation,
                'message': message
            }, default=decimal_default)
        }
        
    except Exception as e:
        print(f"Error updating evaluation status: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': str(e),
                'message': '평가 상태 업데이트에 실패했습니다'
            })
        }
