#!/usr/bin/env python3
"""
도메인 프로젝트 데이터 확인
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

def check_domain_projects():
    """도메인 정보가 있는 프로젝트 확인"""
    projects_table = dynamodb.Table('Projects')
    
    print("=" * 80)
    print("도메인 프로젝트 데이터 확인")
    print("=" * 80)
    
    # 신규 생성된 프로젝트 ID
    new_project_ids = ['P_101', 'P_102', 'P_103', 'P_104', 'P_105']
    
    print("\n[신규 생성 프로젝트]")
    for project_id in new_project_ids:
        try:
            response = projects_table.get_item(Key={'project_id': project_id})
            if 'Item' in response:
                project = response['Item']
                print(f"\n✓ {project_id}: {project.get('project_name')}")
                print(f"  지식 도메인: {project.get('knowledge_domain', 'N/A')}")
                print(f"  기술 도메인: {', '.join(project.get('tech_domains', []))}")
                print(f"  산업: {project.get('client_industry', 'N/A')}")
                print(f"  예산: {project.get('budget_scale', 'N/A')}")
                print(f"  팀 규모: {project.get('team_size', 'N/A')}명")
                
                # 전체 데이터 출력
                print(f"\n  [전체 데이터]")
                print(json.dumps(project, indent=2, ensure_ascii=False, default=decimal_default))
            else:
                print(f"\n✗ {project_id}: 데이터 없음")
        except Exception as e:
            print(f"\n✗ {project_id}: 오류 - {str(e)}")
    
    # 도메인 정보가 있는 모든 프로젝트 확인
    print("\n" + "=" * 80)
    print("[도메인 정보 보유 프로젝트 통계]")
    print("=" * 80)
    
    response = projects_table.scan()
    all_projects = response.get('Items', [])
    
    projects_with_domain = [p for p in all_projects if 'knowledge_domain' in p]
    projects_without_domain = [p for p in all_projects if 'knowledge_domain' not in p]
    
    print(f"\n총 프로젝트: {len(all_projects)}개")
    print(f"도메인 정보 있음: {len(projects_with_domain)}개")
    print(f"도메인 정보 없음: {len(projects_without_domain)}개")
    
    # 도메인별 분류
    domain_counts = {}
    for project in projects_with_domain:
        domain = project.get('knowledge_domain', 'Unknown')
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    print(f"\n[도메인별 프로젝트 수]")
    for domain, count in sorted(domain_counts.items()):
        print(f"  {domain}: {count}개")

def main():
    check_domain_projects()

if __name__ == '__main__':
    main()
