# 🚀 빠른 시작: PDF 변환 가이드

## Windows 사용자를 위한 가장 쉬운 방법

### ⭐ 방법 1: 브라우저에서 직접 변환 (가장 간단!)

1. **HTML 파일 열기**
   - `sample_resume_choi_jungwoo.html` 파일을 더블클릭
   - 또는 파일을 브라우저(Chrome, Edge 등)로 드래그

2. **인쇄 메뉴 열기**
   - `Ctrl + P` 키를 누르거나
   - 브라우저 메뉴에서 "인쇄" 선택

3. **PDF로 저장**
   - **대상**: "PDF로 저장" 또는 "Microsoft Print to PDF" 선택
   - **레이아웃**: 세로
   - **용지 크기**: A4
   - **여백**: 기본값
   - **배경 그래픽**: ✅ 체크 (색상 포함)

4. **저장**
   - 파일명: `sample_resume_choi_jungwoo.pdf`
   - 저장 위치: `test_data` 폴더
   - "저장" 버튼 클릭

5. **반복**
   - `sample_resume_kim_soyeon.html`도 동일하게 진행

**소요 시간: 각 파일당 약 30초**

---

### 🤖 방법 2: PowerShell 스크립트 사용 (자동화)

Chrome 브라우저가 설치되어 있다면 자동으로 변환할 수 있습니다:

```powershell
cd test_data
.\convert_to_pdf_windows.ps1
```

**Chrome이 없는 경우**: 방법 1을 사용하세요.

---

### 🌐 방법 3: 온라인 변환 도구

인터넷 연결이 있다면 온라인 도구를 사용할 수 있습니다:

1. **HTML2PDF.com**
   - https://www.html2pdf.com/
   - HTML 파일 업로드
   - "Convert" 클릭
   - PDF 다운로드

2. **PDFCrowd**
   - https://pdfcrowd.com/
   - HTML 파일 업로드
   - 변환 및 다운로드

3. **Sejda**
   - https://www.sejda.com/html-to-pdf
   - HTML 파일 업로드
   - PDF 다운로드

---

## ✅ 변환 완료 확인

변환이 완료되면 `test_data` 폴더에 다음 파일들이 생성됩니다:

```
test_data/
├── sample_resume_choi_jungwoo.html
├── sample_resume_choi_jungwoo.pdf  ← 생성됨!
├── sample_resume_kim_soyeon.html
└── sample_resume_kim_soyeon.pdf    ← 생성됨!
```

---

## 🎯 다음 단계: 이력서 업로드 테스트

PDF 파일이 생성되었다면 이제 시스템에서 테스트할 수 있습니다!

### 프론트엔드에서 테스트

1. **프론트엔드 실행**
   ```bash
   cd frontend
   npm run dev
   ```

2. **브라우저에서 열기**
   - http://localhost:5173

3. **이력서 업로드**
   - "인력 관리" 탭 클릭
   - "이력서 업로드" 버튼 클릭
   - 생성한 PDF 파일 선택
   - "업로드" 버튼 클릭

4. **결과 확인**
   - 업로드 진행 상황 확인
   - "평가 현황" 탭에서 파싱 결과 확인

---

## 🐛 문제 해결

### PDF가 제대로 보이지 않는 경우

**증상**: PDF에 색상이나 스타일이 없음

**해결**:
- 인쇄 설정에서 "배경 그래픽" 옵션을 체크하세요
- Chrome: "기타 설정" → "배경 그래픽" ✅
- Edge: "기타 설정" → "배경 그래픽" ✅

### 파일 크기가 너무 큰 경우

**증상**: PDF 파일이 10MB를 초과함

**해결**:
- 브라우저의 인쇄 설정에서 해상도를 낮추세요
- 또는 온라인 PDF 압축 도구 사용: https://www.ilovepdf.com/compress_pdf

### 한글이 깨지는 경우

**증상**: PDF에서 한글이 □□□로 표시됨

**해결**:
- 시스템에 "맑은 고딕" 폰트가 설치되어 있는지 확인
- Windows 10/11에는 기본으로 설치되어 있습니다
- 브라우저를 최신 버전으로 업데이트하세요

---

## 💡 팁

### 더 나은 PDF 품질을 위한 설정

**Chrome/Edge 인쇄 설정:**
- ✅ 배경 그래픽: 켜기
- ✅ 여백: 기본값 또는 최소
- ✅ 배율: 100%
- ✅ 용지 크기: A4

### 여러 파일 한 번에 변환

PowerShell 스크립트를 사용하면 모든 HTML 파일을 한 번에 변환할 수 있습니다:

```powershell
cd test_data
.\convert_to_pdf_windows.ps1
```

---

## 📞 추가 도움이 필요하신가요?

- 📖 상세 가이드: `README_RESUME_SAMPLES.md`
- 🔧 문제 해결: `../deployment/RESUME_UPLOAD_TROUBLESHOOTING.md`
- 💬 프로젝트 관리자에게 문의

---

**이제 PDF 파일을 생성하고 시스템에서 테스트할 준비가 되었습니다! 🎉**
