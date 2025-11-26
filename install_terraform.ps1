# Terraform 설치 스크립트 (Windows)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Terraform 설치 시작" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Terraform 버전
$TerraformVersion = "1.7.0"
$TerraformZip = "terraform_${TerraformVersion}_windows_amd64.zip"
$TerraformUrl = "https://releases.hashicorp.com/terraform/${TerraformVersion}/${TerraformZip}"

# 임시 디렉토리
$TempDir = "$env:TEMP\terraform_install"
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

# 설치 디렉토리
$InstallDir = "C:\Program Files\Terraform"
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
    Write-Host "✓ 설치 디렉토리 생성: $InstallDir" -ForegroundColor Green
}

# Terraform 다운로드
Write-Host "Terraform $TerraformVersion 다운로드 중..." -ForegroundColor Yellow
$ZipPath = Join-Path $TempDir $TerraformZip

try {
    Invoke-WebRequest -Uri $TerraformUrl -OutFile $ZipPath
    Write-Host "✓ 다운로드 완료" -ForegroundColor Green
} catch {
    Write-Host "❌ 다운로드 실패: $_" -ForegroundColor Red
    exit 1
}

# 압축 해제
Write-Host "압축 해제 중..." -ForegroundColor Yellow
try {
    Expand-Archive -Path $ZipPath -DestinationPath $TempDir -Force
    Write-Host "✓ 압축 해제 완료" -ForegroundColor Green
} catch {
    Write-Host "❌ 압축 해제 실패: $_" -ForegroundColor Red
    exit 1
}

# Terraform 실행 파일 복사
Write-Host "Terraform 설치 중..." -ForegroundColor Yellow
try {
    Copy-Item -Path (Join-Path $TempDir "terraform.exe") -Destination $InstallDir -Force
    Write-Host "✓ Terraform 설치 완료: $InstallDir\terraform.exe" -ForegroundColor Green
} catch {
    Write-Host "❌ 설치 실패: $_" -ForegroundColor Red
    exit 1
}

# PATH 환경 변수에 추가
Write-Host "PATH 환경 변수 업데이트 중..." -ForegroundColor Yellow
$CurrentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
if ($CurrentPath -notlike "*$InstallDir*") {
    try {
        [Environment]::SetEnvironmentVariable(
            "Path",
            "$CurrentPath;$InstallDir",
            "Machine"
        )
        Write-Host "✓ PATH 환경 변수 업데이트 완료" -ForegroundColor Green
        Write-Host "⚠️  새 터미널을 열어야 terraform 명령을 사용할 수 있습니다." -ForegroundColor Yellow
    } catch {
        Write-Host "⚠️  PATH 업데이트 실패 (관리자 권한 필요)" -ForegroundColor Yellow
        Write-Host "수동으로 PATH에 추가하세요: $InstallDir" -ForegroundColor Yellow
    }
} else {
    Write-Host "✓ PATH에 이미 추가되어 있습니다." -ForegroundColor Green
}

# 현재 세션의 PATH 업데이트
$env:Path += ";$InstallDir"

# 임시 파일 정리
Write-Host "임시 파일 정리 중..." -ForegroundColor Yellow
Remove-Item -Path $TempDir -Recurse -Force
Write-Host "✓ 정리 완료" -ForegroundColor Green

# 설치 확인
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "설치 확인" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

try {
    & "$InstallDir\terraform.exe" version
    Write-Host ""
    Write-Host "✓ Terraform 설치 성공!" -ForegroundColor Green
    Write-Host ""
    Write-Host "사용 방법:" -ForegroundColor Yellow
    Write-Host "  terraform init    # 초기화" -ForegroundColor White
    Write-Host "  terraform plan    # 계획 확인" -ForegroundColor White
    Write-Host "  terraform apply   # 배포" -ForegroundColor White
    Write-Host ""
    Write-Host "⚠️  주의: 새 PowerShell 창을 열어야 'terraform' 명령을 직접 사용할 수 있습니다." -ForegroundColor Yellow
} catch {
    Write-Host "❌ 설치 확인 실패" -ForegroundColor Red
    exit 1
}

Write-Host "=========================================" -ForegroundColor Cyan
