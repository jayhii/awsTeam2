#!/usr/bin/env python3
"""
모든 API 엔드포인트 테스트
"""

import requests

# API 엔드포인트
API_BASE_URL = "https://ifeniowvpb.execute-api.us-east-2.amazonaws.com/prod"

endpoints = [
    ("/employees", "GET"),
    ("/projects", "GET"),
    ("/recommendations", "POST"),
    ("/domain-analysis", "POST"),
    ("/quantitative-analysis", "POST"),
    ("/qualitative-analysis", "POST"),
]

def test_endpoint(path, method):
    """엔드포인트 테스트"""
    url = f"{API_BASE_URL}{path}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, json={}, timeout=5)
        
        status = "✓" if response.status_code != 403 else "✗"
        print(f"{status} {method:4} {path:30} - {response.status_code}")
        
        if response.status_code == 403:
            print(f"     → {response.json().get('message', 'Unknown error')}")
        
    except Exception as e:
        print(f"✗ {method:4} {path:30} - Error: {str(e)[:50]}")

def main():
    print("=" * 70)
    print("API 엔드포인트 상태 확인")
    print("=" * 70)
    print()
    
    for path, method in endpoints:
        test_endpoint(path, method)
    
    print()
    print("=" * 70)
    print("✓ = 정상 (200, 400, 500 등)")
    print("✗ = 엔드포인트 없음 (403 Missing Authentication Token)")
    print("=" * 70)

if __name__ == '__main__':
    main()
