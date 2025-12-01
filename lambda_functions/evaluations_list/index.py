"""
평가 목록 조회 Lambda 함수
직원 평가 목록을 상태별로 조회합니다.

Requirements: 3.1
"""

import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
evaluations_table = dynamodb.Table('EmployeeEvaluations')
employees_table = dynamodb.Table('Employees')

def decimal_default(obj):
    """Decimal 타입을 JSON 직렬화 가능하도록 변환"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def get_employee_details(user_id):
    """
    직원 상세 정보 조회
    
    Args:
        user_id: 직원 ID
        
    Returns:
        직원 정보 딕셔너리 또는 None
    """
    try:
        response = employees_table.get_item(Key={'user_id': user_id})
        return response.get('Item')
    except Exception as e:
        print(f"직원 정보 조회 실패 (user_id: {user_id}): {str(e)}")
        return None


def lambda_handler(event, context):
    """
    평가 목록 조회
    
    Query Parameters:
    - status: pending, approved, rejected, review (선택사항)
    - page: 페이지 번호 (기본값: 1)
    - limit: 페이지당 결과 수 (기본값: 20, 최대: 100)
    
    Response:
    {
        "evaluations": [
            {
                "evaluation_id": "...",
                "user_id": "...",
                "name": "...",
                "type": "career|freelancer",
                "status": "pending|approved|rejected|review",
                "overall_score": 85,
                "submitted_at": "2024-01-15T10:30:00Z",
                "quantitative_analysis": {...},
                "qualitative_analysis": {...},
                "employee_details": {
                    "basic_info": {...},
                    "skills": [...],
                    "work_experience": [...]
                }
            }
        ],
        "count": 10,
        "page": 1,
        "limit": 20,
        "total": 45
    }
    """
    try:
        # CORS 헤더
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,OPTIONS'
        }
        
        # OPTIONS 요청 처리 (CORS preflight)
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'OK'})
            }
        
        # Query parameters 파싱
        query_params = event.get('queryStringParameters') or {}
        status_filter = query_params.get('status')
        page = int(query_params.get('page', 1))
        limit = min(int(query_params.get('limit', 20)), 100)  # 최대 100개
        
        # 상태별 필터링
        if status_filter:
            # 유효한 상태 검증
            valid_statuses = ['pending', 'approved', 'rejected', 'review']
            if status_filter not in valid_statuses:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'Invalid status',
                        'message': f'유효한 상태: {", ".join(valid_statuses)}'
                    })
                }
            
            # StatusIndex GSI 사용
            try:
                response = evaluations_table.query(
                    IndexName='StatusIndex',
                    KeyConditionExpression='#status = :status',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={':status': status_filter},
                    ScanIndexForward=False  # 최신순 정렬
                )
            except Exception as gsi_error:
                print(f"StatusIndex GSI 조회 실패, 스캔으로 대체: {str(gsi_error)}")
                # GSI가 없는 경우 스캔으로 대체
                response = evaluations_table.scan(
                    FilterExpression='#status = :status',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={':status': status_filter}
                )
        else:
            # 전체 조회
            response = evaluations_table.scan()
        
        evaluations = response.get('Items', [])
        
        # 제출일 기준 정렬 (최신순)
        evaluations.sort(key=lambda x: x.get('submitted_at', ''), reverse=True)
        
        # 총 개수
        total = len(evaluations)
        
        # 페이지네이션 적용
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_evaluations = evaluations[start_idx:end_idx]
        
        # 각 평가에 직원 상세 정보 추가
        enriched_evaluations = []
        for evaluation in paginated_evaluations:
            user_id = evaluation.get('user_id')
            if user_id:
                employee_details = get_employee_details(user_id)
                if employee_details:
                    # 필요한 필드만 추가
                    evaluation['employee_details'] = {
                        'basic_info': employee_details.get('basic_info', {}),
                        'skills': employee_details.get('skills', []),
                        'work_experience': employee_details.get('work_experience', [])
                    }
            enriched_evaluations.append(evaluation)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'evaluations': enriched_evaluations,
                'count': len(enriched_evaluations),
                'page': page,
                'limit': limit,
                'total': total
            }, default=decimal_default)
        }
        
    except Exception as e:
        print(f"Error fetching evaluations: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': str(e),
                'message': '평가 목록 조회에 실패했습니다'
            })
        }
