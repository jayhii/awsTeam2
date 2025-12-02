import boto3
import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
client = boto3.client('dynamodb', region_name='us-east-2')

print("=" * 80)
print("DynamoDB 테이블 현황 요약")
print("=" * 80)

# 먼저 실제 테이블 목록 확인
print("\n🔍 실제 테이블 목록 조회 중...")
try:
    response = client.list_tables()
    actual_tables = response.get('TableNames', [])
    print(f"   발견된 테이블: {len(actual_tables)}개")
    for table_name in actual_tables:
        print(f"   - {table_name}")
except Exception as e:
    print(f"❌ 테이블 목록 조회 실패: {str(e)}")
    actual_tables = []

tables = {table: None for table in actual_tables}

print("\n" + "=" * 80)

for table_name in tables.keys():
    try:
        table = dynamodb.Table(table_name)
        
        # 테이블 정보
        table_info = table.table_status
        item_count = table.item_count
        
        print(f"\n📊 테이블: {table_name}")
        print(f"   상태: {table_info}")
        print(f"   항목 수: {item_count:,}개")
        
        # 샘플 데이터 조회
        response = table.scan(Limit=3)
        items = response.get('Items', [])
        
        if items:
            print(f"   샘플 데이터 (최대 3개):")
            for i, item in enumerate(items, 1):
                print(f"\n   [{i}] {json.dumps(item, indent=6, cls=DecimalEncoder, ensure_ascii=False)[:500]}...")
        else:
            print("   ⚠️  데이터 없음")
            
    except Exception as e:
        print(f"\n❌ 테이블 {table_name} 조회 실패: {str(e)}")

print("\n" + "=" * 80)
print("요약 완료")
print("=" * 80)
