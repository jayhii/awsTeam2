import { useState } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';

interface EmployeeFormData {
  name: string;
  email: string;
  role: string;
  years_of_experience: number;
  department: string;
  skills: Array<{
    name: string;
    level: string;
    years: number;
  }>;
  self_introduction: string;
  degree: string;
  university: string;
  certifications: string[];
}

interface EmployeeRegistrationModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: EmployeeFormData) => Promise<void>;
}

const SKILL_LEVELS = ['Beginner', 'Intermediate', 'Advanced', 'Expert'];

export function EmployeeRegistrationModal({ open, onClose, onSubmit }: EmployeeRegistrationModalProps) {
  const [formData, setFormData] = useState<EmployeeFormData>({
    name: '',
    email: '',
    role: '',
    years_of_experience: 0,
    department: '',
    skills: [{ name: '', level: 'Intermediate', years: 0 }],
    self_introduction: '',
    degree: '',
    university: '',
    certifications: [''],
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // 폼 유효성 검사
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = '이름을 입력해주세요';
    }

    if (!formData.email.trim()) {
      newErrors.email = '이메일을 입력해주세요';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = '올바른 이메일 형식이 아닙니다';
    }

    if (!formData.role.trim()) {
      newErrors.role = '직급을 입력해주세요';
    }

    if (formData.years_of_experience < 0) {
      newErrors.years_of_experience = '경력 연수는 0 이상이어야 합니다';
    }

    if (!formData.department.trim()) {
      newErrors.department = '부서를 입력해주세요';
    }

    // 기술 스택 검증
    const validSkills = formData.skills.filter(skill => skill.name.trim());
    if (validSkills.length === 0) {
      newErrors.skills = '최소 1개 이상의 기술을 입력해주세요';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 폼 제출
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      // 빈 값 필터링
      const cleanedData = {
        ...formData,
        skills: formData.skills.filter(skill => skill.name.trim()),
        certifications: formData.certifications.filter(cert => cert.trim()),
      };

      await onSubmit(cleanedData);
      
      // 성공 시 폼 초기화 및 닫기
      setFormData({
        name: '',
        email: '',
        role: '',
        years_of_experience: 0,
        department: '',
        skills: [{ name: '', level: 'Intermediate', years: 0 }],
        self_introduction: '',
        degree: '',
        university: '',
        certifications: [''],
      });
      setErrors({});
      onClose();
    } catch (error) {
      console.error('직원 등록 실패:', error);
      setErrors({ submit: error instanceof Error ? error.message : '직원 등록에 실패했습니다' });
    } finally {
      setLoading(false);
    }
  };

  // 기술 추가
  const addSkill = () => {
    setFormData({
      ...formData,
      skills: [...formData.skills, { name: '', level: 'Intermediate', years: 0 }],
    });
  };

  // 기술 삭제
  const removeSkill = (index: number) => {
    const newSkills = formData.skills.filter((_, i) => i !== index);
    setFormData({ ...formData, skills: newSkills });
  };

  // 기술 업데이트
  const updateSkill = (index: number, field: string, value: string | number) => {
    const newSkills = [...formData.skills];
    newSkills[index] = { ...newSkills[index], [field]: value };
    setFormData({ ...formData, skills: newSkills });
  };

  // 자격증 추가
  const addCertification = () => {
    setFormData({
      ...formData,
      certifications: [...formData.certifications, ''],
    });
  };

  // 자격증 삭제
  const removeCertification = (index: number) => {
    const newCerts = formData.certifications.filter((_, i) => i !== index);
    setFormData({ ...formData, certifications: newCerts });
  };

  // 자격증 업데이트
  const updateCertification = (index: number, value: string) => {
    const newCerts = [...formData.certifications];
    newCerts[index] = value;
    setFormData({ ...formData, certifications: newCerts });
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            신규 인력 등록
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 기본 정보 */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">기본 정보</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">이름 *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="홍길동"
                  className={errors.name ? 'border-red-500' : ''}
                />
                {errors.name && <p className="text-sm text-red-500 mt-1">{errors.name}</p>}
              </div>

              <div>
                <Label htmlFor="email">이메일 *</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="hong@example.com"
                  className={errors.email ? 'border-red-500' : ''}
                />
                {errors.email && <p className="text-sm text-red-500 mt-1">{errors.email}</p>}
              </div>

              <div>
                <Label htmlFor="role">직급 *</Label>
                <Input
                  id="role"
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  placeholder="Senior Software Engineer"
                  className={errors.role ? 'border-red-500' : ''}
                />
                {errors.role && <p className="text-sm text-red-500 mt-1">{errors.role}</p>}
              </div>

              <div>
                <Label htmlFor="department">부서 *</Label>
                <Input
                  id="department"
                  value={formData.department}
                  onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                  placeholder="개발팀"
                  className={errors.department ? 'border-red-500' : ''}
                />
                {errors.department && <p className="text-sm text-red-500 mt-1">{errors.department}</p>}
              </div>

              <div>
                <Label htmlFor="years_of_experience">경력 연수 *</Label>
                <Input
                  id="years_of_experience"
                  type="number"
                  min="0"
                  value={formData.years_of_experience}
                  onChange={(e) => setFormData({ ...formData, years_of_experience: parseInt(e.target.value) || 0 })}
                  placeholder="5"
                  className={errors.years_of_experience ? 'border-red-500' : ''}
                />
                {errors.years_of_experience && <p className="text-sm text-red-500 mt-1">{errors.years_of_experience}</p>}
              </div>
            </div>

            <div>
              <Label htmlFor="self_introduction">자기소개</Label>
              <textarea
                id="self_introduction"
                value={formData.self_introduction}
                onChange={(e) => setFormData({ ...formData, self_introduction: e.target.value })}
                placeholder="간단한 자기소개를 입력해주세요"
                className="w-full min-h-[100px] px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* 기술 스택 */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">기술 스택 *</h3>
              <Button type="button" onClick={addSkill} size="sm" variant="outline">
                <Plus className="w-4 h-4 mr-1" />
                기술 추가
              </Button>
            </div>
            
            {errors.skills && <p className="text-sm text-red-500">{errors.skills}</p>}
            
            <div className="space-y-3">
              {formData.skills.map((skill, index) => (
                <div key={index} className="flex gap-3 items-start">
                  <div className="flex-1">
                    <Input
                      value={skill.name}
                      onChange={(e) => updateSkill(index, 'name', e.target.value)}
                      placeholder="기술 이름 (예: Java, Python)"
                    />
                  </div>
                  <div className="w-40">
                    <Select
                      value={skill.level}
                      onValueChange={(value) => updateSkill(index, 'level', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="숙련도" />
                      </SelectTrigger>
                      <SelectContent>
                        {SKILL_LEVELS.map((level) => (
                          <SelectItem key={level} value={level}>
                            {level}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="w-24">
                    <Input
                      type="number"
                      min="0"
                      value={skill.years}
                      onChange={(e) => updateSkill(index, 'years', parseInt(e.target.value) || 0)}
                      placeholder="연수"
                    />
                  </div>
                  {formData.skills.length > 1 && (
                    <Button
                      type="button"
                      onClick={() => removeSkill(index)}
                      size="sm"
                      variant="ghost"
                      className="text-red-500 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* 학력 정보 */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">학력 정보</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="degree">학위</Label>
                <Input
                  id="degree"
                  value={formData.degree}
                  onChange={(e) => setFormData({ ...formData, degree: e.target.value })}
                  placeholder="Computer Science, BS"
                />
              </div>

              <div>
                <Label htmlFor="university">대학교</Label>
                <Input
                  id="university"
                  value={formData.university}
                  onChange={(e) => setFormData({ ...formData, university: e.target.value })}
                  placeholder="서울대학교"
                />
              </div>
            </div>
          </div>

          {/* 자격증 */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">자격증</h3>
              <Button type="button" onClick={addCertification} size="sm" variant="outline">
                <Plus className="w-4 h-4 mr-1" />
                자격증 추가
              </Button>
            </div>
            
            <div className="space-y-3">
              {formData.certifications.map((cert, index) => (
                <div key={index} className="flex gap-3 items-center">
                  <Input
                    value={cert}
                    onChange={(e) => updateCertification(index, e.target.value)}
                    placeholder="자격증 이름 (예: AWS Certified Solutions Architect)"
                  />
                  {formData.certifications.length > 1 && (
                    <Button
                      type="button"
                      onClick={() => removeCertification(index)}
                      size="sm"
                      variant="ghost"
                      className="text-red-500 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* 에러 메시지 */}
          {errors.submit && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {errors.submit}
            </div>
          )}

          {/* 버튼 */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button type="button" onClick={onClose} variant="outline" disabled={loading}>
              취소
            </Button>
            <Button
              type="submit"
              disabled={loading}
              className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
            >
              {loading ? '등록 중...' : '등록'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
