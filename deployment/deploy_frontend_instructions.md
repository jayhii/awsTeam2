# 프론트엔드 배포 가이드

## 🔧 수정 완료된 파일

1. **frontend/src/config/api.ts**
   - `TeamMember` 인터페이스 추가
   - `Project` 인터페이스에 누락된 필드 추가
   - TypeScript 타입 안전성 확보

2. **frontend/src/components/ProjectManagement.tsx**
   - `as any` 캐스팅 제거
   - 타입 안전한 코드로 변경
   - 날짜 및 팀원 정보 정상 표시

## 📦 배포 단계

### 1. 프론트엔드 빌드

```powershell
# frontend 디렉토리로 이동
cd frontend

# 의존성 설치 (처음 한 번만)
npm install

# 프로덕션 빌드
npm run build
```

빌드가 완료되면 `frontend/dist` 또는 `frontend/build` 폴더가 생성됩니다.

### 2. S3에 배포

#### 방법 1: PowerShell 스크립트 사용 (권장)

```powershell
# 프로젝트 루트로 돌아가기
cd ..

# 배포 스크립트 실행
.\deploy_frontend.ps1
```

#### 방법 2: AWS CLI 직접 사용

```powershell
# Vite는 dist 폴더에 빌드됨
$S3Bucket = "hr-resource-optimization-frontend-hosting-prod"
$AwsRegion = "us-east-2"

# 정적 파일 업로드 (캐시 적용)
aws s3 sync frontend/dist/ s3://$S3Bucket `
    --region $AwsRegion `
    --delete `
    --cache-control "public, max-age=31536000" `
    --exclude "index.html"

# index.html은 캐시 없이 업로드
aws s3 cp frontend/dist/index.html s3://$S3Bucket/index.html `
    --region $AwsRegion `
    --cache-control "no-cache, no-store, must-revalidate" `
    --content-type "text/html"
```

#### 방법 3: 프론트엔드 배포 스크립트 사용

```powershell
cd frontend
.\deploy-to-s3.ps1
```

### 3. 배포 확인

배포 후 브라우저에서 확인:
```
http://hr-resource-optimization-frontend-hosting-prod.s3-website.us-east-2.amazonaws.com/
```

## ✅ 확인 사항

### 프로젝트 관리 페이지에서 확인할 내용

1. **날짜 정보**
   - ✅ 시작일과 종료일이 "미정"이 아닌 실제 날짜로 표시
   - 예: "2022-02-01 ~ 2022-10-29"

2. **팀원 정보**
   - ✅ 정확한 팀원 수 표시
   - 예: "4 / 4명" (이전에는 부정확했음)

3. **진행률 바**
   - ✅ 팀원 배정 진행률이 정확하게 표시

4. **고객사 정보**
   - ✅ 산업 분야가 정확하게 표시
   - 예: "Finance", "E-commerce" 등

### 브라우저 개발자 도구 확인

1. **Network 탭**
   - `/projects` API 호출 확인
   - 응답 데이터에 `end_date`, `team_members`, `team_size` 포함 확인

2. **Console 탭**
   - TypeScript 에러가 없는지 확인
   - "프로젝트 목록 데이터" 로그 확인

## 🐛 문제 해결

### 빌드 오류 발생 시

```powershell
# node_modules 삭제 후 재설치
cd frontend
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
npm run build
```

### 캐시 문제로 변경사항이 안 보일 때

1. **브라우저 캐시 강제 새로고침**
   - Windows: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

2. **S3 캐시 헤더 확인**
   ```powershell
   aws s3api head-object `
       --bucket hr-resource-optimization-frontend-hosting-prod `
       --key index.html `
       --region us-east-2
   ```

3. **CloudFront 사용 시 무효화**
   ```powershell
   aws cloudfront create-invalidation `
       --distribution-id YOUR_DISTRIBUTION_ID `
       --paths "/*"
   ```

### API 응답은 정상인데 UI에 안 보일 때

1. **브라우저 콘솔 확인**
   - F12 → Console 탭
   - 에러 메시지 확인

2. **API 응답 확인**
   - F12 → Network 탭
   - `/projects` 요청 클릭
   - Response 탭에서 데이터 구조 확인

3. **타입 정의 재확인**
   ```typescript
   // frontend/src/config/api.ts
   export interface Project {
     project_id: string;
     project_name: string;
     status: string;
     start_date: string;
     end_date: string;        // ✅ 있어야 함
     team_members: TeamMember[]; // ✅ 있어야 함
     team_size: number;       // ✅ 있어야 함
     // ...
   }
   ```

## 📊 예상 결과

### 수정 전
```
프로젝트명: 증권 거래 시스템
기간: 미정 ~ 미정
팀원: 0 / 5명
```

### 수정 후
```
프로젝트명: 증권 거래 시스템
기간: 2022-02-01 ~ 2022-10-29
팀원: 4 / 4명
고객사: Finance
```

## 🎯 다음 단계

배포 완료 후:

1. ✅ 프로젝트 관리 페이지에서 날짜 정보 확인
2. ✅ 팀원 수가 정확한지 확인
3. ✅ 100개 프로젝트 모두 데이터가 표시되는지 확인
4. ✅ 검색 기능이 정상 작동하는지 확인

문제가 있다면 브라우저 개발자 도구의 Console과 Network 탭을 확인하세요.
