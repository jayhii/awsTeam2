# 이력서 샘플 파일 가이드

## 📋 개요

이 디렉토리에는 HR 인력 배치 최적화 시스템의 이력서 업로드 및 파싱 기능을 테스트하기 위한 샘플 이력서 파일들이 포함되어 있습니다.

## 📁 파일 목록

### HTML 이력서 파일
- `sample_resume_choi_jungwoo.html` - 최정우 (Principal Software Engineer, 경력 13년)
- `sample_resume_kim_soyeon.html` - 김소연 (Senior Backend Developer, 경력 6년)

### 변환 스크립트
- `convert_html_to_pdf.py` - HTML을 PDF로 변환하는 Python 스크립트

## 🔄 HTML을 PDF로 변환하는 방법

### 방법 1: Python 스크립트 사용 (권장)

```bash
# WeasyPrint 설치
pip install weasyprint

# 변환 실행
cd test_data
python convert_html_to_pdf.py
```

### 방법 2: 브라우저에서 수동 변환

1. HTML 파일을 브라우저(Chrome, Edge 등)에서 엽니다
2. `Ctrl + P` (인쇄 단축키)를 누릅니다
3. 대상을 **"PDF로 저장"**으로 선택합니다
4. 다음 설정을 권장합니다:
   - 용지 크기: A4
   - 여백: 기본값
   - 배경 그래픽: 포함
5. "저장" 버튼을 클릭합니다

### 방법 3: 온라인 변환 도구

- https://www.html2pdf.com/
- https://pdfcrowd.com/
- https://www.sejda.com/html-to-pdf

## 📝 이력서 양식 가이드

시스템이 이력서를 정확하게 파싱하려면 다음 정보가 포함되어야 합니다:

### 필수 정보
- ✅ **이름** (한글/영문)
- ✅ **연락처** (이메일, 전화번호)
- ✅ **직무/직급**
- ✅ **경력 년수**
- ✅ **핵심 기술 스택** (기술명, 숙련도, 경험 년수)

### 권장 정보
- 📌 **자기소개** (업무 스타일, 강점)
- 📌 **프로젝트 경험**
  - 프로젝트명
  - 역할
  - 기간
  - 주요 업무
  - 성과
- 📌 **학력** (학교명, 전공, 학위)
- 📌 **자격증** (자격증명, 취득 년도)
- 📌 **기술 스택 상세** (Backend, Frontend, DevOps 등)
- 📌 **언어 능력**

## 🤖 AI 파싱 프로세스

업로드된 이력서는 다음 과정을 거쳐 자동으로 처리됩니다:

1. **S3 업로드**: 프론트엔드에서 Presigned URL을 통해 S3에 직접 업로드
2. **텍스트 추출**: AWS Textract가 PDF에서 텍스트를 추출
3. **구조화**: AWS Bedrock Claude가 텍스트를 분석하여 구조화된 데이터로 변환
4. **정규화**: 기술 스택 이름을 표준화 (예: "react" → "React", "nodejs" → "Node.js")
5. **저장**: DynamoDB에 직원 정보로 저장
6. **평가**: 자동으로 정량적/정성적 평가 수행

## 📊 샘플 이력서 프로필

### 최정우 (Choi Jung-woo)
- **직급**: Principal Software Engineer
- **경력**: 13년
- **핵심 기술**: Java, Spring Boot, Oracle Database, System Architecture
- **특징**: 금융권 차세대 프로젝트 경험, 안정성 지향형 아키텍트
- **주요 프로젝트**:
  - 차세대 금융 코어 뱅킹 시스템 구축
  - 보험사 레거시 시스템 현대화
  - 증권사 통합 거래 플랫폼 구축

### 김소연 (Kim So-yeon)
- **직급**: Senior Backend Developer
- **경력**: 6년
- **핵심 기술**: Kotlin, Java, Spring Boot, Elasticsearch, AWS
- **특징**: 비즈니스 임팩트 중심, 풀스택 개발자
- **주요 프로젝트**:
  - 대형 유통사 옴니채널 커머스 플랫폼
  - 핀테크 모바일 뱅킹 앱 백엔드
  - 소셜 미디어 실시간 알림 시스템

## 🧪 테스트 방법

### 1. 로컬 테스트

```bash
# PDF 생성
python test_data/convert_html_to_pdf.py

# 생성된 PDF 확인
ls test_data/*.pdf
```

### 2. 프론트엔드에서 업로드 테스트

1. 프론트엔드 애플리케이션 실행
2. "인력 관리" 탭으로 이동
3. "이력서 업로드" 버튼 클릭
4. 생성된 PDF 파일 선택
5. 업로드 진행 상황 확인
6. "평가 현황" 탭에서 파싱 결과 확인

### 3. API 직접 테스트

```bash
# 1. Presigned URL 요청
curl -X POST https://your-api-gateway-url/prod/resume/upload-url \
  -H "Content-Type: application/json" \
  -d '{
    "file_name": "sample_resume.pdf",
    "content_type": "application/pdf"
  }'

# 2. 응답에서 받은 upload_url로 파일 업로드
curl -X PUT "PRESIGNED_URL" \
  -H "Content-Type: application/pdf" \
  --data-binary "@test_data/sample_resume_choi_jungwoo.pdf"
```

## 🔍 파싱 결과 확인

### DynamoDB에서 확인

```python
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('hr-resource-optimization-employees-prod')

# 모든 직원 조회
response = table.scan()
for item in response['Items']:
    print(f"Employee: {item['name']}")
    print(f"Skills: {item['skills']}")
    print(f"Experience: {item['experience_years']} years")
    print("---")
```

### CloudWatch Logs에서 확인

```bash
# Lambda 로그 확인
aws logs tail /aws/lambda/hr-resource-optimization-resume-parser-prod --follow
```

## ⚠️ 주의사항

1. **파일 형식**: 현재 시스템은 **PDF 파일만** 지원합니다
2. **파일 크기**: 최대 **10MB**까지 업로드 가능합니다
3. **한글 지원**: 한글 이력서도 정상적으로 파싱됩니다
4. **개인정보**: 테스트용 샘플 이력서는 가상의 정보를 사용합니다

## 🐛 문제 해결

### 업로드가 실패하는 경우

1. **API Gateway URL 확인**
   ```bash
   # Terraform output에서 확인
   cd deployment/terraform
   terraform output api_gateway_url
   ```

2. **CORS 설정 확인**
   - API Gateway에서 CORS가 올바르게 설정되어 있는지 확인
   - 브라우저 개발자 도구의 Network 탭에서 OPTIONS 요청 확인

3. **Lambda 함수 확인**
   ```bash
   # Lambda 함수 목록 확인
   aws lambda list-functions --query 'Functions[?contains(FunctionName, `resume`)].FunctionName'
   ```

4. **S3 버킷 확인**
   ```bash
   # S3 버킷 존재 확인
   aws s3 ls | grep resume
   ```

### 파싱이 실패하는 경우

1. **CloudWatch Logs 확인**
   ```bash
   aws logs tail /aws/lambda/hr-resource-optimization-resume-parser-prod --follow
   ```

2. **Textract 권한 확인**
   - Lambda 실행 역할에 Textract 권한이 있는지 확인

3. **Bedrock 권한 확인**
   - Lambda 실행 역할에 Bedrock 권한이 있는지 확인
   - Bedrock 모델 액세스가 활성화되어 있는지 확인

## 📚 추가 리소스

- [AWS Textract 문서](https://docs.aws.amazon.com/textract/)
- [AWS Bedrock 문서](https://docs.aws.amazon.com/bedrock/)
- [프로젝트 API 문서](../API_DOCUMENTATION.md)
- [사용자 가이드](../USER_GUIDE.md)

## 💡 커스텀 이력서 작성 팁

자신만의 이력서를 작성할 때는 제공된 HTML 템플릿을 참고하세요:

1. HTML 파일을 복사하여 새 파일 생성
2. 개인 정보로 내용 수정
3. 브라우저에서 열어 미리보기
4. PDF로 변환
5. 시스템에 업로드하여 테스트

---

**문의사항이 있으시면 프로젝트 관리자에게 연락해주세요.**
