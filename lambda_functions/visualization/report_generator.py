"""
보고서 생성 모듈

PDF 및 Excel 형식의 보고서를 생성합니다.
"""

import io
import json
from typing import Dict, List, Any
from datetime import datetime


def generate_pdf_report(data: Dict[str, Any], report_type: str) -> bytes:
    """
    PDF 보고서 생성
    
    Args:
        data: 보고서 데이터
        report_type: 보고서 유형 ('skills', 'domains', 'team', 'dashboard')
        
    Returns:
        PDF 바이트 데이터
    """
    try:
        # 간단한 텍스트 기반 PDF 생성 (실제로는 reportlab 등 사용)
        # 여기서는 텍스트 형식으로 간단히 구현
        
        report_content = []
        report_content.append("=" * 80)
        report_content.append(f"HR Resource Optimization System - {report_type.upper()} Report")
        report_content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_content.append("=" * 80)
        report_content.append("")
        
        if report_type == 'skills':
            report_content.append("기술 스택 분포 보고서")
            report_content.append("-" * 80)
            report_content.append(f"총 기술 수: {data.get('total_skills', 0)}")
            report_content.append(f"총 직원 수: {data.get('total_employees', 0)}")
            report_content.append("")
            
            for skill in data.get('skills', [])[:20]:  # 상위 20개만
                report_content.append(
                    f"- {skill['skill_name']}: "
                    f"{skill['employee_count']}명, "
                    f"평균 {skill['average_years']}년"
                )
        
        elif report_type == 'domains':
            report_content.append("도메인 커버리지 보고서")
            report_content.append("-" * 80)
            report_content.append(f"총 도메인 수: {data.get('total_domains', 0)}")
            report_content.append(f"총 프로젝트 수: {data.get('total_projects', 0)}")
            report_content.append("")
            
            for domain in data.get('domains', []):
                report_content.append(
                    f"- {domain['domain']}: "
                    f"{domain['project_count']}개 프로젝트, "
                    f"{domain['unique_tech_count']}개 기술"
                )
        
        elif report_type == 'team':
            report_content.append("팀 구성 보고서")
            report_content.append("-" * 80)
            report_content.append(f"총 직원 수: {data.get('total_employees', 0)}")
            report_content.append("")
            report_content.append("역할별 분포:")
            
            for role_info in data.get('roles', []):
                report_content.append(
                    f"- {role_info['role']}: "
                    f"{role_info['count']}명 ({role_info['percentage']}%)"
                )
            
            report_content.append("")
            report_content.append("경력 분포:")
            for exp_range, count in data.get('experience_distribution', {}).items():
                report_content.append(f"- {exp_range}: {count}명")
        
        elif report_type == 'dashboard':
            report_content.append("대시보드 메트릭 보고서")
            report_content.append("-" * 80)
            
            emp_metrics = data.get('employee_metrics', {})
            report_content.append(f"총 직원 수: {emp_metrics.get('total_employees', 0)}")
            report_content.append(
                f"가용 인력: {emp_metrics.get('available_employees', 0)}"
            )
            
            proj_metrics = data.get('project_metrics', {})
            report_content.append(f"총 프로젝트 수: {proj_metrics.get('total_projects', 0)}")
            report_content.append(
                f"진행 중인 프로젝트: {proj_metrics.get('active_projects', 0)}"
            )
        
        report_content.append("")
        report_content.append("=" * 80)
        report_content.append("End of Report")
        report_content.append("=" * 80)
        
        # 텍스트를 바이트로 변환
        report_text = "\n".join(report_content)
        return report_text.encode('utf-8')
        
    except Exception as e:
        print(f"PDF 보고서 생성 오류: {str(e)}")
        raise


def generate_excel_report(data: Dict[str, Any], report_type: str) -> bytes:
    """
    Excel 보고서 생성
    
    Args:
        data: 보고서 데이터
        report_type: 보고서 유형 ('skills', 'domains', 'team', 'dashboard')
        
    Returns:
        Excel 바이트 데이터
    """
    try:
        # CSV 형식으로 간단히 구현 (실제로는 openpyxl 등 사용)
        csv_lines = []
        
        if report_type == 'skills':
            csv_lines.append("기술명,직원수,평균경력(년)")
            for skill in data.get('skills', []):
                csv_lines.append(
                    f"{skill['skill_name']},"
                    f"{skill['employee_count']},"
                    f"{skill['average_years']}"
                )
        
        elif report_type == 'domains':
            csv_lines.append("도메인,프로젝트수,기술수")
            for domain in data.get('domains', []):
                csv_lines.append(
                    f"{domain['domain']},"
                    f"{domain['project_count']},"
                    f"{domain['unique_tech_count']}"
                )
        
        elif report_type == 'team':
            csv_lines.append("역할,인원수,비율(%)")
            for role_info in data.get('roles', []):
                csv_lines.append(
                    f"{role_info['role']},"
                    f"{role_info['count']},"
                    f"{role_info['percentage']}"
                )
        
        elif report_type == 'dashboard':
            csv_lines.append("메트릭,값")
            emp_metrics = data.get('employee_metrics', {})
            csv_lines.append(f"총 직원 수,{emp_metrics.get('total_employees', 0)}")
            csv_lines.append(f"가용 인력,{emp_metrics.get('available_employees', 0)}")
            
            proj_metrics = data.get('project_metrics', {})
            csv_lines.append(f"총 프로젝트 수,{proj_metrics.get('total_projects', 0)}")
            csv_lines.append(f"진행 중인 프로젝트,{proj_metrics.get('active_projects', 0)}")
        
        # CSV를 바이트로 변환
        csv_text = "\n".join(csv_lines)
        return csv_text.encode('utf-8-sig')  # BOM 포함하여 Excel에서 한글 깨짐 방지
        
    except Exception as e:
        print(f"Excel 보고서 생성 오류: {str(e)}")
        raise


def upload_report_to_s3(
    report_data: bytes,
    report_name: str,
    bucket_name: str = 'hr-reports-bucket'
) -> str:
    """
    생성된 보고서를 S3에 업로드
    
    Args:
        report_data: 보고서 바이트 데이터
        report_name: 보고서 파일명
        bucket_name: S3 버킷 이름
        
    Returns:
        S3 URL
    """
    try:
        import boto3
        
        s3_client = boto3.client('s3')
        
        # S3에 업로드
        s3_client.put_object(
            Bucket=bucket_name,
            Key=f"reports/{report_name}",
            Body=report_data,
            ContentType='application/octet-stream'
        )
        
        # URL 생성
        url = f"https://{bucket_name}.s3.amazonaws.com/reports/{report_name}"
        return url
        
    except Exception as e:
        print(f"S3 업로드 오류: {str(e)}")
        raise
