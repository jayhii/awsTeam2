"""
us-east-2 리전에서 사용 가능한 Bedrock 모델 확인
"""

import boto3

bedrock_client = boto3.client('bedrock', region_name='us-east-2')

print("=" * 80)
print("us-east-2 리전의 사용 가능한 Bedrock 모델")
print("=" * 80)

try:
    response = bedrock_client.list_foundation_models()
    
    claude_models = []
    for model in response.get('modelSummaries', []):
        model_id = model.get('modelId', '')
        if 'claude' in model_id.lower():
            claude_models.append({
                'modelId': model_id,
                'modelName': model.get('modelName', ''),
                'providerName': model.get('providerName', ''),
                'inputModalities': model.get('inputModalities', []),
                'outputModalities': model.get('outputModalities', [])
            })
    
    print(f"\n[Claude 모델 목록 ({len(claude_models)}개)]")
    for model in claude_models:
        print(f"\n모델 ID: {model['modelId']}")
        print(f"  이름: {model['modelName']}")
        print(f"  제공자: {model['providerName']}")
        print(f"  입력: {', '.join(model['inputModalities'])}")
        print(f"  출력: {', '.join(model['outputModalities'])}")
    
    print("\n" + "=" * 80)

except Exception as e:
    print(f"\n✗ 오류: {str(e)}")
