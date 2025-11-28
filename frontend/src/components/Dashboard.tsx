import { Users, Briefcase, TrendingUp, AlertCircle, ArrowUp, ArrowDown } from 'lucide-react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { useEffect, useState } from 'react';
import { api, DashboardMetricsResponse } from '../config/api';

export function Dashboard() {
  const [metrics, setMetrics] = useState<DashboardMetricsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 대시보드 메트릭 데이터 가져오기
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await api.getDashboardMetrics();
        setMetrics(data);
      } catch (err) {
        console.error('대시보드 메트릭 로드 실패:', err);
        setError(err instanceof Error ? err.message : '데이터를 불러오는데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  // 로딩 상태
  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-gray-900 mb-2 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">대시보드</h2>
          <p className="text-gray-600">전체 인력 및 프로젝트 현황을 확인하세요</p>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">데이터를 불러오는 중...</div>
        </div>
      </div>
    );
  }

  // 에러 상태
  if (error || !metrics) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-gray-900 mb-2 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">대시보드</h2>
          <p className="text-gray-600">전체 인력 및 프로젝트 현황을 확인하세요</p>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-red-500">{error || '데이터를 불러올 수 없습니다.'}</div>
        </div>
      </div>
    );
  }

  // 통계 데이터 구성
  const stats = [
    { 
      label: '전체 인력', 
      value: metrics.total_employees.toString(), 
      change: '+0', 
      icon: Users, 
      color: 'from-blue-500 to-blue-600' 
    },
    { 
      label: '진행 중인 프로젝트', 
      value: metrics.active_projects.toString(), 
      change: '+0', 
      icon: Briefcase, 
      color: 'from-green-500 to-emerald-600' 
    },
    { 
      label: '투입 대기 인력', 
      value: metrics.available_employees.toString(), 
      change: '+0', 
      icon: TrendingUp, 
      color: 'from-purple-500 to-purple-600' 
    },
    { 
      label: '검토 필요', 
      value: metrics.pending_reviews.toString(), 
      change: '+0', 
      icon: AlertCircle, 
      color: 'from-orange-500 to-orange-600' 
    },
  ];

  const recentRecommendations = metrics.recent_recommendations;
  const topSkills = metrics.top_skills;

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="text-gray-900 mb-2 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">대시보드</h2>
        <p className="text-gray-600">전체 인력 및 프로젝트 현황을 확인하세요</p>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ scale: 1.05, y: -5 }}
            >
              <Card className="overflow-hidden bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 mb-1">{stat.label}</p>
                      <motion.p 
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ duration: 0.5, delay: index * 0.1 + 0.2 }}
                        className="text-3xl font-bold text-gray-900"
                      >
                        {stat.value}
                      </motion.p>
                      <div className="flex items-center gap-1 text-xs mt-1">
                        {stat.change.startsWith('+') ? (
                          <>
                            <motion.div
                              initial={{ opacity: 0, y: 5 }}
                              animate={{ opacity: 1, y: 0 }}
                              className="flex items-center text-green-600"
                            >
                              <ArrowUp className="w-3 h-3" />
                              <span className="font-medium">{stat.change}</span>
                            </motion.div>
                            <span className="text-gray-500">이번 달</span>
                          </>
                        ) : stat.change.startsWith('-') ? (
                          <>
                            <motion.div
                              initial={{ opacity: 0, y: -5 }}
                              animate={{ opacity: 1, y: 0 }}
                              className="flex items-center text-red-600"
                            >
                              <ArrowDown className="w-3 h-3" />
                              <span className="font-medium">{stat.change}</span>
                            </motion.div>
                            <span className="text-gray-500">이번 달</span>
                          </>
                        ) : (
                          <span className="text-gray-500">변동 없음</span>
                        )}
                      </div>
                    </div>
                    <motion.div 
                      whileHover={{ rotate: 360, scale: 1.1 }}
                      transition={{ duration: 0.6 }}
                      className={`w-12 h-12 bg-gradient-to-br ${stat.color} rounded-xl flex items-center justify-center shadow-lg`}
                    >
                      <Icon className="w-6 h-6 text-white" />
                    </motion.div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Recommendations */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">최근 인력 추천</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentRecommendations.map((rec, index) => (
                  <motion.div 
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                    whileHover={{ scale: 1.02, x: 5 }}
                    className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-blue-50/30 rounded-xl border border-gray-100 cursor-pointer"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 mb-1">{rec.project}</p>
                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        <span className="flex items-center gap-1">
                          <Users className="w-4 h-4" />
                          {rec.recommended}명 추천
                        </span>
                        <motion.span 
                          whileHover={{ scale: 1.1 }}
                          className="text-blue-600 font-semibold"
                        >
                          매칭률 {rec.match_rate}%
                        </motion.span>
                      </div>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs ${
                        rec.status === '승인됨'
                          ? 'bg-green-100 text-green-700'
                          : rec.status === '검토 중'
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-blue-100 text-blue-700'
                      }`}
                    >
                      {rec.status}
                    </span>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Top Skills */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">주요 기술 스택 분포</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {topSkills.map((skill, index) => (
                  <motion.div 
                    key={skill.name}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900">{skill.name}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-600">{skill.count}명</span>
                        <span className="text-xs text-gray-500">({skill.percentage}%)</span>
                      </div>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${skill.percentage}%` }}
                        transition={{ duration: 1, delay: index * 0.1, ease: "easeOut" }}
                        className="bg-gradient-to-r from-blue-600 to-indigo-600 h-2.5 rounded-full shadow-sm"
                      />
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}