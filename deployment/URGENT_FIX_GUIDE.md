# 🚨 긴급 수정 가이드 - API URL 불일치 문제

## 🔍 문제 발견

**증상**: 프론트엔드에서 "Failed to fetch" 오류 발생

**원인**: 프론트엔드가 잘못된 API Gateway URL을 사용

**잘못된 URL**:
```
https://xoc7x1m6p8.execute-api.us-east-2.amazonaws.com/prod
```

**올바른 URL**:
```
https://ifeniowvpb.execute-api.us-east-2.amazonaws.com/prod
```

---

## ✅ 수정 완료 사항

### 1. frontend/.env 파일 생성 ✅
올바른 API URL이 포함된 환경 변수 파일 생성

### 2. frontend/src/config/api.ts 수정 ✅
API URL 로그 추가 (디버깅용)

---

## 🚀 해결 방법

### 방법 1: 프론트엔드 재빌드 및 배포 (권장)

#### 전제 조건
- Node.js 설치 완료

#### 단계

**1. 프론트엔드 빌드**
```powershell
cd frontend
npm install
npm run build
```

**2. S3 업로드**
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

**3. 브라우저에서 확인**
```
http://hr-resource-optimization-frontend-hosting-prod.s3-website.us-east-2.amazonaws.com/
```

**4. 브라우저 캐시 강제 새로고침**
```
Ctrl + Shift + R
```

**5. 개발자 도구에서 확인**
- F12 → Console 탭
- "API Base URL: https://ifeniowvpb..." 메시지 확인

---

### 방법 2: Node.js 설치 (빌드 전 필요)

#### Windows에서 Node.js 설치

**옵션 A: 직접 다운로드 (가장 쉬움)**
1. https://nodejs.org/ 접속
2. "20.11.1 LTS" 다운로드
3. 설치 파일 실행
4. PowerShell 재시작
5. `node --version` 확인

**옵션 B: PowerShell 스크립트 사용**
```powershell
# 관리자 권한 PowerShell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
.\install_nodejs_windows.ps1
```

**옵션 C: 한 줄 명령어**
```powershell
# 관리자 권한 PowerShell
powershell -ExecutionPolicy Bypass -File .\install_nodejs_windows.ps1
```

---

## 🐛 추가 문제 해결

### 문제 1: /projects OPTIONS 요청 실패

**증상**: OPTIONS 요청이 500 오류 반환

**원인**: ProjectsList Lambda 함수에 OPTIONS 처리 누락

**해결**:
```python
# lambda_functions/projects_list/index.py 수정 필요
# OPTIONS 메서드 처리 추가
```

**재배포**:
```powershell
python deployment/redeploy_projects_lambda.py
```

---

### 문제 2: 빌드 후에도 문제 지속

**원인**: 브라우저 캐시

**해결**:
1. **강제 새로고침**: `Ctrl + Shift + R`
2. **캐시 완전 삭제**:
   - Chrome: 설정 → 개인정보 및 보안 → 인터넷 사용 기록 삭제
   - 시간 범위: 전체 기간
   - 캐시된 이미지 및 파일 체크
3. **시크릿 모드**: `Ctrl + Shift + N`

---

### 문제 3: npm 명령어 인식 안 됨

**원인**: Node.js 미설치 또는 PATH 설정 문제

**해결**:
```powershell
# 확인
node --version
npm --version

# PATH 확인
$env:PATH

# PowerShell 재시작
# 또는 컴퓨터 재부팅
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

# 4. 브라우저에서 확인
# http://hr-resource-optimization-frontend-hosting-prod.s3-website.us-east-2.amazonaws.com/
# Ctrl + Shift + R (강제 새로고침)
```

---

## ✅ 성공 확인 방법

### 1. 브라우저 개발자 도구 (F12)

**Console 탭**:
```
API Base URL: https://ifeniowvpb.execute-api.us-east-2.amazonaws.com/prod
```

**Network 탭**:
- `/projects` 요청: Status 200
- `/employees` 요청: Status 200
- URL이 `ifeniowvpb`로 시작

### 2. 프로젝트 관리 페이지

**확인 사항**:
- ✅ 프로젝트 목록 표시 (100개)
- ✅ 날짜 정보 표시 (예: 2022-02-01 ~ 2022-10-29)
- ✅ 팀원 수 표시 (예: 4 / 4명)
- ✅ 고객사 정보 표시 (예: Finance)
- ✅ "Failed to fetch" 오류 없음

### 3. 직원 관리 페이지

**확인 사항**:
- ✅ 직원 목록 표시 (300명)
- ✅ 직원 상세 정보 표시
- ✅ 검색 기능 작동

---

## 🎯 예상 결과

### 수정 전
```
❌ Failed to fetch
❌ API 호출 실패
❌ 데이터 표시 안 됨
```

### 수정 후
```
✅ 프로젝트 목록 정상 표시
✅ 직원 목록 정상 표시
✅ 모든 데이터 로드 성공
```

---

## 📞 추가 지원

### 문제가 계속되면

1. **진단 스크립트 실행**
   ```powershell
   python deployment/diagnose_frontend_api_issue.py
   ```

2. **시스템 점검**
   ```powershell
   python deployment/comprehensive_system_check.py
   ```

3. **브라우저 개발자 도구 스크린샷**
   - Console 탭
   - Network 탭 (실패한 요청)

---

**마지막 업데이트**: 2025-12-02  
**우선순위**: 🔴 긴급 (프론트엔드 재배포 필요)
