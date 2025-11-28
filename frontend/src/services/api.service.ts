/**
 * API 서비스 레이어
 * 백엔드 API와의 통신을 담당
 */

import { API_BASE_URL, API_ENDPOINTS, getAuthHeaders } from '../config/api';
import type {
  Employee,
  Project,
  RecommendationRequest,
  RecommendationResponse,
  DomainAnalysisResponse,
  QuantitativeAnalysisRequest,
  QuantitativeAnalysisResponse,
  QualitativeAnalysisRequest,
  QualitativeAnalysisResponse,
  DashboardMetrics,
  ResumeUploadResponse,
  ResumeParseStatus,
} from '../types/models';

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  /**
   * HTTP 요청 헬퍼
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers = await getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        ...headers,
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Unknown error' }));
      throw new Error(error.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * 대시보드 메트릭 조회
   */
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    const headers = await getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}/dashboard/metrics`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Unknown error' }));
      throw new Error(error.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * 전체 직원 목록 조회
   */
  async getEmployees(): Promise<Employee[]> {
    return this.request<Employee[]>(API_ENDPOINTS.EMPLOYEES);
  }

  /**
   * 특정 직원 조회
   */
  async getEmployeeById(id: string): Promise<Employee> {
    return this.request<Employee>(API_ENDPOINTS.EMPLOYEE_BY_ID(id));
  }

  /**
   * 기술 스택으로 직원 검색
   */
  async getEmployeesBySkill(skills: string[]): Promise<Employee[]> {
    return this.request<Employee[]>(
      `${API_ENDPOINTS.EMPLOYEES_BY_SKILL}?skills=${skills.join(',')}`
    );
  }

  /**
   * 직원 생성
   */
  async createEmployee(employee: Partial<Employee>): Promise<Employee> {
    return this.request<Employee>(API_ENDPOINTS.EMPLOYEES, {
      method: 'POST',
      body: JSON.stringify(employee),
    });
  }

  /**
   * 직원 정보 수정
   */
  async updateEmployee(id: string, employee: Partial<Employee>): Promise<Employee> {
    return this.request<Employee>(API_ENDPOINTS.EMPLOYEE_BY_ID(id), {
      method: 'PUT',
      body: JSON.stringify(employee),
    });
  }

  /**
   * 전체 프로젝트 목록 조회
   */
  async getProjects(): Promise<Project[]> {
    return this.request<Project[]>(API_ENDPOINTS.PROJECTS);
  }

  /**
   * 특정 프로젝트 조회
   */
  async getProjectById(id: string): Promise<Project> {
    return this.request<Project>(API_ENDPOINTS.PROJECT_BY_ID(id));
  }

  /**
   * 프로젝트 생성
   */
  async createProject(project: Partial<Project>): Promise<Project> {
    return this.request<Project>(API_ENDPOINTS.PROJECTS, {
      method: 'POST',
      body: JSON.stringify(project),
    });
  }

  /**
   * 프로젝트 정보 수정
   */
  async updateProject(id: string, project: Partial<Project>): Promise<Project> {
    return this.request<Project>(API_ENDPOINTS.PROJECT_BY_ID(id), {
      method: 'PUT',
      body: JSON.stringify(project),
    });
  }

  /**
   * 프로젝트 인력 추천 요청
   */
  async getRecommendations(request: RecommendationRequest): Promise<RecommendationResponse> {
    return this.request<RecommendationResponse>(API_ENDPOINTS.RECOMMENDATIONS, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * 도메인 분석 요청
   */
  async getDomainAnalysis(): Promise<DomainAnalysisResponse> {
    return this.request<DomainAnalysisResponse>(API_ENDPOINTS.DOMAIN_ANALYSIS, {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  /**
   * 정량적 분석 요청
   */
  async getQuantitativeAnalysis(
    request: QuantitativeAnalysisRequest
  ): Promise<QuantitativeAnalysisResponse> {
    return this.request<QuantitativeAnalysisResponse>(
      API_ENDPOINTS.QUANTITATIVE_ANALYSIS,
      {
        method: 'POST',
        body: JSON.stringify(request),
      }
    );
  }

  /**
   * 정성적 분석 요청
   */
  async getQualitativeAnalysis(
    request: QualitativeAnalysisRequest
  ): Promise<QualitativeAnalysisResponse> {
    return this.request<QualitativeAnalysisResponse>(
      API_ENDPOINTS.QUALITATIVE_ANALYSIS,
      {
        method: 'POST',
        body: JSON.stringify(request),
      }
    );
  }

  /**
   * 이력서 업로드
   */
  async uploadResume(file: File): Promise<ResumeUploadResponse> {
    const formData = new FormData();
    formData.append('resume', file);

    const headers = await getAuthHeaders();
    delete headers['Content-Type']; // FormData가 자동으로 설정

    const response = await fetch(`${this.baseUrl}${API_ENDPOINTS.RESUME_UPLOAD}`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * 이력서 파싱 상태 조회
   */
  async getResumeParseStatus(jobId: string): Promise<ResumeParseStatus> {
    return this.request<ResumeParseStatus>(API_ENDPOINTS.RESUME_PARSE_STATUS(jobId));
  }
}

// 싱글톤 인스턴스 export
export const apiService = new ApiService();
