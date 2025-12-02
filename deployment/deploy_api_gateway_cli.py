import boto3

api = boto3.client('apigateway', region_name='us-east-2')

print("=" * 70)
print("API Gateway 배포")
print("=" * 70)

api_id = 'ifeniowvpb'

print(f"\nAPI Gateway ID: {api_id}")
print(f"배포 중...")

try:
    result = api.create_deployment(
        restApiId=api_id,
        stageName='prod',
        description='Deploy updated ProjectsList Lambda with team member names'
    )
    
    print(f"✓ 배포 완료!")
    print(f"  배포 ID: {result['id']}")
    print(f"  생성 시간: {result.get('createdDate')}")
    
    print(f"\nAPI 엔드포인트:")
    print(f"  https://{api_id}.execute-api.us-east-2.amazonaws.com/prod/projects")
    
    print(f"\n⏳ 배포가 완전히 적용되려면 10-15초 정도 소요됩니다.")
    print(f"\n다음 단계:")
    print(f"  1. 15초 대기")
    print(f"  2. 프론트엔드 새로고침 (Ctrl+F5)")
    print(f"  3. 프로젝트 관리 페이지 확인")
    
except Exception as e:
    print(f"✗ 배포 실패: {str(e)}")
    print(f"\nAWS Console에서 수동 배포를 시도하세요:")
    print(f"  1. API Gateway → HR-Resource-Optimization-API")
    print(f"  2. Actions → Deploy API")
    print(f"  3. Stage: prod")

print("\n" + "=" * 70)
