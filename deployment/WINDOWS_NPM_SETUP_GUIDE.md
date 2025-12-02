# Windows에서 npm 설치 및 프론트엔드 배포 가이드

## 🔍 현재 상황 확인

### npm 설치 여부 확인
```powershell
npm --version
node --version
```

오류가 나면 Node.js가 설치되어 있지 않은 것입니다.

## 📦 해결 방법

### 방법 1: Node.js 설치 (권장)

#### 1-1. Node.js 다운로드
1. https://nodejs.org/ 접속
2. **LTS 버전** 다운로드 (현재 20.x 버전)
3. 설치 파일 실행

#### 1-2. 설치 옵션
- ✅ "Automatically install the necessary tools" 체크
- ✅ 기본 경로 사용 (`C:\Program Files\nodejs\`)
- ✅ "Add to PATH" 체크 (자동으로 체크됨)

#### 1-3. 설치 확인
```powershell
# PowerShell 재시작 후
node --version
npm --version
```

예상 출력:
```
v20.11.0
10.2.4
```

#### 1-4. 프론트엔드 빌드 및 배포
```powershell
# 프로젝트 루트에서
cd frontend
npm install
npm run build

cd ..
aws s3 sync frontend/build/ s3://hr-resource-optimization-frontend-hosting-prod --region us-east-2 --delete --cache-control "public, max-age=31536000" --exclude "index.html"

aws s3 cp frontend/build/index.html s3://hr-resource-optimization-frontend-hosting-prod/index.html --region us-east-2 --cache-control "no-cache, no-store, must-revalidate" --content-type "text/html"
```

---

### 방법 2: 다른 컴퓨터에서 빌드

npm이 설치된 다른 컴퓨터나 서버에서 빌드 후 파일만 복사

#### 2-1. 다른 컴퓨터에서 빌드
```bash
# 코드 복사 (Git 사용)
git clone <repository-url>
cd <project-directory>

# 빌드
cd frontend
npm install
npm run build
```

#### 2-2. 빌드 파일 압축
```bash
# frontend/build 폴더 압축
cd build
tar -czf frontend-build.tar.gz *
# 또는 zip
zip -r frontend-build.zip *
```

#### 2-3. Windows로 복사 후 배포
```powershell
# 압축 해제 후
aws s3 sync frontend-build/ s3://hr-resource-optimization-frontend-hosting-prod --region us-east-2 --delete
```

---

### 방법 3: WSL (Windows Subsystem for Linux) 사용

#### 3-1. WSL 설치
```powershell
# PowerShell (관리자 권한)
wsl --install
```

재부팅 후:

#### 3-2. Ubuntu에서 Node.js 설치
```bash
# WSL Ubuntu 터미널
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 확인
node --version
npm --version
```

#### 3-3. 프로젝트 빌드
```bash
# Windows 파일 시스템 접근
cd /mnt/c/Users/jungjh7/Desktop/Work/c.aws/aws/dist/awsTeam2

# 빌드
cd frontend
npm install
npm run build

# 배포 (AWS CLI 설정 필요)
cd ..
aws s3 sync frontend/build/ s3://hr-resource-optimization-frontend-hosting-prod --region us-east-2 --delete
```

---

### 방법 4: Chocolatey로 Node.js 설치

#### 4-1. Chocolatey 설치
```powershell
# PowerShell (관리자 권한)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

#### 4-2. Node.js 설치
```powershell
choco install nodejs-lts -y
```

#### 4-3. PowerShell 재시작 후 확인
```powershell
node --version
npm --version
```

---

### 방법 5: 이미 빌드된 파일 사용 (임시)

프론트엔드 소스 코드 수정만 했고, 빌드 파일이 이미 있다면:

#### 5-1. 기존 빌드 확인
```powershell
Test-Path frontend/build
Test-Path frontend/dist
```

#### 5-2. 수정된 파일만 교체
```powershell
# 수정된 TypeScript 파일을 JavaScript로 수동 변환은 불가능
# 반드시 빌드 필요
```

❌ 이 방법은 권장하지 않습니다. TypeScript를 JavaScript로 변환하려면 빌드가 필수입니다.

---

## 🎯 권장 방법

### 가장 빠른 방법: Node.js 직접 설치 (방법 1)

**장점**:
- 가장 간단하고 빠름
- 향후 프론트엔드 개발에도 사용 가능
- 10분 이내 설치 완료

**단계**:
1. https://nodejs.org/ → LTS 다운로드
2. 설치 (기본 옵션)
3. PowerShell 재시작
4. `npm install` → `npm run build`
5. S3 업로드

---

## 🐛 문제 해결

### 문제 1: npm 명령어가 인식되지 않음

**원인**: PATH 환경 변수에 Node.js가 추가되지 않음

**해결**:
```powershell
# 환경 변수 확인
$env:PATH

# Node.js 경로 수동 추가 (임시)
$env:PATH += ";C:\Program Files\nodejs"

# 영구 추가 (시스템 설정)
# 제어판 → 시스템 → 고급 시스템 설정 → 환경 변수
# Path에 "C:\Program Files\nodejs" 추가
```

### 문제 2: npm install 실패

**원인**: 네트워크 또는 권한 문제

**해결**:
```powershell
# 캐시 정리
npm cache clean --force

# 관리자 권한으로 실행
# PowerShell 우클릭 → 관리자 권한으로 실행

# 재시도
npm install
```

### 문제 3: npm run build 실패

**원인**: 의존성 문제 또는 메모리 부족

**해결**:
```powershell
# node_modules 삭제 후 재설치
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install

# 메모리 증가
$env:NODE_OPTIONS="--max-old-space-size=4096"
npm run build
```

### 문제 4: 빌드는 되는데 파일이 없음

**원인**: 빌드 출력 폴더 확인

**해결**:
```powershell
# Vite는 기본적으로 dist 폴더 사용
# 하지만 vite.config.ts에서 build로 변경됨
Get-ChildItem frontend/build
Get-ChildItem frontend/dist

# 실제 빌드 폴더 확인
Get-Content frontend/vite.config.ts | Select-String "outDir"
```

---

## 📋 빠른 설치 스크립트

### 자동 설치 스크립트 (관리자 권한 필요)

```powershell
# install_nodejs.ps1
Write-Host "Node.js 설치 시작..." -ForegroundColor Cyan

# Chocolatey 설치 확인
$chocoInstalled = Get-Command choco -ErrorAction SilentlyContinue

if (-not $chocoInstalled) {
    Write-Host "Chocolatey 설치 중..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

# Node.js 설치
Write-Host "Node.js 설치 중..." -ForegroundColor Yellow
choco install nodejs-lts -y

Write-Host "`n설치 완료!" -ForegroundColor Green
Write-Host "PowerShell을 재시작한 후 'node --version'으로 확인하세요." -ForegroundColor Yellow
```

**실행**:
```powershell
# PowerShell (관리자 권한)
.\install_nodejs.ps1
```

---

## ✅ 설치 후 확인

### 1. 버전 확인
```powershell
node --version   # v20.11.0 이상
npm --version    # 10.2.4 이상
```

### 2. 프론트엔드 빌드 테스트
```powershell
cd frontend
npm install
npm run build
```

### 3. 빌드 결과 확인
```powershell
Get-ChildItem frontend/build
```

예상 출력:
```
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----        2025-12-02     11:30                assets
-a----        2025-12-02     11:30           1234 index.html
-a----        2025-12-02     11:30            567 vite.svg
```

### 4. S3 배포
```powershell
cd ..
aws s3 sync frontend/build/ s3://hr-resource-optimization-frontend-hosting-prod --region us-east-2 --delete
```

---

## 🎯 최종 체크리스트

- [ ] Node.js 설치 완료
- [ ] `node --version` 확인
- [ ] `npm --version` 확인
- [ ] PowerShell 재시작
- [ ] `cd frontend`
- [ ] `npm install` 실행
- [ ] `npm run build` 실행
- [ ] `frontend/build` 폴더 확인
- [ ] S3 업로드
- [ ] 브라우저에서 확인

---

## 💡 추가 팁

### npm 대신 yarn 사용
```powershell
# yarn 설치
npm install -g yarn

# 빌드
cd frontend
yarn install
yarn build
```

### 빌드 시간 단축
```powershell
# 병렬 빌드
npm install -g npm-run-all

# package.json에 추가
"scripts": {
  "build:fast": "vite build --mode production"
}
```

### 캐시 활용
```powershell
# 두 번째 빌드부터 빠름
npm run build
```

---

**문제가 계속되면 스크린샷과 함께 오류 메시지를 공유해주세요!**
