"""
DynamoDB Repository 클래스

Employee, Project, Affinity 데이터에 대한 CRUD 작업을 제공합니다.
Requirements: 1.1, 1.2, 2.1, 2.3, 2-1.7
"""

import logging
from typing import List, Optional, Dict, Any
from boto3.dynamodb.conditions import Key, Attr
from common.dynamodb_client import DynamoDBClient, DynamoDBClientError
from common.models import Employee, Project, Affinity
from common.utils import normalize_skill


# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class EmployeeRepository:
    """
    직원 프로필 데이터 저장소
    
    직원 프로필에 대한 CRUD 작업 및 기술 기반 쿼리를 제공합니다.
    Requirements: 1.1, 1.2
    """
    
    def __init__(self, dynamodb_client: DynamoDBClient, table_name: str = 'Employees'):
        """
        Employee Repository 초기화
        
        Args:
            dynamodb_client: DynamoDB 클라이언트
            table_name: 테이블 이름 (기본값: Employees)
        """
        self.client = dynamodb_client
        self.table_name = table_name
        logger.info(f"EmployeeRepository 초기화 완료 (테이블: {table_name})")
    
    def create(self, employee: Employee) -> Employee:
        """
        직원 프로필 생성
        
        Args:
            employee: 생성할 직원 객체
            
        Returns:
            생성된 직원 객체
            
        Raises:
            DynamoDBClientError: 생성 실패 시
        """
        try:
            item = employee.to_dynamodb()
            self.client.put_item(self.table_name, item)
            logger.info(f"직원 생성 완료 (user_id: {employee.user_id})")
            return employee
        except Exception as e:
            logger.error(f"직원 생성 실패 (user_id: {employee.user_id}): {str(e)}")
            raise DynamoDBClientError(f"직원 생성 실패: {str(e)}")
    
    def get(self, user_id: str) -> Optional[Employee]:
        """
        직원 프로필 조회
        
        Args:
            user_id: 직원 ID
            
        Returns:
            조회된 직원 객체 또는 None
            
        Raises:
            DynamoDBClientError: 조회 실패 시
        """
        try:
            item = self.client.get_item(
                self.table_name,
                key={'user_id': user_id}
            )
            
            if item:
                employee = Employee.from_dynamodb(item)
                logger.info(f"직원 조회 완료 (user_id: {user_id})")
                return employee
            
            logger.info(f"직원 없음 (user_id: {user_id})")
            return None
        except Exception as e:
            logger.error(f"직원 조회 실패 (user_id: {user_id}): {str(e)}")
            raise DynamoDBClientError(f"직원 조회 실패: {str(e)}")
    
    def update(self, employee: Employee) -> Employee:
        """
        직원 프로필 업데이트
        
        Args:
            employee: 업데이트할 직원 객체
            
        Returns:
            업데이트된 직원 객체
            
        Raises:
            DynamoDBClientError: 업데이트 실패 시
        """
        try:
            item = employee.to_dynamodb()
            self.client.put_item(self.table_name, item)
            logger.info(f"직원 업데이트 완료 (user_id: {employee.user_id})")
            return employee
        except Exception as e:
            logger.error(f"직원 업데이트 실패 (user_id: {employee.user_id}): {str(e)}")
            raise DynamoDBClientError(f"직원 업데이트 실패: {str(e)}")
    
    def delete(self, user_id: str) -> bool:
        """
        직원 프로필 삭제
        
        Args:
            user_id: 직원 ID
            
        Returns:
            삭제 성공 여부
            
        Raises:
            DynamoDBClientError: 삭제 실패 시
        """
        try:
            self.client.delete_item(
                self.table_name,
                key={'user_id': user_id}
            )
            logger.info(f"직원 삭제 완료 (user_id: {user_id})")
            return True
        except Exception as e:
            logger.error(f"직원 삭제 실패 (user_id: {user_id}): {str(e)}")
            raise DynamoDBClientError(f"직원 삭제 실패: {str(e)}")
    
    def list_all(self, limit: Optional[int] = None) -> List[Employee]:
        """
        모든 직원 프로필 조회
        
        Args:
            limit: 최대 결과 수 (선택사항)
            
        Returns:
            직원 객체 리스트
            
        Raises:
            DynamoDBClientError: 조회 실패 시
        """
        try:
            items = self.client.scan(self.table_name, limit=limit)
            employees = [Employee.from_dynamodb(item) for item in items]
            logger.info(f"전체 직원 조회 완료 (결과: {len(employees)}명)")
            return employees
        except Exception as e:
            logger.error(f"전체 직원 조회 실패: {str(e)}")
            raise DynamoDBClientError(f"전체 직원 조회 실패: {str(e)}")
    
    def find_by_skills(self, required_skills: List[str]) -> List[Employee]:
        """
        특정 기술을 보유한 직원 조회
        
        Requirements: 1.1 - 직무별 요구 기술 스택을 보유한 직원 목록 반환
        
        Args:
            required_skills: 요구 기술 리스트
            
        Returns:
            해당 기술을 보유한 직원 리스트
            
        Raises:
            DynamoDBClientError: 조회 실패 시
        """
        try:
            # 기술 이름 정규화
            normalized_skills = [normalize_skill(skill) for skill in required_skills]
            
            # 모든 직원 조회 (실제 환경에서는 GSI 사용 권장)
            all_employees = self.list_all()
            
            # 요구 기술을 모두 보유한 직원 필터링
            matching_employees = []
            for employee in all_employees:
                employee_skills = {normalize_skill(skill.name) for skill in employee.skills}
                
                # 모든 요구 기술을 보유했는지 확인
                if all(req_skill in employee_skills for req_skill in normalized_skills):
                    matching_employees.append(employee)
            
            logger.info(
                f"기술 기반 직원 조회 완료 "
                f"(요구 기술: {normalized_skills}, 결과: {len(matching_employees)}명)"
            )
            return matching_employees
        except Exception as e:
            logger.error(f"기술 기반 직원 조회 실패: {str(e)}")
            raise DynamoDBClientError(f"기술 기반 직원 조회 실패: {str(e)}")
    
    def get_all_employees(self, limit: Optional[int] = None) -> List[Employee]:
        """
        모든 직원 프로필 조회 (list_all의 별칭)
        
        Args:
            limit: 최대 결과 수 (선택사항)
            
        Returns:
            직원 객체 리스트
        """
        return self.list_all(limit=limit)
    
    def find_by_role(self, role: str) -> List[Employee]:
        """
        특정 역할의 직원 조회
        
        Args:
            role: 직무 (예: Principal Software Engineer)
            
        Returns:
            해당 역할의 직원 리스트
            
        Raises:
            DynamoDBClientError: 조회 실패 시
        """
        try:
            # RoleIndex GSI 사용
            items = self.client.query(
                self.table_name,
                key_condition_expression=Key('role').eq(role),
                index_name='RoleIndex'
            )
            
            employees = [Employee.from_dynamodb(item) for item in items]
            logger.info(f"역할 기반 직원 조회 완료 (역할: {role}, 결과: {len(employees)}명)")
            return employees
        except Exception as e:
            logger.error(f"역할 기반 직원 조회 실패 (역할: {role}): {str(e)}")
            # GSI가 없는 경우 스캔으로 대체
            try:
                items = self.client.scan(
                    self.table_name,
                    filter_expression=Attr('basic_info.role').eq(role)
                )
                employees = [Employee.from_dynamodb(item) for item in items]
                logger.info(
                    f"역할 기반 직원 조회 완료 (스캔 사용, 역할: {role}, "
                    f"결과: {len(employees)}명)"
                )
                return employees
            except Exception as scan_error:
                logger.error(f"역할 기반 직원 조회 실패 (스캔): {str(scan_error)}")
                raise DynamoDBClientError(f"역할 기반 직원 조회 실패: {str(scan_error)}")


class ProjectRepository:
    """
    프로젝트 데이터 저장소
    
    프로젝트에 대한 CRUD 작업 및 산업 분야 기반 쿼리를 제공합니다.
    Requirements: 2.1
    """
    
    def __init__(self, dynamodb_client: DynamoDBClient, table_name: str = 'Projects'):
        """
        Project Repository 초기화
        
        Args:
            dynamodb_client: DynamoDB 클라이언트
            table_name: 테이블 이름 (기본값: Projects)
        """
        self.client = dynamodb_client
        self.table_name = table_name
        logger.info(f"ProjectRepository 초기화 완료 (테이블: {table_name})")
    
    def create(self, project: Project) -> Project:
        """
        프로젝트 생성
        
        Args:
            project: 생성할 프로젝트 객체
            
        Returns:
            생성된 프로젝트 객체
            
        Raises:
            DynamoDBClientError: 생성 실패 시
        """
        try:
            item = project.to_dynamodb()
            self.client.put_item(self.table_name, item)
            logger.info(f"프로젝트 생성 완료 (project_id: {project.project_id})")
            return project
        except Exception as e:
            logger.error(f"프로젝트 생성 실패 (project_id: {project.project_id}): {str(e)}")
            raise DynamoDBClientError(f"프로젝트 생성 실패: {str(e)}")
    
    def get(self, project_id: str) -> Optional[Project]:
        """
        프로젝트 조회
        
        Args:
            project_id: 프로젝트 ID
            
        Returns:
            조회된 프로젝트 객체 또는 None
            
        Raises:
            DynamoDBClientError: 조회 실패 시
        """
        try:
            item = self.client.get_item(
                self.table_name,
                key={'project_id': project_id}
            )
            
            if item:
                project = Project.from_dynamodb(item)
                logger.info(f"프로젝트 조회 완료 (project_id: {project_id})")
                return project
            
            logger.info(f"프로젝트 없음 (project_id: {project_id})")
            return None
        except Exception as e:
            logger.error(f"프로젝트 조회 실패 (project_id: {project_id}): {str(e)}")
            raise DynamoDBClientError(f"프로젝트 조회 실패: {str(e)}")
    
    def update(self, project: Project) -> Project:
        """
        프로젝트 업데이트
        
        Args:
            project: 업데이트할 프로젝트 객체
            
        Returns:
            업데이트된 프로젝트 객체
            
        Raises:
            DynamoDBClientError: 업데이트 실패 시
        """
        try:
            item = project.to_dynamodb()
            self.client.put_item(self.table_name, item)
            logger.info(f"프로젝트 업데이트 완료 (project_id: {project.project_id})")
            return project
        except Exception as e:
            logger.error(
                f"프로젝트 업데이트 실패 (project_id: {project.project_id}): {str(e)}"
            )
            raise DynamoDBClientError(f"프로젝트 업데이트 실패: {str(e)}")
    
    def delete(self, project_id: str) -> bool:
        """
        프로젝트 삭제
        
        Args:
            project_id: 프로젝트 ID
            
        Returns:
            삭제 성공 여부
            
        Raises:
            DynamoDBClientError: 삭제 실패 시
        """
        try:
            self.client.delete_item(
                self.table_name,
                key={'project_id': project_id}
            )
            logger.info(f"프로젝트 삭제 완료 (project_id: {project_id})")
            return True
        except Exception as e:
            logger.error(f"프로젝트 삭제 실패 (project_id: {project_id}): {str(e)}")
            raise DynamoDBClientError(f"프로젝트 삭제 실패: {str(e)}")
    
    def list_all(self, limit: Optional[int] = None) -> List[Project]:
        """
        모든 프로젝트 조회
        
        Args:
            limit: 최대 결과 수 (선택사항)
            
        Returns:
            프로젝트 객체 리스트
            
        Raises:
            DynamoDBClientError: 조회 실패 시
        """
        try:
            items = self.client.scan(self.table_name, limit=limit)
            projects = [Project.from_dynamodb(item) for item in items]
            logger.info(f"전체 프로젝트 조회 완료 (결과: {len(projects)}개)")
            return projects
        except Exception as e:
            logger.error(f"전체 프로젝트 조회 실패: {str(e)}")
            raise DynamoDBClientError(f"전체 프로젝트 조회 실패: {str(e)}")
    
    def get_all_projects(self, limit: Optional[int] = None) -> List[Project]:
        """
        모든 프로젝트 조회 (list_all의 별칭)
        
        Args:
            limit: 최대 결과 수 (선택사항)
            
        Returns:
            프로젝트 객체 리스트
        """
        return self.list_all(limit=limit)
    
    def find_by_industry(self, industry: str) -> List[Project]:
        """
        특정 산업 분야의 프로젝트 조회
        
        Requirements: 2.1 - 산업 분야별 프로젝트 조회
        
        Args:
            industry: 산업 분야 (예: Finance / Banking)
            
        Returns:
            해당 산업 분야의 프로젝트 리스트
            
        Raises:
            DynamoDBClientError: 조회 실패 시
        """
        try:
            # IndustryIndex GSI 사용
            items = self.client.query(
                self.table_name,
                key_condition_expression=Key('client_industry').eq(industry),
                index_name='IndustryIndex'
            )
            
            projects = [Project.from_dynamodb(item) for item in items]
            logger.info(
                f"산업 분야 기반 프로젝트 조회 완료 "
                f"(산업: {industry}, 결과: {len(projects)}개)"
            )
            return projects
        except Exception as e:
            logger.error(f"산업 분야 기반 프로젝트 조회 실패 (산업: {industry}): {str(e)}")
            # GSI가 없는 경우 스캔으로 대체
            try:
                items = self.client.scan(
                    self.table_name,
                    filter_expression=Attr('client_industry').eq(industry)
                )
                projects = [Project.from_dynamodb(item) for item in items]
                logger.info(
                    f"산업 분야 기반 프로젝트 조회 완료 (스캔 사용, 산업: {industry}, "
                    f"결과: {len(projects)}개)"
                )
                return projects
            except Exception as scan_error:
                logger.error(f"산업 분야 기반 프로젝트 조회 실패 (스캔): {str(scan_error)}")
                raise DynamoDBClientError(
                    f"산업 분야 기반 프로젝트 조회 실패: {str(scan_error)}"
                )


class AffinityRepository:
    """
    친밀도 점수 데이터 저장소
    
    직원 간 친밀도 점수에 대한 CRUD 작업 및 직원 쌍 기반 쿼리를 제공합니다.
    Requirements: 2.3, 2-1.7
    """
    
    def __init__(
        self,
        dynamodb_client: DynamoDBClient,
        table_name: str = 'EmployeeAffinity'
    ):
        """
        Affinity Repository 초기화
        
        Args:
            dynamodb_client: DynamoDB 클라이언트
            table_name: 테이블 이름 (기본값: EmployeeAffinity)
        """
        self.client = dynamodb_client
        self.table_name = table_name
        logger.info(f"AffinityRepository 초기화 완료 (테이블: {table_name})")
    
    def create(self, affinity: Affinity) -> Affinity:
        """
        친밀도 점수 생성
        
        Args:
            affinity: 생성할 친밀도 객체
            
        Returns:
            생성된 친밀도 객체
            
        Raises:
            DynamoDBClientError: 생성 실패 시
        """
        try:
            item = affinity.to_dynamodb()
            self.client.put_item(self.table_name, item)
            logger.info(f"친밀도 점수 생성 완료 (affinity_id: {affinity.affinity_id})")
            return affinity
        except Exception as e:
            logger.error(
                f"친밀도 점수 생성 실패 (affinity_id: {affinity.affinity_id}): {str(e)}"
            )
            raise DynamoDBClientError(f"친밀도 점수 생성 실패: {str(e)}")
    
    def get(self, affinity_id: str) -> Optional[Affinity]:
        """
        친밀도 점수 조회
        
        Args:
            affinity_id: 친밀도 ID
            
        Returns:
            조회된 친밀도 객체 또는 None
            
        Raises:
            DynamoDBClientError: 조회 실패 시
        """
        try:
            item = self.client.get_item(
                self.table_name,
                key={'affinity_id': affinity_id}
            )
            
            if item:
                affinity = Affinity.from_dynamodb(item)
                logger.info(f"친밀도 점수 조회 완료 (affinity_id: {affinity_id})")
                return affinity
            
            logger.info(f"친밀도 점수 없음 (affinity_id: {affinity_id})")
            return None
        except Exception as e:
            logger.error(f"친밀도 점수 조회 실패 (affinity_id: {affinity_id}): {str(e)}")
            raise DynamoDBClientError(f"친밀도 점수 조회 실패: {str(e)}")
    
    def update(self, affinity: Affinity) -> Affinity:
        """
        친밀도 점수 업데이트
        
        Requirements: 2-1.7 - 친밀도 점수 주기적 업데이트
        
        Args:
            affinity: 업데이트할 친밀도 객체
            
        Returns:
            업데이트된 친밀도 객체
            
        Raises:
            DynamoDBClientError: 업데이트 실패 시
        """
        try:
            item = affinity.to_dynamodb()
            self.client.put_item(self.table_name, item)
            logger.info(f"친밀도 점수 업데이트 완료 (affinity_id: {affinity.affinity_id})")
            return affinity
        except Exception as e:
            logger.error(
                f"친밀도 점수 업데이트 실패 (affinity_id: {affinity.affinity_id}): {str(e)}"
            )
            raise DynamoDBClientError(f"친밀도 점수 업데이트 실패: {str(e)}")
    
    def delete(self, affinity_id: str) -> bool:
        """
        친밀도 점수 삭제
        
        Args:
            affinity_id: 친밀도 ID
            
        Returns:
            삭제 성공 여부
            
        Raises:
            DynamoDBClientError: 삭제 실패 시
        """
        try:
            self.client.delete_item(
                self.table_name,
                key={'affinity_id': affinity_id}
            )
            logger.info(f"친밀도 점수 삭제 완료 (affinity_id: {affinity_id})")
            return True
        except Exception as e:
            logger.error(f"친밀도 점수 삭제 실패 (affinity_id: {affinity_id}): {str(e)}")
            raise DynamoDBClientError(f"친밀도 점수 삭제 실패: {str(e)}")
    
    def list_all(self, limit: Optional[int] = None) -> List[Affinity]:
        """
        모든 친밀도 점수 조회
        
        Args:
            limit: 최대 결과 수 (선택사항)
            
        Returns:
            친밀도 객체 리스트
            
        Raises:
            DynamoDBClientError: 조회 실패 시
        """
        try:
            items = self.client.scan(self.table_name, limit=limit)
            affinities = [Affinity.from_dynamodb(item) for item in items]
            logger.info(f"전체 친밀도 점수 조회 완료 (결과: {len(affinities)}개)")
            return affinities
        except Exception as e:
            logger.error(f"전체 친밀도 점수 조회 실패: {str(e)}")
            raise DynamoDBClientError(f"전체 친밀도 점수 조회 실패: {str(e)}")
    
    def find_by_employee_pair(
        self,
        employee_1: str,
        employee_2: str
    ) -> Optional[Affinity]:
        """
        특정 직원 쌍의 친밀도 점수 조회
        
        Requirements: 2.3 - 직원 간 친밀도 점수 조회
        
        Args:
            employee_1: 첫 번째 직원 ID
            employee_2: 두 번째 직원 ID
            
        Returns:
            해당 직원 쌍의 친밀도 객체 또는 None
            
        Raises:
            DynamoDBClientError: 조회 실패 시
        """
        try:
            # 먼저 affinity_id로 직접 조회 시도 (정방향)
            affinity_id_forward = f"AFF_{employee_1}_{employee_2}"
            affinity = self.get(affinity_id_forward)
            if affinity:
                logger.info(
                    f"직원 쌍 친밀도 조회 완료 "
                    f"({employee_1} - {employee_2})"
                )
                return affinity
            
            # 역방향으로도 시도
            affinity_id_reverse = f"AFF_{employee_2}_{employee_1}"
            affinity = self.get(affinity_id_reverse)
            if affinity:
                logger.info(
                    f"직원 쌍 친밀도 조회 완료 (역순) "
                    f"({employee_2} - {employee_1})"
                )
                return affinity
            
            # affinity_id로 찾지 못한 경우 GSI 사용
            try:
                # Employee1Index GSI 사용
                items = self.client.query(
                    self.table_name,
                    key_condition_expression=Key('employee_1').eq(employee_1),
                    index_name='Employee1Index'
                )
                
                # employee_2와 매칭되는 항목 찾기
                for item in items:
                    affinity = Affinity.from_dynamodb(item)
                    if affinity.employee_pair.employee_2 == employee_2:
                        logger.info(
                            f"직원 쌍 친밀도 조회 완료 (GSI 사용, "
                            f"{employee_1} - {employee_2})"
                        )
                        return affinity
                
                # 역순으로도 확인 (employee_1과 employee_2가 바뀐 경우)
                items = self.client.query(
                    self.table_name,
                    key_condition_expression=Key('employee_1').eq(employee_2),
                    index_name='Employee1Index'
                )
                
                for item in items:
                    affinity = Affinity.from_dynamodb(item)
                    if affinity.employee_pair.employee_2 == employee_1:
                        logger.info(
                            f"직원 쌍 친밀도 조회 완료 (GSI 역순, "
                            f"{employee_2} - {employee_1})"
                        )
                        return affinity
            except Exception as gsi_error:
                logger.warning(f"GSI 조회 실패, 스캔으로 대체: {str(gsi_error)}")
            
            # GSI가 없거나 실패한 경우 스캔으로 대체
            items = self.client.scan(self.table_name)
            for item in items:
                affinity = Affinity.from_dynamodb(item)
                pair = affinity.employee_pair
                if ((pair.employee_1 == employee_1 and pair.employee_2 == employee_2) or
                    (pair.employee_1 == employee_2 and pair.employee_2 == employee_1)):
                    logger.info(
                        f"직원 쌍 친밀도 조회 완료 (스캔 사용, "
                        f"{employee_1} - {employee_2})"
                    )
                    return affinity
            
            logger.info(f"직원 쌍 친밀도 없음 ({employee_1} - {employee_2})")
            return None
        except Exception as e:
            logger.error(
                f"직원 쌍 친밀도 조회 실패 ({employee_1} - {employee_2}): {str(e)}"
            )
            raise DynamoDBClientError(
                f"직원 쌍 친밀도 조회 실패: {str(e)}"
            )
    
    def find_by_employee(self, employee_id: str) -> List[Affinity]:
        """
        특정 직원과 관련된 모든 친밀도 점수 조회
        
        Args:
            employee_id: 직원 ID
            
        Returns:
            해당 직원과 관련된 친밀도 객체 리스트
            
        Raises:
            DynamoDBClientError: 조회 실패 시
        """
        try:
            # Employee1Index GSI 사용
            items = self.client.query(
                self.table_name,
                key_condition_expression=Key('employee_1').eq(employee_id),
                index_name='Employee1Index'
            )
            
            affinities = [Affinity.from_dynamodb(item) for item in items]
            
            # employee_2로도 검색 (스캔 필요)
            all_items = self.client.scan(self.table_name)
            for item in all_items:
                affinity = Affinity.from_dynamodb(item)
                if (affinity.employee_pair.employee_2 == employee_id and
                    affinity.employee_pair.employee_1 != employee_id):
                    affinities.append(affinity)
            
            logger.info(
                f"직원 관련 친밀도 조회 완료 "
                f"(employee_id: {employee_id}, 결과: {len(affinities)}개)"
            )
            return affinities
        except Exception as e:
            logger.error(f"직원 관련 친밀도 조회 실패 (employee_id: {employee_id}): {str(e)}")
            raise DynamoDBClientError(f"직원 관련 친밀도 조회 실패: {str(e)}")
