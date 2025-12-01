/**
 * 평가 검토 모달 컴포넌트
 * 평가에 대한 검토 의견을 입력하고 제출합니다.
 */

import { useState } from 'react';
import { FileText, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

interface EvaluationReviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (comments: string) => Promise<void>;
  evaluationName: string;
}

export function EvaluationReviewModal({
  isOpen,
  onClose,
  onSubmit,
  evaluationName,
}: EvaluationReviewModalProps) {
  const [comments, setComments] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!comments.trim()) {
      setError('검토 의견을 입력해주세요');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await onSubmit(comments);
      setComments('');
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : '검토 제출에 실패했습니다');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setComments('');
      setError(null);
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* 배경 오버레이 */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
          />

          {/* 모달 */}
          <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="w-full max-w-2xl"
            >
              <Card className="bg-white shadow-2xl border-0">
                <CardHeader className="border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg">
                        <FileText className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <CardTitle>평가 검토</CardTitle>
                        <p className="text-sm text-gray-600 mt-1">{evaluationName}</p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleClose}
                      disabled={isSubmitting}
                      className="rounded-full"
                    >
                      <X className="w-5 h-5" />
                    </Button>
                  </div>
                </CardHeader>

                <CardContent className="p-6">
                  <div className="space-y-4">
                    {/* 안내 메시지 */}
                    <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl">
                      <p className="text-sm text-blue-900">
                        평가에 대한 검토 의견을 입력해주세요. 검토 상태로 변경되며, 추가 확인이 필요한 사항을 기록할 수 있습니다.
                      </p>
                    </div>

                    {/* 검토 의견 입력 */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        검토 의견 <span className="text-red-500">*</span>
                      </label>
                      <textarea
                        value={comments}
                        onChange={(e) => setComments(e.target.value)}
                        placeholder="검토 의견을 입력하세요..."
                        rows={6}
                        disabled={isSubmitting}
                        className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none disabled:bg-gray-100 disabled:cursor-not-allowed"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        {comments.length} / 1000자
                      </p>
                    </div>

                    {/* 에러 메시지 */}
                    {error && (
                      <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="p-4 bg-red-50 border border-red-200 rounded-xl"
                      >
                        <p className="text-sm text-red-700">{error}</p>
                      </motion.div>
                    )}

                    {/* 액션 버튼 */}
                    <div className="flex gap-3 pt-4">
                      <Button
                        onClick={handleClose}
                        variant="outline"
                        disabled={isSubmitting}
                        className="flex-1"
                      >
                        취소
                      </Button>
                      <Button
                        onClick={handleSubmit}
                        disabled={isSubmitting || !comments.trim()}
                        className="flex-1 gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                      >
                        <FileText className="w-4 h-4" />
                        {isSubmitting ? '제출 중...' : '검토 제출'}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
