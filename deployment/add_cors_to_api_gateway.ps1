# API Gateway CORS 설정 스크립트
# 모든 리소스에 OPTIONS 메서드를 추가하여 CORS preflight 요청을 처리합니다

$API_ID = "xoc7x1m6p8"
$REGION = "us-east-2"

Write-Host "API Gateway CORS 설정 시작..." -ForegroundColor Green
Write-Host "API ID: $API_ID" -ForegroundColor Yellow

# 모든 리소스 가져오기
$resources = aws apigateway get-resources --rest-api-id $API_ID --region $REGION | ConvertFrom-Json

foreach ($resource in $resources.items) {
    $resourceId = $resource.id
    $path = $resource.path
    
    # 루트 경로는 건너뛰기
    if ($path -eq "/") {
        continue
    }
    
    Write-Host "`n처리 중: $path (ID: $resourceId)" -ForegroundColor Cyan
    
    # OPTIONS 메서드가 이미 있는지 확인
    $existingMethods = $resource.resourceMethods
    if ($existingMethods -and $existingMethods.PSObject.Properties.Name -contains "OPTIONS") {
        Write-Host "  OPTIONS 메서드가 이미 존재합니다. 건너뛰기..." -ForegroundColor Yellow
        continue
    }
    
    try {
        # OPTIONS 메서드 생성
        Write-Host "  OPTIONS 메서드 생성 중..." -ForegroundColor Gray
        aws apigateway put-method `
            --rest-api-id $API_ID `
            --resource-id $resourceId `
            --http-method OPTIONS `
            --authorization-type NONE `
            --region $REGION `
            --no-cli-pager | Out-Null
        
        # Mock 통합 설정
        Write-Host "  Mock 통합 설정 중..." -ForegroundColor Gray
        aws apigateway put-integration `
            --rest-api-id $API_ID `
            --resource-id $resourceId `
            --http-method OPTIONS `
            --type MOCK `
            --request-templates '{"application/json": "{\"statusCode\": 200}"}' `
            --region $REGION `
            --no-cli-pager | Out-Null
        
        # 메서드 응답 설정
        Write-Host "  메서드 응답 설정 중..." -ForegroundColor Gray
        aws apigateway put-method-response `
            --rest-api-id $API_ID `
            --resource-id $resourceId `
            --http-method OPTIONS `
            --status-code 200 `
            --response-parameters '{\"method.response.header.Access-Control-Allow-Headers\":true,\"method.response.header.Access-Control-Allow-Methods\":true,\"method.response.header.Access-Control-Allow-Origin\":true}' `
            --region $REGION `
            --no-cli-pager | Out-Null
        
        # 통합 응답 설정 (CORS 헤더 포함)
        Write-Host "  통합 응답 설정 중..." -ForegroundColor Gray
        aws apigateway put-integration-response `
            --rest-api-id $API_ID `
            --resource-id $resourceId `
            --http-method OPTIONS `
            --status-code 200 `
            --response-parameters '{\"method.response.header.Access-Control-Allow-Headers\":\"'"'"'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"'"'\",\"method.response.header.Access-Control-Allow-Methods\":\"'"'"'GET,POST,PUT,DELETE,OPTIONS'"'"'\",\"method.response.header.Access-Control-Allow-Origin\":\"'"'"'*'"'"'\"}' `
            --region $REGION `
            --no-cli-pager | Out-Null
        
        Write-Host "  ✓ 완료" -ForegroundColor Green
    }
    catch {
        Write-Host "  ✗ 오류: $_" -ForegroundColor Red
    }
}

# API 배포
Write-Host "`n`nAPI 배포 중..." -ForegroundColor Yellow
aws apigateway create-deployment `
    --rest-api-id $API_ID `
    --stage-name prod `
    --description "CORS 설정 업데이트" `
    --region $REGION `
    --no-cli-pager

Write-Host "`n✓ CORS 설정 완료!" -ForegroundColor Green
Write-Host "API URL: https://$API_ID.execute-api.$REGION.amazonaws.com/prod" -ForegroundColor Cyan
