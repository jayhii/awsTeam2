"""
Property-Based Test for Tag-Based Access Control

**Feature: hr-resource-optimization, Property 42-45: Tag-Based Access Control**
**Validates: Requirements 9-1.2, 9-1.3, 9-1.4, 9-1.5**

Property 42: *For any* Lambda function attempting DynamoDB access, 
            the target table must have the Team=Team2 tag

Property 43: *For any* Lambda function attempting S3 access, 
            the target bucket must have the Team=Team2 tag

Property 44: *For any* Lambda function attempting OpenSearch access, 
            the target domain must have the Team=Team2 tag

Property 45: *For any* resource without the Team=Team2 tag, 
            access attempts must be denied with an error

이 테스트는 IAM 정책이 태그 기반 접근 제어를 올바르게 구현하고 있는지 검증합니다.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pytest
from hypothesis import given, strategies as st, settings, assume


# AWS 서비스별 액션 매핑
SERVICE_ACTIONS = {
    "dynamodb": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan",
    ],
    "s3": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket",
    ],
    "opensearch": [
        "es:ESHttpGet",
        "es:ESHttpPut",
        "es:ESHttpPost",
        "es:ESHttpDelete",
    ],
}


def parse_iam_policies_from_terraform() -> List[Dict]:
    """
    Terraform IAM 파일에서 정책을 파싱합니다.
    
    Returns:
        정책 정보 리스트
    """
    iam_tf_path = Path("deployment/terraform/iam.tf")
    
    if not iam_tf_path.exists():
        return []
    
    content = iam_tf_path.read_text(encoding='utf-8')
    policies = []
    
    # aws_iam_role_policy 리소스 찾기 (중첩된 중괄호 처리)
    # resource "aws_iam_role_policy" "name" { ... }
    resource_starts = []
    for match in re.finditer(r'resource\s+"aws_iam_role_policy"\s+"([^"]+)"\s*\{', content):
        resource_starts.append({
            "name": match.group(1),
            "start": match.end() - 1  # { 위치
        })
    
    for resource_info in resource_starts:
        # 중괄호 카운팅으로 리소스 블록 끝 찾기
        start_pos = resource_info["start"]
        brace_count = 0
        i = start_pos
        
        while i < len(content):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    break
            i += 1
        
        if brace_count == 0:
            policy_body = content[start_pos:i+1]
            policy_name = resource_info["name"]
            
            # name 속성 추출
            name_match = re.search(r'name\s*=\s*"([^"]+)"', policy_body)
            policy_display_name = name_match.group(1) if name_match else policy_name
            
            policies.append({
                "resource_name": policy_name,
                "policy_name": policy_display_name,
                "policy_body": policy_body,
                "raw_json": None
            })
    
    return policies


def check_policy_has_tag_condition(
    policy_body: str, 
    service: str
) -> Tuple[bool, bool]:
    """
    정책이 특정 서비스에 대한 태그 조건을 가지고 있는지 확인합니다.
    
    Args:
        policy_body: 정책 본문
        service: 서비스 이름 (dynamodb, s3, opensearch)
        
    Returns:
        (서비스 액션 포함 여부, Team2 태그 조건 포함 여부)
    """
    # 서비스 액션이 포함되어 있는지 확인
    has_service_action = False
    for action in SERVICE_ACTIONS.get(service, []):
        if action in policy_body:
            has_service_action = True
            break
    
    if not has_service_action:
        return False, False
    
    # Team2 태그 조건 확인
    has_team2_condition = False
    
    # Condition 블록에서 aws:ResourceTag/Team = "Team2" 패턴 찾기
    if 'Condition' in policy_body:
        # StringEquals 조건 확인
        if 'StringEquals' in policy_body:
            # aws:ResourceTag/Team 확인
            if 'aws:ResourceTag/Team' in policy_body or 'aws:ResourceTag\\/Team' in policy_body:
                # Team2 값 확인
                if '"Team2"' in policy_body or "'Team2'" in policy_body:
                    has_team2_condition = True
    
    return has_service_action, has_team2_condition


def get_iam_role_names() -> List[str]:
    """
    Terraform에서 정의된 IAM 역할 이름을 추출합니다.
    
    Returns:
        IAM 역할 이름 리스트
    """
    iam_tf_path = Path("deployment/terraform/iam.tf")
    
    if not iam_tf_path.exists():
        return []
    
    content = iam_tf_path.read_text(encoding='utf-8')
    role_names = []
    
    # aws_iam_role 리소스에서 name 속성 추출
    role_pattern = r'resource\s+"aws_iam_role"\s+"[^"]+"\s*\{([^}]*)\}'
    
    for match in re.finditer(role_pattern, content, re.DOTALL):
        role_body = match.group(1)
        name_match = re.search(r'name\s*=\s*"([^"]+)"', role_body)
        if name_match:
            role_names.append(name_match.group(1))
    
    return role_names


@pytest.mark.property
class TestTagBasedAccessControl:
    """태그 기반 접근 제어 Property 테스트"""
    
    def test_dynamodb_policy_has_team2_tag_condition(self):
        """
        Property 42: DynamoDB Tag-Based Access Control
        
        *For any* Lambda function attempting DynamoDB access, 
        the target table must have the Team=Team2 tag
        
        DynamoDB 접근 정책이 Team=Team2 태그 조건을 포함하는지 검증합니다.
        """
        policies = parse_iam_policies_from_terraform()
        
        # DynamoDB 관련 정책 찾기
        dynamodb_policies = []
        for policy in policies:
            has_action, has_condition = check_policy_has_tag_condition(
                policy["policy_body"], 
                "dynamodb"
            )
            if has_action:
                dynamodb_policies.append({
                    "name": policy["policy_name"],
                    "has_team2_condition": has_condition
                })
        
        # DynamoDB 정책이 최소 하나는 있어야 함
        assert len(dynamodb_policies) > 0, \
            "DynamoDB 접근 정책이 발견되지 않았습니다"
        
        # 모든 DynamoDB 정책이 Team2 태그 조건을 가져야 함
        for policy in dynamodb_policies:
            assert policy["has_team2_condition"], \
                f"DynamoDB 정책 '{policy['name']}'에 Team=Team2 태그 조건이 없습니다. " \
                f"Requirements 9-1.2를 위반합니다."
    
    def test_s3_policy_has_team2_tag_condition(self):
        """
        Property 43: S3 Tag-Based Access Control
        
        *For any* Lambda function attempting S3 access, 
        the target bucket must have the Team=Team2 tag
        
        S3 접근 정책이 Team=Team2 태그 조건을 포함하는지 검증합니다.
        """
        policies = parse_iam_policies_from_terraform()
        
        # S3 관련 정책 찾기
        s3_policies = []
        for policy in policies:
            has_action, has_condition = check_policy_has_tag_condition(
                policy["policy_body"], 
                "s3"
            )
            if has_action:
                s3_policies.append({
                    "name": policy["policy_name"],
                    "has_team2_condition": has_condition
                })
        
        # S3 정책이 최소 하나는 있어야 함
        assert len(s3_policies) > 0, \
            "S3 접근 정책이 발견되지 않았습니다"
        
        # 모든 S3 정책이 Team2 태그 조건을 가져야 함
        for policy in s3_policies:
            assert policy["has_team2_condition"], \
                f"S3 정책 '{policy['name']}'에 Team=Team2 태그 조건이 없습니다. " \
                f"Requirements 9-1.3을 위반합니다."
    
    def test_opensearch_policy_has_team2_tag_condition(self):
        """
        Property 44: OpenSearch Tag-Based Access Control
        
        *For any* Lambda function attempting OpenSearch access, 
        the target domain must have the Team=Team2 tag
        
        OpenSearch 접근 정책이 Team=Team2 태그 조건을 포함하는지 검증합니다.
        """
        policies = parse_iam_policies_from_terraform()
        
        # OpenSearch 관련 정책 찾기
        opensearch_policies = []
        for policy in policies:
            has_action, has_condition = check_policy_has_tag_condition(
                policy["policy_body"], 
                "opensearch"
            )
            if has_action:
                opensearch_policies.append({
                    "name": policy["policy_name"],
                    "has_team2_condition": has_condition
                })
        
        # OpenSearch 정책이 최소 하나는 있어야 함
        assert len(opensearch_policies) > 0, \
            "OpenSearch 접근 정책이 발견되지 않았습니다"
        
        # 모든 OpenSearch 정책이 Team2 태그 조건을 가져야 함
        for policy in opensearch_policies:
            assert policy["has_team2_condition"], \
                f"OpenSearch 정책 '{policy['name']}'에 Team=Team2 태그 조건이 없습니다. " \
                f"Requirements 9-1.4를 위반합니다."
    
    @settings(max_examples=100)
    @given(service=st.sampled_from(["dynamodb", "s3", "opensearch"]))
    def test_all_service_policies_enforce_team2_tag(self, service):
        """
        Property 42-44 통합 테스트
        
        *For any* AWS 서비스 (DynamoDB, S3, OpenSearch)에 대한 접근 정책은
        Team=Team2 태그 조건을 반드시 포함해야 합니다.
        
        이는 태그가 없는 리소스에 대한 접근을 차단합니다.
        """
        policies = parse_iam_policies_from_terraform()
        
        # 해당 서비스 관련 정책 찾기
        service_policies = []
        for policy in policies:
            has_action, has_condition = check_policy_has_tag_condition(
                policy["policy_body"], 
                service
            )
            if has_action:
                service_policies.append({
                    "name": policy["policy_name"],
                    "has_team2_condition": has_condition
                })
        
        # 정책이 없으면 스킵
        assume(len(service_policies) > 0)
        
        # 모든 정책이 Team2 태그 조건을 가져야 함
        for policy in service_policies:
            assert policy["has_team2_condition"], \
                f"{service.upper()} 정책 '{policy['name']}'에 " \
                f"Team=Team2 태그 조건이 없습니다. " \
                f"태그가 없는 리소스에 대한 접근이 허용될 수 있습니다."
    
    def test_untagged_resource_access_denial_policy_structure(self):
        """
        Property 45: Untagged Resource Access Denial
        
        *For any* resource without the Team=Team2 tag, 
        access attempts must be denied with an error
        
        IAM 정책 구조가 태그 조건을 통해 태그가 없는 리소스에 대한 
        접근을 거부하도록 설계되었는지 검증합니다.
        """
        policies = parse_iam_policies_from_terraform()
        
        # 모든 서비스에 대한 정책 검사
        services_checked = []
        
        for service in ["dynamodb", "s3", "opensearch"]:
            service_policies = []
            for policy in policies:
                has_action, has_condition = check_policy_has_tag_condition(
                    policy["policy_body"], 
                    service
                )
                if has_action:
                    service_policies.append({
                        "name": policy["policy_name"],
                        "has_team2_condition": has_condition
                    })
            
            if service_policies:
                services_checked.append({
                    "service": service,
                    "policies": service_policies
                })
        
        # 최소 하나의 서비스는 검사되어야 함
        assert len(services_checked) > 0, \
            "검사할 서비스 정책이 발견되지 않았습니다"
        
        # 각 서비스의 모든 정책이 태그 조건을 가져야 함
        for service_info in services_checked:
            for policy in service_info["policies"]:
                assert policy["has_team2_condition"], \
                    f"{service_info['service'].upper()} 정책 '{policy['name']}'에 " \
                    f"Team=Team2 태그 조건이 없습니다. " \
                    f"이는 태그가 없는 리소스에 대한 접근을 허용할 수 있어 " \
                    f"Requirements 9-1.5를 위반합니다."
    
    def test_iam_role_naming_convention(self):
        """
        Property 46: IAM Role Naming Convention
        
        *For any* created IAM role, its name must match the pattern 
        LambdaExecutionRole-Team2 or APIGatewayExecutionRole-Team2
        
        IAM 역할 이름이 명명 규칙을 따르는지 검증합니다.
        """
        role_names = get_iam_role_names()
        
        # IAM 역할이 최소 하나는 있어야 함
        assert len(role_names) > 0, \
            "IAM 역할이 발견되지 않았습니다"
        
        # 허용된 패턴
        allowed_patterns = [
            r"^LambdaExecutionRole-Team2$",
            r"^APIGatewayExecutionRole-Team2$",
        ]
        
        for role_name in role_names:
            matches_pattern = any(
                re.match(pattern, role_name) 
                for pattern in allowed_patterns
            )
            
            assert matches_pattern, \
                f"IAM 역할 '{role_name}'이 명명 규칙을 따르지 않습니다. " \
                f"'LambdaExecutionRole-Team2' 또는 'APIGatewayExecutionRole-Team2' " \
                f"패턴을 따라야 합니다. Requirements 9-1.6을 위반합니다."
    
    @settings(max_examples=50)
    @given(st.data())
    def test_policy_condition_structure_validity(self, data):
        """
        정책의 Condition 블록 구조가 올바른지 검증합니다.
        
        Condition 블록이 있는 경우, StringEquals와 aws:ResourceTag/Team 키가
        올바르게 구성되어 있는지 확인합니다.
        """
        policies = parse_iam_policies_from_terraform()
        
        # Condition이 있는 정책만 필터링
        policies_with_conditions = [
            p for p in policies 
            if 'Condition' in p["policy_body"]
        ]
        
        assume(len(policies_with_conditions) > 0)
        
        # 샘플 정책 선택
        policy = data.draw(st.sampled_from(policies_with_conditions))
        
        # Condition 블록 구조 검증
        policy_body = policy["policy_body"]
        
        # StringEquals가 있어야 함
        assert 'StringEquals' in policy_body, \
            f"정책 '{policy['policy_name']}'의 Condition 블록에 " \
            f"StringEquals가 없습니다"
        
        # aws:ResourceTag/Team 키가 있어야 함
        has_resource_tag = (
            'aws:ResourceTag/Team' in policy_body or 
            'aws:ResourceTag\\/Team' in policy_body
        )
        assert has_resource_tag, \
            f"정책 '{policy['policy_name']}'의 Condition 블록에 " \
            f"aws:ResourceTag/Team 키가 없습니다"
        
        # Team2 값이 있어야 함
        has_team2_value = (
            '"Team2"' in policy_body or 
            "'Team2'" in policy_body
        )
        assert has_team2_value, \
            f"정책 '{policy['policy_name']}'의 Condition 블록에 " \
            f"Team2 값이 없습니다"
    
    def test_all_critical_services_have_tag_enforcement(self):
        """
        모든 중요 서비스(DynamoDB, S3, OpenSearch)에 대해 
        태그 기반 접근 제어가 구현되어 있는지 종합 검증합니다.
        """
        policies = parse_iam_policies_from_terraform()
        
        critical_services = ["dynamodb", "s3", "opensearch"]
        service_coverage = {}
        
        for service in critical_services:
            service_policies = []
            for policy in policies:
                has_action, has_condition = check_policy_has_tag_condition(
                    policy["policy_body"], 
                    service
                )
                if has_action:
                    service_policies.append({
                        "name": policy["policy_name"],
                        "has_team2_condition": has_condition
                    })
            
            service_coverage[service] = {
                "has_policy": len(service_policies) > 0,
                "all_tagged": all(p["has_team2_condition"] for p in service_policies),
                "policies": service_policies
            }
        
        # 모든 중요 서비스에 정책이 있어야 함
        for service, coverage in service_coverage.items():
            assert coverage["has_policy"], \
                f"{service.upper()} 서비스에 대한 접근 정책이 없습니다"
            
            assert coverage["all_tagged"], \
                f"{service.upper()} 서비스의 일부 정책에 Team2 태그 조건이 없습니다: " \
                f"{[p['name'] for p in coverage['policies'] if not p['has_team2_condition']]}"
        
        # 커버리지 요약 출력 (디버깅용)
        print("\n=== 태그 기반 접근 제어 커버리지 ===")
        for service, coverage in service_coverage.items():
            status = "OK" if coverage['all_tagged'] else "FAIL"
            print(f"{service.upper()}: {len(coverage['policies'])}개 정책, "
                  f"태그 조건: {status}")
