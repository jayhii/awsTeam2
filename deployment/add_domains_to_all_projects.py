#!/usr/bin/env python3
"""
모든 프로젝트에 도메인 정보 추가 및 TechTrends 데이터 생성
"""

import boto3
from decimal import Decimal
import re

REGION = "us-east-2"
dynamodb = boto3.resource('dynamodb', region_name=REGION)

# 프로젝트 이름 패턴으로 도메인 매핑
DOMAIN_MAPPING = {
    'Finance': {
        'keywords': ['금융', '뱅킹', '은행', '증권', '거래', 'Banking', 'Finance', '코어뱅킹', '모바일 뱅킹'],
        'tech_domains': ['Cloud', 'Web', 'Security', 'Data'],
        'industry': 'Finance / Banking'
    },
    'Healthcare': {
        'keywords': ['의료', '병원', '환자', '진료', 'EMR', 'Healthcare', 'Medical', '헬스케어'],
        'tech_domains': ['Web', 'Security', 'Data', 'Cloud'],
        'industry': 'Healthcare / Medical'
    },
    'E-commerce': {
        'keywords': ['커머스', '쇼핑몰', '유통', 'E-commerce', 'Retail', '옴니채널', 'AI 추천'],
        'tech_domains': ['Web', 'Mobile', 'Cloud', 'Data'],
        'industry': 'E-commerce / Retail'
    },
    'Manufacturing': {
        'keywords': ['제조', '공장', 'MES', '품질', '예지 보전', 'Manufacturing', 'Factory', '스마트 팩토리'],
        'tech_domains': ['IoT', 'Data', 'Cloud', 'AI_ML'],
        'industry': 'Manufacturing / Industrial'
    },
    'Logistics': {
        'keywords': ['물류', '배송', '운송', 'Logistics', 'Transportation', 'IoT 플랫폼'],
        'tech_domains': ['IoT', 'Mobile', 'Data', 'Cloud'],
        'industry': 'Logistics / Transportation'
    }
}

def classify_project_domain(project_name: str) -> dict:
    """프로젝트 이름으로 도메인 분류"""
    for domain, info in DOMAIN_MAPPING.items():
        for keyword in info['keywords']:
            if keyword in project_name:
                return {
                    'knowledge_domain': domain,
                    'tech_domains': info['tech_domains'],
                    'client_industry': info['industry']
                }
    
    # 기본값
    return {
        'knowledge_domain': 'General',
        'tech_domains': ['Web', 'Cloud'],
        'client_industry': 'General'
    }

def add_domains_to_projects():
    """모든 프로젝트에 도메인 정보 추가"""
    projects_table = dynamodb.Table('Projects')
    
    print("=" * 80)
    print("프로젝트 도메인 정보 추가")
    print("=" * 80)
    
    # 모든 프로젝트 조회
    response = projects_table.scan()
    projects = response.get('Items', [])
    
    # 페이지네이션 처리
    while 'LastEvaluatedKey' in response:
        response = projects_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        projects.extend(response.get('Items', []))
    
    updated_count = 0
    skipped_count = 0
    
    for project in projects:
        project_id = project.get('project_id')
        project_name = project.get('project_name', '')
        
        # 이미 도메인 정보가 있으면 스킵
        if 'knowledge_domain' in project:
            skipped_count += 1
            continue
        
        # 도메인 분류
        domain_info = classify_project_domain(project_name)
        
        # 프로젝트 업데이트
        try:
            project.update({
                'knowledge_domain': domain_info['knowledge_domain'],
                'tech_domains': domain_info['tech_domains'],
                'client_industry': domain_info.get('client_industry', project.get('client_industry', 'General'))
            })
            
            projects_table.put_item(Item=project)
            print(f"✓ {project_id}: {project_name[:40]} → {domain_info['knowledge_domain']}")
            updated_count += 1
            
        except Exception as e:
            print(f"✗ {project_id}: 업데이트 실패 - {str(e)}")
    
    print(f"\n완료: {updated_count}개 업데이트, {skipped_count}개 스킵")
    return updated_count

def create_tech_trends_data():
    """TechTrends 테이블에 기술 트렌드 데이터 생성"""
    trends_table = dynamodb.Table('TechTrends')
    
    print("\n" + "=" * 80)
    print("TechTrends 데이터 생성")
    print("=" * 80)
    
    # 기술 트렌드 데이터
    tech_trends = [
        # 백엔드 기술
        {
            'tech_name': 'Java',
            'category': 'Backend',
            'trend_score': Decimal('85'),
            'demand_score': Decimal('90'),
            'growth_rate': Decimal('5.2'),
            'market_share': Decimal('35.5'),
            'related_domains': ['Finance', 'Healthcare', 'Manufacturing'],
            'skill_level_required': 'Intermediate',
            'avg_salary_impact': Decimal('15.0'),
            'description': '엔터프라이즈 애플리케이션 개발의 표준'
        },
        {
            'tech_name': 'Python',
            'category': 'Backend',
            'trend_score': Decimal('95'),
            'demand_score': Decimal('95'),
            'growth_rate': Decimal('12.8'),
            'market_share': Decimal('28.3'),
            'related_domains': ['Healthcare', 'E-commerce', 'Manufacturing'],
            'skill_level_required': 'Beginner',
            'avg_salary_impact': Decimal('18.0'),
            'description': 'AI/ML 및 데이터 분석의 핵심 언어'
        },
        {
            'tech_name': 'Node.js',
            'category': 'Backend',
            'trend_score': Decimal('88'),
            'demand_score': Decimal('85'),
            'growth_rate': Decimal('8.5'),
            'market_share': Decimal('22.1'),
            'related_domains': ['E-commerce', 'Aviation', 'Education'],
            'skill_level_required': 'Intermediate',
            'avg_salary_impact': Decimal('16.0'),
            'description': '실시간 애플리케이션 및 마이크로서비스'
        },
        {
            'tech_name': 'Go',
            'category': 'Backend',
            'trend_score': Decimal('82'),
            'demand_score': Decimal('78'),
            'growth_rate': Decimal('15.3'),
            'market_share': Decimal('8.7'),
            'related_domains': ['Telecommunications', 'Finance'],
            'skill_level_required': 'Advanced',
            'avg_salary_impact': Decimal('22.0'),
            'description': '고성능 분산 시스템 개발'
        },
        
        # 프론트엔드 기술
        {
            'tech_name': 'React',
            'category': 'Frontend',
            'trend_score': Decimal('92'),
            'demand_score': Decimal('93'),
            'growth_rate': Decimal('10.2'),
            'market_share': Decimal('42.8'),
            'related_domains': ['E-commerce', 'Healthcare', 'Education', 'Finance'],
            'skill_level_required': 'Intermediate',
            'avg_salary_impact': Decimal('14.0'),
            'description': '가장 인기있는 프론트엔드 라이브러리'
        },
        {
            'tech_name': 'Vue.js',
            'category': 'Frontend',
            'trend_score': Decimal('78'),
            'demand_score': Decimal('75'),
            'growth_rate': Decimal('6.8'),
            'market_share': Decimal('18.5'),
            'related_domains': ['Logistics', 'Manufacturing'],
            'skill_level_required': 'Beginner',
            'avg_salary_impact': Decimal('12.0'),
            'description': '점진적으로 채택 가능한 프레임워크'
        },
        {
            'tech_name': 'Angular',
            'category': 'Frontend',
            'trend_score': Decimal('72'),
            'demand_score': Decimal('70'),
            'growth_rate': Decimal('2.1'),
            'market_share': Decimal('15.2'),
            'related_domains': ['Finance', 'Healthcare'],
            'skill_level_required': 'Advanced',
            'avg_salary_impact': Decimal('13.0'),
            'description': '엔터프라이즈급 프론트엔드 프레임워크'
        },
        
        # 모바일 기술
        {
            'tech_name': 'React Native',
            'category': 'Mobile',
            'trend_score': Decimal('85'),
            'demand_score': Decimal('82'),
            'growth_rate': Decimal('9.5'),
            'market_share': Decimal('32.1'),
            'related_domains': ['E-commerce', 'Aviation', 'Education'],
            'skill_level_required': 'Intermediate',
            'avg_salary_impact': Decimal('17.0'),
            'description': '크로스 플랫폼 모바일 개발'
        },
        {
            'tech_name': 'Flutter',
            'category': 'Mobile',
            'trend_score': Decimal('88'),
            'demand_score': Decimal('80'),
            'growth_rate': Decimal('18.7'),
            'market_share': Decimal('28.5'),
            'related_domains': ['Aviation', 'E-commerce', 'Logistics'],
            'skill_level_required': 'Intermediate',
            'avg_salary_impact': Decimal('18.0'),
            'description': '빠르게 성장하는 크로스 플랫폼 프레임워크'
        },
        
        # 클라우드 기술
        {
            'tech_name': 'AWS',
            'category': 'Cloud',
            'trend_score': Decimal('94'),
            'demand_score': Decimal('96'),
            'growth_rate': Decimal('11.2'),
            'market_share': Decimal('52.3'),
            'related_domains': ['Finance', 'Healthcare', 'E-commerce', 'Manufacturing'],
            'skill_level_required': 'Intermediate',
            'avg_salary_impact': Decimal('20.0'),
            'description': '클라우드 컴퓨팅 시장 리더'
        },
        {
            'tech_name': 'Kubernetes',
            'category': 'Cloud',
            'trend_score': Decimal('91'),
            'demand_score': Decimal('89'),
            'growth_rate': Decimal('14.5'),
            'market_share': Decimal('38.7'),
            'related_domains': ['Telecommunications', 'Finance', 'Healthcare'],
            'skill_level_required': 'Advanced',
            'avg_salary_impact': Decimal('25.0'),
            'description': '컨테이너 오케스트레이션 표준'
        },
        {
            'tech_name': 'Docker',
            'category': 'Cloud',
            'trend_score': Decimal('87'),
            'demand_score': Decimal('88'),
            'growth_rate': Decimal('7.3'),
            'market_share': Decimal('45.2'),
            'related_domains': ['Finance', 'Healthcare', 'E-commerce'],
            'skill_level_required': 'Intermediate',
            'avg_salary_impact': Decimal('16.0'),
            'description': '컨테이너화 기술의 표준'
        },
        
        # 데이터 기술
        {
            'tech_name': 'PostgreSQL',
            'category': 'Database',
            'trend_score': Decimal('86'),
            'demand_score': Decimal('84'),
            'growth_rate': Decimal('8.9'),
            'market_share': Decimal('28.5'),
            'related_domains': ['Healthcare', 'Education', 'Finance'],
            'skill_level_required': 'Intermediate',
            'avg_salary_impact': Decimal('12.0'),
            'description': '오픈소스 관계형 데이터베이스'
        },
        {
            'tech_name': 'MongoDB',
            'category': 'Database',
            'trend_score': Decimal('83'),
            'demand_score': Decimal('81'),
            'growth_rate': Decimal('7.2'),
            'market_share': Decimal('22.8'),
            'related_domains': ['E-commerce', 'Aviation', 'Education'],
            'skill_level_required': 'Beginner',
            'avg_salary_impact': Decimal('14.0'),
            'description': 'NoSQL 문서 데이터베이스'
        },
        {
            'tech_name': 'Redis',
            'category': 'Database',
            'trend_score': Decimal('84'),
            'demand_score': Decimal('82'),
            'growth_rate': Decimal('9.1'),
            'market_share': Decimal('18.3'),
            'related_domains': ['E-commerce', 'Aviation', 'Finance'],
            'skill_level_required': 'Intermediate',
            'avg_salary_impact': Decimal('15.0'),
            'description': '인메모리 데이터 스토어'
        },
        
        # AI/ML 기술
        {
            'tech_name': 'TensorFlow',
            'category': 'AI_ML',
            'trend_score': Decimal('89'),
            'demand_score': Decimal('85'),
            'growth_rate': Decimal('13.5'),
            'market_share': Decimal('35.2'),
            'related_domains': ['Healthcare', 'E-commerce', 'Manufacturing'],
            'skill_level_required': 'Advanced',
            'avg_salary_impact': Decimal('28.0'),
            'description': '딥러닝 프레임워크'
        },
        {
            'tech_name': 'PyTorch',
            'category': 'AI_ML',
            'trend_score': Decimal('92'),
            'demand_score': Decimal('87'),
            'growth_rate': Decimal('16.8'),
            'market_share': Decimal('32.8'),
            'related_domains': ['Healthcare', 'Aviation', 'Telecommunications'],
            'skill_level_required': 'Advanced',
            'avg_salary_impact': Decimal('30.0'),
            'description': '연구 및 프로덕션 ML 프레임워크'
        },
        
        # IoT 기술
        {
            'tech_name': 'IoT',
            'category': 'IoT',
            'trend_score': Decimal('86'),
            'demand_score': Decimal('83'),
            'growth_rate': Decimal('12.3'),
            'market_share': Decimal('25.7'),
            'related_domains': ['Manufacturing', 'Logistics', 'Healthcare'],
            'skill_level_required': 'Advanced',
            'avg_salary_impact': Decimal('22.0'),
            'description': '사물인터넷 플랫폼 및 디바이스'
        },
        
        # 보안 기술
        {
            'tech_name': 'OAuth',
            'category': 'Security',
            'trend_score': Decimal('81'),
            'demand_score': Decimal('85'),
            'growth_rate': Decimal('6.5'),
            'market_share': Decimal('42.1'),
            'related_domains': ['Finance', 'Healthcare', 'E-commerce'],
            'skill_level_required': 'Intermediate',
            'avg_salary_impact': Decimal('14.0'),
            'description': '인증 및 권한 부여 프레임워크'
        },
        {
            'tech_name': 'JWT',
            'category': 'Security',
            'trend_score': Decimal('79'),
            'demand_score': Decimal('82'),
            'growth_rate': Decimal('5.8'),
            'market_share': Decimal('38.5'),
            'related_domains': ['Finance', 'Healthcare', 'E-commerce'],
            'skill_level_required': 'Beginner',
            'avg_salary_impact': Decimal('12.0'),
            'description': 'JSON 웹 토큰 인증'
        },
        
        # DevOps 기술
        {
            'tech_name': 'Jenkins',
            'category': 'DevOps',
            'trend_score': Decimal('76'),
            'demand_score': Decimal('78'),
            'growth_rate': Decimal('3.2'),
            'market_share': Decimal('32.5'),
            'related_domains': ['Finance', 'Healthcare', 'Manufacturing'],
            'skill_level_required': 'Intermediate',
            'avg_salary_impact': Decimal('13.0'),
            'description': 'CI/CD 자동화 서버'
        },
        {
            'tech_name': 'GitHub Actions',
            'category': 'DevOps',
            'trend_score': Decimal('90'),
            'demand_score': Decimal('85'),
            'growth_rate': Decimal('22.5'),
            'market_share': Decimal('28.3'),
            'related_domains': ['E-commerce', 'Education', 'Aviation'],
            'skill_level_required': 'Beginner',
            'avg_salary_impact': Decimal('15.0'),
            'description': 'GitHub 통합 CI/CD'
        },
        
        # 도메인 특화 기술
        {
            'tech_name': 'HL7',
            'category': 'Healthcare',
            'trend_score': Decimal('75'),
            'demand_score': Decimal('88'),
            'growth_rate': Decimal('8.5'),
            'market_share': Decimal('65.2'),
            'related_domains': ['Healthcare'],
            'skill_level_required': 'Advanced',
            'avg_salary_impact': Decimal('25.0'),
            'description': '의료 데이터 교환 표준'
        },
        {
            'tech_name': 'FHIR',
            'category': 'Healthcare',
            'trend_score': Decimal('82'),
            'demand_score': Decimal('85'),
            'growth_rate': Decimal('15.7'),
            'market_share': Decimal('42.8'),
            'related_domains': ['Healthcare'],
            'skill_level_required': 'Advanced',
            'avg_salary_impact': Decimal('28.0'),
            'description': '차세대 의료 데이터 표준'
        },
        {
            'tech_name': 'Blockchain',
            'category': 'Blockchain',
            'trend_score': Decimal('78'),
            'demand_score': Decimal('72'),
            'growth_rate': Decimal('10.5'),
            'market_share': Decimal('8.5'),
            'related_domains': ['Finance'],
            'skill_level_required': 'Expert',
            'avg_salary_impact': Decimal('35.0'),
            'description': '분산원장 기술'
        },
        {
            'tech_name': '5G',
            'category': 'Telecommunications',
            'trend_score': Decimal('88'),
            'demand_score': Decimal('82'),
            'growth_rate': Decimal('18.2'),
            'market_share': Decimal('15.3'),
            'related_domains': ['Telecommunications'],
            'skill_level_required': 'Expert',
            'avg_salary_impact': Decimal('32.0'),
            'description': '5세대 이동통신 기술'
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for trend in tech_trends:
        try:
            # 기존 데이터 확인
            response = trends_table.get_item(Key={'tech_name': trend['tech_name']})
            
            if 'Item' in response:
                # 업데이트
                trends_table.put_item(Item=trend)
                print(f"✓ 업데이트: {trend['tech_name']} (트렌드: {trend['trend_score']}, 수요: {trend['demand_score']})")
                updated_count += 1
            else:
                # 생성
                trends_table.put_item(Item=trend)
                print(f"✓ 생성: {trend['tech_name']} (트렌드: {trend['trend_score']}, 수요: {trend['demand_score']})")
                created_count += 1
                
        except Exception as e:
            print(f"✗ 실패: {trend['tech_name']} - {str(e)}")
    
    print(f"\n완료: {created_count}개 생성, {updated_count}개 업데이트")
    return created_count + updated_count

def main():
    print("=" * 80)
    print("도메인 데이터 추가 및 TechTrends 생성")
    print("=" * 80)
    
    # 1. 프로젝트에 도메인 추가
    project_count = add_domains_to_projects()
    
    # 2. TechTrends 데이터 생성
    trend_count = create_tech_trends_data()
    
    print("\n" + "=" * 80)
    print("✓ 모든 작업 완료!")
    print("=" * 80)
    print(f"\n프로젝트 도메인 추가: {project_count}개")
    print(f"TechTrends 데이터: {trend_count}개")
    
    print("\n다음 명령어로 확인하세요:")
    print("  python deployment/verify_domain_data.py")

if __name__ == '__main__':
    main()
