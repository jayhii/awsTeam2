"""
이력서 업로드를 위한 Presigned URL 생성 Lambda 함수
S3에 직접 업로드할 수 있는 임시 URL을 생성합니다.
"""

import json
import boto3
import os
import uuid
from datetime import datetime

s3_client = boto3.client('s3')

# 환경 변수
RESUMES_BUCKET = os.environ.get('RESUMES_BUCKET', 'hr-resource-optimization-resumes-prod')

def lambda_handler(event, context):
    """
    이력서 업로드를 위한 Presigned URL 생성
    
    Request Body:
    {
        "file_name": "resume.pdf",
        "content_type": "application/pdf"
    }
    
    Response:
    {
        "upload_url": "https://...",
        "file_key": "uploads/...",
        "expires_in": 3600
    }
    """
    try:
        # CORS 헤더
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        }
        
        # OPTIONS 요청 처리 (CORS preflight)
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'OK'})
            }
        
        # 요청 본문 파싱
        body = json.loads(event.get('body', '{}'))
        file_name = body.get('file_name')
        content_type = body.get('content_type', 'application/pdf')
        
        # 필수 필드 검증
        if not file_name:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Missing required field: file_name',
                    'message': '파일 이름은 필수 항목입니다'
                })
            }
        
        # PDF 파일만 허용
        if not file_name.lower().endswith('.pdf'):
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Only PDF files are supported',
                    'message': 'PDF 파일만 업로드 가능합니다'
                })
            }
        
        # 고유한 파일 키 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        file_key = f"uploads/{timestamp}_{unique_id}_{file_name}"
        
        # Presigned URL 생성 (1시간 유효)
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': RESUMES_BUCKET,
                'Key': file_key,
                'ContentType': content_type
            },
            ExpiresIn=3600  # 1시간
        )
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'upload_url': presigned_url,
                'file_key': file_key,
                'bucket': RESUMES_BUCKET,
                'expires_in': 3600,
                'message': '업로드 URL이 생성되었습니다'
            })
        }
        
    except Exception as e:
        print(f"Error generating presigned URL: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': str(e),
                'message': '업로드 URL 생성에 실패했습니다'
            })
        }
