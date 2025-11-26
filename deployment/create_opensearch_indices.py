#!/usr/bin/env python3
"""
OpenSearch 인덱스 생성 스크립트

이 스크립트는 HR Resource Optimization 시스템에 필요한 OpenSearch 인덱스를 생성합니다.
- employee_profiles: 직원 프로필 벡터 검색용
- project_requirements: 프로젝트 요구사항 벡터 검색용
"""

import boto3
import json
import sys
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

def get_opensearch_client(endpoint, region='us-east-2'):
    """
    OpenSearch 클라이언트를 생성합니다.
    
    Args:
        endpoint: OpenSearch 도메인 엔드포인트
        region: AWS 리전
        
    Returns:
        OpenSearch 클라이언트 인스턴스
    """
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        'es',
        session_token=credentials.token
    )
    
    client = OpenSearch(
        hosts=[{'host': endpoint, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    
    return client

def create_employee_profiles_index(client):
    """
    employee_profiles 인덱스를 생성합니다.
    
    이 인덱스는 직원 프로필 정보와 벡터 임베딩을 저장합니다.
    """
    index_name = 'employee_profiles'
    
    # 인덱스 매핑 정의
    index_body = {
        'settings': {
            'index': {
                'number_of_shards': 2,
                'number_of_replicas': 1,
                'knn': True,  # k-NN 플러그인 활성화
                'knn.algo_param.ef_search': 512
            }
        },
        'mappings': {
            'properties': {
                'user_id': {
                    'type': 'keyword'
                },
                'name': {
                    'type': 'text',
                    'fields': {
                        'keyword': {
                            'type': 'keyword'
                        }
                    }
                },
                'role': {
                    'type': 'keyword'
                },
                'years_of_experience': {
                    'type': 'integer'
                },
                'skills': {
                    'type': 'nested',
                    'properties': {
                        'name': {
                            'type': 'keyword'
                        },
                        'level': {
                            'type': 'keyword'
                        },
                        'years': {
                            'type': 'integer'
                        }
                    }
                },
                'profile_vector': {
                    'type': 'knn_vector',
                    'dimension': 1536,  # Titan Embeddings 차원
                    'method': {
                        'name': 'hnsw',
                        'space_type': 'cosinesimil',
                        'engine': 'nmslib',
                        'parameters': {
                            'ef_construction': 512,
                            'm': 16
                        }
                    }
                },
                'created_at': {
                    'type': 'date'
                },
                'updated_at': {
                    'type': 'date'
                }
            }
        }
    }
    
    # 인덱스가 이미 존재하는지 확인
    if client.indices.exists(index=index_name):
        print(f"인덱스 '{index_name}'가 이미 존재합니다. 삭제 후 재생성합니다.")
        client.indices.delete(index=index_name)
    
    # 인덱스 생성
    response = client.indices.create(index=index_name, body=index_body)
    print(f"인덱스 '{index_name}' 생성 완료: {response}")
    
    return response

def create_project_requirements_index(client):
    """
    project_requirements 인덱스를 생성합니다.
    
    이 인덱스는 프로젝트 요구사항 정보와 벡터 임베딩을 저장합니다.
    """
    index_name = 'project_requirements'
    
    # 인덱스 매핑 정의
    index_body = {
        'settings': {
            'index': {
                'number_of_shards': 2,
                'number_of_replicas': 1,
                'knn': True,
                'knn.algo_param.ef_search': 512
            }
        },
        'mappings': {
            'properties': {
                'project_id': {
                    'type': 'keyword'
                },
                'project_name': {
                    'type': 'text',
                    'fields': {
                        'keyword': {
                            'type': 'keyword'
                        }
                    }
                },
                'client_industry': {
                    'type': 'keyword'
                },
                'required_skills': {
                    'type': 'keyword'
                },
                'tech_stack': {
                    'type': 'object',
                    'properties': {
                        'backend': {
                            'type': 'keyword'
                        },
                        'frontend': {
                            'type': 'keyword'
                        },
                        'data': {
                            'type': 'keyword'
                        },
                        'infra': {
                            'type': 'keyword'
                        }
                    }
                },
                'requirement_vector': {
                    'type': 'knn_vector',
                    'dimension': 1536,
                    'method': {
                        'name': 'hnsw',
                        'space_type': 'cosinesimil',
                        'engine': 'nmslib',
                        'parameters': {
                            'ef_construction': 512,
                            'm': 16
                        }
                    }
                },
                'created_at': {
                    'type': 'date'
                },
                'updated_at': {
                    'type': 'date'
                }
            }
        }
    }
    
    # 인덱스가 이미 존재하는지 확인
    if client.indices.exists(index=index_name):
        print(f"인덱스 '{index_name}'가 이미 존재합니다. 삭제 후 재생성합니다.")
        client.indices.delete(index=index_name)
    
    # 인덱스 생성
    response = client.indices.create(index=index_name, body=index_body)
    print(f"인덱스 '{index_name}' 생성 완료: {response}")
    
    return response

def main():
    """
    메인 함수: OpenSearch 인덱스를 생성합니다.
    """
    if len(sys.argv) < 2:
        print("사용법: python create_opensearch_indices.py <opensearch_endpoint>")
        print("예시: python create_opensearch_indices.py search-hr-employee-search-team2-xxx.us-east-2.es.amazonaws.com")
        sys.exit(1)
    
    endpoint = sys.argv[1]
    
    try:
        print(f"OpenSearch 엔드포인트에 연결 중: {endpoint}")
        client = get_opensearch_client(endpoint)
        
        # 클러스터 상태 확인
        health = client.cluster.health()
        print(f"클러스터 상태: {health['status']}")
        
        # 인덱스 생성
        print("\n=== employee_profiles 인덱스 생성 ===")
        create_employee_profiles_index(client)
        
        print("\n=== project_requirements 인덱스 생성 ===")
        create_project_requirements_index(client)
        
        # 생성된 인덱스 확인
        print("\n=== 생성된 인덱스 목록 ===")
        indices = client.cat.indices(format='json')
        for index in indices:
            if index['index'] in ['employee_profiles', 'project_requirements']:
                print(f"- {index['index']}: {index['docs.count']} 문서, {index['store.size']}")
        
        print("\n✅ 모든 인덱스 생성 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
