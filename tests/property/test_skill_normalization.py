"""
Property-Based Test for Skill Normalization Consistency

**Feature: hr-resource-optimization, Property 2: Skill Normalization Consistency**
**Validates: Requirements 1.2**

Property: *For any* skill string, normalizing it multiple times should produce 
          the same result

이 테스트는 스킬 정규화 함수가 멱등성(idempotency)을 가지는지 검증합니다.
"""

import pytest
from hypothesis import given, strategies as st, settings
from common.utils import normalize_skill, normalize_skills, get_unique_skills


@pytest.mark.property
class TestSkillNormalizationConsistency:
    """스킬 정규화 일관성 Property 테스트"""
    
    @settings(max_examples=200)
    @given(skill_name=st.text(min_size=1, max_size=50))
    def test_skill_normalization_idempotency(self, skill_name):
        """
        Property 2: Skill Normalization Consistency
        
        *For any* skill string, normalizing it multiple times should produce 
        the same result
        
        이 테스트는 스킬 이름을 여러 번 정규화해도 동일한 결과가 
        나오는지 검증합니다 (멱등성).
        """
        # 첫 번째 정규화
        normalized_once = normalize_skill(skill_name)
        
        # 두 번째 정규화 (첫 번째 결과를 다시 정규화)
        normalized_twice = normalize_skill(normalized_once)
        
        # 세 번째 정규화 (두 번째 결과를 다시 정규화)
        normalized_thrice = normalize_skill(normalized_twice)
        
        # 모든 결과가 동일해야 함
        assert normalized_once == normalized_twice, \
            f"첫 번째와 두 번째 정규화 결과가 다릅니다: '{normalized_once}' != '{normalized_twice}'"
        
        assert normalized_twice == normalized_thrice, \
            f"두 번째와 세 번째 정규화 결과가 다릅니다: '{normalized_twice}' != '{normalized_thrice}'"
        
        assert normalized_once == normalized_thrice, \
            f"첫 번째와 세 번째 정규화 결과가 다릅니다: '{normalized_once}' != '{normalized_thrice}'"
    
    @settings(max_examples=100)
    @given(skill_names=st.lists(
        st.text(min_size=1, max_size=30),
        min_size=1,
        max_size=20
    ))
    def test_skill_list_normalization_idempotency(self, skill_names):
        """
        스킬 리스트 정규화 멱등성 검증
        
        여러 스킬을 한 번에 정규화할 때도 멱등성이 유지되는지 검증합니다.
        """
        # 첫 번째 정규화
        normalized_once = normalize_skills(skill_names)
        
        # 두 번째 정규화
        normalized_twice = normalize_skills(normalized_once)
        
        # 결과가 동일해야 함
        assert normalized_once == normalized_twice, \
            f"스킬 리스트 정규화 결과가 일치하지 않습니다"
    
    @settings(max_examples=100)
    @given(
        skill1=st.text(min_size=1, max_size=30),
        skill2=st.text(min_size=1, max_size=30)
    )
    def test_same_normalized_skills_are_equal(self, skill1, skill2):
        """
        동일하게 정규화된 스킬은 같은 것으로 취급
        
        두 개의 다른 입력이 같은 정규화 결과를 가지면, 
        그들은 동일한 스킬로 간주되어야 합니다.
        """
        normalized1 = normalize_skill(skill1)
        normalized2 = normalize_skill(skill2)
        
        # 정규화 결과가 같으면, 다시 정규화해도 같아야 함
        if normalized1 == normalized2:
            assert normalize_skill(normalized1) == normalize_skill(normalized2), \
                "동일하게 정규화된 스킬이 재정규화 후 달라졌습니다"
    
    def test_known_skill_variations_normalize_consistently(self):
        """
        알려진 스킬 변형들이 일관되게 정규화되는지 검증
        
        실제 사용 사례에서 자주 발생하는 스킬 이름 변형들을 테스트합니다.
        """
        # JavaScript 변형들
        js_variations = ["javascript", "JavaScript", "JAVASCRIPT", "js", "JS", "Java Script"]
        js_normalized = [normalize_skill(v) for v in js_variations]
        assert all(n == "JavaScript" for n in js_normalized), \
            f"JavaScript 변형들이 일관되게 정규화되지 않았습니다: {js_normalized}"
        
        # Python 변형들
        python_variations = ["python", "Python", "PYTHON", "PyThOn"]
        python_normalized = [normalize_skill(v) for v in python_variations]
        assert all(n == "Python" for n in python_normalized), \
            f"Python 변형들이 일관되게 정규화되지 않았습니다: {python_normalized}"
        
        # Spring Boot 변형들
        spring_variations = ["spring boot", "Spring Boot", "SPRING BOOT", "springboot", "SpringBoot"]
        spring_normalized = [normalize_skill(v) for v in spring_variations]
        assert all(n == "Spring Boot" for n in spring_normalized), \
            f"Spring Boot 변형들이 일관되게 정규화되지 않았습니다: {spring_normalized}"
    
    @settings(max_examples=100)
    @given(skill_names=st.lists(
        st.text(min_size=1, max_size=30),
        min_size=1,
        max_size=20
    ))
    def test_unique_skills_removes_duplicates_after_normalization(self, skill_names):
        """
        중복 제거 함수가 정규화 후 중복을 올바르게 제거하는지 검증
        
        예: ["python", "PYTHON", "Python"] -> ["Python"]
        """
        unique_skills = get_unique_skills(skill_names)
        
        # 결과에 중복이 없어야 함
        assert len(unique_skills) == len(set(unique_skills)), \
            f"중복 제거 후에도 중복이 남아있습니다: {unique_skills}"
        
        # 모든 스킬이 정규화되어 있어야 함 (멱등성)
        re_normalized = [normalize_skill(s) for s in unique_skills]
        assert unique_skills == re_normalized, \
            "중복 제거된 스킬들이 정규화되지 않았습니다"
    
    def test_empty_string_normalization(self):
        """빈 문자열 정규화 처리"""
        assert normalize_skill("") == "", \
            "빈 문자열은 빈 문자열로 정규화되어야 합니다"
        
        assert normalize_skill("   ") == "", \
            "공백만 있는 문자열은 빈 문자열로 정규화되어야 합니다"
    
    def test_whitespace_handling(self):
        """공백 처리 일관성 검증"""
        # 앞뒤 공백 제거
        assert normalize_skill("  python  ") == normalize_skill("python"), \
            "앞뒤 공백이 정규화 결과에 영향을 주면 안 됩니다"
        
        # 매핑에 있는 스킬은 공백 상관없이 정규화됨
        assert normalize_skill("spring boot") == "Spring Boot", \
            "매핑에 있는 스킬은 올바르게 정규화되어야 합니다"
