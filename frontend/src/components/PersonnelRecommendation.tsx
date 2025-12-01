import { useState, useEffect } from 'react';
import { Sparkles, TrendingUp, Users, CheckCircle, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { ProjectAssignmentModal } from './ProjectAssignmentModal';
import { RecommendationDetailModal } from './RecommendationDetailModal';
import { api } from '../config/api';
import type { Project } from '../config/api';

interface Recommendation {
  user_id: string;
  name: string;
  role: string;
  skill_match_score: number;
  affinity_score: number;
  availability_score: number;
  overall_score: number;
  reasoning: string;
  matched_skills: string[];
  team_synergy: string[];
  years_of_experience?: number;
  availability?: 'available' | 'busy' | 'pending';
}

export function PersonnelRecommendation() {
  const [selectedProject, setSelectedProject] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isLoadingProjects, setIsLoadingProjects] = useState(true);
  const [projects, setProjects] = useState<Project[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [error, setError] = useState<string | null>(null);
  
  // 배정 모달 상태
  const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState<Recommendation | null>(null);
  
  // 상세 정보 모달 상태
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [selectedDetail, setSelectedDetail] = useState<Recommendation | null>(null);

  // 프로젝트 목록 로드
  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setIsLoadingProjects(true);
      setError(null);
      const response = await api.getProjects();
      setProjects(response.projects || []);
      
      // 첫 번째 프로젝트를 기본 선택
      if (response.projects && response.projects.length > 0) {
        setSelectedProject(response.projects[0].project_id);
      }
    } catch (err) {
      console.error('프로젝트 목록 로드 실패:', err);
      setError('프로젝트 목록을 불러오는데 실패했습니다.');
    } finally {
      setIsLoadingProjects(false);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedProject) {
      setError('프로젝트를 선택해주세요.');
      return;
    }

    try {
      setIsAnalyzing(true);
      setError(null);
      
      // API 호출하여 추천 결과 가져오기
      const response = await api.recommendations({ project_id: selectedProject });
      
      // 응답 데이터를 컴포넌트 형식에 맞게 변환
      const formattedRecommendations: Recommendation[] = response.recommendations.map((rec: any) => ({
        user_id: rec.user_id,
        name: rec.name,
        role: rec.role || 'Developer',
        skill_match_score: rec.skill_match_score || rec.score || 0,
        affinity_score: rec.affinity_score || 0,
        availability_score: rec.availability_score || 100,
        overall_score: rec.overall_score || rec.score || 0,
        reasoning: rec.reasoning || '',
        matched_skills: rec.matched_skills || [],
        team_synergy: rec.team_synergy || [],
        years_of_experience: rec.years_of_experience || 0,
        availability: rec.availability || 'available',
      }));
      
      setRecommendations(formattedRecommendations);
    } catch (err: any) {
      console.error('추천 분석 실패:', err);
      setError(err.message || '추천 분석에 실패했습니다.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // 배정 모달 열기
  const handleOpenAssignModal = (employee: Recommendation) => {
    setSelectedEmployee(employee);
    setIsAssignModalOpen(true);
  };

  // 상세 정보 모달 열기
  const handleOpenDetailModal = (employee: Recommendation) => {
    setSelectedDetail(employee);
    setIsDetailModalOpen(true);
  };

  // 프로젝트 배정 확인
  const handleConfirmAssignment = async () => {
    if (!selectedEmployee || !selectedProject) return;

    try {
      // API 호출하여 프로젝트 배정
      const response = await api.assignProject(selectedProject, selectedEmployee.user_id);
      
      console.log('배정 완료:', response);
      
      // 성공 메시지 표시
      alert(`${selectedEmployee.name}님이 프로젝트에 배정되었습니다.`);
      
      // 추천 목록 새로고침
      await handleAnalyze();
    } catch (err: any) {
      console.error('배정 실패:', err);
      throw err; // 모달에서 에러 처리
    }
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h2 className="text-gray-900 mb-2 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">인력 추천</h2>
        <p className="text-gray-600">AI가 프로젝트에 최적화된 인력을 추천합니다</p>
      </motion.div>

      {/* 에러 메시지 */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 bg-red-50 border border-red-200 rounded-lg"
        >
          <p className="text-sm text-red-800">{error}</p>
        </motion.div>
      )}

      {/* Project Selection */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-blue-500/10 to-indigo-500/10 rounded-full blur-3xl" />
          <CardHeader>
            <CardTitle className="flex items-center gap-2 relative">
              <motion.div
                animate={{ rotate: [0, 360] }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              >
                <Sparkles className="w-5 h-5 text-blue-600" />
              </motion.div>
              프로젝트 선택 및 AI 분석
            </CardTitle>
          </CardHeader>
          <CardContent className="relative">
            {isLoadingProjects ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
                <span className="ml-2 text-gray-600">프로젝트 목록 로딩 중...</span>
              </div>
            ) : (
              <div className="flex gap-4">
                <div className="flex-1">
                  <Select value={selectedProject} onValueChange={setSelectedProject}>
                    <SelectTrigger>
                      <SelectValue placeholder="프로젝트 선택" />
                    </SelectTrigger>
                    <SelectContent>
                      {projects.map((project) => (
                        <SelectItem key={project.project_id} value={project.project_id}>
                          {project.project_name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button 
                    onClick={handleAnalyze} 
                    disabled={isAnalyzing || !selectedProject} 
                    className="gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg shadow-blue-500/30"
                  >
                    {isAnalyzing ? (
                      <>
                        <motion.div 
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                          className="w-4 h-4 border-2 border-white border-t-transparent rounded-full"
                        />
                        분석 중...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4" />
                        AI 분석 시작
                      </>
                    )}
                  </Button>
                </motion.div>
              </div>
            )}

            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="mt-4 p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-100"
            >
              <p className="text-sm text-blue-900 mb-2">분석 기준</p>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• 기술 스택 매칭률 (40%)</li>
                <li>• 프로젝트 참여 이력 유사도 (30%)</li>
                <li>• 팀원 간 친밀도 및 협업 경험 (20%)</li>
                <li>• 현재 가용성 및 투입 가능 시기 (10%)</li>
              </ul>
            </motion.div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Analysis Results */}
      {recommendations.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-900">추천 결과</h3>
            <span className="text-sm text-gray-600">{recommendations.length}명의 후보</span>
          </div>

          <div className="space-y-4">
            <AnimatePresence>
              {recommendations.map((rec, index) => (
                <motion.div
                  key={rec.user_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  whileHover={{ scale: 1.02, y: -2 }}
                >
                  <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-full blur-2xl" />
                    <CardContent className="p-6 relative">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-4">
                          <motion.div 
                            whileHover={{ rotate: 360 }}
                            transition={{ duration: 0.6 }}
                            className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg"
                          >
                            <span className="text-white">#{index + 1}</span>
                          </motion.div>
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <p className="text-gray-900">{rec.name}</p>
                              <Badge variant="secondary" className="bg-blue-50 text-blue-700">{rec.role}</Badge>
                              {rec.availability && (
                                <Badge 
                                  variant={rec.availability === 'available' ? 'default' : 'secondary'}
                                  className={rec.availability === 'available' ? 'bg-green-500' : 'bg-yellow-500'}
                                >
                                  {rec.availability === 'available' ? '가용' : rec.availability === 'busy' ? '투입중' : '대기'}
                                </Badge>
                              )}
                            </div>
                            <p className="text-sm text-gray-600">경력 {rec.years_of_experience || 0}년</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="flex items-center gap-2 mb-1">
                            <TrendingUp className="w-4 h-4 text-blue-600" />
                            <span className="text-blue-600">종합 점수</span>
                          </div>
                          <motion.p 
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ duration: 0.5, delay: index * 0.1 + 0.3 }}
                            className="text-gray-900"
                          >
                            {Math.round(rec.overall_score)}%
                          </motion.p>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
                        <div>
                          <div className="flex items-center gap-2 text-gray-600 mb-2">
                            <CheckCircle className="w-4 h-4" />
                            <span className="text-sm">매칭 기술 ({rec.matched_skills.length}개)</span>
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {rec.matched_skills.slice(0, 5).map((skill, idx) => (
                              <motion.div
                                key={skill}
                                initial={{ opacity: 0, scale: 0 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: index * 0.1 + idx * 0.05 }}
                              >
                                <Badge className="bg-gradient-to-r from-blue-600 to-indigo-600">{skill}</Badge>
                              </motion.div>
                            ))}
                            {rec.matched_skills.length > 5 && (
                              <Badge variant="outline">+{rec.matched_skills.length - 5}</Badge>
                            )}
                          </div>
                        </div>

                        <div>
                          <div className="flex items-center gap-2 text-gray-600 mb-2">
                            <Users className="w-4 h-4" />
                            <span className="text-sm">팀 친밀도</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                              <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${rec.affinity_score}%` }}
                                transition={{ duration: 1, delay: index * 0.1, ease: "easeOut" }}
                                className="bg-gradient-to-r from-green-500 to-emerald-500 h-2 rounded-full"
                              />
                            </div>
                            <span className="text-sm text-gray-900">{Math.round(rec.affinity_score)}%</span>
                          </div>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div className="text-center p-3 bg-blue-50 rounded-lg">
                          <p className="text-xs text-gray-600 mb-1">기술 매칭</p>
                          <p className="text-lg font-semibold text-blue-600">{Math.round(rec.skill_match_score)}%</p>
                        </div>
                        <div className="text-center p-3 bg-green-50 rounded-lg">
                          <p className="text-xs text-gray-600 mb-1">가용성</p>
                          <p className="text-lg font-semibold text-green-600">{Math.round(rec.availability_score)}%</p>
                        </div>
                      </div>

                      {rec.reasoning && (
                        <div className="pt-4 border-t border-gray-200">
                          <p className="text-sm text-gray-600 mb-2">AI 추천 근거</p>
                          <motion.div 
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg"
                          >
                            {rec.reasoning}
                          </motion.div>
                        </div>
                      )}

                      <div className="mt-4 flex gap-2">
                        <motion.div className="flex-1" whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                          <Button 
                            size="sm" 
                            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                            disabled={rec.availability === 'busy'}
                            onClick={() => handleOpenAssignModal(rec)}
                          >
                            프로젝트에 투입
                          </Button>
                        </motion.div>
                        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleOpenDetailModal(rec)}
                          >
                            상세 정보
                          </Button>
                        </motion.div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}

      {/* 추천 결과가 없을 때 */}
      {!isAnalyzing && recommendations.length === 0 && selectedProject && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <p className="text-gray-500">프로젝트를 선택하고 AI 분석을 시작해주세요.</p>
        </motion.div>
      )}

      {/* 프로젝트 배정 모달 */}
      <ProjectAssignmentModal
        isOpen={isAssignModalOpen}
        onClose={() => setIsAssignModalOpen(false)}
        onConfirm={handleConfirmAssignment}
        employeeName={selectedEmployee?.name || ''}
        projectName={projects.find(p => p.project_id === selectedProject)?.project_name || ''}
        employeeAvailability={selectedEmployee?.availability}
      />

      {/* 상세 정보 모달 */}
      <RecommendationDetailModal
        isOpen={isDetailModalOpen}
        onClose={() => setIsDetailModalOpen(false)}
        recommendation={selectedDetail}
      />
    </div>
  );
}