import { useState, useEffect } from 'react';
import { TrendingUp, Users, Lightbulb, ArrowRight, Search, AlertCircle, CheckCircle, Target, Zap, BarChart3, Activity, RefreshCw, Briefcase, Database, TrendingDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { api } from '../config/api';

// 타입 정의
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

interface DomainPortfolio {
  domain_name: string;
  project_count: number;
  expert_count: number;
  maturity_level: string;
  tech_domains?: string[];
}

interface TechTrend {
  tech_name: string;
  category: string;
  trend_score: number;
  demand_score: number;
  growth_rate: number;
  market_share: number;
  related_domains: string[];
}

export function DomainAnalysisEnhanced() {
  const [activeTab, setActiveTab] = useState<'analysis' | 'portfolio' | 'trends'>('portfolio');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [domainData, setDomainData] = useState<DomainAnalysisResult | null>(null);
  const [portfolioData, setPortfolioData] = useState<DomainPortfolio[]>([]);
  const [trendData, setTrendData] = useState<TechTrend[]>([]);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [selectedDomain, setSelectedDomain] = useState<IdentifiedDomain | null>(null);

  // 초기 데이터 로드
  useEffect(() => {
    loadPortfolioData();
    loadTrendData();
  }, []);

  // 자동 새로고침
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        loadPortfolioData();
        loadTrendData();
      }, 30000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadPortfolioData = async () => {
    try {
      const projects = await api.getProjects();
      const employees = await api.getEmployees();
      
      const domainMap = new Map<string, DomainPortfolio>();
      
      projects.projects.forEach(project => {
        const domain = (project as any).knowledge_domain || 'General';
        const existing = domainMap.get(domain) || {
          domain_name: domain,
          project_count: 0,
          expert_count: 0,
          maturity_level: 'Developing',
          tech_domains: []
        };
        
        existing.project_count++;
        if ((project as any).tech_domains) {
          existing.tech_domains = Array.from(new Set([
            ...(existing.tech_domains || []),
            ...(project as any).tech_domains
          ]));
        }
        
        domainMap.set(domain, existing);
      });
      
      employees.employees.forEach(employee => {
        const domainExp = (employee as any).domain_experience;
        if (domainExp?.knowledge_domains) {
          domainExp.knowledge_domains.forEach((kd: any) => {
            const domain = kd.domain;
            const existing = domainMap.get(domain);
            if (existing) {
              existing.expert_count++;
            }
          });
        }
      });
      
      setPortfolioData(Array.from(domainMap.values()).filter(d => d.domain_name !== 'General'));
    } catch (err) {
      console.error('포트폴리오 데이터 로드 실패:', err);
    }
  };

  const loadTrendData = async () => {
    const mockTrends: TechTrend[] = [
      { tech_name: 'Python', category: 'Backend', trend_score: 95, demand_score: 95, growth_rate: 12.8, market_share: 28.3, related_domains: ['Healthcare', 'E-commerce'] },
      { tech_name: 'AWS', category: 'Cloud', trend_score: 94, demand_score: 96, growth_rate: 11.2, market_share: 52.3, related_domains: ['Finance', 'Healthcare'] },
      { tech_name: 'React', category: 'Frontend', trend_score: 92, demand_score: 93, growth_rate: 10.2, market_share: 42.8, related_domains: ['E-commerce', 'Education'] },
      { tech_name: 'PyTorch', category: 'AI_ML', trend_score: 92, demand_score: 87, growth_rate: 16.8, market_share: 32.8, related_domains: ['Healthcare', 'Aviation'] },
      { tech_name: 'Kubernetes', category: 'Cloud', trend_score: 91, demand_score: 89, growth_rate: 14.5, market_share: 38.7, related_domains: ['Telecommunications', 'Finance'] },
      { tech_name: 'Node.js', category: 'Backend', trend_score: 88, demand_score: 85, growth_rate: 8.5, market_share: 22.1, related_domains: ['E-commerce', 'Aviation'] },
      { tech_name: 'Flutter', category: 'Mobile', trend_score: 88, demand_score: 80, growth_rate: 18.7, market_share: 28.5, related_domains: ['Aviation', 'E-commerce'] },
      { tech_name: 'Docker', category: 'Cloud', trend_score: 87, demand_score: 88, growth_rate: 7.3, market_share: 45.2, related_domains: ['Finance', 'Healthcare'] },
    ];
    setTrendData(mockTrends);
  };

  const handleDomainAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.domainAnalysis({ analysis_type: 'new_domains' });
      setDomainData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : '도메인 분석 실패');
    } finally {
      setLoading(false);
    }
  };

  const getDomainColor = (domain: string): string => {
    const colors: Record<string, string> = {
      'Finance': 'from-blue-500 to-blue-600',
      'Healthcare': 'from-green-500 to-emerald-600',
      'E-commerce': 'from-purple-500 to-purple-600',
      'Manufacturing': 'from-orange-500 to-orange-600',
      'Aviation': 'from-sky-500 to-sky-600',
      'Education': 'from-yellow-500 to-yellow-600',
      'Logistics': 'from-red-500 to-red-600',
      'Telecommunications': 'from-indigo-500 to-indigo-600',
    };
    return colors[domain] || 'from-gray-500 to-gray-600';
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
          <h2 className="text-3xl font-bold text-gray-900 mb-2 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            도메인 분석 & 관리
          </h2>
          <p className="text-gray-600">인력 이력과 기술 트렌드를 기반으로 도메인 포트폴리오를 관리합니다</p>
        </div>
        
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              loadPortfolioData();
              loadTrendData();
            }}
            className="gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            새로고침
          </Button>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded"
            />
            <span className="text-sm text-gray-600">자동 새로고침</span>
          </label>
        </div>
      </motion.div>

      {/* 탭 네비게이션 */}
      <div className="flex gap-2 border-b border-gray-200">
        {[
          { id: 'portfolio', label: '도메인 포트폴리오', icon: Briefcase },
          { id: 'analysis', label: '신규 도메인 분석', icon: Target },
          { id: 'trends', label: '기술 트렌드', icon: Activity },
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-6 py-3 font-medium transition-all ${
                activeTab === tab.id
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <div className="flex items-center gap-2">
                <Icon className="w-4 h-4" />
                {tab.label}
              </div>
            </button>
          );
        })}
      </div>

      {/* 탭 컨텐츠 */}
      <AnimatePresence mode="wait">
        {activeTab === 'portfolio' && (
          <motion.div
            key="portfolio"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            {/* 도메인 포트폴리오 대시보드 */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {portfolioData.map((domain, index) => (
                <motion.div
                  key={domain.domain_name}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.05 }}
                  whileHover={{ scale: 1.02, y: -5 }}
                >
                  <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all overflow-hidden">
                    <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${getDomainColor(domain.domain_name)}/10 rounded-full blur-2xl`} />
                    
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle className="text-xl mb-2">{domain.domain_name}</CardTitle>
                          <Badge className="bg-blue-100 text-blue-700">
                            {domain.maturity_level}
                          </Badge>
                        </div>
                        <div className={`w-12 h-12 bg-gradient-to-br ${getDomainColor(domain.domain_name)} rounded-xl flex items-center justify-center shadow-lg`}>
                          <Database className="w-6 h-6 text-white" />
                        </div>
                      </div>
                    </CardHeader>

                    <CardContent>
                      <div className="space-y-4">
                        {/* 통계 */}
                        <div className="grid grid-cols-2 gap-4">
                          <div className="p-3 bg-blue-50 rounded-lg">
                            <p className="text-xs text-blue-600 mb-1">프로젝트</p>
                            <p className="text-2xl font-bold text-blue-900">{domain.project_count}</p>
                          </div>
                          <div className="p-3 bg-green-50 rounded-lg">
                            <p className="text-xs text-green-600 mb-1">전문가</p>
                            <p className="text-2xl font-bold text-green-900">{domain.expert_count}</p>
                          </div>
                        </div>

                        {/* 기술 도메인 */}
                        {domain.tech_domains && domain.tech_domains.length > 0 && (
                          <div>
                            <p className="text-xs text-gray-600 mb-2">주요 기술</p>
                            <div className="flex flex-wrap gap-1">
                              {domain.tech_domains.slice(0, 4).map((tech, idx) => (
                                <Badge key={idx} variant="outline" className="text-xs">
                                  {tech}
                                </Badge>
                              ))}
                              {domain.tech_domains.length > 4 && (
                                <Badge variant="outline" className="text-xs">
                                  +{domain.tech_domains.length - 4}
                                </Badge>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>

            {/* 요약 통계 */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
              <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm opacity-90">총 도메인</p>
                      <p className="text-3xl font-bold mt-1">{portfolioData.length}</p>
                    </div>
                    <Briefcase className="w-10 h-10 opacity-50" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-green-500 to-emerald-600 text-white">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm opacity-90">총 프로젝트</p>
                      <p className="text-3xl font-bold mt-1">
                        {portfolioData.reduce((sum, d) => sum + d.project_count, 0)}
                      </p>
                    </div>
                    <BarChart3 className="w-10 h-10 opacity-50" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm opacity-90">총 전문가</p>
                      <p className="text-3xl font-bold mt-1">
                        {portfolioData.reduce((sum, d) => sum + d.expert_count, 0)}
                      </p>
                    </div>
                    <Users className="w-10 h-10 opacity-50" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm opacity-90">평균 팀 규모</p>
                      <p className="text-3xl font-bold mt-1">
                        {portfolioData.length > 0
                          ? Math.round(portfolioData.reduce((sum, d) => sum + d.project_count, 0) / portfolioData.length)
                          : 0}
                      </p>
                    </div>
                    <Target className="w-10 h-10 opacity-50" />
                  </div>
                </CardContent>
              </Card>
            </div>
          </motion.div>
        )}

        {activeTab === 'trends' && (
          <motion.div
            key="trends"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            {/* 기술 트렌드 차트 */}
            <div className="space-y-6">
              {/* TOP 트렌드 */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-green-600" />
                    트렌드 점수 TOP 8
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {trendData
                      .sort((a, b) => b.trend_score - a.trend_score)
                      .map((trend, index) => (
                        <motion.div
                          key={trend.tech_name}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                        >
                          <div className="flex-shrink-0 w-8 text-center">
                            <span className="text-lg font-bold text-gray-400">#{index + 1}</span>
                          </div>
                          
                          <div className="flex-1">
                            <div className="flex items-center justify-between mb-2">
                              <div>
                                <span className="font-semibold text-gray-900">{trend.tech_name}</span>
                                <Badge variant="outline" className="ml-2 text-xs">
                                  {trend.category}
                                </Badge>
                              </div>
                              <div className="flex items-center gap-4 text-sm">
                                <div className="flex items-center gap-1">
                                  <TrendingUp className="w-4 h-4 text-green-600" />
                                  <span className="font-semibold">{trend.trend_score}</span>
                                </div>
                                <div className="text-gray-600">
                                  성장률: <span className="font-semibold text-green-600">+{trend.growth_rate}%</span>
                                </div>
                              </div>
                            </div>
                            
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${trend.trend_score}%` }}
                                transition={{ duration: 1, delay: index * 0.1 }}
                                className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2 rounded-full"
                              />
                            </div>
                            
                            <div className="flex items-center gap-2 mt-2">
                              <span className="text-xs text-gray-600">관련 도메인:</span>
                              {trend.related_domains.slice(0, 3).map((domain, idx) => (
                                <Badge key={idx} variant="secondary" className="text-xs">
                                  {domain}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        </motion.div>
                      ))}
                  </div>
                </CardContent>
              </Card>

              {/* 카테고리별 트렌드 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {['Backend', 'Frontend', 'Cloud', 'AI_ML'].map((category) => {
                  const categoryTrends = trendData.filter(t => t.category === category);
                  if (categoryTrends.length === 0) return null;
                  
                  return (
                    <Card key={category}>
                      <CardHeader>
                        <CardTitle className="text-lg">{category}</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          {categoryTrends.map((trend) => (
                            <div key={trend.tech_name} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                              <span className="font-medium">{trend.tech_name}</span>
                              <div className="flex items-center gap-2">
                                <span className="text-sm text-gray-600">{trend.trend_score}</span>
                                <div className={`flex items-center ${trend.growth_rate > 10 ? 'text-green-600' : 'text-gray-600'}`}>
                                  {trend.growth_rate > 10 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'analysis' && (
          <motion.div
            key="analysis"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            {/* 기존 도메인 분석 UI */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5 text-blue-600" />
                  신규 도메인 진출 분석
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <Button
                    onClick={handleDomainAnalysis}
                    disabled={loading}
                    className="gap-2 bg-gradient-to-r from-blue-600 to-indigo-600"
                  >
                    <Search className="w-4 h-4" />
                    {loading ? '분석 중...' : '신규 도메인 분석 시작'}
                  </Button>

                  {error && (
                    <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
                      <AlertCircle className="w-5 h-5 inline mr-2" />
                      {error}
                    </div>
                  )}

                  {domainData && (
                    <div className="space-y-4">
                      <div className="grid grid-cols-3 gap-4">
                        <div className="p-4 bg-blue-50 rounded-lg">
                          <p className="text-sm text-blue-600 mb-1">현재 도메인</p>
                          <p className="text-2xl font-bold text-blue-900">{domainData.current_domains.length}</p>
                        </div>
                        <div className="p-4 bg-purple-50 rounded-lg">
                          <p className="text-sm text-purple-600 mb-1">신규 기회</p>
                          <p className="text-2xl font-bold text-purple-900">{domainData.identified_domains.length}</p>
                        </div>
                        <div className="p-4 bg-green-50 rounded-lg">
                          <p className="text-sm text-green-600 mb-1">분석 프로젝트</p>
                          <p className="text-2xl font-bold text-green-900">{domainData.total_projects_analyzed}</p>
                        </div>
                      </div>

                      <div className="space-y-3">
                        {domainData.identified_domains.slice(0, 5).map((domain, index) => (
                          <div key={index} className="p-4 bg-white border rounded-lg hover:shadow-md transition-shadow">
                            <div className="flex items-center justify-between mb-2">
                              <h3 className="font-semibold text-lg">{domain.domain_name}</h3>
                              <Badge className={domain.feasibility_score >= 70 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}>
                                실현가능성: {domain.feasibility_score.toFixed(1)}%
                              </Badge>
                            </div>
                            <p className="text-sm text-gray-600 mb-3">{domain.reasoning}</p>
                            <div className="flex items-center gap-4 text-sm">
                              <span className="text-gray-600">
                                보유 기술: <span className="font-semibold">{domain.matched_skills.length}</span>
                              </span>
                              <span className="text-gray-600">
                                필요 기술: <span className="font-semibold">{domain.skill_gap.length}</span>
                              </span>
                              <span className="text-gray-600">
                                전환 가능 인력: <span className="font-semibold">{domain.transferable_employees}명</span>
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
