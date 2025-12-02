#!/usr/bin/env python3
"""
도메인 데이터 관리 파이프라인 설정
"""

import boto3
import json
import zipfile
from pathlib import Path

REGION = "us-east-2"
ACCOUNT_ID = "412677576136"

lambda_client = boto3.client('lambda', region_name=REGION)
events_client = boto3.client('events', region_name=REGION)
dynamodb = boto3.client('dynamodb', region_name=REGION)

def create_lambda_deployment_package(lambda_dir: str) -> Path:
    """Lambda 배포 패키지 생성"""
    lambda_path = Path(f'lambda_functions/{lambda_dir}')
    zip_path = Path(f'lambda_functions/{lambda_dir}_deployment.zip')
    
    print(f"배포 패키지 생성 중: {lambda_dir}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # index.py 추가
        index_file = lambda_path / 'index.py'
        if index_file.exists():
            zipf.write(index_file, 'index.py')
            print(f"  ✓ {index_file}")
        
        # __init__.py 추가
        init_file = lambda_path / '__init__.py'
        if init_file.exists():
            zipf.write(init_file, '__init__.py')
    
    print(f"✓ 배포 패키지 생성 완료: {zip_path}")
    return zip_path

def setup_tech_trend_collector():
    """TechTrendCollector Lambda 함수 설정"""
    print("\n" + "=" * 60)
    print("TechTrendCollector 설정")
    print("=" * 60)
    
    function_name = 'TechTrendCollector'
    
    try:
        # 배포 패키지 생성
        zip_path = create_lambda_deployment_package('tech_trend_collector')
        
        # Lambda 함수 생성 또는 업데이트
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        try:
            # 함수 업데이트 시도
            response = lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_content
            )
            print(f"✓ Lambda 함수 업데이트: {function_name}")
        except lambda_client.exceptions.ResourceNotFoundException:
            # 함수 생성
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.11',
                Role=f'arn:aws:iam::{ACCOUNT_ID}:role/LambdaExecutionRole-Team2',
                Handler='index.handler',
                Code={'ZipFile': zip_content},
                Timeout=300,
                MemorySize=512,
                Environment={
                    'Variables': {
                        'AWS_REGION': REGION
                    }
                },
                Tags={
                    'Team': 'Team2',
                    'Project': 'HR-Resource-Optimization'
                }
            )
            print(f"✓ Lambda 함수 생성: {function_name}")
        
        # EventBridge Rule 생성 (매주 일요일 오전 2시 UTC)
        rule_name = 'TechTrendCollectionSchedule'
        
        try:
            events_client.put_rule(
                Name=rule_name,
                ScheduleExpression='cron(0 2 ? * SUN *)',
                State='ENABLED',
                Description='주간 기술 트렌드 수집'
            )
            print(f"✓ EventBridge Rule 생성: {rule_name}")
            
            # Lambda 권한 추가
            try:
                lambda_client.add_permission(
                    FunctionName=function_name,
                    StatementId='AllowEventBridgeInvoke',
                    Action='lambda:InvokeFunction',
                    Principal='events.amazonaws.com',
                    SourceArn=f'arn:aws:events:{REGION}:{ACCOUNT_ID}:rule/{rule_name}'
                )
            except lambda_client.exceptions.ResourceConflictException:
                pass
            
            # Target 추가
            events_client.put_targets(
                Rule=rule_name,
                Targets=[{
                    'Id': '1',
                    'Arn': f'arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:{function_name}'
                }]
            )
            print(f"✓ EventBridge Target 설정 완료")
            
        except Exception as e:
            print(f"⚠ EventBridge 설정 실패: {str(e)}")
        
        # 임시 파일 삭제
        zip_path.unlink()
        
        return True
        
    except Exception as e:
        print(f"✗ TechTrendCollector 설정 실패: {str(e)}")
        return False

def setup_domain_portfolio_updater():
    """DomainPortfolioUpdater Lambda 함수 설정"""
    print("\n" + "=" * 60)
    print("DomainPortfolioUpdater 설정")
    print("=" * 60)
    
    function_name = 'DomainPortfolioUpdater'
    
    try:
        # 배포 패키지 생성
        zip_path = create_lambda_deployment_package('domain_portfolio_updater')
        
        # Lambda 함수 생성 또는 업데이트
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        try:
            # 함수 업데이트 시도
            response = lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_content
            )
            print(f"✓ Lambda 함수 업데이트: {function_name}")
        except lambda_client.exceptions.ResourceNotFoundException:
            # 함수 생성
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.11',
                Role=f'arn:aws:iam::{ACCOUNT_ID}:role/LambdaExecutionRole-Team2',
                Handler='index.handler',
                Code={'ZipFile': zip_content},
                Timeout=60,
                MemorySize=256,
                Environment={
                    'Variables': {
                        'AWS_REGION': REGION
                    }
                },
                Tags={
                    'Team': 'Team2',
                    'Project': 'HR-Resource-Optimization'
                }
            )
            print(f"✓ Lambda 함수 생성: {function_name}")
        
        # DynamoDB Stream 연결 (수동 설정 필요)
        print("\n⚠ DynamoDB Stream 연결은 수동으로 설정해야 합니다:")
        print("  1. DynamoDB Console → Projects 테이블 → Exports and streams")
        print("  2. DynamoDB stream details → Enable")
        print("  3. Lambda Console → DomainPortfolioUpdater → Add trigger")
        print("  4. Select DynamoDB → Projects 테이블 선택")
        print("  5. Employees 테이블도 동일하게 설정")
        
        # 임시 파일 삭제
        zip_path.unlink()
        
        return True
        
    except Exception as e:
        print(f"✗ DomainPortfolioUpdater 설정 실패: {str(e)}")
        return False

def enable_dynamodb_streams():
    """DynamoDB Stream 활성화"""
    print("\n" + "=" * 60)
    print("DynamoDB Stream 활성화")
    print("=" * 60)
    
    tables = ['Projects', 'Employees']
    
    for table_name in tables:
        try:
            response = dynamodb.update_table(
                TableName=table_name,
                StreamSpecification={
                    'StreamEnabled': True,
                    'StreamViewType': 'NEW_AND_OLD_IMAGES'
                }
            )
            print(f"✓ {table_name} 테이블 Stream 활성화")
        except Exception as e:
            if 'ResourceInUseException' in str(e):
                print(f"✓ {table_name} 테이블 Stream 이미 활성화됨")
            else:
                print(f"✗ {table_name} 테이블 Stream 활성화 실패: {str(e)}")

def test_pipeline():
    """파이프라인 테스트"""
    print("\n" + "=" * 60)
    print("파이프라인 테스트")
    print("=" * 60)
    
    # TechTrendCollector 테스트
    print("\n[TechTrendCollector 테스트]")
    try:
        response = lambda_client.invoke(
            FunctionName='TechTrendCollector',
            InvocationType='RequestResponse',
            Payload=json.dumps({})
        )
        
        result = json.loads(response['Payload'].read())
        print(f"✓ TechTrendCollector 실행 성공")
        print(f"  응답: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"✗ TechTrendCollector 테스트 실패: {str(e)}")
    
    print("\n⚠ DomainPortfolioUpdater는 DynamoDB Stream 이벤트로 자동 실행됩니다.")

def main():
    print("=" * 60)
    print("도메인 데이터 관리 파이프라인 설정")
    print("=" * 60)
    
    # 1. TechTrendCollector 설정
    tech_trend_success = setup_tech_trend_collector()
    
    # 2. DomainPortfolioUpdater 설정
    portfolio_success = setup_domain_portfolio_updater()
    
    # 3. DynamoDB Stream 활성화
    enable_dynamodb_streams()
    
    # 4. 테스트
    if tech_trend_success:
        test_pipeline()
    
    print("\n" + "=" * 60)
    print("설정 완료!")
    print("=" * 60)
    
    print("\n다음 단계:")
    print("1. DynamoDB Stream을 Lambda 함수에 연결 (수동)")
    print("2. 프론트엔드 UI 배포")
    print("3. 도메인 분석 API 테스트")
    print("\n자세한 내용은 DOMAIN_PIPELINE_GUIDE.md를 참조하세요.")

if __name__ == '__main__':
    main()
