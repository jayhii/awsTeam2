# S3 버킷 목록 확인
Write-Host "S3 버킷 목록 조회 중..." -ForegroundColor Yellow
aws s3 ls | Select-String "hr"
