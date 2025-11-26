"""
유틸리티 함수 유닛 테스트

skill normalization 및 기타 유틸리티 함수를 테스트합니다.
"""

import pytest
from common.utils import (
    normalize_skill,
    normalize_skills,
    get_unique_skills,
    SKILL_NORMALIZATION_MAP
)


class TestNormalizeSkill:
    """normalize_skill 함수 테스트"""

    def test_normalize_lowercase_skill(self):
        """소문자 기술 이름 정규화 테스트"""
        assert normalize_skill("python") == "Python"
        assert normalize_skill("java") == "Java"
        assert normalize_skill("javascript") == "JavaScript"

    def test_normalize_uppercase_skill(self):
        """대문자 기술 이름 정규화 테스트"""
        assert normalize_skill("PYTHON") == "Python"
        assert normalize_skill("JAVA") == "Java"
        assert normalize_skill("JAVASCRIPT") == "JavaScript"

    def test_normalize_mixed_case_skill(self):
        """혼합 대소문자 기술 이름 정규화 테스트"""
        assert normalize_skill("PyThOn") == "Python"
        assert normalize_skill("JaVa") == "Java"

    def test_normalize_skill_with_spaces(self):
        """공백이 포함된 기술 이름 정규화 테스트"""
        assert normalize_skill("spring boot") == "Spring Boot"
        assert normalize_skill("java script") == "JavaScript"
        assert normalize_skill("ruby on rails") == "Ruby on Rails"

    def test_normalize_skill_with_leading_trailing_spaces(self):
        """앞뒤 공백이 있는 기술 이름 정규화 테스트"""
        assert normalize_skill("  python  ") == "Python"
        assert normalize_skill("  java  ") == "Java"

    def test_normalize_abbreviations(self):
        """약어 정규화 테스트"""
        assert normalize_skill("js") == "JavaScript"
        assert normalize_skill("ts") == "TypeScript"
        assert normalize_skill("k8s") == "Kubernetes"

    def test_normalize_frameworks(self):
        """프레임워크 이름 정규화 테스트"""
        assert normalize_skill("react") == "React"
        assert normalize_skill("vue") == "Vue.js"
        assert normalize_skill("angular") == "Angular"
        assert normalize_skill("django") == "Django"
        assert normalize_skill("flask") == "Flask"

    def test_normalize_databases(self):
        """데이터베이스 이름 정규화 테스트"""
        assert normalize_skill("mysql") == "MySQL"
        assert normalize_skill("postgresql") == "PostgreSQL"
        assert normalize_skill("mongodb") == "MongoDB"
        assert normalize_skill("redis") == "Redis"

    def test_normalize_cloud_platforms(self):
        """클라우드 플랫폼 이름 정규화 테스트"""
        assert normalize_skill("aws") == "AWS"
        assert normalize_skill("azure") == "Azure"
        assert normalize_skill("gcp") == "GCP"

    def test_normalize_devops_tools(self):
        """DevOps 도구 이름 정규화 테스트"""
        assert normalize_skill("docker") == "Docker"
        assert normalize_skill("kubernetes") == "Kubernetes"
        assert normalize_skill("terraform") == "Terraform"

    def test_normalize_unknown_skill(self):
        """매핑에 없는 기술 이름 정규화 테스트 (title case로 변환)"""
        assert normalize_skill("unknown skill") == "Unknown Skill"
        assert normalize_skill("new technology") == "New Technology"

    def test_normalize_empty_string(self):
        """빈 문자열 정규화 테스트"""
        assert normalize_skill("") == ""

    def test_normalize_skill_consistency(self):
        """동일한 입력에 대해 일관된 결과 반환 테스트"""
        skill = "python"
        result1 = normalize_skill(skill)
        result2 = normalize_skill(skill)
        assert result1 == result2

    def test_normalize_skill_idempotent(self):
        """정규화를 여러 번 적용해도 같은 결과 반환 테스트"""
        skill = "javascript"
        normalized_once = normalize_skill(skill)
        normalized_twice = normalize_skill(normalized_once)
        assert normalized_once == normalized_twice


class TestNormalizeSkills:
    """normalize_skills 함수 테스트"""

    def test_normalize_multiple_skills(self):
        """여러 기술 이름 정규화 테스트"""
        skills = ["python", "JAVA", "javascript"]
        expected = ["Python", "Java", "JavaScript"]
        assert normalize_skills(skills) == expected

    def test_normalize_empty_list(self):
        """빈 리스트 정규화 테스트"""
        assert normalize_skills([]) == []

    def test_normalize_skills_with_duplicates(self):
        """중복이 있는 리스트 정규화 테스트 (중복 유지)"""
        skills = ["python", "PYTHON", "java"]
        result = normalize_skills(skills)
        assert result == ["Python", "Python", "Java"]

    def test_normalize_mixed_skills(self):
        """다양한 형태의 기술 이름 정규화 테스트"""
        skills = ["react", "vue.js", "spring boot", "aws", "docker"]
        expected = ["React", "Vue.js", "Spring Boot", "AWS", "Docker"]
        assert normalize_skills(skills) == expected


class TestGetUniqueSkills:
    """get_unique_skills 함수 테스트"""

    def test_remove_duplicates(self):
        """중복 제거 테스트"""
        skills = ["python", "PYTHON", "java", "Python"]
        result = get_unique_skills(skills)
        assert result == ["Python", "Java"]

    def test_preserve_order(self):
        """순서 유지 테스트"""
        skills = ["java", "python", "javascript", "JAVA"]
        result = get_unique_skills(skills)
        assert result == ["Java", "Python", "JavaScript"]

    def test_empty_list(self):
        """빈 리스트 테스트"""
        assert get_unique_skills([]) == []

    def test_no_duplicates(self):
        """중복이 없는 경우 테스트"""
        skills = ["python", "java", "javascript"]
        result = get_unique_skills(skills)
        assert result == ["Python", "Java", "JavaScript"]

    def test_all_duplicates(self):
        """모두 중복인 경우 테스트"""
        skills = ["python", "PYTHON", "Python", "python"]
        result = get_unique_skills(skills)
        assert result == ["Python"]

    def test_case_insensitive_deduplication(self):
        """대소문자 구분 없이 중복 제거 테스트"""
        skills = ["React", "react", "REACT", "Vue", "vue"]
        result = get_unique_skills(skills)
        assert result == ["React", "Vue.js"]


class TestSkillNormalizationMap:
    """SKILL_NORMALIZATION_MAP 딕셔너리 테스트"""

    def test_map_exists(self):
        """매핑 딕셔너리가 존재하는지 테스트"""
        assert SKILL_NORMALIZATION_MAP is not None
        assert isinstance(SKILL_NORMALIZATION_MAP, dict)

    def test_map_has_entries(self):
        """매핑 딕셔너리에 항목이 있는지 테스트"""
        assert len(SKILL_NORMALIZATION_MAP) > 0

    def test_map_keys_are_lowercase(self):
        """모든 키가 소문자인지 테스트"""
        for key in SKILL_NORMALIZATION_MAP.keys():
            assert key == key.lower(), f"Key '{key}' is not lowercase"

    def test_common_skills_in_map(self):
        """일반적인 기술들이 매핑에 포함되어 있는지 테스트"""
        common_skills = [
            "python", "java", "javascript", "react", "vue",
            "docker", "kubernetes", "aws", "mysql", "postgresql"
        ]
        for skill in common_skills:
            assert skill in SKILL_NORMALIZATION_MAP, f"'{skill}' not in map"


class TestSkillNormalizationIntegration:
    """통합 테스트"""

    def test_real_world_scenario(self):
        """실제 사용 시나리오 테스트"""
        # 이력서에서 추출된 다양한 형태의 기술 이름
        raw_skills = [
            "PYTHON", "python", "Java", "JAVA",
            "react", "React.js", "vue", "VueJS",
            "docker", "Docker", "kubernetes", "K8S",
            "aws", "AWS", "Amazon Web Services"
        ]
        
        # 정규화 및 중복 제거
        normalized = get_unique_skills(raw_skills)
        
        # 결과 검증
        assert "Python" in normalized
        assert "Java" in normalized
        assert "React" in normalized
        assert "Vue.js" in normalized
        assert "Docker" in normalized
        assert "Kubernetes" in normalized
        assert "AWS" in normalized
        
        # 중복이 제거되었는지 확인
        assert normalized.count("Python") == 1
        assert normalized.count("Java") == 1
        assert normalized.count("AWS") == 1

    def test_skill_matching_scenario(self):
        """기술 매칭 시나리오 테스트"""
        # 프로젝트 요구 기술
        required_skills = ["Python", "React", "AWS"]
        
        # 직원 보유 기술 (다양한 형태)
        employee_skills = ["python", "REACT", "aws", "docker"]
        
        # 정규화
        normalized_required = normalize_skills(required_skills)
        normalized_employee = normalize_skills(employee_skills)
        
        # 매칭 확인
        matches = set(normalized_required) & set(normalized_employee)
        assert len(matches) == 3
        assert "Python" in matches
        assert "React" in matches
        assert "AWS" in matches
