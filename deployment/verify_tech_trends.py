#!/usr/bin/env python3
"""
TechTrends 데이터 확인
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

def verify_tech_trends():
    """TechTrends 데이터 확인"""
    trends_table = dynamodb.Table('TechTrends')
    
    print("=" * 80)
    print("TechTrends 데이터 확인")
    print("=" * 80)
    
    response = trends_table.scan()
    trends = response.get('Items', [])
    
    # 페이지네이션 처리
    while 'LastEvaluatedKey' in response:
        response = trends_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        trends.extend(response.get('Items', []))
    
    print(f"\n총 기술 트렌드: {len(trends)}개\n")
    
    # 카테고리별 분류
    by_category = {}
    for trend in trends:
        category = trend.get('category', 'Unknown')
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(trend)
    
    # 카테고리별 출력
    for category, items in sorted(by_category.items()):
        print(f"\n[{category}] ({len(items)}개)")
        print("-" * 80)
        
        # 트렌드 점수로 정렬
        sorted_items = sorted(items, key=lambda x: float(x.get('trend_score', 0)), reverse=True)
        
        for item in sorted_items:
            tech_name = item.get('tech_name')
            trend_score = float(item.get('trend_score', 0))
            demand_score = float(item.get('demand_score', 0))
            growth_rate = float(item.get('growth_rate', 0))
            market_share = float(item.get('market_share', 0))
            related_domains = item.get('related_domains', [])
            
            print(f"\n  {tech_name}")
            print(f"    트렌드 점수: {trend_score:.1f} | 수요 점수: {demand_score:.1f}")
            print(f"    성장률: {growth_rate:.1f}% | 시장 점유율: {market_share:.1f}%")
            print(f"    관련 도메인: {', '.join(related_domains)}")
            print(f"    설명: {item.get('description', 'N/A')}")
    
    # 상위 10개 기술 (트렌드 점수 기준)
    print("\n" + "=" * 80)
    print("[트렌드 점수 TOP 10]")
    print("=" * 80)
    
    top_trends = sorted(trends, key=lambda x: float(x.get('trend_score', 0)), reverse=True)[:10]
    
    for i, trend in enumerate(top_trends, 1):
        print(f"{i:2d}. {trend.get('tech_name'):20s} - 트렌드: {float(trend.get('trend_score', 0)):5.1f}, 수요: {float(trend.get('demand_score', 0)):5.1f}")
    
    # 상위 10개 기술 (수요 점수 기준)
    print("\n" + "=" * 80)
    print("[수요 점수 TOP 10]")
    print("=" * 80)
    
    top_demand = sorted(trends, key=lambda x: float(x.get('demand_score', 0)), reverse=True)[:10]
    
    for i, trend in enumerate(top_demand, 1):
        print(f"{i:2d}. {trend.get('tech_name'):20s} - 수요: {float(trend.get('demand_score', 0)):5.1f}, 트렌드: {float(trend.get('trend_score', 0)):5.1f}")
    
    # 성장률 TOP 10
    print("\n" + "=" * 80)
    print("[성장률 TOP 10]")
    print("=" * 80)
    
    top_growth = sorted(trends, key=lambda x: float(x.get('growth_rate', 0)), reverse=True)[:10]
    
    for i, trend in enumerate(top_growth, 1):
        print(f"{i:2d}. {trend.get('tech_name'):20s} - 성장률: {float(trend.get('growth_rate', 0)):5.1f}%")
    
    # 도메인별 기술 매핑
    print("\n" + "=" * 80)
    print("[도메인별 주요 기술]")
    print("=" * 80)
    
    domain_techs = {}
    for trend in trends:
        for domain in trend.get('related_domains', []):
            if domain not in domain_techs:
                domain_techs[domain] = []
            domain_techs[domain].append({
                'name': trend.get('tech_name'),
                'trend': float(trend.get('trend_score', 0))
            })
    
    for domain, techs in sorted(domain_techs.items()):
        sorted_techs = sorted(techs, key=lambda x: x['trend'], reverse=True)[:5]
        tech_names = [t['name'] for t in sorted_techs]
        print(f"\n  {domain}: {', '.join(tech_names)}")

def main():
    verify_tech_trends()

if __name__ == '__main__':
    main()
