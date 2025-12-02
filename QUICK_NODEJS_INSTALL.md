# Node.js 빠른 설치 가이드 (Windows)

## 🚨 PowerShell 실행 정책 오류 해결

### 오류 메시지
```
이 시스템에서 스크립트를 실행할 수 없으므로...
PSSecurityException
UnauthorizedAccess
```

---

## ✅ 해결 방법 (3가지)

### 방법 1: 실행 정책 임시 변경 (가장 쉬움)

```powershell
# 관리자 권한 PowerShell에서 실행
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# 그 다음 스크립트 실행
.\install_nodejs_windows.ps1
```

**설명**: 현재 PowerShell 세션에만 적용되므로 안전합니다.

---

### 방법 2: 스크립트 직접 실행

```powershell
# 관리자 권한 PowerShell에서 실행
powershell -ExecutionPolicy Bypass -File .\install_nodejs_windows.ps1
```

---

### 방법 3: Node.js 수동 설치 (가장 권장)

스크립트 없이 직접 설치하는 것이 가장 간단합니다!

#### 단계 1: 다운로드
1. 브라우저에서 https://nodejs.org/ 접속
2. **"20.11.1 LTS"** (녹색 버튼) 클릭
3. `node-v20.11.1-x64.msi` 다운로드

#### 단계 2: 설치
1. 다운로드한 파일 더블클릭
2. "Next" 계속 클릭 (기본 옵션 사용)
3. "Install" 클릭
4. 설치 완료 후 "Finish"

#### 단계 3: 확인
```powershell
# 새 PowerShell 창 열기 (중요!)
node --version
npm --version
```

예상 출력:
```
v20.11.1
10.2.4
```

---

## 🎯 Node.js 설치 후 프론트엔드 배포

### 1. 의존성 설치
```powershell
cd frontend
npm install
```

처음 실행 시 2-3분 소요됩니다.

### 2. 빌드
```powershell
npm run build
```

빌드 완료 시 `frontend/build` 폴더가 생성됩니다.

### 3. S3 배포
```powershell
cd ..

# 정적 파일 업로드
aws s3 sync frontend/build/ s3://hr-resource-optimization-frontend-hosting-prod `
    --region us-east-2 `
    --delete `
    --cache-control "public, max-age=31536000" `
    --exclude "index.html"

# index.html 업로드 (캐시 없음)
aws s3 cp frontend/build/index.html s3://hr-resource-optimization-frontend-hosting-prod/index.html `
    --region us-east-2 `
    --cache-control "no-cache, no-store, must-revalidate" `
    --content-type "text/html"
```

### 4. 배포 확인
브라우저에서 접속:
```
http://hr-resource-optimization-frontend-hosting-prod.s3-website.us-east-2.amazonaws.com/
```

**확인 사항**:
1. 프로젝트 관리 페이지 접속
2. 날짜가 "미정"이 아닌 실제 날짜로 표시 (예: 2022-02-01 ~ 2022-10-29)
3. 팀원 수가 정확하게 표시 (예: 4 / 4명)
4. 고객사 정보 표시 (예: Finance)
5. **브라우저 캐시 강제 새로고침**: `Ctrl + Shift + R`

---

## 🐛 문제 해결

### 문제 1: npm 명령어를 찾을 수 없음
```powershell
# PowerShell을 완전히 닫고 다시 열기
# 또는 컴퓨터 재부팅
```

### 문제 2: npm install 실패
```powershell
# 캐시 정리
npm cache clean --force

# 재시도
npm install
```

### 문제 3: npm run build 실패
```powershell
# node_modules 삭제 후 재설치
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
npm run build
```

### 문제 4: 빌드 폴더가 없음
```powershell
# 빌드 폴더 확인
Get-ChildItem frontend/build
Get-ChildItem frontend/dist

# vite.config.ts 확인
Get-Content frontend/vite.config.ts | Select-String "outDir"
```

### 문제 5: S3 업로드 실패
```powershell
# AWS 자격 증명 확인
aws sts get-caller-identity

# S3 버킷 접근 확인
aws s3 ls s3://hr-resource-optimization-frontend-hosting-prod --region us-east-2
```

---

## 📋 전체 명령어 요약

```powershell
# 1. Node.js 설치 확인
node --version
npm --version

# 2. 프론트엔드 빌드
cd frontend
npm install
npm run build

# 3. S3 배포
cd ..
aws s3 sync frontend/build/ s3://hr-resource-optimization-frontend-hosting-prod --region us-east-2 --delete --cache-control "public, max-age=31536000" --exclude "index.html"
aws s3 cp frontend/build/index.html s3://hr-resource-optimization-frontend-hosting-prod/index.html --region us-east-2 --cache-control "no-cache, no-store, must-revalidate" --content-type "text/html"

# 4. 브라우저에서 확인 (캐시 강제 새로고침)
# http://hr-resource-optimization-frontend-hosting-prod.s3-website.us-east-2.amazonaws.com/
# Ctrl + Shift + R
```

---

## 💡 왜 이 작업이 필요한가?

### 수정된 내용
1. **Lambda 함수**: `team_composition`을 올바르게 변환하도록 수정 ✅
2. **TypeScript 타입**: 누락된 필드 추가 ✅
3. **프론트엔드 컴포넌트**: `as any` 캐스팅 제거 ✅

### 현재 상태
- Lambda 함수: ✅ 재배포 완료
- API Gateway: ✅ 정상 작동
- 프론트엔드: ⚠️ 재배포 필요

### 배포 후 결과
**수정 전**:
```
프로젝트명: 증권 거래 시스템
고객사: 고객사
기간: 미정 ~ 미정
팀원: 0 / 5명
```

**수정 후**:
```
프로젝트명: 증권 거래 시스템
고객사: Finance
기간: 2022-02-01 ~ 2022-10-29
팀원: 4 / 4명
팀원 목록:
  - 임예은 (Security Engineer)
  - 박민수 (DevOps Engineer)
  - 김준호 (Backend Developer)
  - 최서연 (System Architect)
```

---

## 🎯 다음 단계

1. ✅ Node.js 설치
2. ✅ `npm install` 실행
3. ✅ `npm run build` 실행
4. ✅ S3 업로드
5. ✅ 브라우저에서 확인 (`Ctrl + Shift + R`)

**문제가 있으면 스크린샷과 함께 오류 메시지를 공유해주세요!**
