# HR Resource Optimization System - 모니터링 설정 스크립트 (PowerShell)
# 이 스크립트는 CloudWatch 대시보드와 알람을 확인하고 SNS 구독을 설정합니다.

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "HR Resource Optimization - 모니터링 설정" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Terraform 디렉토리로 이동
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$scriptPath\terraform"

# Terraform outputs 확인
Write-Host "1. CloudWatch 대시보드 확인 중..." -ForegroundColor Yellow

try {
    $dashboards = terraform output -json cloudwatch_dashboards 2>$null | ConvertFrom-Json
    
    if ($dashboards) {
        Write-Host "✓ 생성된 대시보드:" -ForegroundColor Green
        $dashboards.PSObject.Properties | ForEach-Object {
            Write-Host "  - $($_.Name): $($_.Value)" -ForegroundColor White
        }
        Write-Host ""
        Write-Host "AWS Console에서 확인:" -ForegroundColor White
        Write-Host "https://console.aws.amazon.com/cloudwatch/home?region=us-east-2#dashboards:" -ForegroundColor Cyan
    }
} catch {
    Write-Host "✗ 대시보드를 찾을 수 없습니다. Terraform apply를 먼저 실행하세요." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "2. SNS Topic 확인 중..." -ForegroundColor Yellow

try {
    $snsTopicArn = terraform output -raw sns_topic_arn 2>$null
    
    if ($snsTopicArn) {
        Write-Host "✓ SNS Topic ARN: $snsTopicArn" -ForegroundColor Green
        
        # 구독 목록 확인
        Write-Host ""
        Write-Host "3. 현재 SNS 구독 확인 중..." -ForegroundColor Yellow
        
        $subscriptions = aws sns list-subscriptions-by-topic --topic-arn $snsTopicArn --query 'Subscriptions[*].[Protocol,Endpoint,SubscriptionArn]' --output table 2>$null
        
        if ($subscriptions) {
            Write-Host $subscriptions -ForegroundColor White
        } else {
            Write-Host "  현재 구독이 없습니다." -ForegroundColor Gray
        }
        
        # 이메일 구독 추가 옵션
        Write-Host ""
        $addEmail = Read-Host "이메일 알림을 추가하시겠습니까? (y/n)"
        
        if ($addEmail -eq 'y' -or $addEmail -eq 'Y') {
            $email = Read-Host "이메일 주소를 입력하세요"
            
            if ($email) {
                Write-Host "이메일 구독 추가 중..." -ForegroundColor Yellow
                aws sns subscribe `
                    --topic-arn $snsTopicArn `
                    --protocol email `
                    --notification-endpoint $email
                
                Write-Host "✓ 구독 요청이 전송되었습니다." -ForegroundColor Green
                Write-Host "  $email 로 전송된 확인 이메일의 링크를 클릭하세요." -ForegroundColor White
            }
        }
    }
} catch {
    Write-Host "✗ SNS Topic을 찾을 수 없습니다." -ForegroundColor Red
}

Write-Host ""
Write-Host "4. CloudWatch 알람 확인 중..." -ForegroundColor Yellow

try {
    $alarms = aws cloudwatch describe-alarms --alarm-name-prefix "lambda-errors" --query 'MetricAlarms[*].[AlarmName,StateValue]' --output table 2>$null
    
    if ($alarms) {
        Write-Host $alarms -ForegroundColor White
    } else {
        Write-Host "  알람을 찾을 수 없습니다." -ForegroundColor Gray
    }
} catch {
    Write-Host "  알람 조회 중 오류가 발생했습니다." -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "모니터링 설정 완료" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "다음 단계:" -ForegroundColor Yellow
Write-Host "1. AWS Console에서 CloudWatch 대시보드 확인" -ForegroundColor White
Write-Host "2. 이메일 구독 확인 링크 클릭 (구독 추가한 경우)" -ForegroundColor White
Write-Host "3. 알람 테스트 수행" -ForegroundColor White
Write-Host ""
Write-Host "대시보드 URL:" -ForegroundColor Yellow
Write-Host "https://console.aws.amazon.com/cloudwatch/home?region=us-east-2#dashboards:" -ForegroundColor Cyan
Write-Host ""
Write-Host "알람 URL:" -ForegroundColor Yellow
Write-Host "https://console.aws.amazon.com/cloudwatch/home?region=us-east-2#alarmsV2:" -ForegroundColor Cyan
Write-Host ""

