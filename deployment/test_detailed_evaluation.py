"""
인력평가 상세 결과 테스트
AI 추천 의견 및 프로젝트 매칭 결과 확인
"""

import requests
import json

API_URL = "https://xoc7x1m6p8.execute-api.us-east-2.amazonaws.com/prod/employee-evaluation"

# 테스트할 직원 ID
test_employee = {
    "id": "U_003",
    "name": "박민수",
    "experience": 11,
    "role": "Senior System Architect"
}

print("=" * 80)
print(f"[{test_employee['name']}] 상세 평가 결과")
print("=" * 80)

try:
    response = requests.post(
        API_URL,
        json={"employee_id": test_employee['id']},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n[기본 정보]")
        print(f"  - 직원 ID: {data.get('employee_id')}")
        print(f"  - 이름: {data.get('employee_name')}")
        print(f"  - 경력: {data.get('experience_years')}년")
        print(f"  - 평가 일시: {data.get('evaluation_date')}")
        
        print(f"\n[평가 점수]")
        scores = data.get('scores', {})
        print(f"  - 기술 역량: {scores.get('technical_skills')}점")
        print(f"  - 프로젝트 경험: {scores.get('project_experience')}점")
        print(f"  - 이력 신뢰도: {scores.get('resume_credibility')}점")
        print(f"  - 문화 적합성: {scores.get('cultural_fit')}점")
        print(f"  - 종합 점수: {data.get('overall_score')}점")
        
        print(f"\n[투입 가능 여부]")
        print(f"  {data.get('deployable', 'N/A')}")
        
        print(f"\n[추천 역할]")
        for role in data.get('recommended_roles', []):
            print(f"  - {role}")
        
        print(f"\n[강점]")
        for strength in data.get('strengths', []):
            print(f"  - {strength}")
        
        print(f"\n[개선 필요 사항]")
        for weakness in data.get('weaknesses', []):
            print(f"  - {weakness}")
        
        print(f"\n[상세 분석]")
        analysis = data.get('analysis', {})
        print(f"  [기술 스택]")
        print(f"    {analysis.get('tech_stack', 'N/A')}")
        print(f"  [프로젝트 유사도]")
        print(f"    {analysis.get('project_similarity', 'N/A')}")
        print(f"  [이력 신뢰도]")
        print(f"    {analysis.get('credibility', 'N/A')}")
        print(f"  [시장 비교]")
        print(f"    {analysis.get('market_comparison', 'N/A')}")
        
        print(f"\n[AI 추천 의견]")
        print(f"  {data.get('ai_recommendation', 'N/A')}")
        
        print(f"\n[추천 프로젝트]")
        for proj in data.get('recommended_projects', []):
            print(f"  - {proj.get('project_name', 'N/A')}")
            print(f"    적합도: {proj.get('fit_score')}점")
            print(f"    사유: {proj.get('reason')}")
        
        print(f"\n[보유 기술]")
        for skill in data.get('skills', [])[:5]:
            if isinstance(skill, dict):
                print(f"  - {skill.get('name')}: {skill.get('level')} ({skill.get('years')}년)")
        
        print(f"\n[프로젝트 이력]")
        for proj in data.get('project_history', []):
            if isinstance(proj, dict):
                print(f"  - {proj.get('project_name')}")
                print(f"    역할: {proj.get('role')}")
                print(f"    기간: {proj.get('period')}")
        
        print("\n" + "=" * 80)
        print("✓ 평가 완료")
        print("=" * 80)
        
        # JSON 전체 출력 (디버깅용)
        print("\n[전체 JSON 응답]")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
    else:
        print(f"✗ 오류: {response.status_code}")
        print(f"  {response.text}")

except Exception as e:
    print(f"✗ 예외 발생: {str(e)}")
