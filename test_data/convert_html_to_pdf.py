"""
HTML 이력서를 PDF로 변환하는 스크립트

사용법:
    pip install weasyprint
    python convert_html_to_pdf.py

또는 브라우저에서 HTML 파일을 열고 "인쇄" -> "PDF로 저장"을 선택하세요.
"""

try:
    from weasyprint import HTML
    import os
    
    # 현재 디렉토리
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 변환할 HTML 파일 목록
    html_files = [
        'sample_resume_choi_jungwoo.html',
        'sample_resume_kim_soyeon.html'
    ]
    
    print("HTML 파일을 PDF로 변환 중...")
    
    for html_file in html_files:
        html_path = os.path.join(current_dir, html_file)
        pdf_path = os.path.join(current_dir, html_file.replace('.html', '.pdf'))
        
        if os.path.exists(html_path):
            print(f"변환 중: {html_file} -> {os.path.basename(pdf_path)}")
            HTML(filename=html_path).write_pdf(pdf_path)
            print(f"✓ 완료: {os.path.basename(pdf_path)}")
        else:
            print(f"✗ 파일을 찾을 수 없음: {html_file}")
    
    print("\n모든 변환이 완료되었습니다!")
    print("\n생성된 PDF 파일:")
    for html_file in html_files:
        pdf_file = html_file.replace('.html', '.pdf')
        pdf_path = os.path.join(current_dir, pdf_file)
        if os.path.exists(pdf_path):
            print(f"  - {pdf_file}")

except ImportError:
    print("=" * 60)
    print("WeasyPrint가 설치되지 않았습니다.")
    print("=" * 60)
    print("\n다음 방법 중 하나를 선택하세요:\n")
    print("방법 1: WeasyPrint 설치 (권장)")
    print("  pip install weasyprint")
    print("  python convert_html_to_pdf.py")
    print("\n방법 2: 브라우저에서 수동 변환")
    print("  1. HTML 파일을 브라우저에서 열기")
    print("  2. Ctrl+P (인쇄)")
    print("  3. 대상을 'PDF로 저장'으로 선택")
    print("  4. 저장")
    print("\n방법 3: 온라인 변환 도구 사용")
    print("  - https://www.html2pdf.com/")
    print("  - https://pdfcrowd.com/")
    print("=" * 60)

except Exception as e:
    print(f"오류 발생: {str(e)}")
    print("\n브라우저에서 HTML 파일을 열고 '인쇄' -> 'PDF로 저장'을 선택하세요.")
