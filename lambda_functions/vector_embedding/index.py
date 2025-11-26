"""
Vector Embedding Generator Lambda Function
벡터 임베딩 생성

Requirements: 11.1, 11.2
"""

import json
import logging
import boto3
from typing import Dict, Any, List
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS 클라이언트 초기화
bedrock_runtime = boto3.client('bedrock-runtime')
dynamodb = boto3.resource('dynamodb')


def handler(event, context):
    """
    Lambda handler for DynamoDB Stream
    
    Requirements: 11.1 - DynamoDB Stream 이벤트 처리
    
    Args:
        event: DynamoDB Stream 이벤트
        context: Lambda 컨텍스트
        
    Returns:
        dict: 처리 결과
    """
    try:
        logger.info(f"DynamoDB Stream 이벤트 수신: {len(event.get('Records', []))} records")
        
        processed_count = 0
        
        for record in event.get('Records', []):
            # INSERT 또는 MODIFY 이벤트만 처리
            event_name = record.get('eventName')
            if event_name not in ['INSERT', 'MODIFY']:
                logger.info(f"이벤트 타입 스킵: {event_name}")
                continue
            
            # 새 이미지 데이터 추출
            new_image = record.get('dynamodb', {}).get('NewImage', {})
            if not new_image:
                logger.warning("NewImage 데이터가 없습니다")
                continue
            
            # DynamoDB 형식을 Python 딕셔너리로 변환
            employee_data = deserialize_dynamodb_item(new_image)
            
            logger.info(f"직원 프로필 처리 시작: {employee_data.get('employee_id')}")
            
            # 벡터 임베딩 생성 및 인덱싱
            process_employee_profile(employee_data)
            
            processed_count += 1
        
        logger.info(f"처리 완료: {processed_count} records")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': '벡터 임베딩 생성 완료',
                'processed_records': processed_count
            })
        }
        
    except Exception as e:
        logger.error(f"벡터 임베딩 생성 중 오류 발생: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }


def deserialize_dynamodb_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    DynamoDB 형식의 아이템을 Python 딕셔너리로 변환
    
    Args:
        item: DynamoDB 형식의 아이템
        
    Returns:
        dict: Python 딕셔너리
    """
    result = {}
    
    for key, value in item.items():
        if 'S' in value:
            result[key] = value['S']
        elif 'N' in value:
            result[key] = float(value['N']) if '.' in value['N'] else int(value['N'])
        elif 'BOOL' in value:
            result[key] = value['BOOL']
        elif 'L' in value:
            result[key] = [deserialize_dynamodb_value(v) for v in value['L']]
        elif 'M' in value:
            result[key] = deserialize_dynamodb_item(value['M'])
        elif 'NULL' in value:
            result[key] = None
    
    return result


def deserialize_dynamodb_value(value: Dict[str, Any]) -> Any:
    """
    DynamoDB 값을 Python 값으로 변환
    
    Args:
        value: DynamoDB 값
        
    Returns:
        Python 값
    """
    if 'S' in value:
        return value['S']
    elif 'N' in value:
        return float(value['N']) if '.' in value['N'] else int(value['N'])
    elif 'BOOL' in value:
        return value['BOOL']
    elif 'L' in value:
        return [deserialize_dynamodb_value(v) for v in value['L']]
    elif 'M' in value:
        return deserialize_dynamodb_item(value['M'])
    elif 'NULL' in value:
        return None
    return None


def process_employee_profile(employee_data: Dict[str, Any]) -> None:
    """
    직원 프로필 처리 메인 함수
    
    Args:
        employee_data: 직원 데이터
    """
    # 벡터 임베딩 생성 (Requirements: 11.1)
    embedding_vector = generate_embedding_with_bedrock(employee_data)
    
    # OpenSearch에 인덱싱 (Requirements: 11.2)
    index_to_opensearch(employee_data, embedding_vector)


def generate_embedding_with_bedrock(employee_data: Dict[str, Any]) -> List[float]:
    """
    Bedrock Titan을 사용하여 벡터 임베딩 생성
    
    Requirements: 11.1
    
    Args:
        employee_data: 직원 데이터
        
    Returns:
        list: 임베딩 벡터
    """
    try:
        logger.info(f"Bedrock Titan 임베딩 생성 시작: {employee_data.get('employee_id')}")
        
        # 직원 프로필 텍스트 생성
        profile_text = create_profile_text(employee_data)
        
        # Bedrock Titan Embeddings 호출
        request_body = {
            "inputText": profile_text
        }
        
        response = bedrock_runtime.invoke_model(
            modelId="amazon.titan-embed-text-v1",
            body=json.dumps(request_body)
        )
        
        # 응답 파싱
        response_body = json.loads(response['body'].read())
        embedding_vector = response_body.get('embedding', [])
        
        logger.info(f"Bedrock Titan 임베딩 생성 완료: {len(embedding_vector)} dimensions")
        
        return embedding_vector
        
    except Exception as e:
        logger.error(f"Bedrock Titan 임베딩 생성 실패: {str(e)}")
        raise


def create_profile_text(employee_data: Dict[str, Any]) -> str:
    """
    직원 프로필을 텍스트로 변환
    
    Args:
        employee_data: 직원 데이터
        
    Returns:
        str: 프로필 텍스트
    """
    parts = []
    
    # 이름
    if employee_data.get('name'):
        parts.append(f"이름: {employee_data['name']}")
    
    # 스킬
    if employee_data.get('skills'):
        skills_text = ', '.join(employee_data['skills'])
        parts.append(f"기술: {skills_text}")
    
    # 경력
    if employee_data.get('experience_years'):
        parts.append(f"경력: {employee_data['experience_years']}년")
    
    # 학력
    if employee_data.get('education'):
        parts.append(f"학력: {employee_data['education']}")
    
    # 자격증
    if employee_data.get('certifications'):
        certs_text = ', '.join(employee_data['certifications'])
        parts.append(f"자격증: {certs_text}")
    
    # 프로젝트 이력
    if employee_data.get('project_history'):
        projects = employee_data['project_history']
        if isinstance(projects, list) and len(projects) > 0:
            project_texts = []
            for project in projects[:5]:  # 최근 5개 프로젝트만
                if isinstance(project, dict):
                    project_name = project.get('project_name', '')
                    role = project.get('role', '')
                    if project_name:
                        project_texts.append(f"{project_name} ({role})")
            if project_texts:
                parts.append(f"프로젝트: {', '.join(project_texts)}")
    
    return '. '.join(parts)


def index_to_opensearch(employee_data: Dict[str, Any], embedding_vector: List[float]) -> None:
    """
    OpenSearch에 벡터 임베딩 인덱싱
    
    Requirements: 11.2
    
    Args:
        employee_data: 직원 데이터
        embedding_vector: 임베딩 벡터
    """
    try:
        logger.info(f"OpenSearch 인덱싱 시작: {employee_data.get('employee_id')}")
        
        # OpenSearch 클라이언트 생성
        opensearch_client = get_opensearch_client()
        
        # 인덱스 이름
        index_name = 'employee_profiles'
        
        # 문서 생성
        document = {
            'employee_id': employee_data.get('employee_id'),
            'name': employee_data.get('name'),
            'skills': employee_data.get('skills', []),
            'experience_years': employee_data.get('experience_years', 0),
            'education': employee_data.get('education'),
            'certifications': employee_data.get('certifications', []),
            'embedding_vector': embedding_vector,
            'profile_text': create_profile_text(employee_data)
        }
        
        # OpenSearch에 인덱싱
        response = opensearch_client.index(
            index=index_name,
            id=employee_data.get('employee_id'),
            body=document
        )
        
        logger.info(f"OpenSearch 인덱싱 완료: {response.get('result')}")
        
    except Exception as e:
        logger.error(f"OpenSearch 인덱싱 실패: {str(e)}")
        raise


def get_opensearch_client() -> OpenSearch:
    """
    OpenSearch 클라이언트 생성
    
    Returns:
        OpenSearch: OpenSearch 클라이언트
    """
    import os
    
    # 환경 변수에서 OpenSearch 엔드포인트 가져오기
    opensearch_endpoint = os.environ.get('OPENSEARCH_ENDPOINT', 'localhost:9200')
    region = os.environ.get('AWS_REGION', 'us-east-2')
    
    # AWS 인증 설정
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        'es',
        session_token=credentials.token
    )
    
    # OpenSearch 클라이언트 생성
    client = OpenSearch(
        hosts=[{'host': opensearch_endpoint.replace('https://', ''), 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    
    return client
