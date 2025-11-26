#!/bin/bash

# HR Resource Optimization System - 원클릭 배포 스크립트
# 사용법: ./deploy.sh YOUR_ACCESS_KEY YOUR_SECRET_KEY

set -e

echo "========================================="
echo "HR Resource Optimization System 배포 시작"
echo "========================================="

# 인자 확인
if [ "$#" -ne 2 ]; then
    echo "사용법: $0 AWS_ACCESS_KEY AWS_SECRET_KEY"
    exit 1
fi

AWS_ACCESS_KEY=$1
AWS_SECRET_KEY=$2
AWS_REGION="us-east-2"

# AWS 자격 증명 설정
export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_KEY
export AWS_DEFAULT_REGION=$AWS_REGION

echo "✓ AWS 자격 증명 설정 완료"

# AWS CLI 설치 확인
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI가 설치되어 있지 않습니다."
    echo "설치 방법: https://aws.amazon.com/cli/"
    exit 1
fi
echo "✓ AWS CLI 확인 완료"

# Terraform 설치 확인
if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform이 설치되어 있지 않습니다."
    echo "설치 방법: https://www.terraform.io/downloads"
    exit 1
fi
echo "✓ Terraform 확인 완료"

# Python 설치 확인
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3가 설치되어 있지 않습니다."
    exit 1
fi
echo "✓ Python 확인 완료"

# AWS 계정 확인
echo "AWS 계정 확인 중..."
aws sts get-caller-identity
if [ $? -ne 0 ]; then
    echo "❌ AWS 자격 증명이 올바르지 않습니다."
    exit 1
fi
echo "✓ AWS 계정 확인 완료"

# Bedrock 모델 액세스 확인
echo "Bedrock 모델 액세스를 활성화해야 합니다."
echo "AWS Console > Bedrock > Model access에서 다음 모델을 활성화하세요:"
echo "  - Claude v2"
echo "  - Titan Embeddings"
read -p "활성화를 완료했습니까? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Bedrock 모델 액세스를 활성화한 후 다시 실행하세요."
    exit 1
fi

# Lambda 함수 패키징
echo ""
echo "========================================="
echo "Step 1: Lambda 함수 패키징"
echo "========================================="
cd scripts
python3 package_lambdas.py
if [ $? -ne 0 ]; then
    echo "❌ Lambda 함수 패키징 실패"
    exit 1
fi
echo "✓ Lambda 함수 패키징 완료"
cd ..

# Terraform 초기화
echo ""
echo "========================================="
echo "Step 2: Terraform 초기화"
echo "========================================="
cd terraform
terraform init
if [ $? -ne 0 ]; then
    echo "❌ Terraform 초기화 실패"
    exit 1
fi
echo "✓ Terraform 초기화 완료"

# Terraform 변수 파일 생성
echo ""
echo "========================================="
echo "Step 3: Terraform 변수 설정"
echo "========================================="
cat > terraform.tfvars <<EOF
aws_region       = "$AWS_REGION"
environment      = "prod"
project_name     = "hr-resource-optimization"
external_api_key = ""
EOF
echo "✓ Terraform 변수 설정 완료"

# Terraform 계획 확인
echo ""
echo "========================================="
echo "Step 4: 배포 계획 확인"
echo "========================================="
terraform plan
if [ $? -ne 0 ]; then
    echo "❌ Terraform 계획 생성 실패"
    exit 1
fi

read -p "배포를 계속하시겠습니까? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "배포가 취소되었습니다."
    exit 0
fi

# Terraform 배포
echo ""
echo "========================================="
echo "Step 5: 인프라 배포 (15-20분 소요)"
echo "========================================="
terraform apply -auto-approve
if [ $? -ne 0 ]; then
    echo "❌ Terraform 배포 실패"
    exit 1
fi
echo "✓ 인프라 배포 완료"

# 출력 값 저장
API_GATEWAY_URL=$(terraform output -raw api_gateway_url)
OPENSEARCH_ENDPOINT=$(terraform output -raw opensearch_endpoint)

echo ""
echo "========================================="
echo "배포 완료!"
echo "========================================="
echo "API Gateway URL: $API_GATEWAY_URL"
echo "OpenSearch Endpoint: $OPENSEARCH_ENDPOINT"
echo ""

# 테스트 데이터 로드
echo "========================================="
echo "Step 6: 테스트 데이터 로드"
echo "========================================="
cd ../scripts
python3 load_test_data.py
if [ $? -ne 0 ]; then
    echo "⚠️  테스트 데이터 로드 실패 (수동으로 실행하세요)"
else
    echo "✓ 테스트 데이터 로드 완료"
fi

# OpenSearch 인덱스 생성
echo ""
echo "========================================="
echo "Step 7: OpenSearch 인덱스 생성"
echo "========================================="
python3 create_opensearch_indices.py
if [ $? -ne 0 ]; then
    echo "⚠️  OpenSearch 인덱스 생성 실패 (수동으로 실행하세요)"
else
    echo "✓ OpenSearch 인덱스 생성 완료"
fi

echo ""
echo "========================================="
echo "배포 완료 요약"
echo "========================================="
echo "✓ DynamoDB 테이블 6개 생성"
echo "✓ S3 버킷 4개 생성"
echo "✓ Lambda 함수 8개 배포"
echo "✓ OpenSearch 도메인 생성"
echo "✓ API Gateway 설정"
echo "✓ IAM 역할 및 정책 생성"
echo ""
echo "다음 단계:"
echo "1. API 엔드포인트 테스트"
echo "2. 프론트엔드 배포"
echo "3. 모니터링 설정"
echo ""
echo "API Gateway URL: $API_GATEWAY_URL"
echo ""
echo "배포 가이드: awsTeam2/deployment/DEPLOYMENT_GUIDE.md"
echo "========================================="
