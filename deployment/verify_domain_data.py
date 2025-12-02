#!/usr/bin/env python3
"""
생성된 도메인 데이터 확인
"""

import boto3
import json
from decimal import Decimal

REGION = "us-east-2"
dynamodb = boto3.resource('dynamodb', region_name=REGION)

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def verify_projects():
    """프로젝트 도메인 데이터 확인"""
    projects_table = dynamodb.Table('Projects')
    
    print("=" * 60)
    print("프로젝트 도메인 데이터 확인")
    print("=" * 60)
    
    response = projects_table.scan()
    projects = response.get('Items', [])
    
    # 도메인별 프로젝트 분류
    domain_projects = {}
    
    for project in projects:
        knowledge_domain = project.get('knowledge_domain', 'Unknown')
        if knowledge_domain not in domain_projects:
            domain_projects[knowledge_domain] = []
        domain_projects[knowledge_domain].append({
            'id': project.get('project_id'),
            'name': project.get('project_name'),
            'tech_domains': project.get('tech_domains', [])
        })
    
    print(f"\n총 프로젝트: {len(projects)}개")
    print(f"도메인 분류: {len(domain_projects)}개 도메인\n")
    
    for domain, projs in sorted(domain_projects.items()):
        print(f"\n{domain} ({len(projs)}개 프로젝트):")
        for proj in projs:
            print(f"  - {proj['id']}: {proj['name']}")
            if proj['tech_domains']:
                print(f"    기술 도메인: {', '.join(proj['tech_domains'])}")
    
    return domain_projects

def verify_employees():
    """직원 도메인 경험 확인"""
    employees_table = dynamodb.Table('Employees')
    
    print("\n" + "=" * 60)
    print("직원 도메인 경험 확인")
    print("=" * 60)
    
    response = employees_table.scan()
    employees = response.get('Items', [])
    
    employees_with_domain = [e for e in employees if 'domain_experience' in e]
    
    print(f"\n총 직원: {len(employees)}명")
    print(f"도메인 경험 보유: {len(employees_with_domain)}명\n")
    
    for emp in employees_with_domain:
        print(f"\n{emp.get('user_id')} - {emp.get('basic_info', {}).get('name', 'Unknown')}:")
        
        domain_exp = emp.get('domain_experience', {})
        
        # 지식 도메인
        knowledge_domains = domain_exp.get('knowledge_domains', [])
        if knowledge_domains:
            print("  지식 도메인:")
            for kd in knowledge_domains:
                print(f"    - {kd['domain']}: {kd['years']}년, {kd['projects']}개 프로젝트")
        
        # 기술 도메인
        tech_domains = domain_exp.get('tech_domains', [])
        if tech_domains:
            print("  기술 도메인:")
            for td in tech_domains:
                print(f"    - {td['domain']}: {td['proficiency']}")
        
        # 인증
        certs = emp.get('domain_certifications', [])
        if certs:
            print(f"  인증: {', '.join(certs)}")

def main():
    print("=" * 60)
    print("도메인 데이터 검증")
    print("=" * 60)
    
    domain_projects = verify_projects()
    verify_employees()
    
    print("\n" + "=" * 60)
    print("요약")
    print("=" * 60)
    print(f"\n지식 도메인 분포:")
    for domain, projs in sorted(domain_projects.items()):
        print(f"  {domain}: {len(projs)}개 프로젝트")

if __name__ == '__main__':
    main()
