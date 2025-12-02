#!/usr/bin/env python3
"""
도메인 분석 API 직접 테스트
"""

import requests
import json

# API 엔드포인트
API_BASE_URL = "https://ifeniowvpb.execute-api.us-east-2.amazonaws.com/prod"
ENDPOINT = f"{API_BASE_URL}/domain-analysis"

def test_domain_analysis():
    """도메인 분석 API 테스트"""
    print("=" * 60)
    print("도메인 분석 API 테스트")
    print("=" * 60)
    print(f"\nURL: {ENDPOINT}")
    
    # 요청 데이터
    payload = {
        "analysis_type": "new_domains"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"\n요청 데이터:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    try:
        print("\n요청 전송 중...")
        response = requests.post(
            ENDPOINT,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"\n응답 상태 코드: {response.status_code}")
        print(f"응답 헤더:")
        for key, value in response.headers.items():
            if 'access-control' in key.lower() or 'content-type' in key.lower():
                print(f"  {key}: {value}")
        
        if response.status_code == 200:
            print("\n✓ API 호출 성공!")
            data = response.json()
            print(f"\n응답 데이터:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"\n✗ API 호출 실패!")
            print(f"응답 내용: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"\n✗ 연결 오류: {str(e)}")
        print("  - API Gateway가 존재하지 않거나 접근할 수 없습니다.")
    except requests.exceptions.Timeout:
        print(f"\n✗ 타임아웃: 30초 내에 응답이 없습니다.")
    except Exception as e:
        print(f"\n✗ 오류 발생: {str(e)}")

if __name__ == '__main__':
    test_domain_analysis()
