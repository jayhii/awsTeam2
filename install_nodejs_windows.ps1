# Node.js 자동 설치 스크립트 (Windows)
# 관리자 권한으로 실행 필요

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Node.js 자동 설치 스크립트" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# 관리자 권한 확인
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "`n❌ 오류: 관리자 권한이 필요합니다." -ForegroundColor Red
    Write-Host "PowerShell을 우클릭하여 '관리자 권한으로 실행'을 선택하세요." -ForegroundColor Yellow
    exit 1
}

# 1. Node.js 설치 여부 확인
Write-Host "`n[1/4] Node.js 설치 확인 중..." -ForegroundColor Yellow

$nodeInstalled = Get-Command node -ErrorAction SilentlyContinue

if ($nodeInstalled) {
    $nodeVersion = node --version
    $npmVersion = npm --version
    Write-Host "✓ Node.js가 이미 설치되어 있습니다." -ForegroundColor Green
    Write-Host "  Node.js 버전: $nodeVersion" -ForegroundColor Cyan
    Write-Host "  npm 버전: $npmVersion" -ForegroundColor Cyan
    
    $continue = Read-Host "`n재설치하시겠습니까? (y/N)"
    if ($continue -ne 'y' -and $continue -ne 'Y') {
        Write-Host "`n설치를 취소합니다." -ForegroundColor Yellow
        exit 0
    }
}

# 2. Chocolatey 설치 확인
Write-Host "`n[2/4] Chocolatey 확인 중..." -ForegroundColor Yellow

$chocoInstalled = Get-Command choco -ErrorAction SilentlyContinue

if (-not $chocoInstalled) {
    Write-Host "Chocolatey가 설치되어 있지 않습니다. 설치 중..." -ForegroundColor Yellow
    
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        
        Write-Host "✓ Chocolatey 설치 완료" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Chocolatey 설치 실패: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "`n수동 설치 방법:" -ForegroundColor Yellow
        Write-Host "1. https://nodejs.org/ 접속" -ForegroundColor White
        Write-Host "2. LTS 버전 다운로드" -ForegroundColor White
        Write-Host "3. 설치 파일 실행" -ForegroundColor White
        exit 1
    }
}
else {
    Write-Host "✓ Chocolatey가 이미 설치되어 있습니다." -ForegroundColor Green
}

# 3. Node.js 설치
Write-Host "`n[3/4] Node.js 설치 중..." -ForegroundColor Yellow
Write-Host "이 작업은 몇 분 정도 걸릴 수 있습니다..." -ForegroundColor Cyan

try {
    choco install nodejs-lts -y
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Node.js 설치 완료" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️  설치 중 경고가 발생했지만 계속 진행합니다." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "❌ Node.js 설치 실패: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 4. 환경 변수 새로고침
Write-Host "`n[4/4] 환경 변수 새로고침 중..." -ForegroundColor Yellow

$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# 5. 설치 확인
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "설치 확인" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

Start-Sleep -Seconds 2

$nodeInstalled = Get-Command node -ErrorAction SilentlyContinue

if ($nodeInstalled) {
    $nodeVersion = node --version
    $npmVersion = npm --version
    
    Write-Host "`n✅ 설치 성공!" -ForegroundColor Green
    Write-Host "  Node.js 버전: $nodeVersion" -ForegroundColor Cyan
    Write-Host "  npm 버전: $npmVersion" -ForegroundColor Cyan
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "다음 단계" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "`n1. 새 PowerShell 창을 열어주세요 (현재 창 닫기)" -ForegroundColor White
    Write-Host "2. 프로젝트 디렉토리로 이동:" -ForegroundColor White
    Write-Host "   cd frontend" -ForegroundColor Cyan
    Write-Host "3. 의존성 설치:" -ForegroundColor White
    Write-Host "   npm install" -ForegroundColor Cyan
    Write-Host "4. 빌드:" -ForegroundColor White
    Write-Host "   npm run build" -ForegroundColor Cyan
    Write-Host "5. S3 배포:" -ForegroundColor White
    Write-Host "   cd .." -ForegroundColor Cyan
    Write-Host "   aws s3 sync frontend/build/ s3://hr-resource-optimization-frontend-hosting-prod --region us-east-2 --delete" -ForegroundColor Cyan
    
}
else {
    Write-Host "`n❌ 설치 확인 실패" -ForegroundColor Red
    Write-Host "PowerShell을 완전히 닫고 다시 열어주세요." -ForegroundColor Yellow
    Write-Host "그래도 안 되면 컴퓨터를 재부팅해주세요." -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "스크립트 완료" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
