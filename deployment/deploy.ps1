# HR Resource Optimization System - 원클릭 배포 스크립트 (Windows PowerShell)
# 사용법: .\deploy.ps1 -AccessKey "YOUR_ACCESS_KEY" -SecretKey "YOUR_SECRET_KEY"

param(
    [Parameter(Mandatory=$true)]
    [string]$AccessKey,
    
    [Parameter(Mandatory=$true)]
    [string]$SecretKey,
    
    [string]$Region = "us-east-2"
)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "HR Resource Optimization System 배포 시작" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# AWS 자격 증명 설정
$env:AWS_ACCESS_KEY_ID = $AccessKey
$env:AWS_SECRET_ACCESS_KEY = $SecretKey
$env:AWS_DEFAULT_REGION = $Region

Write-Host "✓ AWS 자격 증명 설정 완료" -ForegroundColor Green

# AWS CLI 설치 확인
try {
    aws --version | Out-Null
    Write-Host "✓ AWS CLI 확인 완료" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI가 설치되어 있지 않습니다." -ForegroundColor Red
    Write-Host "설치 방법: https://aws.amazon.com/cli/" -ForegroundColor Yellow
    exit 1
}

# Terraform 설치 확인
try {
    terraform version | Out-Null
    Write-Host "✓ Terraform 확인 완료" -ForegroundColor Green
} catch {
    Write-Host "❌ Terraform이 설치되어 있지 않습니다." -ForegroundColor Red
    Write-Host "설치 방법: https://www.terraform.io/downloads" -ForegroundColor Yellow
    exit 1
}

# Python 설치 확인
try {
    python --version | Out-Null
    Write-Host "✓ Python 확인 완료" -ForegroundColor Green
} catch {
    Write-Host "❌ Python 3가 설치되어 있지 않습니다." -ForegroundColor Red
    exit 1
}

# AWS 계정 확인
Write-Host "AWS 계정 확인 중..." -ForegroundColor Yellow
try {
    aws sts get-caller-identity
    Write-Host "✓ AWS 계정 확인 완료" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS 자격 증명이 올바르지 않습니다." -ForegroundColor Red
    exit 1
}

# Bedrock 모델 액세스 확인
Write-Host ""
Write-Host "Bedrock 모델 액세스를 활성화해야 합니다." -ForegroundColor Yellow
Write-Host "AWS Console > Bedrock > Model access에서 다음 모델을 활성화하세요:" -ForegroundColor Yellow
Write-Host "  - Claude v2" -ForegroundColor Yellow
Write-Host "  - Titan Embeddings" -ForegroundColor Yellow
$response = Read-Host "활성화를 완료했습니까? (y/n)"
if ($response -ne "y" -and $response -ne "Y") {
    Write-Host "Bedrock 모델 액세스를 활성화한 후 다시 실행하세요." -ForegroundColor Yellow
    exit 1
}

# Lambda 함수 패키징
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Step 1: Lambda 함수 패키징" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Set-Location scripts
try {
    python package_lambdas.py
    Write-Host "✓ Lambda 함수 패키징 완료" -ForegroundColor Green
} catch {
    Write-Host "❌ Lambda 함수 패키징 실패" -ForegroundColor Red
    exit 1
}
Set-Location ..

# Terraform 초기화
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Step 2: Terraform 초기화" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Set-Location terraform
try {
    terraform init
    Write-Host "✓ Terraform 초기화 완료" -ForegroundColor Green
} catch {
    Write-Host "❌ Terraform 초기화 실패" -ForegroundColor Red
    exit 1
}

# Terraform 변수 파일 생성
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Step 3: Terraform 변수 설정" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
@"
aws_region       = "$Region"
environment      = "prod"
project_name     = "hr-resource-optimization"
external_api_key = ""
"@ | Out-File -FilePath terraform.tfvars -Encoding UTF8
Write-Host "✓ Terraform 변수 설정 완료" -ForegroundColor Green

# Terraform 계획 확인
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Step 4: 배포 계획 확인" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
try {
    terraform plan
} catch {
    Write-Host "❌ Terraform 계획 생성 실패" -ForegroundColor Red
    exit 1
}

$response = Read-Host "배포를 계속하시겠습니까? (y/n)"
if ($response -ne "y" -and $response -ne "Y") {
    Write-Host "배포가 취소되었습니다." -ForegroundColor Yellow
    exit 0
}

# Terraform 배포
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Step 5: 인프라 배포 (15-20분 소요)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
try {
    terraform apply -auto-approve
    Write-Host "✓ 인프라 배포 완료" -ForegroundColor Green
} catch {
    Write-Host "❌ Terraform 배포 실패" -ForegroundColor Red
    exit 1
}

# 출력 값 저장
$ApiGatewayUrl = terraform output -raw api_gateway_url
$OpenSearchEndpoint = terraform output -raw opensearch_endpoint

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "배포 완료!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "API Gateway URL: $ApiGatewayUrl" -ForegroundColor Yellow
Write-Host "OpenSearch Endpoint: $OpenSearchEndpoint" -ForegroundColor Yellow
Write-Host ""

# 테스트 데이터 로드
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Step 6: 테스트 데이터 로드" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Set-Location ..\scripts
try {
    python load_test_data.py
    Write-Host "✓ 테스트 데이터 로드 완료" -ForegroundColor Green
} catch {
    Write-Host "⚠️  테스트 데이터 로드 실패 (수동으로 실행하세요)" -ForegroundColor Yellow
}

# OpenSearch 인덱스 생성
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Step 7: OpenSearch 인덱스 생성" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
try {
    python create_opensearch_indices.py
    Write-Host "✓ OpenSearch 인덱스 생성 완료" -ForegroundColor Green
} catch {
    Write-Host "⚠️  OpenSearch 인덱스 생성 실패 (수동으로 실행하세요)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "배포 완료 요약" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✓ DynamoDB 테이블 6개 생성" -ForegroundColor Green
Write-Host "✓ S3 버킷 4개 생성" -ForegroundColor Green
Write-Host "✓ Lambda 함수 8개 배포" -ForegroundColor Green
Write-Host "✓ OpenSearch 도메인 생성" -ForegroundColor Green
Write-Host "✓ API Gateway 설정" -ForegroundColor Green
Write-Host "✓ IAM 역할 및 정책 생성" -ForegroundColor Green
Write-Host ""
Write-Host "다음 단계:" -ForegroundColor Yellow
Write-Host "1. API 엔드포인트 테스트" -ForegroundColor Yellow
Write-Host "2. 프론트엔드 배포" -ForegroundColor Yellow
Write-Host "3. 모니터링 설정" -ForegroundColor Yellow
Write-Host ""
Write-Host "API Gateway URL: $ApiGatewayUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "배포 가이드: awsTeam2\deployment\DEPLOYMENT_GUIDE.md" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
