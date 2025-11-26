"""
DynamoDB Client Wrapper

연결 관리, 재시도 로직, 에러 핸들링을 포함한 DynamoDB 클라이언트 래퍼입니다.
Requirements: 7.1
"""

import boto3
import logging
import time
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError, BotoCoreError
from decimal import Decimal


# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DynamoDBClientError(Exception):
    """DynamoDB 클라이언트 커스텀 예외"""
    pass


class DynamoDBClient:
    """
    DynamoDB 클라이언트 래퍼 클래스
    
    연결 관리, 자동 재시도, 에러 핸들링을 제공합니다.
    """
    
    def __init__(
        self,
        region_name: str = 'us-east-2',
        max_retries: int = 3,
        retry_delay: float = 1.0,
        endpoint_url: Optional[str] = None
    ):
        """
        DynamoDB 클라이언트 초기화
        
        Args:
            region_name: AWS 리전 (기본값: us-east-2)
            max_retries: 최대 재시도 횟수 (기본값: 3)
            retry_delay: 재시도 간 대기 시간 (초, 기본값: 1.0)
            endpoint_url: 테스트용 엔드포인트 URL (선택사항)
        """
        self.region_name = region_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        try:
            # DynamoDB 리소스 및 클라이언트 생성
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=region_name,
                endpoint_url=endpoint_url
            )
            self.client = boto3.client(
                'dynamodb',
                region_name=region_name,
                endpoint_url=endpoint_url
            )
            logger.info(f"DynamoDB 클라이언트 초기화 완료 (리전: {region_name})")
        except Exception as e:
            logger.error(f"DynamoDB 클라이언트 초기화 실패: {str(e)}")
            raise DynamoDBClientError(f"DynamoDB 클라이언트 초기화 실패: {str(e)}")
    
    def _execute_with_retry(self, operation, *args, **kwargs) -> Any:
        """
        재시도 로직을 포함한 작업 실행
        
        Args:
            operation: 실행할 작업 함수
            *args: 위치 인자
            **kwargs: 키워드 인자
            
        Returns:
            작업 실행 결과
            
        Raises:
            DynamoDBClientError: 최대 재시도 횟수 초과 시
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return operation(*args, **kwargs)
            except ClientError as e:
                error_code = e.response['Error']['Code']
                last_exception = e
                
                # 재시도 가능한 에러인지 확인
                if error_code in ['ProvisionedThroughputExceededException', 
                                 'ThrottlingException',
                                 'RequestLimitExceeded',
                                 'InternalServerError',
                                 'ServiceUnavailable']:
                    if attempt < self.max_retries - 1:
                        # 지수 백오프 적용
                        wait_time = self.retry_delay * (2 ** attempt)
                        logger.warning(
                            f"재시도 가능한 에러 발생 ({error_code}). "
                            f"{wait_time}초 후 재시도 ({attempt + 1}/{self.max_retries})"
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"최대 재시도 횟수 초과: {error_code}")
                        raise DynamoDBClientError(
                            f"최대 재시도 횟수 초과: {error_code} - {str(e)}"
                        )
                else:
                    # 재시도 불가능한 에러
                    logger.error(f"재시도 불가능한 에러: {error_code} - {str(e)}")
                    raise DynamoDBClientError(f"{error_code}: {str(e)}")
            except BotoCoreError as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(
                        f"BotoCore 에러 발생. {wait_time}초 후 재시도 "
                        f"({attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"최대 재시도 횟수 초과: {str(e)}")
                    raise DynamoDBClientError(f"BotoCore 에러: {str(e)}")
        
        # 모든 재시도 실패
        raise DynamoDBClientError(f"작업 실패: {str(last_exception)}")
    
    def get_table(self, table_name: str):
        """
        DynamoDB 테이블 객체 반환
        
        Args:
            table_name: 테이블 이름
            
        Returns:
            DynamoDB 테이블 객체
        """
        try:
            return self.dynamodb.Table(table_name)
        except Exception as e:
            logger.error(f"테이블 접근 실패 ({table_name}): {str(e)}")
            raise DynamoDBClientError(f"테이블 접근 실패: {str(e)}")
    
    def put_item(self, table_name: str, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        아이템 저장
        
        Args:
            table_name: 테이블 이름
            item: 저장할 아이템
            
        Returns:
            응답 메타데이터
            
        Raises:
            DynamoDBClientError: 저장 실패 시
        """
        def _put():
            table = self.get_table(table_name)
            # Python float를 Decimal로 변환
            converted_item = self._convert_floats_to_decimal(item)
            response = table.put_item(Item=converted_item)
            logger.info(f"아이템 저장 완료 (테이블: {table_name})")
            return response
        
        return self._execute_with_retry(_put)
    
    def get_item(
        self,
        table_name: str,
        key: Dict[str, Any],
        consistent_read: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        아이템 조회
        
        Args:
            table_name: 테이블 이름
            key: 조회할 키
            consistent_read: 강력한 일관성 읽기 여부
            
        Returns:
            조회된 아이템 또는 None
            
        Raises:
            DynamoDBClientError: 조회 실패 시
        """
        def _get():
            table = self.get_table(table_name)
            response = table.get_item(Key=key, ConsistentRead=consistent_read)
            item = response.get('Item')
            if item:
                # Decimal을 float로 변환
                item = self._convert_decimals_to_float(item)
                logger.info(f"아이템 조회 완료 (테이블: {table_name})")
            else:
                logger.info(f"아이템 없음 (테이블: {table_name}, 키: {key})")
            return item
        
        return self._execute_with_retry(_get)
    
    def update_item(
        self,
        table_name: str,
        key: Dict[str, Any],
        update_expression: str,
        expression_attribute_values: Dict[str, Any],
        expression_attribute_names: Optional[Dict[str, str]] = None,
        return_values: str = 'ALL_NEW'
    ) -> Dict[str, Any]:
        """
        아이템 업데이트
        
        Args:
            table_name: 테이블 이름
            key: 업데이트할 키
            update_expression: 업데이트 표현식
            expression_attribute_values: 표현식 속성 값
            expression_attribute_names: 표현식 속성 이름 (선택사항)
            return_values: 반환 값 옵션
            
        Returns:
            업데이트된 아이템
            
        Raises:
            DynamoDBClientError: 업데이트 실패 시
        """
        def _update():
            table = self.get_table(table_name)
            # float를 Decimal로 변환
            converted_values = self._convert_floats_to_decimal(expression_attribute_values)
            
            kwargs = {
                'Key': key,
                'UpdateExpression': update_expression,
                'ExpressionAttributeValues': converted_values,
                'ReturnValues': return_values
            }
            
            if expression_attribute_names:
                kwargs['ExpressionAttributeNames'] = expression_attribute_names
            
            response = table.update_item(**kwargs)
            attributes = response.get('Attributes', {})
            # Decimal을 float로 변환
            attributes = self._convert_decimals_to_float(attributes)
            logger.info(f"아이템 업데이트 완료 (테이블: {table_name})")
            return attributes
        
        return self._execute_with_retry(_update)
    
    def delete_item(self, table_name: str, key: Dict[str, Any]) -> Dict[str, Any]:
        """
        아이템 삭제
        
        Args:
            table_name: 테이블 이름
            key: 삭제할 키
            
        Returns:
            응답 메타데이터
            
        Raises:
            DynamoDBClientError: 삭제 실패 시
        """
        def _delete():
            table = self.get_table(table_name)
            response = table.delete_item(Key=key)
            logger.info(f"아이템 삭제 완료 (테이블: {table_name})")
            return response
        
        return self._execute_with_retry(_delete)
    
    def query(
        self,
        table_name: str,
        key_condition_expression,
        filter_expression=None,
        index_name: Optional[str] = None,
        limit: Optional[int] = None,
        scan_index_forward: bool = True
    ) -> List[Dict[str, Any]]:
        """
        쿼리 실행
        
        Args:
            table_name: 테이블 이름
            key_condition_expression: 키 조건 표현식
            filter_expression: 필터 표현식 (선택사항)
            index_name: 인덱스 이름 (선택사항)
            limit: 최대 결과 수 (선택사항)
            scan_index_forward: 정렬 순서 (기본값: True - 오름차순)
            
        Returns:
            조회된 아이템 리스트
            
        Raises:
            DynamoDBClientError: 쿼리 실패 시
        """
        def _query():
            table = self.get_table(table_name)
            
            kwargs = {
                'KeyConditionExpression': key_condition_expression,
                'ScanIndexForward': scan_index_forward
            }
            
            if filter_expression:
                kwargs['FilterExpression'] = filter_expression
            if index_name:
                kwargs['IndexName'] = index_name
            if limit:
                kwargs['Limit'] = limit
            
            response = table.query(**kwargs)
            items = response.get('Items', [])
            # Decimal을 float로 변환
            items = [self._convert_decimals_to_float(item) for item in items]
            logger.info(f"쿼리 완료 (테이블: {table_name}, 결과: {len(items)}개)")
            return items
        
        return self._execute_with_retry(_query)
    
    def scan(
        self,
        table_name: str,
        filter_expression=None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        테이블 스캔
        
        Args:
            table_name: 테이블 이름
            filter_expression: 필터 표현식 (선택사항)
            limit: 최대 결과 수 (선택사항)
            
        Returns:
            조회된 아이템 리스트
            
        Raises:
            DynamoDBClientError: 스캔 실패 시
        """
        def _scan():
            table = self.get_table(table_name)
            
            kwargs = {}
            if filter_expression:
                kwargs['FilterExpression'] = filter_expression
            if limit:
                kwargs['Limit'] = limit
            
            response = table.scan(**kwargs)
            items = response.get('Items', [])
            # Decimal을 float로 변환
            items = [self._convert_decimals_to_float(item) for item in items]
            logger.info(f"스캔 완료 (테이블: {table_name}, 결과: {len(items)}개)")
            return items
        
        return self._execute_with_retry(_scan)
    
    def batch_write(
        self,
        table_name: str,
        items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        배치 쓰기
        
        Args:
            table_name: 테이블 이름
            items: 저장할 아이템 리스트
            
        Returns:
            응답 메타데이터
            
        Raises:
            DynamoDBClientError: 배치 쓰기 실패 시
        """
        def _batch_write():
            table = self.get_table(table_name)
            
            with table.batch_writer() as batch:
                for item in items:
                    # float를 Decimal로 변환
                    converted_item = self._convert_floats_to_decimal(item)
                    batch.put_item(Item=converted_item)
            
            logger.info(f"배치 쓰기 완료 (테이블: {table_name}, 아이템: {len(items)}개)")
            return {'status': 'success', 'count': len(items)}
        
        return self._execute_with_retry(_batch_write)
    
    @staticmethod
    def _convert_floats_to_decimal(obj: Any) -> Any:
        """
        Python float를 DynamoDB Decimal로 변환
        
        Args:
            obj: 변환할 객체
            
        Returns:
            변환된 객체
        """
        if isinstance(obj, float):
            return Decimal(str(obj))
        elif isinstance(obj, dict):
            return {k: DynamoDBClient._convert_floats_to_decimal(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [DynamoDBClient._convert_floats_to_decimal(item) for item in obj]
        return obj
    
    @staticmethod
    def _convert_decimals_to_float(obj: Any) -> Any:
        """
        DynamoDB Decimal을 Python float로 변환
        
        Args:
            obj: 변환할 객체
            
        Returns:
            변환된 객체
        """
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: DynamoDBClient._convert_decimals_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [DynamoDBClient._convert_decimals_to_float(item) for item in obj]
        return obj
