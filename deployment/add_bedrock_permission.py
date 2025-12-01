"""
Lambda 실행 역할에 Bedrock 권한 추가
"""

import boto3
import json

iam_client = boto3.client('iam')
lambda_client = boto3.client('lambda', region_name='us-east-2')

print("=" * 80)
print("Lambda 실행 역할에 Bedrock 권한 추가")
print("=" * 80)

# Lambda 함수 정보 조회
function_name = 'EmployeeEvaluation'

try:
    response = lambda_client.get_function(FunctionName=function_name)
    role_arn = response['Configuration']['Role']
    role_name = role_arn.split('/')[-1]
    
    print(f"\n[Lambda 함수: {function_name}]")
    print(f"실행 역할: {role_name}")
    print(f"역할 ARN: {role_arn}")
    
    # Bedrock 권한 정책 생성
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                "Resource": [
                    "arn:aws:bedrock:*::foundation-model/*",
                    "arn:aws:bedrock:*:412677576136:inference-profile/*"
                ]
            }
        ]
    }
    
    policy_name = "BedrockInvokeModelPolicy"
    
    print(f"\n[정책 추가 중...]")
    print(f"정책 이름: {policy_name}")
    
    try:
        # 기존 정책 삭제 (있다면)
        iam_client.delete_role_policy(
            RoleName=role_name,
            PolicyName=policy_name
        )
        print("  - 기존 정책 삭제됨")
    except:
        pass
    
    # 새 정책 추가
    iam_client.put_role_policy(
        RoleName=role_name,
        PolicyName=policy_name,
        PolicyDocument=json.dumps(policy_document)
    )
    
    print(f"  ✓ Bedrock 권한 추가 완료")
    
    # 현재 역할의 모든 정책 확인
    print(f"\n[현재 역할의 인라인 정책 목록]")
    response = iam_client.list_role_policies(RoleName=role_name)
    for policy in response['PolicyNames']:
        print(f"  - {policy}")
    
    print("\n" + "=" * 80)
    print("✓ 권한 추가 완료!")
    print("=" * 80)

except Exception as e:
    print(f"\n✗ 오류: {str(e)}")
