/**
 * 추천 상세 정보 모달 컴포넌트
 * Requirements: 2.4 - 추천 근거 및 상세 정보 표시
 */

import { motion, AnimatePresence } from 'framer-motion';
import { X, TrendingUp, Users, CheckCircle, Briefcase, Award } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

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

interface RecommendationDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  recommendation: Recommendation | null;
}

export function RecommendationDetailModal({
  isOpen,
  onClose,
  recommendation,
}: RecommendationDetailModalProps) {
  if (!isOpen || !recommendation) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
          className="w-full max-w-4xl max-h-[90vh] overflow-y-auto"
        >
          <Card className="border-0 shadow-2xl">
            <CardHeader className="relative bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
              <button
                onClick={onClose}
                className="absolute right-4 top-4 text-white/80 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
                  <span className="text-2xl font-bold">{recommendation.name.charAt(0)}</span>
                </div>
                <div>
                  <CardTitle className="text-2xl mb-1">{recommendation.name}</CardTitle>
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary" className="bg-white/20 text-white">
                      {recommendation.role}
                    </Badge>
                    <Badge 
                      variant={recommendation.availability === 'available' ? 'default' : 'secondary'}
                      className={recommendation.availability === 'available' ? 'bg-green-500' : 'bg-yellow-500'}
                    >
                      {recommendation.availability === 'available' ? '가용' : recommendation.availability === 'busy' ? '투입중' : '대기'}
                    </Badge>
                  </div>
                </div>
              </div>
            </CardHeader>

            <CardContent className="p-6 space-y-6">
              {/* 종합 점수 */}
              <div className="grid grid-cols-4 gap-4">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="text-center p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl"
                >
                  <TrendingUp className="w-6 h-6 text-blue-600 mx-auto mb-2" />
                  <p className="text-xs text-gray-600 mb-1">종합 점수</p>
                  <p className="text-2xl font-bold text-blue-600">{Math.round(recommendation.overall_score)}%</p>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="text-center p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl"
                >
                  <CheckCircle className="w-6 h-6 text-green-600 mx-auto mb-2" />
                  <p className="text-xs text-gray-600 mb-1">기술 매칭</p>
                  <p className="text-2xl font-bold text-green-600">{Math.round(recommendation.skill_match_score)}%</p>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="text-center p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl"
                >
                  <Users className="w-6 h-6 text-purple-600 mx-auto mb-2" />
                  <p className="text-xs text-gray-600 mb-1">팀 친밀도</p>
                  <p className="text-2xl font-bold text-purple-600">{Math.round(recommendation.affinity_score)}%</p>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="text-center p-4 bg-gradient-to-br from-orange-50 to-amber-50 rounded-xl"
                >
                  <Award className="w-6 h-6 text-orange-600 mx-auto mb-2" />
                  <p className="text-xs text-gray-600 mb-1">가용성</p>
                  <p className="text-2xl font-bold text-orange-600">{Math.round(recommendation.availability_score)}%</p>
                </motion.div>
              </div>

              {/* 경력 정보 */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
              >
                <div className="flex items-center gap-2 mb-3">
                  <Briefcase className="w-5 h-5 text-gray-600" />
                  <h3 className="font-semibold text-gray-900">경력 정보</h3>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-gray-700">
                    총 경력: <span className="font-semibold">{recommendation.years_of_experience || 0}년</span>
                  </p>
                </div>
              </motion.div>

              {/* 매칭 기술 */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
              >
                <div className="flex items-center gap-2 mb-3">
                  <CheckCircle className="w-5 h-5 text-gray-600" />
                  <h3 className="font-semibold text-gray-900">매칭 기술 스택</h3>
                </div>
                <div className="flex flex-wrap gap-2">
                  {recommendation.matched_skills.map((skill, idx) => (
                    <motion.div
                      key={skill}
                      initial={{ opacity: 0, scale: 0 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.6 + idx * 0.05 }}
                    >
                      <Badge className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
                        {skill}
                      </Badge>
                    </motion.div>
                  ))}
                </div>
              </motion.div>

              {/* 팀 시너지 */}
              {recommendation.team_synergy && recommendation.team_synergy.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.7 }}
                >
                  <div className="flex items-center gap-2 mb-3">
                    <Users className="w-5 h-5 text-gray-600" />
                    <h3 className="font-semibold text-gray-900">팀 시너지</h3>
                  </div>
                  <div className="space-y-2">
                    {recommendation.team_synergy.map((synergy, idx) => (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.7 + idx * 0.1 }}
                        className="flex items-start gap-2 p-3 bg-purple-50 rounded-lg"
                      >
                        <span className="text-purple-600 mt-1">•</span>
                        <span className="text-sm text-gray-700">{synergy}</span>
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* AI 추천 근거 */}
              {recommendation.reasoning && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.8 }}
                >
                  <div className="flex items-center gap-2 mb-3">
                    <TrendingUp className="w-5 h-5 text-gray-600" />
                    <h3 className="font-semibold text-gray-900">AI 추천 근거</h3>
                  </div>
                  <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-100">
                    <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                      {recommendation.reasoning}
                    </p>
                  </div>
                </motion.div>
              )}

              {/* 닫기 버튼 */}
              <div className="flex justify-end pt-4">
                <Button
                  onClick={onClose}
                  variant="outline"
                  className="px-6"
                >
                  닫기
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
