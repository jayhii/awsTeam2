# 빠른 프론트엔드 배포 스크립트
# 수정된 타입 정의를 반영하여 재배포

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "프론트엔드 빌드 및 배포" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

$S3Bucket = "hr-resource-optimization-frontend-hosting-prod"
$AwsRegion = "us-east-2"

# 1. 프론트엔드 빌드
Write-Host "`n[1/3] 프론트엔드 빌드 중..." -ForegroundColor Yellow
Set-Location frontend

# Node.js 및 npm 확인
$npmVersion = npm --version 2>$null
if (-not $npmVersion) {
    Write-Host "오류: npm이 설치되어 있지 않습니다." -ForegroundColor Red
    Write-Host "Node.js를 설치해주세요: https://nodejs.org/" -ForegroundColor Yellow
    Set-Location ..
    exit 1
}

Write-Host "npm 버전: $npmVersion" -ForegroundColor Cyan

# 의존성 설치 (node_modules가 없는 경우)
if (-not (Test-Path "node_modules")) {
    Write-Host "의존성 설치 중..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "오류: npm install 실패" -ForegroundColor Red
        Set-Location ..
        exit 1
    }
}

# 빌드 실행
Write-Host "Vite 빌드 실행 중..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "오류: 빌드 실패" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Set-Location ..

# 2. 빌드 폴더 확인
Write-Host "`n[2/3] 빌드 결과 확인 중..." -ForegroundColor Yellow
if (-not (Test-Path "frontend/build")) {
    Write-Host "오류: frontend/build 폴더가 없습니다." -ForegroundColor Red
    exit 1
}

$buildFiles = Get-ChildItem -Path "frontend/build" -Recurse -File
Write-Host "빌드된 파일 수: $($buildFiles.Count)개" -ForegroundColor Cyan

# 3. S3에 배포
Write-Host "`n[3/3] S3에 업로드 중..." -ForegroundColor Yellow
Write-Host "버킷: s3://$S3Bucket" -ForegroundColor Cyan
Write-Host "리전: $AwsRegion" -ForegroundColor Cyan

# AWS CLI 확인
$awsVersion = aws --version 2>$null
if (-not $awsVersion) {
    Write-Host "오류: AWS CLI가 설치되어 있지 않습니다." -ForegroundColor Red
    exit 1
}

# 정적 파일 업로드 (캐시 적용)
Write-Host "`n정적 파일 업로드 중..." -ForegroundColor Yellow
aws s3 sync frontend/build/ s3://$S3Bucket `
    --region $AwsRegion `
    --delete `
    --cache-control "public, max-age=31536000" `
    --exclude "index.html" `
    --exclude "*.map"

if ($LASTEXITCODE -ne 0) {
    Write-Host "오류: S3 업로드 실패" -ForegroundColor Red
    exit 1
}

# index.html은 캐시 없이 업로드
Write-Host "`nindex.html 업로드 중..." -ForegroundColor Yellow
aws s3 cp frontend/build/index.html s3://$S3Bucket/index.html `
    --region $AwsRegion `
    --cache-control "no-cache, no-store, must-revalidate" `
    --content-type "text/html"

if ($LASTEXITCODE -ne 0) {
    Write-Host "오류: index.html 업로드 실패" -ForegroundColor Red
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "배포 완료!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`n✅ 수정 사항:" -ForegroundColor Green
Write-Host "  - TypeScript 타입 정의 수정 (api.ts)" -ForegroundColor White
Write-Host "  - 프로젝트 날짜 정보 표시 수정" -ForegroundColor White
Write-Host "  - 팀원 수 정확하게 표시" -ForegroundColor White
Write-Host "  - 'as any' 캐스팅 제거" -ForegroundColor White

Write-Host "`n🌐 URL:" -ForegroundColor Cyan
Write-Host "  http://$S3Bucket.s3-website.$AwsRegion.amazonaws.com" -ForegroundColor Yellow

Write-Host "`n📋 확인 사항:" -ForegroundColor Cyan
Write-Host "  1. 프로젝트 관리 페이지 접속" -ForegroundColor White
Write-Host "  2. 날짜가 '미정'이 아닌 실제 날짜로 표시되는지 확인" -ForegroundColor White
Write-Host "  3. 팀원 수가 정확하게 표시되는지 확인" -ForegroundColor White
Write-Host "  4. 브라우저 캐시 강제 새로고침 (Ctrl+Shift+R)" -ForegroundColor White

Write-Host "`n💡 팁: 변경사항이 안 보이면 브라우저 캐시를 지우세요!" -ForegroundColor Yellow
