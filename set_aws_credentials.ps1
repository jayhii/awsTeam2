# AWS 자격 증명 설정 스크립트
# 사용법: 이 파일을 편집하여 실제 키 값을 입력한 후 실행하세요

Write-Host "AWS 자격 증명 설정 중..." -ForegroundColor Green

# TODO: 아래 값을 실제 AWS 자격 증명으로 변경하세요
$env:AWS_ACCESS_KEY_ID="ABSKQmVkcm9ja0FQSUtleS02a3g1LWF0LTQxMjY3NzU3NjEzNjpJRnRaMWNkamdXdjZJV3VtbTgyS2Nxbm5jVFZFVUQwN1IyZzVtc2FBaGQreWNhaW5HeEcwY2g2bGoyVT0="
$env:AWS_SECRET_ACCESS_KEY="ABSKanVuZ2poN0Bhc2lhbmFpZHQuY29tLWF0LTQxMjY3NzU3NjEzNjp2M1VqYW5TK2QvbkpYbG54Q1FndlF4Vm50Q2MrVU9QRnlWSisxbktQVit1akU3Mi9xWGZLejFNa3plUT0="
$env:AWS_DEFAULT_REGION="us-east-2"

# 설정 확인
Write-Host "`n환경 변수 설정 완료:" -ForegroundColor Cyan
Write-Host "  AWS_ACCESS_KEY_ID: $($env:AWS_ACCESS_KEY_ID.Substring(0, [Math]::Min(10, $env:AWS_ACCESS_KEY_ID.Length)))..." -ForegroundColor Yellow
Write-Host "  AWS_DEFAULT_REGION: $env:AWS_DEFAULT_REGION" -ForegroundColor Yellow

Write-Host "`n이제 데이터 로드를 실행할 수 있습니다:" -ForegroundColor Green
Write-Host "  python deployment/load_extended_data.py" -ForegroundColor White
