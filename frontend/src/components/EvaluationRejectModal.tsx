import { useState } from 'react';
import { XCircle, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

interface EvaluationRejectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (reason: string) => Promise<void>;
  evaluationName: string;
}

export function EvaluationRejectModal({
  isOpen,
  onClose,
  onSubmit,
  evaluationName,
}: EvaluationRejectModalProps) {
  const [reason, setReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!reason.trim()) {
      setError('반려 사유를 입력해주세요');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await onSubmit(reason);
      // 성공 시 모달 닫기 및 초기화
      setReason('');
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : '반려 처리에 실패했습니다');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setReason('');
      setError(null);
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={handleClose}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-lg"
          >
            <Card className="border-0 shadow-2xl">
              <CardHeader className="border-b bg-gradient-to-r from-red-50 to-orange-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-red-100 rounded-lg">
                      <XCircle className="w-5 h-5 text-red-600" />
                    </div>
                    <CardTitle className="text-red-900">평가 반려</CardTitle>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleClose}
                    disabled={isSubmitting}
                    className="h-8 w-8 p-0"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-600 mb-2">
                      <span className="font-semibold text-gray-900">{evaluationName}</span>님의 평가를 반려합니다
                    </p>
                    <p className="text-sm text-gray-500">
                      반려 사유를 입력해주세요. 입력하신 내용은 평가 이력에 기록됩니다.
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      반려 사유 <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      value={reason}
                      onChange={(e) => setReason(e.target.value)}
                      placeholder="반려 사유를 상세히 입력해주세요..."
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500 min-h-[120px] resize-none"
                      disabled={isSubmitting}
                    />
                    {error && (
                      <p className="mt-2 text-sm text-red-600">{error}</p>
                    )}
                  </div>

                  <div className="flex gap-3 pt-4">
                    <Button
                      variant="outline"
                      onClick={handleClose}
                      disabled={isSubmitting}
                      className="flex-1"
                    >
                      취소
                    </Button>
                    <Button
                      onClick={handleSubmit}
                      disabled={isSubmitting || !reason.trim()}
                      className="flex-1 bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700"
                    >
                      {isSubmitting ? '처리 중...' : '반려하기'}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
