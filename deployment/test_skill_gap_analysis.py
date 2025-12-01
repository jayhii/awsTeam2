"""
기술 격차 분석 테스트 스크립트
"""

import boto3
import json

def test_employee_evaluation():
    """직원 평가 테스트 (기술 격차 분석 포함)"""
    print("=" * 60)
    print("직원 평가 테스트 - 기술 격차 분석")
    print("=" * 60)
    
    lambda_client = boto3.client('lambda', region_name='us-east-2')
    
    # 테스트할 직원 ID
    test_employee_ids = ['U_003', 'U_004', 'U_008']  # 박민수, 이지은, 김준호
    
    for test_employee_id in test_employee_ids:
        print(f"\n{'=' * 60}")
        print(f"평가 대상: {test_employee_id}")
        print(f"{'=' * 60}")
        
        try:
            # Lambda 함수 호출
            response = lambda_client.invoke(
                FunctionName='EmployeeEvaluation',
                InvocationType='RequestResponse',
                Payload=json.dumps({
                    'body': json.dumps({
                        'employee_id': test_employee_id
                    })
                })
            )
            
            payload = json.loads(response['Payload'].read())
            
            if payload.get('statusCode') == 200:
                body = json.loads(payload.get('body', '{}'))
                
                print(f"\n✓ 평가 완료!")
                print(f"직원명: {body.get('employee_name')}")
                print(f"종합 점수: {body.get('overall_score')}")
                
                # 기술 격차 분석 결과
                skill_gap = body.get('skill_gap_analysis', {})
                
                if skill_gap:
                    print(f"\n기술 격차 분석 결과")
                    print("-" * 60)
                    print(f"{skill_gap.get('peer_comparison', '')}")
                    print(f"비교 대상: {skill_gap.get('peer_count', 0)}명")
                    
                    # 필수 기술
                    missing_skills = skill_gap.get('missing_skills', [])
                    if missing_skills:
                        print(f"\n[필수 기술 - 동료의 50% 이상 보유]")
                        for skill in missing_skills:
                            print(f"  • {skill['name']}: {skill['percentage']}% ({skill['count']}/{skill['total']}명)")
                    else:
                        print(f"\n[필수 기술] 없음 - 우수!")
                    
                    # 추천 기술
                    recommended_skills = skill_gap.get('recommended_skills', [])
                    if recommended_skills:
                        print(f"\n[추천 기술 - 동료의 30-50% 보유]")
                        for skill in recommended_skills:
                            print(f"  • {skill['name']}: {skill['percentage']}% ({skill['count']}/{skill['total']}명)")
                    else:
                        print(f"\n[추천 기술] 없음")
                else:
                    print("\n기술 격차 분석 데이터 없음")
                
                # 개선 필요 사항
                print(f"\n개선 필요 사항:")
                for weakness in body.get('weaknesses', []):
                    print(f"  • {weakness}")
            
            else:
                print(f"\n✗ 평가 실패")
                print(f"상태 코드: {payload.get('statusCode')}")
                print(f"오류: {payload}")
                
        except Exception as e:
            print(f"\n✗ 테스트 실패: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_employee_evaluation()
