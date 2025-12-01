# CORS 문제 빠른 해결 스크립트
# API Gateway 통합을 직접 생성

$API_ID = "xoc7x1m6p8"
$REGION = "us-east-2"
$ACCOUNT_ID = "412677576136"

Write-Host "API Gateway 통합 생성 시작..." -ForegroundColor Green

# DashboardMetrics 통합
Write-Host "`n1. /dashboard/metrics GET 통합 생성..." -ForegroundColor Cyan
$lambdaArn = "arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:DashboardMetrics"
$uri = "arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/${lambdaArn}/invocations"

aws apigateway put-integration `
    --rest-api-id $API_ID `
    --resource-id 8nheik `
    --http-method GET `
    --type AWS_PROXY `
    --integration-http-method POST `
    --uri $uri `
    --region $REGION `
    --no-cli-pager

aws lambda add-permission `
    --function-name DashboardMetrics `
    --statement-id AllowAPIGatewayInvokeDashboard `
    --action lambda:InvokeFunction `
    --principal apigateway.amazonaws.com `
    --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/*" `
    --region $REGION `
    --no-cli-pager 2>$null

Write-Host "✓ DashboardMetrics 통합 완료" -ForegroundColor Green

# API 배포
Write-Host "`n API 배포 중..." -ForegroundColor Yellow
aws apigateway create-deployment `
    --rest-api-id $API_ID `
    --stage-name prod `
    --description "CORS 수정 및 통합 추가" `
    --region $REGION `
    --no-cli-pager

Write-Host "`n✓ 완료! 브라우저를 새로고침하세요." -ForegroundColor Green
Write-Host "API URL: https://${API_ID}.execute-api.${REGION}.amazonaws.com/prod" -ForegroundColor Cyan
