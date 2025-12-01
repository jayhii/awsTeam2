/**
 * API 설정 및 엔드포인트 정의
 */

/// <reference types="vite/client" />

// API Gateway URL
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://ifeniowvpb.execute-api.us-east-2.amazonaws.com/prod';

// API 엔드포인트
export const API_ENDPOINTS = {
  // 인력 추천
  RECOMMENDATIONS: '/recommendations',
  
  // 도메인 분석
  DOMAIN_ANALYSIS: '/domain-analysis',
  
  // 정량적 분석
  QUANTITATIVE_ANALYSIS: '/quantitative-analysis',
  
  // 정성적 분석
  QUALITATIVE_ANALYSIS: '/qualitative-analysis',
  
  // 직원 목록 조회 (추가)
  EMPLOYEES_LIST: '/employees',
  
  // 프로젝트 목록 조회 (추가)
  PROJECTS_LIST: '/projects',
  
  // 대시보드 메트릭
  DASHBOARD_METRICS: '/dashboard/metrics',
  
  // 프로젝트 배정
  PROJECT_ASSIGN: (projectId: string) => `/projects/${projectId}/assign`,
  
  // 평가 관련
  EVALUATIONS: '/evaluations',
  EVALUATION_APPROVE: (evaluationId: string) => `/evaluations/${evaluationId}/approve`,
  EVALUATION_REVIEW: (evaluationId: string) => `/evaluations/${evaluationId}/review`,
  EVALUATION_REJECT: (evaluationId: string) => `/evaluations/${evaluationId}/reject`,
} as const;

// API 요청 헤더
const getHeaders = (): Record<string, string> => {
  return {
    'Content-Type': 'application/json',
  };
};

// 인증 헤더 가져오기 (API 서비스에서 사용)
export const getAuthHeaders = async (): Promise<Record<string, string>> => {
  return {
    'Content-Type': 'application/json',
  };
};

// API 호출 헬퍼 함수
async function apiCall<T>(endpoint: string, body: any): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  console.log('API 호출:', url, body);
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(body),
    });

    console.log('API 응답 상태:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('API 에러 응답:', errorText);
      let error;
      try {
        error = JSON.parse(errorText);
      } catch {
        error = { message: errorText || 'Unknown error' };
      }
      throw new Error(error.message || `API Error: ${response.status}`);
    }

    const data = await response.json();
    console.log('API 응답 데이터:', data);
    return data;
  } catch (err) {
    console.error('API 호출 실패:', err);
    throw err;
  }
}

// API 타입 정의
export interface DomainAnalysisRequest {
  analysis_type?: string;
}

export interface DomainAnalysisResponse {
  current_domains: string[];
  identified_domains: Array<{
    domain_name: string;
    feasibility_score: number;
    reasoning: string;
  }>;
}

export interface QuantitativeAnalysisRequest {
  user_id: string;
}

export interface QuantitativeAnalysisResponse {
  user_id: string;
  name: string;
  experience_metrics: {
    years_of_experience: number;
    project_count: number;
    skill_diversity: number;
    experience_score: number;
    project_score: number;
    diversity_score: number;
  };
  tech_evaluation: {
    skill_evaluations: Array<{
      skill_name: string;
      trend_score: number;
      demand_score: number;
    }>;
    avg_trend_score: number;
    avg_demand_score: number;
    tech_stack_score: number;
  };
  project_scores: {
    project_evaluations: any[];
    avg_scale_score: number;
    avg_role_score: number;
    avg_performance_score: number;
    project_experience_score: number;
  };
  overall_score: number;
}

export interface QualitativeAnalysisRequest {
  user_id: string;
}

export interface QualitativeAnalysisResponse {
  user_id: string;
  name: string;
  strengths: any[];
  weaknesses: any[];
  suitable_projects: any[];
  development_areas: any[];
  suspicious_flags: Array<{
    type: string;
    description: string;
    severity: string;
  }>;
  overall_assessment: string;
}

export interface RecommendationsRequest {
  project_id: string;
}

export interface RecommendationsResponse {
  project_id: string;
  recommendations: Array<{
    user_id: string;
    name: string;
    score: number;
    reasoning: string;
  }>;
}

// 직원 목록 응답 타입
export interface Employee {
  user_id: string;
  basic_info: {
    name: string;
    role: string;
    email: string;
    years_of_experience: number;
  };
  skills: Array<{
    name: string;
    level: string;
    years: number;
  }>;
}

export interface EmployeesListResponse {
  employees: Employee[];
  count: number;
}

// 프로젝트 목록 응답 타입
export interface Project {
  project_id: string;
  project_name: string;
  status: string;
  start_date: string;
  required_skills: string[];
}

export interface ProjectsListResponse {
  projects: Project[];
  count: number;
}

// 대시보드 메트릭 응답 타입
export interface DashboardMetricsResponse {
  total_employees: number;
  active_projects: number;
  available_employees: number;
  pending_reviews: number;
  recent_recommendations: Array<{
    project: string;
    recommended: number;
    match_rate: number;
    status: string;
  }>;
  top_skills: Array<{
    name: string;
    count: number;
    percentage: number;
  }>;
}

// API 함수들
export const api = {
  /**
   * 도메인 분석 API
   */
  domainAnalysis: (request: DomainAnalysisRequest): Promise<DomainAnalysisResponse> => {
    return apiCall(API_ENDPOINTS.DOMAIN_ANALYSIS, request);
  },

  /**
   * 정량적 분석 API
   */
  quantitativeAnalysis: (request: QuantitativeAnalysisRequest): Promise<QuantitativeAnalysisResponse> => {
    return apiCall(API_ENDPOINTS.QUANTITATIVE_ANALYSIS, request);
  },

  /**
   * 정성적 분석 API
   */
  qualitativeAnalysis: (request: QualitativeAnalysisRequest): Promise<QualitativeAnalysisResponse> => {
    return apiCall(API_ENDPOINTS.QUALITATIVE_ANALYSIS, request);
  },

  /**
   * 인력 추천 API
   */
  recommendations: (request: RecommendationsRequest): Promise<RecommendationsResponse> => {
    return apiCall(API_ENDPOINTS.RECOMMENDATIONS, request);
  },

  /**
   * 직원 목록 조회 API
   */
  getEmployees: async (): Promise<EmployeesListResponse> => {
    const url = `${API_BASE_URL}${API_ENDPOINTS.EMPLOYEES_LIST}`;
    console.log('직원 목록 조회:', url);
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: getHeaders(),
      });

      console.log('직원 목록 응답 상태:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('직원 목록 조회 에러:', errorText);
        throw new Error(`API Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('직원 목록 데이터:', data);
      return data;
    } catch (err) {
      console.error('직원 목록 조회 실패:', err);
      throw err;
    }
  },

  /**
   * 프로젝트 목록 조회 API
   */
  getProjects: async (): Promise<ProjectsListResponse> => {
    const url = `${API_BASE_URL}${API_ENDPOINTS.PROJECTS_LIST}`;
    console.log('프로젝트 목록 조회:', url);
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: getHeaders(),
      });

      console.log('프로젝트 목록 응답 상태:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('프로젝트 목록 조회 에러:', errorText);
        throw new Error(`API Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('프로젝트 목록 데이터:', data);
      return data;
    } catch (err) {
      console.error('프로젝트 목록 조회 실패:', err);
      throw err;
    }
  },

  /**
   * 대시보드 메트릭 조회 API
   */
  getDashboardMetrics: async (): Promise<DashboardMetricsResponse> => {
    const url = `${API_BASE_URL}${API_ENDPOINTS.DASHBOARD_METRICS}`;
    console.log('대시보드 메트릭 조회:', url);
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: getHeaders(),
      });

      console.log('대시보드 메트릭 응답 상태:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('대시보드 메트릭 조회 에러:', errorText);
        throw new Error(`API Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('대시보드 메트릭 데이터:', data);
      return data;
    } catch (err) {
      console.error('대시보드 메트릭 조회 실패:', err);
      throw err;
    }
  },

  /**
   * 직원 생성 API
   */
  createEmployee: async (employeeData: any): Promise<Employee> => {
    const url = `${API_BASE_URL}${API_ENDPOINTS.EMPLOYEES_LIST}`;
    console.log('직원 생성:', url, employeeData);
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(employeeData),
      });

      console.log('직원 생성 응답 상태:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('직원 생성 에러:', errorText);
        let errorData;
        try {
          errorData = JSON.parse(errorText);
        } catch {
          errorData = { message: errorText || 'Unknown error' };
        }
        throw new Error(errorData.message || `API Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('직원 생성 데이터:', data);
      return data.employee;
    } catch (err) {
      console.error('직원 생성 실패:', err);
      throw err;
    }
  },

  /**
   * 프로젝트 생성 API
   */
  createProject: async (projectData: any): Promise<Project> => {
    const url = `${API_BASE_URL}${API_ENDPOINTS.PROJECTS_LIST}`;
    console.log('프로젝트 생성:', url, projectData);
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(projectData),
      });

      console.log('프로젝트 생성 응답 상태:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('프로젝트 생성 에러:', errorText);
        let errorData;
        try {
          errorData = JSON.parse(errorText);
        } catch {
          errorData = { message: errorText || 'Unknown error' };
        }
        throw new Error(errorData.message || `API Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('프로젝트 생성 데이터:', data);
      return data;
    } catch (err) {
      console.error('프로젝트 생성 실패:', err);
      throw err;
    }
  },

  /**
   * 프로젝트 배정 API
   */
  assignProject: async (projectId: string, employeeId: string): Promise<any> => {
    const url = `${API_BASE_URL}/projects/${projectId}/assign`;
    console.log('프로젝트 배정:', url, { employee_id: employeeId });
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ employee_id: employeeId }),
      });

      console.log('프로젝트 배정 응답 상태:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('프로젝트 배정 에러:', errorText);
        let errorData;
        try {
          errorData = JSON.parse(errorText);
        } catch {
          errorData = { message: errorText || 'Unknown error' };
        }
        throw new Error(errorData.error || errorData.message || `API Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('프로젝트 배정 데이터:', data);
      return data;
    } catch (err) {
      console.error('프로젝트 배정 실패:', err);
      throw err;
    }
  },
};
