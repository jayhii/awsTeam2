"""
인력평가 결과 차이 테스트
서로 다른 직원들의 평가 결과가 실제로 다르게 나오는지 확인
"""

import requests
import json

API_URL = "https://xoc7x1m6p8.execute-api.us-east-2.amazonaws.com/prod/employee-evaluation"

# 테스트할 직원 ID 목록
test_employees = [
    {"id": "U_003", "name": "박민수", "experience": 11, "role": "Senior System Architect"},
    {"id": "U_004", "name": "이지은", "experience": 5, "role": "Frontend Developer"},
    {"id": "U_005", "name": "정현우", "experience": 7, "role": "DevOps Engineer"}
]

print("=" * 80)
print("인력평가 결과 비교 테스트")
print("=" * 80)

results = []

for employee in test_employees:
    print(f"\n[{employee['name']}] 평가 중...")
    print(f"  - 경력: {employee['experience']}년")
    print(f"  - 역할: {employee['role']}")
    
    try:
        response = requests.post(
            API_URL,
            json={"employee_id": employee['id']},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            scores = data.get('scores', {})
            overall = data.get('overall_score', 0)
            
            result = {
                'name': employee['name'],
                'experience': employee['experience'],
                'role': employee['role'],
                'technical_skills': scores.get('technical_skills', 0),
                'project_experience': scores.get('project_experience', 0),
                'resume_credibility': scores.get('resume_credibility', 0),
                'cultural_fit': scores.get('cultural_fit', 0),
                'overall_score': overall
            }
            results.append(result)
            
            print(f"  ✓ 평가 완료")
            print(f"    - 기술 역량: {scores.get('technical_skills', 0)}")
            print(f"    - 프로젝트 경험: {scores.get('project_experience', 0)}")
            print(f"    - 이력 신뢰도: {scores.get('resume_credibility', 0)}")
            print(f"    - 문화 적합성: {scores.get('cultural_fit', 0)}")
            print(f"    - 종합 점수: {overall}")
        else:
            print(f"  ✗ 오류: {response.status_code}")
            print(f"    {response.text}")
    
    except Exception as e:
        print(f"  ✗ 예외 발생: {str(e)}")

# 결과 비교 분석
print("\n" + "=" * 80)
print("평가 결과 비교 분석")
print("=" * 80)

if len(results) >= 2:
    print("\n[점수 차이 분석]")
    
    # 기술 역량 비교
    tech_scores = [r['technical_skills'] for r in results]
    print(f"\n기술 역량 점수:")
    for r in results:
        print(f"  - {r['name']}: {r['technical_skills']}점")
    print(f"  최고-최저 차이: {max(tech_scores) - min(tech_scores)}점")
    
    # 프로젝트 경험 비교
    proj_scores = [r['project_experience'] for r in results]
    print(f"\n프로젝트 경험 점수:")
    for r in results:
        print(f"  - {r['name']}: {r['project_experience']}점")
    print(f"  최고-최저 차이: {max(proj_scores) - min(proj_scores)}점")
    
    # 이력 신뢰도 비교
    cred_scores = [r['resume_credibility'] for r in results]
    print(f"\n이력 신뢰도 점수:")
    for r in results:
        print(f"  - {r['name']}: {r['resume_credibility']}점")
    print(f"  최고-최저 차이: {max(cred_scores) - min(cred_scores)}점")
    
    # 종합 점수 비교
    overall_scores = [r['overall_score'] for r in results]
    print(f"\n종합 점수:")
    for r in results:
        print(f"  - {r['name']}: {r['overall_score']}점")
    print(f"  최고-최저 차이: {max(overall_scores) - min(overall_scores)}점")
    
    # 결론
    print("\n" + "=" * 80)
    if max(overall_scores) - min(overall_scores) > 5:
        print("✓ 평가 결과가 직원별로 다르게 나타납니다. (정상)")
    else:
        print("✗ 평가 결과가 거의 동일합니다. (문제 있음)")
    print("=" * 80)
else:
    print("\n평가 결과가 충분하지 않습니다.")
