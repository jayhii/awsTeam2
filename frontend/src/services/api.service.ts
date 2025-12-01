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
  PersonnelEvaluation,
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
  async getEmployees(): Promise<any[]> {
    console.log('getEmployees 호출됨');
    const headers = await getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}${API_ENDPOINTS.EMPLOYEES_LIST}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Unknown error' }));
      throw new Error(error.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    console.log('getEmployees 응답:', data);
    
    // 응답 구조에 따라 처리
    if (Array.isArray(data)) {
      return data;
    } else if (data.employees && Array.isArray(data.employees)) {
      return data.employees;
    } else if (data.Items && Array.isArray(data.Items)) {
      return data.Items;
    }
    
    return [];
  }

  /**
   * 직원 생성
   */
  async createEmployee(employee: Partial<Employee>): Promise<Employee> {
    return this.request<Employee>(API_ENDPOINTS.EMPLOYEES_LIST, {
      method: 'POST',
      body: JSON.stringify(employee),
    });
  }

  /**
   * 전체 프로젝트 목록 조회
   */
  async getProjects(): Promise<any[]> {
    const headers = await getAuthHeaders();
    
    const response = await fetch(`${this.baseUrl}${API_ENDPOINTS.PROJECTS_LIST}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Unknown error' }));
      throw new Error(error.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    
    // 응답 구조에 따라 처리
    if (Array.isArray(data)) {
      return data;
    } else if (data.projects && Array.isArray(data.projects)) {
      return data.projects;
    } else if (data.Items && Array.isArray(data.Items)) {
      return data.Items;
    }
    
    return [];
  }

  /**
   * 프로젝트 생성
   */
  async createProject(project: Partial<Project>): Promise<Project> {
    return this.request<Project>(API_ENDPOINTS.PROJECTS_LIST, {
      method: 'POST',
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

  /**
   * 평가 목록 조회
   */
  async getEvaluations(status?: 'pending' | 'approved' | 'rejected' | 'review'): Promise<PersonnelEvaluation[]> {
    const endpoint = status 
      ? `${API_ENDPOINTS.EVALUATIONS}?status=${status}`
      : API_ENDPOINTS.EVALUATIONS;
    
    const response = await this.request<{ evaluations: PersonnelEvaluation[] }>(endpoint);
    return response.evaluations;
  }

  /**
   * 평가 승인
   */
  async approveEvaluation(evaluationId: string): Promise<PersonnelEvaluation> {
    return this.request<PersonnelEvaluation>(
      API_ENDPOINTS.EVALUATION_APPROVE(evaluationId),
      {
        method: 'PUT',
        body: JSON.stringify({ status: 'approved' }),
      }
    );
  }

  /**
   * 평가 검토
   */
  async reviewEvaluation(evaluationId: string, comments: string): Promise<PersonnelEvaluation> {
    return this.request<PersonnelEvaluation>(
      API_ENDPOINTS.EVALUATION_REVIEW(evaluationId),
      {
        method: 'PUT',
        body: JSON.stringify({ status: 'review', comments }),
      }
    );
  }

  /**
   * 평가 반려
   */
  async rejectEvaluation(evaluationId: string, reason: string): Promise<PersonnelEvaluation> {
    return this.request<PersonnelEvaluation>(
      API_ENDPOINTS.EVALUATION_REJECT(evaluationId),
      {
        method: 'PUT',
        body: JSON.stringify({ status: 'rejected', reason }),
      }
    );
  }
}

// 싱글톤 인스턴스 export
export const apiService = new ApiService();
