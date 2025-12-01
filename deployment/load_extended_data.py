import json
import boto3
from decimal import Decimal
from botocore.exceptions import ClientError

def convert_to_decimal(obj):
    """DynamoDB용 float를 Decimal로 변환"""
    if isinstance(obj, list):
        return [convert_to_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    return obj

def batch_write_items(table, items, batch_size=25):
    """배치로 아이템 쓰기 (DynamoDB 제한: 25개)"""
    total = len(items)
    success_count = 0
    
    for i in range(0, total, batch_size):
        batch = items[i:i + batch_size]
        
        try:
            with table.batch_writer() as writer:
                for item in batch:
                    writer.put_item(Item=convert_to_decimal(item))
                    success_count += 1
            
            print(f"  진행: {success_count}/{total} ({success_count*100//total}%)")
        
        except ClientError as e:
            print(f"  ✗ 배치 쓰기 실패: {e.response['Error']['Message']}")
            # 실패한 경우 개별 아이템으로 재시도
            for item in batch:
                try:
                    table.put_item(Item=convert_to_decimal(item))
                    success_count += 1
                except ClientError as e2:
                    print(f"  ✗ 아이템 쓰기 실패: {e2.response['Error']['Message']}")
    
    return success_count

# AWS 리전 설정
REGION = 'us-east-2'
dynamodb = boto3.resource('dynamodb', region_name=REGION)

print("=" * 60)
print("HR Resource Optimization - 확장 데이터 로드")
print("=" * 60)
print("직원 300명 + 메신저 로그 2000개 + 프로젝트 데이터")

# 1. 직원 데이터 로드
print("\n[1/3] 직원 데이터 로드 중...")
try:
    with open('test_data/employees_extended.json', 'r', encoding='utf-8') as f:
        employees = json.load(f)
    
    print(f"  파일에서 {len(employees)}명의 직원 데이터 로드됨")
    
    table = dynamodb.Table('Employees')
    success = batch_write_items(table, employees)
    
    print(f"  ✓ {success}명의 직원 데이터 DynamoDB에 저장 완료!")

except FileNotFoundError:
    print("  ✗ employees_extended.json 파일을 찾을 수 없습니다.")
except ClientError as e:
    print(f"  ✗ DynamoDB 오류: {e.response['Error']['Message']}")
    print("  힌트: 'Employees' 테이블이 존재하는지 확인하세요.")
except Exception as e:
    print(f"  ✗ 예상치 못한 오류: {str(e)}")

# 2. 메신저 로그 로드
print("\n[2/3] 메신저 로그 데이터 로드 중...")
try:
    with open('test_data/messenger_logs_anonymized.json', 'r', encoding='utf-8') as f:
        logs = json.load(f)
    
    print(f"  파일에서 {len(logs)}개의 메신저 로그 로드됨")
    
    table = dynamodb.Table('MessengerLogs')
    success = batch_write_items(table, logs)
    
    print(f"  ✓ {success}개의 메신저 로그 DynamoDB에 저장 완료!")

except FileNotFoundError:
    print("  ✗ messenger_logs_anonymized.json 파일을 찾을 수 없습니다.")
except ClientError as e:
    print(f"  ✗ DynamoDB 오류: {e.response['Error']['Message']}")
    print("  힌트: 'MessengerLogs' 테이블이 존재하는지 확인하세요.")
except Exception as e:
    print(f"  ✗ 예상치 못한 오류: {str(e)}")

# 3. 프로젝트 데이터 로드
print("\n[3/3] 프로젝트 데이터 로드 중...")
try:
    with open('test_data/projects_data.json', 'r', encoding='utf-8') as f:
        projects = json.load(f)
    
    print(f"  파일에서 {len(projects)}개의 프로젝트 데이터 로드됨")
    
    table = dynamodb.Table('Projects')
    success = batch_write_items(table, projects)
    
    print(f"  ✓ {success}개의 프로젝트 데이터 DynamoDB에 저장 완료!")

except FileNotFoundError:
    print("  ✗ projects_data.json 파일을 찾을 수 없습니다.")
    print("  힌트: 먼저 'python test_data/generate_project_data.py'를 실행하세요.")
except ClientError as e:
    print(f"  ✗ DynamoDB 오류: {e.response['Error']['Message']}")
    print("  힌트: 'Projects' 테이블이 존재하는지 확인하세요.")
except Exception as e:
    print(f"  ✗ 예상치 못한 오류: {str(e)}")

print("\n" + "=" * 60)
print("데이터 로드 완료!")
print("=" * 60)
print("\n다음 단계:")
print("1. DynamoDB 콘솔에서 데이터 확인")
print("2. OpenSearch에 벡터 임베딩 생성 (자동 트리거)")
print("3. API 테스트 실행")
