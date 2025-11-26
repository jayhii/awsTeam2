"""
Property-Based Test for Resource Tagging Enforcement

**Feature: hr-resource-optimization, Property 41: Resource Tagging Enforcement**
**Validates: Requirements 9-1.1**

Property: *For any* created AWS resource, it must have the Team=Team2 tag applied

이 테스트는 Terraform 설정 파일들을 파싱하여 모든 AWS 리소스가 
Team=Team2 태그를 포함하고 있는지 검증합니다.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple
import pytest
from hypothesis import given, strategies as st, settings


# Terraform 리소스 타입 정의
TERRAFORM_RESOURCE_TYPES = [
    "aws_dynamodb_table",
    "aws_s3_bucket",
    "aws_lambda_function",
    "aws_iam_role",
    "aws_opensearch_domain",
    "aws_api_gateway_rest_api",
    "aws_cloudwatch_event_rule",
]


def parse_terraform_file(file_path: Path) -> List[Dict[str, any]]:
    """
    Terraform 파일을 파싱하여 리소스 정보를 추출합니다.
    
    Args:
        file_path: Terraform 파일 경로
        
    Returns:
        리소스 정보 리스트 (타입, 이름, 태그 포함 여부)
    """
    content = file_path.read_text(encoding='utf-8')
    resources = []
    
    # 리소스 블록 패턴: resource "type" "name" { ... }
    resource_pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
    
    for match in re.finditer(resource_pattern, content, re.DOTALL):
        resource_type = match.group(1)
        resource_name = match.group(2)
        resource_body = match.group(3)
        
        # 태그 블록 찾기
        tags_pattern = r'tags\s*=\s*\{([^}]*)\}'
        tags_match = re.search(tags_pattern, resource_body, re.DOTALL)
        
        has_team2_tag = False
        if tags_match:
            tags_content = tags_match.group(1)
            # Team = "Team2" 패턴 찾기
            if re.search(r'Team\s*=\s*"Team2"', tags_content):
                has_team2_tag = True
        
        resources.append({
            "type": resource_type,
            "name": resource_name,
            "file": file_path.name,
            "has_team2_tag": has_team2_tag
        })
    
    return resources


def get_all_terraform_resources() -> List[Dict[str, any]]:
    """
    모든 Terraform 파일에서 리소스를 추출합니다.
    
    Returns:
        모든 리소스 정보 리스트
    """
    terraform_dir = Path("deployment/terraform")
    all_resources = []
    
    # .tf 파일들 순회
    for tf_file in terraform_dir.glob("*.tf"):
        resources = parse_terraform_file(tf_file)
        all_resources.extend(resources)
    
    return all_resources


def check_default_tags_in_provider() -> bool:
    """
    Provider 설정에 default_tags가 있는지 확인합니다.
    
    Returns:
        default_tags에 Team=Team2가 있으면 True
    """
    main_tf = Path("deployment/terraform/main.tf")
    content = main_tf.read_text(encoding='utf-8')
    
    # provider "aws" 블록 찾기 (중첩된 블록 처리)
    # provider 블록의 시작을 찾고, 중괄호 카운팅으로 끝을 찾음
    provider_start = content.find('provider "aws"')
    if provider_start == -1:
        return False
    
    # provider 블록의 내용 추출
    brace_start = content.find('{', provider_start)
    if brace_start == -1:
        return False
    
    brace_count = 1
    i = brace_start + 1
    while i < len(content) and brace_count > 0:
        if content[i] == '{':
            brace_count += 1
        elif content[i] == '}':
            brace_count -= 1
        i += 1
    
    provider_body = content[brace_start:i]
    
    # default_tags 블록 찾기
    default_tags_start = provider_body.find('default_tags')
    if default_tags_start == -1:
        return False
    
    # default_tags 블록의 내용 추출
    tags_brace_start = provider_body.find('{', default_tags_start)
    if tags_brace_start == -1:
        return False
    
    tags_brace_count = 1
    j = tags_brace_start + 1
    while j < len(provider_body) and tags_brace_count > 0:
        if provider_body[j] == '{':
            tags_brace_count += 1
        elif provider_body[j] == '}':
            tags_brace_count -= 1
        j += 1
    
    tags_content = provider_body[tags_brace_start:j]
    
    # Team = "Team2" 확인
    return bool(re.search(r'Team\s*=\s*"Team2"', tags_content))


@pytest.mark.property
class TestResourceTaggingEnforcement:
    """리소스 태깅 강제 적용 Property 테스트"""
    
    def test_provider_has_default_team2_tag(self):
        """
        Provider 설정에 default_tags로 Team=Team2가 설정되어 있는지 테스트
        
        이는 모든 리소스에 자동으로 태그가 적용되도록 보장합니다.
        """
        assert check_default_tags_in_provider(), \
            "Provider 설정에 default_tags로 Team=Team2가 설정되어 있지 않습니다"
    
    @settings(max_examples=100)
    @given(st.data())
    def test_all_resources_have_team2_tag(self, data):
        """
        Property 41: Resource Tagging Enforcement
        
        *For any* created AWS resource, it must have the Team=Team2 tag applied
        
        이 테스트는 Terraform 설정의 모든 리소스가 Team=Team2 태그를 
        가지고 있는지 검증합니다. Provider의 default_tags 또는 
        개별 리소스의 tags 블록에 태그가 있어야 합니다.
        """
        # 모든 Terraform 리소스 가져오기
        all_resources = get_all_terraform_resources()
        
        # 리소스가 없으면 테스트 스킵
        if not all_resources:
            pytest.skip("Terraform 리소스가 발견되지 않았습니다")
        
        # Hypothesis로 리소스 샘플링
        resource = data.draw(st.sampled_from(all_resources))
        
        # Provider에 default_tags가 있는지 확인
        has_default_tags = check_default_tags_in_provider()
        
        # 리소스가 Team2 태그를 가지고 있거나, Provider에 default_tags가 있어야 함
        assert resource["has_team2_tag"] or has_default_tags, \
            f"리소스 {resource['type']}.{resource['name']} (파일: {resource['file']})에 " \
            f"Team=Team2 태그가 없고, Provider에도 default_tags가 설정되어 있지 않습니다"
    
    def test_all_dynamodb_tables_have_team2_tag(self):
        """
        모든 DynamoDB 테이블이 Team=Team2 태그를 가지고 있는지 테스트
        
        DynamoDB 테이블은 명시적으로 태그를 가져야 합니다.
        """
        all_resources = get_all_terraform_resources()
        dynamodb_tables = [r for r in all_resources if r["type"] == "aws_dynamodb_table"]
        
        assert len(dynamodb_tables) > 0, "DynamoDB 테이블이 발견되지 않았습니다"
        
        has_default_tags = check_default_tags_in_provider()
        
        for table in dynamodb_tables:
            assert table["has_team2_tag"] or has_default_tags, \
                f"DynamoDB 테이블 {table['name']}에 Team=Team2 태그가 없습니다"
    
    def test_all_s3_buckets_have_team2_tag(self):
        """
        모든 S3 버킷이 Team=Team2 태그를 가지고 있는지 테스트
        
        S3 버킷은 명시적으로 태그를 가져야 합니다.
        """
        all_resources = get_all_terraform_resources()
        s3_buckets = [r for r in all_resources if r["type"] == "aws_s3_bucket"]
        
        assert len(s3_buckets) > 0, "S3 버킷이 발견되지 않았습니다"
        
        has_default_tags = check_default_tags_in_provider()
        
        for bucket in s3_buckets:
            assert bucket["has_team2_tag"] or has_default_tags, \
                f"S3 버킷 {bucket['name']}에 Team=Team2 태그가 없습니다"
    
    def test_all_lambda_functions_have_team2_tag(self):
        """
        모든 Lambda 함수가 Team=Team2 태그를 가지고 있는지 테스트
        
        Lambda 함수는 명시적으로 태그를 가져야 합니다.
        """
        all_resources = get_all_terraform_resources()
        lambda_functions = [r for r in all_resources if r["type"] == "aws_lambda_function"]
        
        assert len(lambda_functions) > 0, "Lambda 함수가 발견되지 않았습니다"
        
        has_default_tags = check_default_tags_in_provider()
        
        for function in lambda_functions:
            assert function["has_team2_tag"] or has_default_tags, \
                f"Lambda 함수 {function['name']}에 Team=Team2 태그가 없습니다"
    
    def test_all_iam_roles_have_team2_tag(self):
        """
        모든 IAM 역할이 Team=Team2 태그를 가지고 있는지 테스트
        
        IAM 역할은 명시적으로 태그를 가져야 합니다.
        """
        all_resources = get_all_terraform_resources()
        iam_roles = [r for r in all_resources if r["type"] == "aws_iam_role"]
        
        # IAM 역할이 없을 수도 있음 (선택적)
        if len(iam_roles) == 0:
            pytest.skip("IAM 역할이 발견되지 않았습니다")
        
        has_default_tags = check_default_tags_in_provider()
        
        for role in iam_roles:
            assert role["has_team2_tag"] or has_default_tags, \
                f"IAM 역할 {role['name']}에 Team=Team2 태그가 없습니다"
    
    def test_all_eventbridge_rules_have_team2_tag(self):
        """
        모든 EventBridge 규칙이 Team=Team2 태그를 가지고 있는지 테스트
        
        EventBridge 규칙은 명시적으로 태그를 가져야 합니다.
        """
        all_resources = get_all_terraform_resources()
        event_rules = [r for r in all_resources if r["type"] == "aws_cloudwatch_event_rule"]
        
        # EventBridge 규칙이 없을 수도 있음 (선택적)
        if len(event_rules) == 0:
            pytest.skip("EventBridge 규칙이 발견되지 않았습니다")
        
        has_default_tags = check_default_tags_in_provider()
        
        for rule in event_rules:
            assert rule["has_team2_tag"] or has_default_tags, \
                f"EventBridge 규칙 {rule['name']}에 Team=Team2 태그가 없습니다"
    
    @settings(max_examples=50)
    @given(
        resource_type=st.sampled_from(TERRAFORM_RESOURCE_TYPES),
    )
    def test_resource_type_tagging_consistency(self, resource_type):
        """
        특정 리소스 타입의 모든 인스턴스가 일관되게 태그를 가지고 있는지 테스트
        
        동일한 타입의 리소스들은 모두 동일한 태깅 전략을 따라야 합니다.
        """
        all_resources = get_all_terraform_resources()
        resources_of_type = [r for r in all_resources if r["type"] == resource_type]
        
        # 해당 타입의 리소스가 없으면 스킵
        if not resources_of_type:
            pytest.skip(f"{resource_type} 타입의 리소스가 발견되지 않았습니다")
        
        has_default_tags = check_default_tags_in_provider()
        
        # 모든 리소스가 태그를 가지고 있어야 함
        for resource in resources_of_type:
            assert resource["has_team2_tag"] or has_default_tags, \
                f"{resource_type} 타입의 리소스 {resource['name']}에 " \
                f"Team=Team2 태그가 없습니다"
    
    def test_tagging_coverage_percentage(self):
        """
        전체 리소스 중 Team=Team2 태그를 가진 리소스의 비율을 테스트
        
        100% 커버리지를 목표로 합니다.
        """
        all_resources = get_all_terraform_resources()
        
        if not all_resources:
            pytest.skip("Terraform 리소스가 발견되지 않았습니다")
        
        has_default_tags = check_default_tags_in_provider()
        
        # 태그를 가진 리소스 수 계산
        tagged_resources = sum(
            1 for r in all_resources 
            if r["has_team2_tag"] or has_default_tags
        )
        
        coverage_percentage = (tagged_resources / len(all_resources)) * 100
        
        # 100% 커버리지 요구
        assert coverage_percentage == 100.0, \
            f"태깅 커버리지가 {coverage_percentage:.1f}%입니다. " \
            f"100% 커버리지가 필요합니다. " \
            f"({tagged_resources}/{len(all_resources)} 리소스가 태그됨)"
