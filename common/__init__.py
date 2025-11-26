"""
Common utilities and shared code

이 모듈은 HR Resource Optimization System의 공통 유틸리티와 데이터 액세스 레이어를 제공합니다.
"""

from common.models import (
    Employee, Project, Affinity,
    BasicInfo, Skill, SkillLevel, Education, WorkExperience,
    ProjectPeriod, TechStack, EmployeePair,
    ProjectCollaboration, SharedProject,
    MessengerCommunication, CompanyEvents, PersonalCloseness,
    Recommendation, RecommendationResult
)
from common.utils import (
    normalize_skill,
    normalize_skills,
    get_unique_skills,
    SKILL_NORMALIZATION_MAP
)
from common.dynamodb_client import DynamoDBClient, DynamoDBClientError
from common.repositories import (
    EmployeeRepository,
    ProjectRepository,
    AffinityRepository
)

__all__ = [
    # Models
    'Employee', 'Project', 'Affinity',
    'BasicInfo', 'Skill', 'SkillLevel', 'Education', 'WorkExperience',
    'ProjectPeriod', 'TechStack', 'EmployeePair',
    'ProjectCollaboration', 'SharedProject',
    'MessengerCommunication', 'CompanyEvents', 'PersonalCloseness',
    'Recommendation', 'RecommendationResult',
    # Utils
    'normalize_skill', 'normalize_skills', 'get_unique_skills',
    'SKILL_NORMALIZATION_MAP',
    # DynamoDB Client
    'DynamoDBClient', 'DynamoDBClientError',
    # Repositories
    'EmployeeRepository', 'ProjectRepository', 'AffinityRepository'
]
