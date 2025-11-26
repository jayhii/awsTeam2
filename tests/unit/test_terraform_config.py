"""
Terraform 설정 검증 테스트

Terraform 파일들이 올바르게 구성되어 있는지 검증합니다.
"""

import os
import json
import pytest
from pathlib import Path


class TestTerraformStructure:
    """Terraform 파일 구조 테스트"""
    
    @pytest.fixture
    def terraform_dir(self):
        """Terraform 디렉토리 경로"""
        return Path("deployment/terraform")
    
    def test_terraform_directory_exists(self, terraform_dir):
        """Terraform 디렉토리가 존재하는지 테스트"""
        assert terraform_dir.exists()
        assert terraform_dir.is_dir()
    
    def test_required_terraform_files_exist(self, terraform_dir):
        """필수 Terraform 파일들이 존재하는지 테스트"""
        required_files = [
            "main.tf",
            "dynamodb.tf",
            "s3.tf",
            "iam.tf",
            "outputs.tf"
        ]
        
        for file_name in required_files:
            file_path = terraform_dir / file_name
            assert file_path.exists(), f"{file_name} 파일이 존재하지 않습니다"
    
    def test_terraform_files_not_empty(self, terraform_dir):
        """Terraform 파일들이 비어있지 않은지 테스트"""
        terraform_files = [
            "main.tf",
            "dynamodb.tf",
            "s3.tf",
            "iam.tf"
        ]
        
        for file_name in terraform_files:
            file_path = terraform_dir / file_name
            content = file_path.read_text(encoding='utf-8')
            assert len(content) > 0, f"{file_name} 파일이 비어있습니다"


class TestDynamoDBConfiguration:
    """DynamoDB 설정 테스트"""
    
    @pytest.fixture
    def dynamodb_config(self):
        """DynamoDB Terraform 설정 읽기"""
        config_path = Path("deployment/terraform/dynamodb.tf")
        return config_path.read_text(encoding='utf-8')
    
    def test_all_tables_defined(self, dynamodb_config):
        """모든 필수 테이블이 정의되어 있는지 테스트"""
        required_tables = [
            "employees",
            "projects",
            "employee_affinity",
            "messenger_logs",
            "company_events",
            "tech_trends"
        ]
        
        for table in required_tables:
            assert f'resource "aws_dynamodb_table" "{table}"' in dynamodb_config, \
                f"{table} 테이블이 정의되지 않았습니다"
    
    def test_team2_tags_present(self, dynamodb_config):
        """Team2 태그가 모든 테이블에 있는지 테스트"""
        # Team2 태그가 최소 6번 (6개 테이블) 나타나야 함
        team2_count = dynamodb_config.count('Team        = "Team2"')
        assert team2_count >= 6, "모든 테이블에 Team2 태그가 없습니다"
    
    def test_employees_table_has_stream(self, dynamodb_config):
        """Employees 테이블에 스트림이 활성화되어 있는지 테스트"""
        # employees 리소스 블록 찾기
        employees_section = dynamodb_config[
            dynamodb_config.find('resource "aws_dynamodb_table" "employees"'):
            dynamodb_config.find('resource "aws_dynamodb_table" "projects"')
        ]
        
        assert "stream_enabled   = true" in employees_section, \
            "Employees 테이블에 스트림이 활성화되지 않았습니다"
    
    def test_gsi_defined_for_tables(self, dynamodb_config):
        """필요한 테이블에 GSI가 정의되어 있는지 테스트"""
        # Employees 테이블에 RoleIndex GSI
        assert "RoleIndex" in dynamodb_config
        
        # Projects 테이블에 IndustryIndex GSI
        assert "IndustryIndex" in dynamodb_config
        
        # EmployeeAffinity 테이블에 Employee1Index GSI
        assert "Employee1Index" in dynamodb_config


class TestS3Configuration:
    """S3 설정 테스트"""
    
    @pytest.fixture
    def s3_config(self):
        """S3 Terraform 설정 읽기"""
        config_path = Path("deployment/terraform/s3.tf")
        return config_path.read_text(encoding='utf-8')
    
    def test_all_buckets_defined(self, s3_config):
        """모든 필수 버킷이 정의되어 있는지 테스트"""
        required_buckets = [
            "frontend_hosting",
            "resumes",
            "reports",
            "data_lake"
        ]
        
        for bucket in required_buckets:
            assert f'resource "aws_s3_bucket" "{bucket}"' in s3_config, \
                f"{bucket} 버킷이 정의되지 않았습니다"
    
    def test_team2_tags_present(self, s3_config):
        """Team2 태그가 모든 버킷에 있는지 테스트"""
        # Team2 태그가 최소 4번 (4개 버킷) 나타나야 함
        team2_count = s3_config.count('Team        = "Team2"')
        assert team2_count >= 4, "모든 버킷에 Team2 태그가 없습니다"
    
    def test_resumes_bucket_has_encryption(self, s3_config):
        """Resumes 버킷에 암호화가 설정되어 있는지 테스트"""
        assert "aws_s3_bucket_server_side_encryption_configuration" in s3_config
        assert "AES256" in s3_config
    
    def test_resumes_bucket_has_versioning(self, s3_config):
        """Resumes 버킷에 버전 관리가 활성화되어 있는지 테스트"""
        assert 'resource "aws_s3_bucket_versioning" "resumes"' in s3_config
        assert 'status = "Enabled"' in s3_config
    
    def test_lifecycle_policies_defined(self, s3_config):
        """라이프사이클 정책이 정의되어 있는지 테스트"""
        # Resumes 버킷: 90일 후 Glacier
        assert "GLACIER" in s3_config
        
        # Reports 버킷: 365일 후 삭제
        assert "expiration" in s3_config
        
        # Data Lake: IA 및 Glacier 전환
        assert "STANDARD_IA" in s3_config


class TestIAMConfiguration:
    """IAM 설정 테스트"""
    
    @pytest.fixture
    def iam_config(self):
        """IAM Terraform 설정 읽기"""
        config_path = Path("deployment/terraform/iam.tf")
        return config_path.read_text(encoding='utf-8')
    
    def test_lambda_execution_role_exists(self, iam_config):
        """Lambda 실행 역할이 정의되어 있는지 테스트"""
        assert 'resource "aws_iam_role" "lambda_execution_team2"' in iam_config
        assert 'name = "LambdaExecutionRole-Team2"' in iam_config
    
    def test_api_gateway_execution_role_exists(self, iam_config):
        """API Gateway 실행 역할이 정의되어 있는지 테스트"""
        assert 'resource "aws_iam_role" "api_gateway_execution_team2"' in iam_config
        assert 'name = "APIGatewayExecutionRole-Team2"' in iam_config
    
    def test_tag_based_policies_present(self, iam_config):
        """태그 기반 접근 제어 정책이 있는지 테스트"""
        # DynamoDB 태그 기반 접근
        assert '"aws:ResourceTag/Team" = "Team2"' in iam_config
        
        # 여러 서비스에 대한 태그 기반 접근 제어
        tag_count = iam_config.count('"aws:ResourceTag/Team" = "Team2"')
        assert tag_count >= 3, "충분한 태그 기반 접근 제어 정책이 없습니다"
    
    def test_required_service_policies_exist(self, iam_config):
        """필수 서비스 정책이 존재하는지 테스트"""
        required_policies = [
            "lambda_dynamodb_access",
            "lambda_s3_access",
            "lambda_bedrock_access",
            "lambda_textract_access",
            "lambda_opensearch_access"
        ]
        
        for policy in required_policies:
            assert f'resource "aws_iam_role_policy" "{policy}"' in iam_config, \
                f"{policy} 정책이 정의되지 않았습니다"
    
    def test_bedrock_model_access(self, iam_config):
        """Bedrock 모델 접근 권한이 있는지 테스트"""
        assert "anthropic.claude-v2" in iam_config
        assert "amazon.titan-embed-text-v1" in iam_config


class TestMainConfiguration:
    """Main Terraform 설정 테스트"""
    
    @pytest.fixture
    def main_config(self):
        """Main Terraform 설정 읽기"""
        config_path = Path("deployment/terraform/main.tf")
        return config_path.read_text(encoding='utf-8')
    
    def test_terraform_version_specified(self, main_config):
        """Terraform 버전이 지정되어 있는지 테스트"""
        assert "required_version" in main_config
        assert ">= 1.0" in main_config
    
    def test_aws_provider_configured(self, main_config):
        """AWS provider가 설정되어 있는지 테스트"""
        assert 'provider "aws"' in main_config
        assert "region = var.aws_region" in main_config
    
    def test_default_tags_configured(self, main_config):
        """기본 태그가 설정되어 있는지 테스트"""
        assert "default_tags" in main_config
        assert 'Team    = "Team2"' in main_config
        assert 'Project = "HR-Resource-Optimization"' in main_config
    
    def test_required_variables_defined(self, main_config):
        """필수 변수들이 정의되어 있는지 테스트"""
        required_vars = [
            "aws_region",
            "environment",
            "project_name"
        ]
        
        for var in required_vars:
            assert f'variable "{var}"' in main_config, \
                f"{var} 변수가 정의되지 않았습니다"
    
    def test_default_region_is_us_east_2(self, main_config):
        """기본 리전이 us-east-2인지 테스트"""
        assert 'default     = "us-east-2"' in main_config


class TestOutputsConfiguration:
    """Outputs 설정 테스트"""
    
    @pytest.fixture
    def outputs_config(self):
        """Outputs Terraform 설정 읽기"""
        config_path = Path("deployment/terraform/outputs.tf")
        return config_path.read_text(encoding='utf-8')
    
    def test_outputs_file_exists(self):
        """outputs.tf 파일이 존재하는지 테스트"""
        outputs_path = Path("deployment/terraform/outputs.tf")
        assert outputs_path.exists()
    
    def test_dynamodb_outputs_defined(self, outputs_config):
        """DynamoDB 출력이 정의되어 있는지 테스트"""
        assert 'output "dynamodb_tables"' in outputs_config
        assert 'output "dynamodb_table_arns"' in outputs_config
    
    def test_s3_outputs_defined(self, outputs_config):
        """S3 출력이 정의되어 있는지 테스트"""
        assert 'output "s3_buckets"' in outputs_config
        assert 'output "s3_bucket_arns"' in outputs_config
    
    def test_iam_outputs_defined(self, outputs_config):
        """IAM 출력이 정의되어 있는지 테스트"""
        assert 'output "iam_roles"' in outputs_config
        assert 'output "iam_role_arns"' in outputs_config
