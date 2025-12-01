/**
 * 프로젝트 배정 확인 모달 컴포넌트
 * Requirements: 2.5 - 프로젝트 배정 기능
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

interface ProjectAssignmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => Promise<void>;
  employeeName: string;
  projectName: string;
  employeeAvailability?: 'available' | 'busy' | 'pending';
}

export function ProjectAssignmentModal({
  isOpen,
  onClose,
  onConfirm,
  employeeName,
  projectName,
  employeeAvailability = 'available',
}: ProjectAssignmentModalProps) {
  const [isAssigning, setIsAssigning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleConfirm = async () => {
    try {
      setIsAssigning(true);
      setError(null);
      await onConfirm();
      onClose();
    } catch (err: any) {
      setError(err.message || '배정에 실패했습니다.');
    } finally {
      setIsAssigning(false);
    }
  };

  if (!isOpen) return null;

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
          className="w-full max-w-md"
        >
          <Card className="border-0 shadow-2xl">
            <CardHeader className="relative">
              <button
                onClick={onClose}
                className="absolute right-4 top-4 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                프로젝트 배정 확인
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* 배정 정보 */}
              <div className="space-y-3">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">직원</p>
                  <p className="font-semibold text-gray-900">{employeeName}</p>
                </div>
                <div className="p-4 bg-indigo-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">프로젝트</p>
                  <p className="font-semibold text-gray-900">{projectName}</p>
                </div>
              </div>

              {/* 가용성 경고 */}
              {employeeAvailability !== 'available' && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-start gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg"
                >
                  <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-yellow-900">가용성 확인 필요</p>
                    <p className="text-xs text-yellow-700 mt-1">
                      {employeeAvailability === 'busy'
                        ? '이 직원은 현재 다른 프로젝트에 투입되어 있습니다.'
                        : '이 직원의 가용성이 확인되지 않았습니다.'}
                    </p>
                  </div>
                </motion.div>
              )}

              {/* 에러 메시지 */}
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg"
                >
                  <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-red-800">{error}</p>
                </motion.div>
              )}

              {/* 확인 메시지 */}
              <p className="text-sm text-gray-600">
                해당 직원을 프로젝트에 배정하시겠습니까?
              </p>

              {/* 액션 버튼 */}
              <div className="flex gap-3 pt-2">
                <Button
                  variant="outline"
                  onClick={onClose}
                  disabled={isAssigning}
                  className="flex-1"
                >
                  취소
                </Button>
                <Button
                  onClick={handleConfirm}
                  disabled={isAssigning}
                  className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                >
                  {isAssigning ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      배정 중...
                    </>
                  ) : (
                    '배정 확인'
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
