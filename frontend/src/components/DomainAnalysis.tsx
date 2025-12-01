import { useState } from 'react';
import { TrendingUp, Users, Lightbulb, ArrowRight, Search, AlertCircle, CheckCircle, Target, Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { api } from '../config/api';

// API 응답 타입 정의
interface IdentifiedDomain {
  domain_name: string;
  feasibility_score: number;
  required_skills: string[];
  matched_skills: string[];
  skill_gap: string[];
  skill_proficiency: Record<string, string>;
  transferable_employees: number;
  recommended_team: string[];
  reasoning: string;
}

interface DomainAnalysisResult {
  current_domains: string[];
  identified_domains: IdentifiedDomain[];
  total_projects_analyzed: number;
  total_employees: number;
}

export function DomainAnalysis() {
  const [selectedDomain, setSelectedDomain] = useState<IdentifiedDomain | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [domainData, setDomainData] = useState<DomainAnalysisResult | null>(null);

  const handleDomainAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.domainAnalysis({ 
        analysis_type: 'new_domains' 
      });
      setDomainData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : '도메인 분석 실패');
    } finally {
      setLoading(false);
    }
  };

  // 실현 가능성 점수에 따른 색상 반환
  const getFeasibilityColor = (score: number): string => {
    if (score >= 70) return 'from-green-500 to-emerald-600';
    if (score >= 40) return 'from-yellow-500 to-orange-600';
    return 'from-red-500 to-rose-600';
  };

  // 실현 가능성 점수에 따른 배지 색상
  const getFeasibilityBadgeColor = (score: number): string => {
    if (score >= 70) return 'bg-green-100 text-green-700 border-green-200';
    if (score >= 40) return 'bg-yellow-100 text-yellow-700 border-yellow-200';
    return 'bg-red-100 text-red-700 border-red-200';
  };

  // 실현 가능성 레벨 텍스트
  const getFeasibilityLevel = (score: number): string => {
    if (score >= 70) return '높음';
    if (score >= 40) return '중간';
    return '낮음';
  };

  // 숙련도 레벨에 따른 색상
  const getProficiencyColor = (level: string): string => {
    switch (level) {
      case 'Expert': return 'bg-purple-100 text-purple-700';
      case 'Advanced': return 'bg-blue-100 text-blue-700';
      case 'Intermediate': return 'bg-green-100 text-green-700';
      case 'Beginner': return 'bg-gray-100 text-gray-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="space-y-6">
      {/* 헤더 섹션 */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h2 className="text-3xl font-bold text-gray-900 mb-2 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
          도메인 분석
        </h2>
        <p className="text-gray-600">인력 이력을 기반으로 신규 도메인 진출 가능성을 분석합니다</p>
      </motion.div>

      {/* 분석 실행 섹션 */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-blue-500/10 to-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="w-5 h-5 text-blue-600" />
              도메인 확장 분석
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4 mb-6">
              <Button 
                onClick={handleDomainAnalysis} 
                disabled={loading}
                className="gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
              >
                <Search className="w-4 h-4" />
                {loading ? '분석 중...' : '신규 도메인 분석 시작'}
              </Button>
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 mb-4 flex items-start gap-3"
              >
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold">분석 실패</p>
                  <p className="text-sm">{error}</p>
                </div>
              </motion.div>
            )}

            {domainData && (
              <div className="space-y-6">
                {/* 현재 도메인 vs 잠재 도메인 비교 - Task 27.1 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* 현재 도메인 */}
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-100"
                  >
                    <div className="flex items-center gap-2 mb-3">
                      <CheckCircle className="w-5 h-5 text-blue-600" />
                      <h3 className="text-lg font-semibold text-blue-900">현재 보유 도메인</h3>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {domainData.current_domains.map((domain, idx) => (
                        <motion.div
                          key={idx}
                          initial={{ opacity: 0, scale: 0 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: idx * 0.05 }}
                        >
                          <Badge className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
                            {domain}
                          </Badge>
                        </motion.div>
                      ))}
                    </div>
                    <p className="text-sm text-blue-700 mt-3">
                      총 {domainData.current_domains.length}개 도메인
                    </p>
                  </motion.div>

                  {/* 잠재 도메인 */}
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-100"
                  >
                    <div className="flex items-center gap-2 mb-3">
                      <Lightbulb className="w-5 h-5 text-purple-600" />
                      <h3 className="text-lg font-semibold text-purple-900">신규 진출 기회</h3>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {domainData.identified_domains.slice(0, 5).map((domain, idx) => (
                        <motion.div
                          key={idx}
                          initial={{ opacity: 0, scale: 0 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: idx * 0.05 }}
                        >
                          <Badge variant="outline" className="border-purple-200 text-purple-700">
                            {domain.domain_name}
                          </Badge>
                        </motion.div>
                      ))}
                    </div>
                    <p className="text-sm text-purple-700 mt-3">
                      총 {domainData.identified_domains.length}개 기회 발견
                    </p>
                  </motion.div>
                </div>

                {/* 분석 통계 */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="p-4 bg-white rounded-xl border border-gray-200">
                    <p className="text-sm text-gray-600 mb-1">분석 프로젝트</p>
                    <p className="text-2xl font-bold text-gray-900">{domainData.total_projects_analyzed}</p>
                  </div>
                  <div className="p-4 bg-white rounded-xl border border-gray-200">
                    <p className="text-sm text-gray-600 mb-1">분석 인력</p>
                    <p className="text-2xl font-bold text-gray-900">{domainData.total_employees}</p>
                  </div>
                  <div className="p-4 bg-white rounded-xl border border-gray-200">
                    <p className="text-sm text-gray-600 mb-1">현재 도메인</p>
                    <p className="text-2xl font-bold text-blue-600">{domainData.current_domains.length}</p>
                  </div>
                  <div className="p-4 bg-white rounded-xl border border-gray-200">
                    <p className="text-sm text-gray-600 mb-1">신규 기회</p>
                    <p className="text-2xl font-bold text-purple-600">{domainData.identified_domains.length}</p>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* 도메인 확장 추천 섹션 - Task 27.3 */}
      {domainData && domainData.identified_domains.length > 0 && (
        <div>
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-2 mb-4"
          >
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <Zap className="w-5 h-5 text-purple-600" />
            </motion.div>
            <h3 className="text-xl font-bold text-gray-900">도메인 확장 추천 (우선순위 순)</h3>
          </motion.div>

          <div className="grid grid-cols-1 gap-6">
            {domainData.identified_domains
              .sort((a, b) => b.feasibility_score - a.feasibility_score)
              .map((domain, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  whileHover={{ scale: 1.01, y: -2 }}
                  onClick={() => setSelectedDomain(domain)}
                >
                  <Card className="cursor-pointer bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all overflow-hidden">
                    {/* 배경 그라데이션 */}
                    <div className={`absolute top-0 right-0 w-64 h-64 bg-gradient-to-br ${getFeasibilityColor(domain.feasibility_score)}/10 rounded-full blur-3xl pointer-events-none`} />
                    
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <CardTitle className="text-2xl bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                              {domain.domain_name}
                            </CardTitle>
                            <Badge className={getFeasibilityBadgeColor(domain.feasibility_score)}>
                              실현가능성: {getFeasibilityLevel(domain.feasibility_score)}
                            </Badge>
                          </div>
                          
                          {/* 진행률 표시 - Task 27.1 */}
                          <div className="space-y-2">
                            <div className="flex items-center justify-between text-sm">
                              <span className="text-gray-600">실현 가능성 점수</span>
                              <span className="font-semibold text-gray-900">{domain.feasibility_score.toFixed(1)}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                              <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${domain.feasibility_score}%` }}
                                transition={{ duration: 1, delay: index * 0.1, ease: "easeOut" }}
                                className={`bg-gradient-to-r ${getFeasibilityColor(domain.feasibility_score)} h-3 rounded-full`}
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    </CardHeader>

                    <CardContent>
                      <div className="space-y-6">
                        {/* AI 분석 근거 */}
                        <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-100">
                          <div className="flex items-start gap-2 mb-2">
                            <Lightbulb className="w-4 h-4 text-blue-600 flex-shrink-0 mt-1" />
                            <p className="text-sm font-semibold text-blue-900">AI 분석 근거</p>
                          </div>
                          <p className="text-sm text-blue-800 leading-relaxed">{domain.reasoning}</p>
                        </div>

                        {/* 기술 갭 시각화 - Task 27.2 */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {/* 보유 기술 */}
                          <div className="p-4 bg-green-50 rounded-xl border border-green-100">
                            <div className="flex items-center gap-2 mb-3">
                              <CheckCircle className="w-4 h-4 text-green-600" />
                              <p className="text-sm font-semibold text-green-900">
                                보유 기술 ({domain.matched_skills.length}개)
                              </p>
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {domain.matched_skills.length > 0 ? (
                                domain.matched_skills.map((skill, idx) => (
                                  <motion.div
                                    key={idx}
                                    initial={{ opacity: 0, scale: 0 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: index * 0.05 + idx * 0.02 }}
                                  >
                                    <Badge className="bg-green-600 text-white">
                                      {skill}
                                      {domain.skill_proficiency[skill] && (
                                        <span className="ml-1 text-xs opacity-80">
                                          ({domain.skill_proficiency[skill]})
                                        </span>
                                      )}
                                    </Badge>
                                  </motion.div>
                                ))
                              ) : (
                                <p className="text-sm text-green-700">보유 기술 없음</p>
                              )}
                            </div>
                          </div>

                          {/* 부족한 기술 - Task 27.2 */}
                          <div className="p-4 bg-red-50 rounded-xl border border-red-100">
                            <div className="flex items-center gap-2 mb-3">
                              <AlertCircle className="w-4 h-4 text-red-600" />
                              <p className="text-sm font-semibold text-red-900">
                                필요 기술 ({domain.skill_gap.length}개)
                              </p>
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {domain.skill_gap.length > 0 ? (
                                domain.skill_gap.map((skill, idx) => (
                                  <motion.div
                                    key={idx}
                                    initial={{ opacity: 0, scale: 0 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: index * 0.05 + idx * 0.02 }}
                                  >
                                    <Badge variant="outline" className="border-red-200 text-red-700">
                                      {skill}
                                    </Badge>
                                  </motion.div>
                                ))
                              ) : (
                                <p className="text-sm text-red-700">모든 필요 기술 보유</p>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* 전환 가능 인력 및 추천 팀 - Task 27.3 */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="p-4 bg-purple-50 rounded-xl border border-purple-100">
                            <div className="flex items-center gap-2 mb-2">
                              <Users className="w-4 h-4 text-purple-600" />
                              <p className="text-sm font-semibold text-purple-900">전환 가능 인력</p>
                            </div>
                            <p className="text-3xl font-bold text-purple-600">{domain.transferable_employees}명</p>
                            <p className="text-xs text-purple-700 mt-1">
                              필요 기술의 30% 이상 보유
                            </p>
                          </div>

                          <div className="p-4 bg-blue-50 rounded-xl border border-blue-100">
                            <div className="flex items-center gap-2 mb-2">
                              <Target className="w-4 h-4 text-blue-600" />
                              <p className="text-sm font-semibold text-blue-900">추천 팀원</p>
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {domain.recommended_team.slice(0, 5).map((userId, idx) => (
                                <Badge key={idx} variant="secondary" className="text-xs">
                                  {userId}
                                </Badge>
                              ))}
                              {domain.recommended_team.length > 5 && (
                                <Badge variant="secondary" className="text-xs">
                                  +{domain.recommended_team.length - 5}
                                </Badge>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* 상세 분석 버튼 */}
                        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                          <Button 
                            variant="outline" 
                            size="sm" 
                            className="w-full gap-2 border-blue-200 text-blue-700 hover:bg-blue-50"
                          >
                            상세 전략 수립하기
                            <ArrowRight className="w-4 h-4" />
                          </Button>
                        </motion.div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
          </div>
        </div>
      )}

      {/* 선택된 도메인 상세 정보 모달 */}
      {selectedDomain && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedDomain(null)}
        >
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            onClick={(e) => e.stopPropagation()}
            className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
          >
            <Card className="border-0">
              <CardHeader className="border-b">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-2xl mb-2">{selectedDomain.domain_name}</CardTitle>
                    <Badge className={getFeasibilityBadgeColor(selectedDomain.feasibility_score)}>
                      실현가능성: {selectedDomain.feasibility_score.toFixed(1)}%
                    </Badge>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedDomain(null)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    ✕
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="p-6">
                <div className="space-y-6">
                  {/* AI 분석 */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">AI 분석 근거</h4>
                    <p className="text-gray-700 leading-relaxed">{selectedDomain.reasoning}</p>
                  </div>

                  {/* 필요 기술 전체 목록 */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">필요 기술 전체 목록</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedDomain.required_skills.map((skill, idx) => (
                        <Badge key={idx} variant="outline">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* 추천 팀 전체 */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">추천 팀원 전체</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      {selectedDomain.recommended_team.map((userId, idx) => (
                        <div key={idx} className="p-2 bg-gray-100 rounded-lg text-sm text-center">
                          {userId}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* 액션 버튼 */}
                  <div className="flex gap-3 pt-4 border-t">
                    <Button className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600">
                      팀 구성 시작
                    </Button>
                    <Button variant="outline" onClick={() => setSelectedDomain(null)}>
                      닫기
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>
      )}

      {/* 통계 요약 */}
      {domainData && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { 
              icon: TrendingUp, 
              label: '신규 도메인 기회', 
              value: domainData.identified_domains.length, 
              color: 'from-blue-500 to-blue-600',
              description: '진출 가능한 신규 도메인'
            },
            { 
              icon: Users, 
              label: '전환 가능 인력', 
              value: domainData.identified_domains.reduce((acc, d) => acc + d.transferable_employees, 0), 
              color: 'from-green-500 to-emerald-600',
              description: '도메인 전환 가능 인력'
            },
            { 
              icon: CheckCircle, 
              label: '현재 보유 도메인', 
              value: domainData.current_domains.length, 
              color: 'from-purple-500 to-purple-600',
              description: '현재 운영 중인 도메인'
            },
          ].map((stat, index) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.05, y: -5 }}
              >
                <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-4">
                      <motion.div 
                        whileHover={{ rotate: 360 }}
                        transition={{ duration: 0.6 }}
                        className={`w-12 h-12 bg-gradient-to-br ${stat.color} rounded-xl flex items-center justify-center shadow-lg`}
                      >
                        <Icon className="w-6 h-6 text-white" />
                      </motion.div>
                      <div className="flex-1">
                        <p className="text-sm text-gray-600 mb-1">{stat.label}</p>
                        <motion.p 
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ delay: index * 0.1 + 0.2 }}
                          className="text-2xl font-bold text-gray-900"
                        >
                          {stat.value}
                          <span className="text-sm font-normal text-gray-600 ml-1">
                            {stat.label.includes('인력') ? '명' : '개'}
                          </span>
                        </motion.p>
                        <p className="text-xs text-gray-500 mt-1">{stat.description}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}