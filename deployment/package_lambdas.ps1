# Lambda 함수 패키징 스크립트

Write-Host "Lambda 함수 패키징 시작..." -ForegroundColor Green

$lambdaFunctions = @(
    "resume_parser",
    "affinity_calculator",
    "quantitative_analysis",
    "qualitative_analysis",
    "recommendation_engine",
    "domain_analysis",
    "tech_trend_collector",
    "vector_embedding"
)

foreach ($func in $lambdaFunctions) {
    Write-Host "패키징 중: $func" -ForegroundColor Yellow
    
    $sourcePath = "lambda_functions\$func"
    $zipPath = "lambda_functions\$func.zip"
    
    if (Test-Path $zipPath) {
        Remove-Item $zipPath
    }
    
    Compress-Archive -Path "$sourcePath\*" -DestinationPath $zipPath
    
    Write-Host "✓ 완료: $zipPath" -ForegroundColor Green
}

Write-Host "`n모든 Lambda 함수 패키징 완료!" -ForegroundColor Green
