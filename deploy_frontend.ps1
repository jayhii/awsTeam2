# 프론트엔드 배포 스크립트

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "프론트엔드 S3 배포 시작" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

$S3Bucket = "hr-resource-optimization-frontend-hosting-prod"
$AwsRegion = "us-east-2"

# 빌드 폴더 확인
if (-not (Test-Path "frontend/build")) {
    Write-Host "오류: frontend/build 폴더가 없습니다." -ForegroundColor Red
    Write-Host "먼저 'npm run build'를 실행하세요." -ForegroundColor Red
    exit 1
}

Write-Host "`nS3 버킷에 업로드 중..." -ForegroundColor Yellow
Write-Host "버킷: s3://$S3Bucket" -ForegroundColor Cyan
Write-Host "리전: $AwsRegion" -ForegroundColor Cyan

# 정적 파일 업로드 (캐시 적용)
Write-Host "`n정적 파일 업로드 중..." -ForegroundColor Yellow
aws s3 sync frontend/build/ s3://$S3Bucket `
    --region $AwsRegion `
    --delete `
    --cache-control "public, max-age=31536000" `
    --exclude "index.html"

# index.html은 캐시 없이 업로드
Write-Host "`nindex.html 업로드 중..." -ForegroundColor Yellow
aws s3 cp frontend/build/index.html s3://$S3Bucket/index.html `
    --region $AwsRegion `
    --cache-control "no-cache, no-store, must-revalidate" `
    --content-type "text/html"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "배포 완료!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nS3 URL: http://$S3Bucket.s3-website.$AwsRegion.amazonaws.com" -ForegroundColor Green
Write-Host "`n이력서 업로드 버튼이 추가되었습니다!" -ForegroundColor Green
