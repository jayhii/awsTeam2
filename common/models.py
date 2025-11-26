"""
HR System 데이터 모델

이 모듈은 HR Resource Optimization System의 핵심 데이터 모델을 정의합니다.
모든 모델은 Pydantic을 사용하여 유효성 검사와 직렬화/역직렬화를 지원합니다.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class SkillLevel(str, Enum):
    """기술 숙련도 레벨"""
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"


class Skill(BaseModel):
    """직원의 기술 스택"""
    name: str = Field(..., description="기술 이름 (예: Java, Python)")
    level: SkillLevel = Field(..., description="숙련도 레벨")
    years: int = Field(..., ge=0, description="해당 기술 사용 연수")

    model_config = ConfigDict(use_enum_values=True)


class BasicInfo(BaseModel):
    """직원 기본 정보"""
    name: str = Field(..., description="직원 이름")
    role: str = Field(..., description="직무 (예: Principal Software Engineer)")
    years_of_experience: int = Field(..., ge=0, description="총 경력 연수")
    email: str = Field(..., description="이메일 주소")


class Education(BaseModel):
    """학력 정보"""
    degree: str = Field(..., description="학위 (예: Computer Science, MS)")
    university: str = Field(..., description="대학교 이름")


class WorkExperience(BaseModel):
    """프로젝트 참여 이력"""
    project_id: str = Field(..., description="프로젝트 ID")
    project_name: str = Field(..., description="프로젝트 이름")
    role: str = Field(..., description="프로젝트에서의 역할")
    period: str = Field(..., description="참여 기간 (예: 2024-01 ~ 2025-07)")
    main_tasks: List[str] = Field(default_factory=list, description="주요 업무")
    performance_result: Optional[str] = Field(None, description="성과")


class Employee(BaseModel):
    """직원 프로필 모델"""
    user_id: str = Field(..., description="직원 고유 ID")
    basic_info: BasicInfo = Field(..., description="기본 정보")
    self_introduction: Optional[str] = Field(None, description="자기소개")
    skills: List[Skill] = Field(default_factory=list, description="보유 기술")
    work_experience: List[WorkExperience] = Field(default_factory=list, description="프로젝트 이력")
    education: Optional[Education] = Field(None, description="학력")
    certifications: List[str] = Field(default_factory=list, description="자격증")

    def to_dynamodb(self) -> Dict[str, Any]:
        """DynamoDB 저장용 딕셔너리로 변환"""
        return self.model_dump(mode='json', exclude_none=True)

    @classmethod
    def from_dynamodb(cls, data: Dict[str, Any]) -> 'Employee':
        """DynamoDB 데이터에서 Employee 객체 생성"""
        return cls(**data)


class ProjectPeriod(BaseModel):
    """프로젝트 기간"""
    start: str = Field(..., description="시작일 (YYYY-MM-DD)")
    end: str = Field(..., description="종료일 (YYYY-MM-DD)")
    duration_months: int = Field(..., ge=0, description="기간 (개월)")


class TechStack(BaseModel):
    """프로젝트 기술 스택"""
    backend: List[str] = Field(default_factory=list, description="백엔드 기술")
    frontend: List[str] = Field(default_factory=list, description="프론트엔드 기술")
    data: List[str] = Field(default_factory=list, description="데이터 기술")
    infra: List[str] = Field(default_factory=list, description="인프라 기술")


class TeamComposition(BaseModel):
    """팀 구성"""
    model_config = ConfigDict(extra='allow')  # 동적 필드 허용 (PM, Backend_Dev 등)


class Project(BaseModel):
    """프로젝트 모델"""
    project_id: str = Field(..., description="프로젝트 고유 ID")
    project_name: str = Field(..., description="프로젝트 이름")
    client_industry: str = Field(..., description="고객 산업 분야")
    period: ProjectPeriod = Field(..., description="프로젝트 기간")
    budget_scale: Optional[str] = Field(None, description="예산 규모")
    description: Optional[str] = Field(None, description="프로젝트 설명")
    tech_stack: TechStack = Field(..., description="사용 기술 스택")
    requirements: List[str] = Field(default_factory=list, description="요구사항")
    team_composition: Optional[Dict[str, int]] = Field(None, description="팀 구성")

    def to_dynamodb(self) -> Dict[str, Any]:
        """DynamoDB 저장용 딕셔너리로 변환"""
        return self.model_dump(mode='json', exclude_none=True)

    @classmethod
    def from_dynamodb(cls, data: Dict[str, Any]) -> 'Project':
        """DynamoDB 데이터에서 Project 객체 생성"""
        return cls(**data)


class EmployeePair(BaseModel):
    """직원 쌍"""
    employee_1: str = Field(..., description="첫 번째 직원 ID")
    employee_2: str = Field(..., description="두 번째 직원 ID")


class SharedProject(BaseModel):
    """공동 참여 프로젝트"""
    project_id: str = Field(..., description="프로젝트 ID")
    overlap_period_months: int = Field(..., ge=0, description="중복 참여 기간 (개월)")
    same_team: bool = Field(..., description="같은 팀 여부")


class ProjectCollaboration(BaseModel):
    """프로젝트 협업 이력"""
    shared_projects: List[SharedProject] = Field(default_factory=list, description="공동 참여 프로젝트")
    collaboration_score: float = Field(..., ge=0, le=100, description="협업 점수")


class MessengerCommunication(BaseModel):
    """메신저 커뮤니케이션 분석"""
    total_messages_exchanged: int = Field(..., ge=0, description="총 메시지 교환 수")
    avg_response_time_minutes: float = Field(..., ge=0, description="평균 응답 시간 (분)")
    communication_score: float = Field(..., ge=0, le=100, description="커뮤니케이션 점수")


class CompanyEvents(BaseModel):
    """회사 행사 참여"""
    shared_events: List[str] = Field(default_factory=list, description="공동 참여 행사 ID")
    social_score: float = Field(..., ge=0, le=100, description="사회적 친밀도 점수")


class PersonalCloseness(BaseModel):
    """개인적 친밀도"""
    payday_contact_frequency: int = Field(..., ge=0, description="월급일 연락 빈도")
    vacation_day_contact_frequency: int = Field(..., ge=0, description="연차일 연락 빈도")
    personal_score: float = Field(..., ge=0, le=100, description="개인적 친밀도 점수")


class Affinity(BaseModel):
    """직원 간 친밀도 모델"""
    affinity_id: str = Field(..., description="친밀도 고유 ID")
    employee_pair: EmployeePair = Field(..., description="직원 쌍")
    project_collaboration: ProjectCollaboration = Field(..., description="프로젝트 협업 이력")
    messenger_communication: MessengerCommunication = Field(..., description="메신저 커뮤니케이션")
    company_events: CompanyEvents = Field(..., description="회사 행사 참여")
    personal_closeness: PersonalCloseness = Field(..., description="개인적 친밀도")
    overall_affinity_score: float = Field(..., ge=0, le=100, description="종합 친밀도 점수")

    def to_dynamodb(self) -> Dict[str, Any]:
        """DynamoDB 저장용 딕셔너리로 변환"""
        return self.model_dump(mode='json', exclude_none=True)

    @classmethod
    def from_dynamodb(cls, data: Dict[str, Any]) -> 'Affinity':
        """DynamoDB 데이터에서 Affinity 객체 생성"""
        return cls(**data)


class Recommendation(BaseModel):
    """추천 결과 모델"""
    user_id: str = Field(..., description="직원 ID")
    name: str = Field(..., description="직원 이름")
    skill_match_score: float = Field(..., ge=0, le=100, description="기술 적합도 점수")
    affinity_score: float = Field(..., ge=0, le=100, description="친밀도 점수")
    availability_score: float = Field(..., ge=0, le=100, description="가용성 점수")
    overall_score: float = Field(..., ge=0, le=100, description="종합 점수")
    reasoning: str = Field(..., description="추천 근거")
    matched_skills: List[str] = Field(default_factory=list, description="매칭된 기술")
    team_synergy: List[str] = Field(default_factory=list, description="팀 시너지 정보")


class RecommendationResult(BaseModel):
    """프로젝트 추천 결과"""
    project_id: str = Field(..., description="프로젝트 ID")
    recommendations: List[Recommendation] = Field(default_factory=list, description="추천 목록")
