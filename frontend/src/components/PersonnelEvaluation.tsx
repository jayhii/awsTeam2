import { useState, useEffect } from 'react';
import { Search, Upload, User, TrendingUp, Shield, Users, FileText, CheckCircle, AlertCircle, BarChart3, Target } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Progress } from './ui/progress';
import { apiService } from '../services/api.service';
import { ResumeUploadModal } from './ResumeUploadModal';
import { toast } from 'sonner';
import { API_BASE_URL } from '../config/api';

interface EvaluationResult {
  evaluation_id: string;
  employee_id: string;
  employee_name: string;
  evaluation_date: string;
  scores: {
    technical_skills: number;
    project_experience: number;
    resume_credibility: number;
    cultural_fit: number;
  };
  overall_score: number;
  strengths: string[];
  weaknesses: string[];
  analysis: {
    tech_stack: string;
    project_similarity: string;
    credibility: string;
    market_comparison: string;
  };
  ai_recommendation: string;
  project_history: any[];
  skills: any[];
  experience_years: number;
  status: string;
}

export function PersonnelEvaluation() {
  const [searchMode, setSearchMode] = useState<'name' | 'upload'>('name');
  const [searchQuery, setSearchQuery] = useState('');
  const [employees, setEmployees] = useState<any[]>([]);
  const [searchingEmployee, setSearchingEmployee] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState<any>(null);
  const [evaluationResult, setEvaluationResult] = useState<EvaluationResult | null>(null);
  const [evaluating, setEvaluating] = useState(false);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

  // 직원 검색
  const handleSearchEmployee = async () => {
    console.log('=== handleSearchEmployee 함수 호출됨 ===');
    console.log('검색어:', searchQuery);
    
    if (!searchQuery.trim()) {
      console.log('검색어가 비어있음');
      toast.error('검색할 이름을 입력하세요');
      return;
    }

    try {
      setSearchingEmployee(true);
      console.log('직원 검색 시작:', searchQuery);
      
      const response = await apiService.getEmployees();
      console.log('API 응답:', response);
      
      // API 응답 구조 확인 및 처리
      let allEmployees = [];
      if (Array.isArray(response)) {
        allEmployees = response;
      } else if (response.employees && Array.isArray(response.employees)) {
        allEmployees = response.employees;
      } else if (response.Items && Array.isArray(response.Items)) {
        allEmployees = response.Items;
      }
      
      console.log('전체 직원 수:', allEmployees.length);
      console.log('첫 번째 직원 데이터:', allEmployees[0]);
      
      const filtered = allEmployees.filter((emp: any) => {
        // 다양한 필드명 지원
        const name = emp.name || emp.employeeName || emp.basic_info?.name || '';
        console.log('직원 이름:', name, '검색어:', searchQuery);
        return name.toLowerCase().includes(searchQuery.toLowerCase());
      });
      
      console.log('검색 결과:', filtered.length);
      console.log('필터링된 직원:', filtered);
      setEmployees(filtered);

      if (filtered.length === 0) {
        toast.info('검색 결과가 없습니다');
      } else {
        toast.success(`${filtered.length}명의 직원을 찾았습니다`);
      }
    } catch (error) {
      console.error('직원 검색 실패:', error);
      toast.error('직원 검색에 실패했습니다');
    } finally {
      setSearchingEmployee(false);
    }
  };

  // 직원 평가 수행
  const handleEvaluateEmployee = async (employee: any) => {
    try {
      setEvaluating(true);
      setSelectedEmployee(employee);
      
      // employee_id 추출 (다양한 필드명 지원)
      const employeeId = employee.user_id || employee.employeeId || employee.employee_id || employee.id;
      console.log('평가 대상 직원 ID:', employeeId);
      console.log('직원 데이터:', employee);
      
      // API 호출 (employee_evaluation Lambda)
      const response = await fetch(
        `${API_BASE_URL}/employee-evaluation`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            employee_id: employeeId,
          }),
        }
      );

      if (!response.ok) {
        throw new Error('평가 요청 실패');
      }

      const result = await response.json();
      setEvaluationResult(result);
      toast.success('평가가 완료되었습니다');
    } catch (error) {
      console.error('평가 실패:', error);
      toast.error('평가에 실패했습니다');
    } finally {
      setEvaluating(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-600';
    if (score >= 70) return 'text-blue-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 85) return 'bg-green-50';
    if (score >= 70) return 'bg-blue-50';
    if (score >= 60) return 'bg-yellow-50';
    return 'bg-red-50';
  };

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            인력 평가
          </h2>
          <p className="text-gray-600 mt-1">
            등록된 직원 검색 또는 이력서 업로드를 통해 인력을 평가합니다
          </p>
        </div>
      </motion.div>

      {/* 평가 방법 선택 */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex gap-3"
      >
        <Button
          onClick={() => setSearchMode('name')}
          variant={searchMode === 'name' ? 'default' : 'outline'}
          className={`flex-1 h-16 ${
            searchMode === 'name'
              ? 'bg-gradient-to-r from-blue-600 to-indigo-600'
              : ''
          }`}
        >
          <User className="w-5 h-5 mr-2" />
          등록된 직원 검색
        </Button>
        <Button
          onClick={() => setSearchMode('upload')}
          variant={searchMode === 'upload' ? 'default' : 'outline'}
          className={`flex-1 h-16 ${
            searchMode === 'upload'
              ? 'bg-gradient-to-r from-blue-600 to-indigo-600'
              : ''
          }`}
        >
          <Upload className="w-5 h-5 mr-2" />
          이력서 업로드
        </Button>
      </motion.div>

      {/* 검색 영역 */}
      <AnimatePresence mode="wait">
        {searchMode === 'name' ? (
          <motion.div
            key="search"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="space-y-4"
          >
            <Card>
              <CardContent className="p-6">
                <div className="flex gap-3">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <Input
                      placeholder="직원 이름으로 검색"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSearchEmployee()}
                      className="pl-10 h-12"
                    />
                  </div>
                  <Button
                    onClick={() => {
                      console.log('검색 버튼 클릭됨!');
                      handleSearchEmployee();
                    }}
                    disabled={searchingEmployee}
                    className="h-12 px-12 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-base font-semibold min-w-[120px]"
                    type="button"
                  >
                    {searchingEmployee ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        검색 중...
                      </>
                    ) : (
                      <>
                        <Search className="w-4 h-4 mr-2" />
                        검색
                      </>
                    )}
                  </Button>
                </div>

                {/* 검색 결과 */}
                {employees.length > 0 && (
                  <div className="mt-6 space-y-3">
                    <h3 className="font-semibold text-gray-900">검색 결과 ({employees.length}명)</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {employees.map((employee, idx) => {
                        const name = employee.name || employee.employeeName || employee.basic_info?.name || '이름 없음';
                        const position = employee.position || employee.role || '직책 미정';
                        const experience = employee.experienceYears || employee.experience_years || 0;
                        const employeeId = employee.employeeId || employee.employee_id || employee.id || idx;
                        
                        return (
                          <motion.div
                            key={employeeId}
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all cursor-pointer"
                            onClick={() => handleEvaluateEmployee(employee)}
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-3">
                                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-indigo-500 flex items-center justify-center text-white font-bold">
                                  {name.charAt(0)}
                                </div>
                                <div>
                                  <div className="font-semibold text-gray-900">{name}</div>
                                  <div className="text-sm text-gray-500">
                                    {position} · {experience}년 경력
                                  </div>
                                </div>
                              </div>
                              <Button size="sm" variant="outline">
                                평가하기
                              </Button>
                            </div>
                          </motion.div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        ) : (
          <motion.div
            key="upload"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
          >
            <Card>
              <CardContent className="p-12 text-center">
                <Upload className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  이력서를 업로드하세요
                </h3>
                <p className="text-gray-600 mb-6">
                  PDF 형식의 이력서를 업로드하면 AI가 자동으로 분석하여 평가합니다
                </p>
                <Button
                  onClick={() => setIsUploadModalOpen(true)}
                  className="bg-gradient-to-r from-blue-600 to-indigo-600"
                  size="lg"
                >
                  <Upload className="w-5 h-5 mr-2" />
                  이력서 업로드
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 평가 진행 중 */}
      {evaluating && (
        <Card>
          <CardContent className="p-12 text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">평가 진행 중...</h3>
            <p className="text-gray-600">
              AI가 {selectedEmployee?.name}님의 이력을 분석하고 있습니다
            </p>
          </CardContent>
        </Card>
      )}

      {/* 평가 결과 */}
      <AnimatePresence>
        {evaluationResult && !evaluating && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* 종합 점수 카드 */}
            <Card className="overflow-hidden">
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-6 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-2xl font-bold mb-1">{evaluationResult.employee_name}</h3>
                    <p className="text-blue-100">
                      {evaluationResult.experience_years}년 경력 · 평가일: {new Date(evaluationResult.evaluation_date).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-blue-100 mb-1">종합 점수</div>
                    <div className="text-5xl font-bold">{evaluationResult.overall_score}</div>
                    <div className="text-blue-100">/ 100</div>
                  </div>
                </div>
              </div>
            </Card>

            {/* 평가 항목 상세 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                {
                  key: 'technical_skills',
                  label: '기술 역량',
                  icon: Target,
                  description: '보유 기술 스택 및 숙련도',
                  color: 'blue',
                },
                {
                  key: 'project_experience',
                  label: '프로젝트 경험',
                  icon: BarChart3,
                  description: '프로젝트 경험 유사도',
                  color: 'indigo',
                },
                {
                  key: 'resume_credibility',
                  label: '이력 신뢰도',
                  icon: Shield,
                  description: '경력 이력 진위 여부',
                  color: 'green',
                },
                {
                  key: 'cultural_fit',
                  label: '문화 적합성',
                  icon: Users,
                  description: '조직 문화 적합도',
                  color: 'purple',
                },
              ].map((item) => {
                const score = evaluationResult.scores[item.key as keyof typeof evaluationResult.scores];
                const Icon = item.icon;
                
                return (
                  <motion.div
                    key={item.key}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.1 }}
                  >
                    <Card className={`${getScoreBgColor(score)} border-2`}>
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center gap-3">
                            <div className={`w-12 h-12 rounded-lg bg-${item.color}-100 flex items-center justify-center`}>
                              <Icon className={`w-6 h-6 text-${item.color}-600`} />
                            </div>
                            <div>
                              <h4 className="font-semibold text-gray-900">{item.label}</h4>
                              <p className="text-sm text-gray-600">{item.description}</p>
                            </div>
                          </div>
                          <div className={`text-3xl font-bold ${getScoreColor(score)}`}>
                            {score}
                          </div>
                        </div>
                        <Progress value={score} className="h-3" />
                        <div className="mt-2 text-xs text-gray-500 text-right">
                          상위 {Math.round(100 - score)}% 수준
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })}
            </div>

            {/* 상세 분석 */}
            <Card>
              <CardContent className="p-6 space-y-6">
                <h3 className="text-xl font-bold text-gray-900">상세 분석</h3>

                {/* 기술 스택 분석 */}
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <Target className="w-5 h-5 text-blue-600" />
                    <h4 className="font-semibold text-gray-900">기술 스택 및 숙련도 평가</h4>
                  </div>
                  <p className="text-gray-700 leading-relaxed">{evaluationResult.analysis.tech_stack}</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {evaluationResult.skills.slice(0, 10).map((skill: any, idx: number) => (
                      <Badge key={idx} className="bg-blue-100 text-blue-700">
                        {typeof skill === 'string' ? skill : skill.name}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* 프로젝트 경험 유사도 */}
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <BarChart3 className="w-5 h-5 text-indigo-600" />
                    <h4 className="font-semibold text-gray-900">프로젝트 경험 유사도 분석</h4>
                  </div>
                  <p className="text-gray-700 leading-relaxed">{evaluationResult.analysis.project_similarity}</p>
                </div>

                {/* 이력 진위 검증 */}
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <Shield className="w-5 h-5 text-green-600" />
                    <h4 className="font-semibold text-gray-900">경력 이력 진위 여부 검증</h4>
                  </div>
                  <p className="text-gray-700 leading-relaxed">{evaluationResult.analysis.credibility}</p>
                </div>

                {/* 시장 비교 */}
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <TrendingUp className="w-5 h-5 text-purple-600" />
                    <h4 className="font-semibold text-gray-900">시장 평균 대비 역량 비교</h4>
                  </div>
                  <p className="text-gray-700 leading-relaxed">{evaluationResult.analysis.market_comparison}</p>
                </div>
              </CardContent>
            </Card>

            {/* 강점과 약점 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <h4 className="font-semibold text-gray-900">강점</h4>
                  </div>
                  <ul className="space-y-2">
                    {evaluationResult.strengths.map((strength, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-green-600 mt-2"></div>
                        <span className="text-gray-700">{strength}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <AlertCircle className="w-5 h-5 text-yellow-600" />
                    <h4 className="font-semibold text-gray-900">개선 필요 사항</h4>
                  </div>
                  <ul className="space-y-2">
                    {evaluationResult.weaknesses.map((weakness, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-yellow-600 mt-2"></div>
                        <span className="text-gray-700">{weakness}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>

            {/* AI 추천 의견 */}
            <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200">
              <CardContent className="p-6">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
                    <FileText className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">AI 추천 의견</h4>
                    <p className="text-gray-700 leading-relaxed">{evaluationResult.ai_recommendation}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 액션 버튼 */}
            <div className="flex gap-3">
              <Button
                onClick={() => {
                  setEvaluationResult(null);
                  setSelectedEmployee(null);
                  setEmployees([]);
                  setSearchQuery('');
                }}
                variant="outline"
                className="flex-1"
              >
                새로운 평가
              </Button>
              <Button
                onClick={() => {
                  toast.success('평가 결과가 저장되었습니다');
                }}
                className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600"
              >
                평가 결과 저장
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 이력서 업로드 모달 */}
      {isUploadModalOpen && (
        <ResumeUploadModal
          onClose={() => setIsUploadModalOpen(false)}
          onSuccess={() => {
            setIsUploadModalOpen(false);
            toast.success('이력서가 업로드되었습니다. 분석이 완료되면 결과가 표시됩니다.');
          }}
        />
      )}
    </div>
  );
}
