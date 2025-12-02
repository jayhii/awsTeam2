#!/usr/bin/env python3
"""
도메인 관련 데이터 생성 및 DynamoDB 업데이트

기술 도메인: 기술 스택 기반 (Cloud, AI/ML, Web, Mobile 등)
지식 도메인: 산업 분야 기반 (Finance, Healthcare, Aviation, Education 등)
"""

import boto3
from decimal import Decimal
import json

REGION = "us-east-2"
dynamodb = boto3.resource('dynamodb', region_name=REGION)

# 지식 도메인 정의 (산업 분야)
KNOWLEDGE_DOMAINS = {
    'Finance': {
        'name': 'Finance / Banking',
        'description': '금융 및 은행 서비스',
        'key_skills': ['Java', 'Spring', 'Oracle', 'Security', 'Compliance', 'Blockchain'],
        'sub_domains': ['Core Banking', 'Payment Systems', 'Trading Platforms', 'Insurance']
    },
    'Healthcare': {
        'name': 'Healthcare / Medical',
        'description': '의료 및 헬스케어',
        'key_skills': ['Python', 'HIPAA', 'HL7', 'FHIR', 'Data Privacy', 'Medical Imaging'],
        'sub_domains': ['EMR/EHR', 'Telemedicine', 'Medical Devices', 'Health Analytics']
    },
    'Aviation': {
        'name': 'Aviation / Aerospace',
        'description': '항공 및 우주',
        'key_skills': ['C++', 'Real-time Systems', 'Safety Critical', 'Embedded', 'IoT'],
        'sub_domains': ['Flight Systems', 'Ground Operations', 'Maintenance', 'Air Traffic']
    },
    'Education': {
        'name': 'Education / E-Learning',
        'description': '교육 및 이러닝',
        'key_skills': ['LMS', 'Video Streaming', 'Mobile', 'Gamification', 'React', 'Node.js'],
        'sub_domains': ['Online Learning', 'School Management', 'Assessment', 'Content Management']
    },
    'E-commerce': {
        'name': 'E-commerce / Retail',
        'description': '전자상거래 및 유통',
        'key_skills': ['Node.js', 'React', 'MongoDB', 'Payment Gateway', 'AWS', 'Microservices'],
        'sub_domains': ['Online Shopping', 'Inventory Management', 'Order Fulfillment', 'CRM']
    },
    'Manufacturing': {
        'name': 'Manufacturing / Industrial',
        'description': '제조 및 산업',
        'key_skills': ['IoT', 'Python', 'Data Analytics', 'ERP', 'MES', 'SCADA'],
        'sub_domains': ['Production Management', 'Quality Control', 'Supply Chain', 'Automation']
    },
    'Logistics': {
        'name': 'Logistics / Transportation',
        'description': '물류 및 운송',
        'key_skills': ['GPS', 'Route Optimization', 'Mobile', 'Real-time Tracking', 'IoT'],
        'sub_domains': ['Fleet Management', 'Warehouse Management', 'Last Mile Delivery', 'Freight']
    },
    'Telecommunications': {
        'name': 'Telecommunications',
        'description': '통신 및 네트워크',
        'key_skills': ['5G', 'Network', 'Real-time', 'High Availability', 'SDN', 'NFV'],
        'sub_domains': ['Mobile Networks', 'Broadband', 'IoT Connectivity', 'Network Management']
    }
}

# 기술 도메인 정의 (기술 스택 기반)
TECH_DOMAINS = {
    'Cloud': {
        'name': 'Cloud Computing',
        'description': '클라우드 컴퓨팅 및 인프라',
        'technologies': ['AWS', 'Azure', 'GCP', 'Kubernetes', 'Docker', 'Terraform'],
        'maturity_level': 'Advanced'
    },
    'AI_ML': {
        'name': 'AI / Machine Learning',
        'description': '인공지능 및 머신러닝',
        'technologies': ['Python', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'NLP', 'Computer Vision'],
        'maturity_level': 'Intermediate'
    },
    'Web': {
        'name': 'Web Development',
        'description': '웹 개발',
        'technologies': ['React', 'Vue.js', 'Angular', 'Node.js', 'Django', 'Spring Boot'],
        'maturity_level': 'Advanced'
    },
    'Mobile': {
        'name': 'Mobile Development',
        'description': '모바일 앱 개발',
        'technologies': ['React Native', 'Flutter', 'Swift', 'Kotlin', 'iOS', 'Android'],
        'maturity_level': 'Intermediate'
    },
    'Data': {
        'name': 'Data Engineering',
        'description': '데이터 엔지니어링 및 분석',
        'technologies': ['Spark', 'Hadoop', 'Kafka', 'Airflow', 'SQL', 'NoSQL'],
        'maturity_level': 'Advanced'
    },
    'Security': {
        'name': 'Security',
        'description': '보안 및 컴플라이언스',
        'technologies': ['OAuth', 'JWT', 'Encryption', 'Penetration Testing', 'SIEM', 'IAM'],
        'maturity_level': 'Intermediate'
    },
    'DevOps': {
        'name': 'DevOps',
        'description': 'DevOps 및 CI/CD',
        'technologies': ['Jenkins', 'GitLab CI', 'GitHub Actions', 'Ansible', 'Prometheus', 'Grafana'],
        'maturity_level': 'Advanced'
    },
    'Blockchain': {
        'name': 'Blockchain',
        'description': '블록체인 및 분산원장',
        'technologies': ['Ethereum', 'Hyperledger', 'Solidity', 'Smart Contracts', 'Web3'],
        'maturity_level': 'Beginner'
    }
}

def update_projects_with_domains():
    """프로젝트에 도메인 정보 추가"""
    projects_table = dynamodb.Table('Projects')
    
    print("=" * 60)
    print("프로젝트 도메인 정보 업데이트")
    print("=" * 60)
    
    # 프로젝트별 도메인 매핑
    project_domain_mapping = [
        {
            'project_id': 'P_001',
            'knowledge_domain': 'Finance',
            'tech_domains': ['Cloud', 'Web', 'Security', 'Data'],
            'domain_expertise_required': ['Core Banking', 'Payment Systems'],
            'industry_certifications': ['PCI-DSS', 'ISO 27001']
        },
        {
            'project_id': 'P_002',
            'knowledge_domain': 'Manufacturing',
            'tech_domains': ['IoT', 'Data', 'Cloud'],
            'domain_expertise_required': ['Production Management', 'Quality Control'],
            'industry_certifications': ['ISO 9001', 'Six Sigma']
        },
        {
            'project_id': 'P_003',
            'knowledge_domain': 'E-commerce',
            'tech_domains': ['Web', 'Mobile', 'Cloud', 'Data'],
            'domain_expertise_required': ['Online Shopping', 'Inventory Management'],
            'industry_certifications': []
        }
    ]
    
    # 추가 프로젝트 생성 (다양한 도메인)
    additional_projects = [
        {
            'project_id': 'P_101',
            'project_name': '병원 통합 EMR 시스템 구축',
            'client_industry': 'Healthcare / Medical',
            'knowledge_domain': 'Healthcare',
            'tech_domains': ['Web', 'Security', 'Data', 'Cloud'],
            'domain_expertise_required': ['EMR/EHR', 'Medical Devices'],
            'industry_certifications': ['HIPAA', 'HL7'],
            'description': '대형 병원의 전자의무기록(EMR) 시스템 통합 및 고도화',
            'period': {
                'start': '2024-03-01',
                'end': '2025-02-28',
                'duration_months': 12
            },
            'budget_scale': '50억원',
            'tech_stack': {
                'backend': ['Java', 'Spring Boot', 'PostgreSQL'],
                'frontend': ['React', 'TypeScript'],
                'data': ['HL7', 'FHIR', 'Medical Imaging'],
                'infra': ['AWS', 'Docker', 'Kubernetes']
            },
            'requirements': [
                'HIPAA 컴플라이언스 준수',
                '의료 데이터 표준 (HL7, FHIR) 적용',
                '실시간 환자 모니터링',
                '의료 영상 통합',
                '전자처방전 시스템'
            ],
            'team_size': 15,
            'status': 'active'
        },
        {
            'project_id': 'P_102',
            'project_name': '항공사 승객 서비스 플랫폼',
            'client_industry': 'Aviation / Aerospace',
            'knowledge_domain': 'Aviation',
            'tech_domains': ['Mobile', 'Web', 'Cloud', 'AI_ML'],
            'domain_expertise_required': ['Flight Systems', 'Ground Operations'],
            'industry_certifications': ['IATA', 'ICAO'],
            'description': '항공사 승객 예약, 체크인, 탑승 통합 플랫폼',
            'period': {
                'start': '2024-01-15',
                'end': '2024-12-31',
                'duration_months': 12
            },
            'budget_scale': '40억원',
            'tech_stack': {
                'backend': ['Node.js', 'Express', 'MongoDB'],
                'frontend': ['React Native', 'Flutter'],
                'data': ['Redis', 'Elasticsearch'],
                'infra': ['AWS', 'CloudFront', 'Lambda']
            },
            'requirements': [
                '실시간 항공편 정보 연동',
                '모바일 체크인 및 탑승권',
                '수하물 추적',
                'AI 기반 고객 서비스',
                '다국어 지원'
            ],
            'team_size': 12,
            'status': 'active'
        },
        {
            'project_id': 'P_103',
            'project_name': '온라인 교육 플랫폼 구축',
            'client_industry': 'Education / E-Learning',
            'knowledge_domain': 'Education',
            'tech_domains': ['Web', 'Mobile', 'AI_ML', 'Cloud'],
            'domain_expertise_required': ['Online Learning', 'Assessment'],
            'industry_certifications': ['SCORM', 'LTI'],
            'description': 'K-12 및 대학 온라인 교육 통합 플랫폼',
            'period': {
                'start': '2024-02-01',
                'end': '2025-01-31',
                'duration_months': 12
            },
            'budget_scale': '30억원',
            'tech_stack': {
                'backend': ['Python', 'Django', 'PostgreSQL'],
                'frontend': ['React', 'Next.js'],
                'data': ['Video Streaming', 'CDN'],
                'infra': ['AWS', 'S3', 'CloudFront']
            },
            'requirements': [
                'LMS 기능 (강의, 과제, 시험)',
                '실시간 화상 강의',
                'AI 기반 학습 추천',
                '학습 분석 대시보드',
                '모바일 앱'
            ],
            'team_size': 10,
            'status': 'active'
        },
        {
            'project_id': 'P_104',
            'project_name': '물류 통합 관리 시스템',
            'client_industry': 'Logistics / Transportation',
            'knowledge_domain': 'Logistics',
            'tech_domains': ['IoT', 'Mobile', 'Data', 'Cloud'],
            'domain_expertise_required': ['Fleet Management', 'Warehouse Management'],
            'industry_certifications': [],
            'description': '전국 물류 네트워크 통합 관리 및 최적화',
            'period': {
                'start': '2024-04-01',
                'end': '2025-03-31',
                'duration_months': 12
            },
            'budget_scale': '35억원',
            'tech_stack': {
                'backend': ['Java', 'Spring Boot', 'MySQL'],
                'frontend': ['Vue.js', 'Vuetify'],
                'data': ['GPS', 'IoT', 'Route Optimization'],
                'infra': ['AWS', 'IoT Core', 'Lambda']
            },
            'requirements': [
                '실시간 차량 위치 추적',
                '배송 경로 최적화',
                '창고 재고 관리',
                '배송 예측 분석',
                '모바일 드라이버 앱'
            ],
            'team_size': 13,
            'status': 'active'
        },
        {
            'project_id': 'P_105',
            'project_name': '5G 네트워크 관리 시스템',
            'client_industry': 'Telecommunications',
            'knowledge_domain': 'Telecommunications',
            'tech_domains': ['Cloud', 'Data', 'DevOps'],
            'domain_expertise_required': ['Mobile Networks', 'Network Management'],
            'industry_certifications': ['3GPP', '5G Certification'],
            'description': '5G 네트워크 모니터링 및 관리 플랫폼',
            'period': {
                'start': '2024-05-01',
                'end': '2025-04-30',
                'duration_months': 12
            },
            'budget_scale': '60억원',
            'tech_stack': {
                'backend': ['Go', 'gRPC', 'Cassandra'],
                'frontend': ['React', 'D3.js'],
                'data': ['Kafka', 'Prometheus', 'Grafana'],
                'infra': ['Kubernetes', 'Helm', 'Istio']
            },
            'requirements': [
                '실시간 네트워크 모니터링',
                '장애 예측 및 자동 복구',
                '성능 최적화',
                '5G 슬라이싱 관리',
                'AI 기반 이상 탐지'
            ],
            'team_size': 18,
            'status': 'active'
        }
    ]
    
    updated_count = 0
    created_count = 0
    
    # 기존 프로젝트 업데이트
    for mapping in project_domain_mapping:
        try:
            response = projects_table.get_item(Key={'project_id': mapping['project_id']})
            if 'Item' in response:
                project = response['Item']
                project.update({
                    'knowledge_domain': mapping['knowledge_domain'],
                    'tech_domains': mapping['tech_domains'],
                    'domain_expertise_required': mapping['domain_expertise_required'],
                    'industry_certifications': mapping['industry_certifications']
                })
                projects_table.put_item(Item=project)
                print(f"✓ 업데이트: {mapping['project_id']} - {mapping['knowledge_domain']}")
                updated_count += 1
        except Exception as e:
            print(f"✗ 업데이트 실패: {mapping['project_id']} - {str(e)}")
    
    # 새 프로젝트 생성
    for project in additional_projects:
        try:
            # Decimal 변환
            if 'period' in project and 'duration_months' in project['period']:
                project['period']['duration_months'] = Decimal(str(project['period']['duration_months']))
            if 'team_size' in project:
                project['team_size'] = Decimal(str(project['team_size']))
            
            projects_table.put_item(Item=project)
            print(f"✓ 생성: {project['project_id']} - {project['project_name']}")
            created_count += 1
        except Exception as e:
            print(f"✗ 생성 실패: {project['project_id']} - {str(e)}")
    
    print(f"\n완료: {updated_count}개 업데이트, {created_count}개 생성")

def update_employees_with_domain_experience():
    """직원에 도메인 경험 추가"""
    employees_table = dynamodb.Table('Employees')
    
    print("\n" + "=" * 60)
    print("직원 도메인 경험 업데이트")
    print("=" * 60)
    
    # 직원별 도메인 경험 매핑
    employee_domain_experience = [
        {
            'user_id': 'U_001',
            'domain_experience': {
                'knowledge_domains': [
                    {'domain': 'Finance', 'years': 5, 'projects': 3},
                    {'domain': 'E-commerce', 'years': 2, 'projects': 1}
                ],
                'tech_domains': [
                    {'domain': 'Cloud', 'proficiency': 'Advanced'},
                    {'domain': 'Web', 'proficiency': 'Expert'},
                    {'domain': 'Security', 'proficiency': 'Advanced'}
                ]
            },
            'domain_certifications': ['AWS Solutions Architect', 'PCI-DSS']
        },
        {
            'user_id': 'U_002',
            'domain_experience': {
                'knowledge_domains': [
                    {'domain': 'Manufacturing', 'years': 4, 'projects': 2},
                    {'domain': 'Logistics', 'years': 1, 'projects': 1}
                ],
                'tech_domains': [
                    {'domain': 'IoT', 'proficiency': 'Advanced'},
                    {'domain': 'Data', 'proficiency': 'Advanced'},
                    {'domain': 'Cloud', 'proficiency': 'Intermediate'}
                ]
            },
            'domain_certifications': ['ISO 9001', 'Six Sigma Green Belt']
        },
        {
            'user_id': 'U_003',
            'domain_experience': {
                'knowledge_domains': [
                    {'domain': 'E-commerce', 'years': 3, 'projects': 2}
                ],
                'tech_domains': [
                    {'domain': 'Web', 'proficiency': 'Advanced'},
                    {'domain': 'Mobile', 'proficiency': 'Intermediate'},
                    {'domain': 'Cloud', 'proficiency': 'Advanced'}
                ]
            },
            'domain_certifications': ['AWS Developer Associate']
        }
    ]
    
    updated_count = 0
    
    for exp in employee_domain_experience:
        try:
            response = employees_table.get_item(Key={'user_id': exp['user_id']})
            if 'Item' in response:
                employee = response['Item']
                employee['domain_experience'] = exp['domain_experience']
                employee['domain_certifications'] = exp['domain_certifications']
                employees_table.put_item(Item=employee)
                print(f"✓ 업데이트: {exp['user_id']}")
                updated_count += 1
        except Exception as e:
            print(f"✗ 업데이트 실패: {exp['user_id']} - {str(e)}")
    
    print(f"\n완료: {updated_count}개 업데이트")

def create_domain_portfolio_table():
    """도메인 포트폴리오 테이블 생성"""
    print("\n" + "=" * 60)
    print("도메인 포트폴리오 테이블 생성")
    print("=" * 60)
    
    try:
        table = dynamodb.create_table(
            TableName='DomainPortfolio',
            KeySchema=[
                {'AttributeName': 'portfolio_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'portfolio_id', 'AttributeType': 'S'},
                {'AttributeName': 'domain_type', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'DomainTypeIndex',
                    'KeySchema': [
                        {'AttributeName': 'domain_type', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            Tags=[
                {'Key': 'Team', 'Value': 'Team2'},
                {'Key': 'Project', 'Value': 'HR-Resource-Optimization'}
            ]
        )
        
        print("✓ DomainPortfolio 테이블 생성 중...")
        table.wait_until_exists()
        print("✓ 테이블 생성 완료!")
        
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print("✓ DomainPortfolio 테이블이 이미 존재합니다.")
    except Exception as e:
        print(f"✗ 테이블 생성 실패: {str(e)}")

def populate_domain_portfolio():
    """도메인 포트폴리오 데이터 생성"""
    portfolio_table = dynamodb.Table('DomainPortfolio')
    
    print("\n" + "=" * 60)
    print("도메인 포트폴리오 데이터 생성")
    print("=" * 60)
    
    # 지식 도메인 포트폴리오
    knowledge_portfolio = []
    for domain_key, domain_info in KNOWLEDGE_DOMAINS.items():
        knowledge_portfolio.append({
            'portfolio_id': f'KD_{domain_key}',
            'domain_type': 'knowledge',
            'domain_key': domain_key,
            'domain_name': domain_info['name'],
            'description': domain_info['description'],
            'key_skills': domain_info['key_skills'],
            'sub_domains': domain_info['sub_domains'],
            'current_projects': Decimal('0'),
            'available_experts': Decimal('0'),
            'maturity_level': 'Developing'
        })
    
    # 기술 도메인 포트폴리오
    tech_portfolio = []
    for domain_key, domain_info in TECH_DOMAINS.items():
        tech_portfolio.append({
            'portfolio_id': f'TD_{domain_key}',
            'domain_type': 'tech',
            'domain_key': domain_key,
            'domain_name': domain_info['name'],
            'description': domain_info['description'],
            'technologies': domain_info['technologies'],
            'maturity_level': domain_info['maturity_level'],
            'current_projects': Decimal('0'),
            'skilled_employees': Decimal('0')
        })
    
    created_count = 0
    
    # 지식 도메인 저장
    for item in knowledge_portfolio:
        try:
            portfolio_table.put_item(Item=item)
            print(f"✓ 생성: {item['domain_name']}")
            created_count += 1
        except Exception as e:
            print(f"✗ 생성 실패: {item['domain_name']} - {str(e)}")
    
    # 기술 도메인 저장
    for item in tech_portfolio:
        try:
            portfolio_table.put_item(Item=item)
            print(f"✓ 생성: {item['domain_name']}")
            created_count += 1
        except Exception as e:
            print(f"✗ 생성 실패: {item['domain_name']} - {str(e)}")
    
    print(f"\n완료: {created_count}개 생성")

def main():
    print("=" * 60)
    print("도메인 데이터 생성 시작")
    print("=" * 60)
    
    # 1. 프로젝트에 도메인 정보 추가
    update_projects_with_domains()
    
    # 2. 직원에 도메인 경험 추가
    update_employees_with_domain_experience()
    
    # 3. 도메인 포트폴리오 테이블 생성
    create_domain_portfolio_table()
    
    # 4. 도메인 포트폴리오 데이터 생성
    populate_domain_portfolio()
    
    print("\n" + "=" * 60)
    print("✓ 모든 도메인 데이터 생성 완료!")
    print("=" * 60)
    
    print("\n생성된 데이터:")
    print("  - 지식 도메인: Finance, Healthcare, Aviation, Education, E-commerce, Manufacturing, Logistics, Telecommunications")
    print("  - 기술 도메인: Cloud, AI/ML, Web, Mobile, Data, Security, DevOps, Blockchain")
    print("  - 신규 프로젝트: 5개 (Healthcare, Aviation, Education, Logistics, Telecommunications)")
    print("  - DomainPortfolio 테이블: 16개 항목")

if __name__ == '__main__':
    main()
