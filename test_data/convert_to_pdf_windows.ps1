# Windows에서 HTML을 PDF로 변환하는 PowerShell 스크립트
# Chrome 브라우저를 사용하여 자동으로 PDF 생성

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "HTML을 PDF로 변환" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Chrome 실행 파일 경로 찾기
$chromePaths = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)

$chromePath = $null
foreach ($path in $chromePaths) {
    if (Test-Path $path) {
        $chromePath = $path
        break
    }
}

if ($null -eq $chromePath) {
    Write-Host "Chrome 브라우저를 찾을 수 없습니다." -ForegroundColor Red
    Write-Host ""
    Write-Host "다음 방법 중 하나를 선택하세요:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "방법 1: 브라우저에서 수동 변환 (권장)" -ForegroundColor Green
    Write-Host "  1. HTML 파일을 더블클릭하여 브라우저에서 열기"
    Write-Host "  2. Ctrl+P (인쇄)"
    Write-Host "  3. 대상을 'PDF로 저장'으로 선택"
    Write-Host "  4. 저장 위치를 현재 폴더로 선택"
    Write-Host "  5. 파일명을 'sample_resume_choi_jungwoo.pdf'로 입력"
    Write-Host "  6. 저장"
    Write-Host ""
    Write-Host "방법 2: Microsoft Edge 사용" -ForegroundColor Green
    Write-Host "  Edge 브라우저로 HTML 파일을 열고 위와 동일하게 진행"
    Write-Host ""
    Write-Host "방법 3: 온라인 변환 도구" -ForegroundColor Green
    Write-Host "  - https://www.html2pdf.com/"
    Write-Host "  - https://pdfcrowd.com/"
    Write-Host ""
    exit 1
}

Write-Host "Chrome 브라우저를 찾았습니다: $chromePath" -ForegroundColor Green
Write-Host ""

# 현재 디렉토리
$currentDir = Get-Location

# 변환할 HTML 파일 목록
$htmlFiles = @(
    "sample_resume_choi_jungwoo.html",
    "sample_resume_kim_soyeon.html"
)

Write-Host "PDF 변환을 시작합니다..." -ForegroundColor Yellow
Write-Host ""

foreach ($htmlFile in $htmlFiles) {
    $htmlPath = Join-Path $currentDir $htmlFile
    $pdfFile = $htmlFile -replace '\.html$', '.pdf'
    $pdfPath = Join-Path $currentDir $pdfFile
    
    if (Test-Path $htmlPath) {
        Write-Host "변환 중: $htmlFile -> $pdfFile" -ForegroundColor Cyan
        
        # Chrome의 headless 모드로 PDF 생성
        $arguments = @(
            "--headless",
            "--disable-gpu",
            "--print-to-pdf=`"$pdfPath`"",
            "--no-margins",
            "`"$htmlPath`""
        )
        
        try {
            Start-Process -FilePath $chromePath -ArgumentList $arguments -Wait -NoNewWindow
            
            if (Test-Path $pdfPath) {
                Write-Host "✓ 완료: $pdfFile" -ForegroundColor Green
            } else {
                Write-Host "✗ 실패: PDF 파일이 생성되지 않았습니다" -ForegroundColor Red
            }
        } catch {
            Write-Host "✗ 오류: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "✗ 파일을 찾을 수 없음: $htmlFile" -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "변환 완료!" -ForegroundColor Green
Write-Host ""
Write-Host "생성된 PDF 파일:" -ForegroundColor Yellow
foreach ($htmlFile in $htmlFiles) {
    $pdfFile = $htmlFile -replace '\.html$', '.pdf'
    $pdfPath = Join-Path $currentDir $pdfFile
    if (Test-Path $pdfPath) {
        $fileSize = (Get-Item $pdfPath).Length / 1KB
        Write-Host "  ✓ $pdfFile ($([math]::Round($fileSize, 2)) KB)" -ForegroundColor Green
    }
}
Write-Host ""
Write-Host "이제 프론트엔드에서 이 PDF 파일들을 업로드할 수 있습니다!" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
