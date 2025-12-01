import { useState } from 'react';
import { X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';

interface ProjectRegistrationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (projectData: ProjectFormData) => Promise<void>;
}

export interface ProjectFormData {
  project_name: string;
  client_industry: string;
  required_skills: string[];
  duration_months: number;
  team_size: number;
  start_date: string;
  budget_scale?: string;
  description?: string;
}

export function ProjectRegistrationModal({
  isOpen,
  onClose,
  onSubmit,
}: ProjectRegistrationModalProps) {
  const [formData, setFormData] = useState<ProjectFormData>({
    project_name: '',
    client_industry: '',
    required_skills: [],
    duration_months: 0,
    team_size: 0,
    start_date: '',
    budget_scale: '',
    description: '',
  });

  const [skillInput, setSkillInput] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // 폼 유효성 검사
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.project_name.trim()) {
      newErrors.project_name = '프로젝트명을 입력해주세요';
    }

    if (!formData.client_industry.trim()) {
      newErrors.client_industry = '산업 분야를 입력해주세요';
    }

    if (formData.required_skills.length === 0) {
      newErrors.required_skills = '최소 1개 이상의 기술을 입력해주세요';
    }

    if (formData.duration_months <= 0) {
      newErrors.duration_months = '프로젝트 기간을 입력해주세요';
    }

    if (formData.team_size <= 0) {
      newErrors.team_size = '팀 규모를 입력해주세요';
    }

    if (!formData.start_date) {
      newErrors.start_date = '시작일을 선택해주세요';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 기술 추가
  const handleAddSkill = () => {
    const trimmedSkill = skillInput.trim();
    if (trimmedSkill && !formData.required_skills.includes(trimmedSkill)) {
      setFormData({
        ...formData,
        required_skills: [...formData.required_skills, trimmedSkill],
      });
      setSkillInput('');
      // 기술이 추가되면 에러 제거
      if (errors.required_skills) {
        const newErrors = { ...errors };
        delete newErrors.required_skills;
        setErrors(newErrors);
      }
    }
  };

  // 기술 제거
  const handleRemoveSkill = (skillToRemove: string) => {
    setFormData({
      ...formData,
      required_skills: formData.required_skills.filter(
        (skill) => skill !== skillToRemove
      ),
    });
  };

  // Enter 키로 기술 추가
  const handleSkillKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddSkill();
    }
  };

  // 폼 제출
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(formData);
      // 성공 시 폼 초기화 및 모달 닫기
      setFormData({
        project_name: '',
        client_industry: '',
        required_skills: [],
        duration_months: 0,
        team_size: 0,
        start_date: '',
        budget_scale: '',
        description: '',
      });
      setErrors({});
      onClose();
    } catch (error) {
      console.error('프로젝트 등록 실패:', error);
      // 에러는 부모 컴포넌트에서 처리
    } finally {
      setIsSubmitting(false);
    }
  };

  // 모달 닫기
  const handleClose = () => {
    if (!isSubmitting) {
      setErrors({});
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
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              {/* 헤더 */}
              <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between rounded-t-2xl">
                <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  신규 프로젝트 등록
                </h2>
                <button
                  onClick={handleClose}
                  disabled={isSubmitting}
                  className="text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* 폼 */}
              <form onSubmit={handleSubmit} className="p-6 space-y-6">
                {/* 프로젝트명 */}
                <div>
                  <Label htmlFor="project_name" className="text-gray-700">
                    프로젝트명 <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="project_name"
                    value={formData.project_name}
                    onChange={(e) =>
                      setFormData({ ...formData, project_name: e.target.value })
                    }
                    placeholder="예: 차세대 금융 코어 뱅킹 시스템"
                    className={errors.project_name ? 'border-red-500' : ''}
                    disabled={isSubmitting}
                  />
                  {errors.project_name && (
                    <p className="text-red-500 text-sm mt-1">{errors.project_name}</p>
                  )}
                </div>

                {/* 산업 분야 */}
                <div>
                  <Label htmlFor="client_industry" className="text-gray-700">
                    산업 분야 <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="client_industry"
                    value={formData.client_industry}
                    onChange={(e) =>
                      setFormData({ ...formData, client_industry: e.target.value })
                    }
                    placeholder="예: Finance / Banking"
                    className={errors.client_industry ? 'border-red-500' : ''}
                    disabled={isSubmitting}
                  />
                  {errors.client_industry && (
                    <p className="text-red-500 text-sm mt-1">
                      {errors.client_industry}
                    </p>
                  )}
                </div>

                {/* 요구 기술 */}
                <div>
                  <Label htmlFor="required_skills" className="text-gray-700">
                    요구 기술 <span className="text-red-500">*</span>
                  </Label>
                  <div className="flex gap-2">
                    <Input
                      id="required_skills"
                      value={skillInput}
                      onChange={(e) => setSkillInput(e.target.value)}
                      onKeyPress={handleSkillKeyPress}
                      placeholder="기술을 입력하고 Enter를 누르세요"
                      className={errors.required_skills ? 'border-red-500' : ''}
                      disabled={isSubmitting}
                    />
                    <Button
                      type="button"
                      onClick={handleAddSkill}
                      disabled={!skillInput.trim() || isSubmitting}
                      variant="outline"
                    >
                      추가
                    </Button>
                  </div>
                  {errors.required_skills && (
                    <p className="text-red-500 text-sm mt-1">
                      {errors.required_skills}
                    </p>
                  )}
                  {/* 추가된 기술 목록 */}
                  {formData.required_skills.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-3">
                      {formData.required_skills.map((skill) => (
                        <Badge
                          key={skill}
                          variant="outline"
                          className="border-blue-200 text-blue-700 px-3 py-1"
                        >
                          {skill}
                          <button
                            type="button"
                            onClick={() => handleRemoveSkill(skill)}
                            disabled={isSubmitting}
                            className="ml-2 text-blue-500 hover:text-blue-700 disabled:opacity-50"
                          >
                            ×
                          </button>
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>

                {/* 프로젝트 기간 및 팀 규모 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="duration_months" className="text-gray-700">
                      프로젝트 기간 (개월) <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="duration_months"
                      type="number"
                      min="1"
                      value={formData.duration_months || ''}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          duration_months: parseInt(e.target.value) || 0,
                        })
                      }
                      placeholder="예: 18"
                      className={errors.duration_months ? 'border-red-500' : ''}
                      disabled={isSubmitting}
                    />
                    {errors.duration_months && (
                      <p className="text-red-500 text-sm mt-1">
                        {errors.duration_months}
                      </p>
                    )}
                  </div>

                  <div>
                    <Label htmlFor="team_size" className="text-gray-700">
                      팀 규모 (명) <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="team_size"
                      type="number"
                      min="1"
                      value={formData.team_size || ''}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          team_size: parseInt(e.target.value) || 0,
                        })
                      }
                      placeholder="예: 20"
                      className={errors.team_size ? 'border-red-500' : ''}
                      disabled={isSubmitting}
                    />
                    {errors.team_size && (
                      <p className="text-red-500 text-sm mt-1">{errors.team_size}</p>
                    )}
                  </div>
                </div>

                {/* 시작일 */}
                <div>
                  <Label htmlFor="start_date" className="text-gray-700">
                    시작일 <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="start_date"
                    type="date"
                    value={formData.start_date}
                    onChange={(e) =>
                      setFormData({ ...formData, start_date: e.target.value })
                    }
                    className={errors.start_date ? 'border-red-500' : ''}
                    disabled={isSubmitting}
                  />
                  {errors.start_date && (
                    <p className="text-red-500 text-sm mt-1">{errors.start_date}</p>
                  )}
                </div>

                {/* 예산 규모 (선택사항) */}
                <div>
                  <Label htmlFor="budget_scale" className="text-gray-700">
                    예산 규모 (선택사항)
                  </Label>
                  <Input
                    id="budget_scale"
                    value={formData.budget_scale}
                    onChange={(e) =>
                      setFormData({ ...formData, budget_scale: e.target.value })
                    }
                    placeholder="예: 150억 원"
                    disabled={isSubmitting}
                  />
                </div>

                {/* 프로젝트 설명 (선택사항) */}
                <div>
                  <Label htmlFor="description" className="text-gray-700">
                    프로젝트 설명 (선택사항)
                  </Label>
                  <textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) =>
                      setFormData({ ...formData, description: e.target.value })
                    }
                    placeholder="프로젝트에 대한 간단한 설명을 입력하세요"
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    disabled={isSubmitting}
                  />
                </div>

                {/* 버튼 */}
                <div className="flex gap-3 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleClose}
                    disabled={isSubmitting}
                    className="flex-1"
                  >
                    취소
                  </Button>
                  <Button
                    type="submit"
                    disabled={isSubmitting}
                    className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                  >
                    {isSubmitting ? '등록 중...' : '프로젝트 등록'}
                  </Button>
                </div>
              </form>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
