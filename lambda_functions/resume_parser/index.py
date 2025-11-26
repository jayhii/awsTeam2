"""
Resume Parser Lambda Function
이력서 파싱 및 데이터 추출

Requirements: 10.1, 10.2, 10.3, 10.4
"""

import json
import logging
import os
import boto3
from typing import Dict, Any, Optional
from urllib.parse import unquote_plus

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS 클라이언트 초기화
s3_client = boto3.client('s3')
textract_client = boto3.client('textract')
bedrock_runtime = boto3.client('bedrock-runtime')


def handler(event, context):
    """
    Lambda handler for S3 trigger
    
    Requirements: 10.1 - S3 이벤트 처리 및 PDF 다운로드
    
    Args:
        event: S3 이벤트
        context: Lambda 컨텍스트
        
    Returns:
        dict: 처리 결과
    """
    try:
        logger.info(f"이벤트 수신: {json.dumps(event)}")
        
        # S3 이벤트 파싱
        for record in event.get('Records', []):
            # S3 이벤트 타입 확인
            event_name = record.get('eventName', '')
            if not event_name.startswith('ObjectCreated:'):
                logger.info(f"ObjectCreated 이벤트가 아님: {event_name}")
                continue
            
            # S3 버킷 및 키 정보 추출
            s3_info = record.get('s3', {})
            bucket_name = s3_info.get('bucket', {}).get('name')
            object_key = unquote_plus(s3_info.get('object', {}).get('key', ''))
            
            if not bucket_name or not object_key:
                logger.error("S3 버킷 또는 키 정보가 없습니다")
                continue
            
            logger.info(f"S3 객체 처리 시작: s3://{bucket_name}/{object_key}")
            
            # PDF 파일인지 확인
            if not object_key.lower().endswith('.pdf'):
                logger.warning(f"PDF 파일이 아님: {object_key}")
                continue
            
            # PDF 다운로드
            try:
                response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
                pdf_content = response['Body'].read()
                logger.info(f"PDF 다운로드 완료: {len(pdf_content)} bytes")
            except Exception as e:
                logger.error(f"PDF 다운로드 실패: {str(e)}")
                raise
            
            # 이력서 파싱 처리 (다음 단계에서 구현)
            # result = process_resume(bucket_name, object_key, pdf_content)
            
            logger.info(f"이력서 처리 완료: {object_key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': '이력서 파싱 완료',
                'processed_records': len(event.get('Records', []))
            })
        }
        
    except Exception as e:
        logger.error(f"이력서 파싱 중 오류 발생: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }


def process_resume(bucket_name: str, object_key: str, pdf_content: bytes) -> Dict[str, Any]:
    """
    이력서 처리 메인 함수
    
    Args:
        bucket_name: S3 버킷 이름
        object_key: S3 객체 키
        pdf_content: PDF 파일 내용
        
    Returns:
        dict: 처리 결과
    """
    # Textract로 텍스트 추출 (Requirements: 10.2)
    extracted_text = extract_text_with_textract(bucket_name, object_key)
    
    # Bedrock Claude로 구조화된 데이터 추출 (Requirements: 10.3)
    structured_data = extract_structured_data_with_bedrock(extracted_text)
    
    # 스킬 정규화 및 DynamoDB 저장 (Requirements: 10.4)
    save_to_dynamodb(structured_data)
    
    return {
        'bucket': bucket_name,
        'key': object_key,
        'employee_id': structured_data.get('employee_id'),
        'status': 'success'
    }


def extract_text_with_textract(bucket_name: str, object_key: str) -> str:
    """
    Textract를 사용하여 PDF에서 텍스트 추출
    
    Requirements: 10.1, 10.2
    
    Args:
        bucket_name: S3 버킷 이름
        object_key: S3 객체 키
        
    Returns:
        str: 추출된 텍스트
    """
    try:
        logger.info(f"Textract 텍스트 추출 시작: {object_key}")
        
        # Textract 호출
        response = textract_client.detect_document_text(
            Document={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': object_key
                }
            }
        )
        
        # 텍스트 블록 추출
        text_blocks = []
        for block in response.get('Blocks', []):
            if block['BlockType'] == 'LINE':
                text_blocks.append(block.get('Text', ''))
        
        extracted_text = '\n'.join(text_blocks)
        logger.info(f"Textract 텍스트 추출 완료: {len(extracted_text)} characters")
        
        return extracted_text
        
    except Exception as e:
        logger.error(f"Textract 텍스트 추출 실패: {str(e)}")
        raise


def extract_structured_data_with_bedrock(text: str) -> Dict[str, Any]:
    """
    Bedrock Claude를 사용하여 구조화된 데이터 추출
    
    Requirements: 10.3
    
    Args:
        text: 추출된 텍스트
        
    Returns:
        dict: 구조화된 직원 데이터
    """
    try:
        logger.info("Bedrock Claude로 구조화된 데이터 추출 시작")
        
        # Claude 프롬프트 생성
        prompt = f"""다음은 이력서에서 추출한 텍스트입니다. 이 텍스트를 분석하여 JSON 형식으로 구조화된 데이터를 추출해주세요.

이력서 텍스트:
{text}

다음 형식의 JSON으로 응답해주세요:
{{
    "name": "이름",
    "email": "이메일",
    "phone": "전화번호",
    "skills": ["기술1", "기술2", ...],
    "experience_years": 경력년수,
    "education": "최종학력",
    "certifications": ["자격증1", "자격증2", ...],
    "project_history": [
        {{
            "project_name": "프로젝트명",
            "role": "역할",
            "duration": "기간",
            "description": "설명"
        }}
    ]
}}

JSON만 응답하고 다른 설명은 포함하지 마세요."""

        # Bedrock Claude 호출
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-v2",
            body=json.dumps(request_body)
        )
        
        # 응답 파싱
        response_body = json.loads(response['body'].read())
        content = response_body.get('content', [{}])[0].get('text', '{}')
        
        # JSON 추출 (마크다운 코드 블록 제거)
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        
        structured_data = json.loads(content)
        logger.info("Bedrock Claude 데이터 추출 완료")
        
        return structured_data
        
    except Exception as e:
        logger.error(f"Bedrock Claude 데이터 추출 실패: {str(e)}")
        raise


def save_to_dynamodb(data: Dict[str, Any]) -> None:
    """
    구조화된 데이터를 DynamoDB에 저장
    
    Requirements: 10.4
    
    Args:
        data: 구조화된 직원 데이터
    """
    try:
        logger.info("DynamoDB에 데이터 저장 시작")
        
        # 스킬 정규화 (Requirements: 10.4)
        from common.utils import normalize_skill
        normalized_skills = [normalize_skill(skill) for skill in data.get('skills', [])]
        
        # Employee 데이터 생성
        employee_data = {
            'employee_id': f"EMP_{data.get('email', '').split('@')[0]}",
            'name': data.get('name'),
            'email': data.get('email'),
            'phone': data.get('phone'),
            'skills': normalized_skills,
            'experience_years': data.get('experience_years', 0),
            'education': data.get('education'),
            'certifications': data.get('certifications', []),
            'project_history': data.get('project_history', [])
        }
        
        # DynamoDB에 저장
        from common.repositories import EmployeeRepository
        from common.dynamodb_client import DynamoDBClient
        
        dynamodb_client = DynamoDBClient()
        employee_repo = EmployeeRepository(dynamodb_client)
        
        # Employee 모델로 변환
        from common.models import Employee
        employee = Employee(**employee_data)
        
        # 저장
        employee_repo.create(employee)
        
        logger.info(f"DynamoDB에 데이터 저장 완료: {employee_data['employee_id']}")
        
    except Exception as e:
        logger.error(f"DynamoDB 저장 실패: {str(e)}")
        raise
