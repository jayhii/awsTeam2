import { useState, useEffect } from 'react';
import { Search, Plus, Calendar, Users as UsersIcon } from 'lucide-react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { api, Project as APIProject } from '../config/api';
import { ProjectRegistrationModal, ProjectFormData } from './ProjectRegistrationModal';
import { toast } from 'sonner';

interface Project {
  id: string;
  name: string;
  client: string;
  status: 'planning' | 'in-progress' | 'completed';
  requiredSkills: string[];
  assignedMembers: number;
  requiredMembers: number;
  startDate: string;
  endDate: string;
  matchRate?: number;
}

export function ProjectManagement() {
  const [searchQuery, setSearchQuery] = useState('');
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // DB에서 프로젝트 목록 가져오기
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        setLoading(true);
        const response = await api.getProjects();
        
        // API 응답을 Project 형식으로 변환
        const transformedData: Project[] = response.projects.map((proj: APIProject) => {
          // 상태 매핑
          let status: 'planning' | 'in-progress' | 'completed' = 'planning';
          const projStatus = proj.status?.toLowerCase();
          if (projStatus === '진행중' || projStatus === 'active' || projStatus === 'in-progress') {
            status = 'in-progress';
          } else if (projStatus === '완료' || projStatus === 'completed') {
            status = 'completed';
          }

          // 팀원 수 계산
          const teamMembers = (proj as any).team_members || [];
          const assignedMembers = Array.isArray(teamMembers) ? teamMembers.length : ((proj as any).team_size || 0);
          const requiredMembers = (proj as any).team_size || assignedMembers || 5;

          return {
            id: proj.project_id,
            name: proj.project_name,
            client: (proj as any).client_name || (proj as any).client_industry || '고객사',
            status,
            requiredSkills: proj.required_skills || [],
            assignedMembers: assignedMembers,
            requiredMembers: requiredMembers,
            startDate: proj.start_date || '미정',
            endDate: (proj as any).end_date || proj.start_date || '미정',
            matchRate: undefined,
          };
        });
        
        setProjects(transformedData);
        setError(null);
      } catch (err) {
        console.error('프로젝트 목록 조회 실패:', err);
        setError(err instanceof Error ? err.message : '프로젝트 목록을 불러오는데 실패했습니다');
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, []);

  const filteredProjects = projects.filter((project) =>
    project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.client.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.requiredSkills.some((skill) => skill.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const getStatusColor = (status: Project['status']) => {
    switch (status) {
      case 'planning':
        return 'bg-yellow-100 text-yellow-700';
      case 'in-progress':
        return 'bg-blue-100 text-blue-700';
      case 'completed':
        return 'bg-green-100 text-green-700';
    }
  };

  const getStatusText = (status: Project['status']) => {
    switch (status) {
      case 'planning':
        return '계획 중';
      case 'in-progress':
        return '진행 중';
      case 'completed':
        return '완료';
    }
  };

  // 프로젝트 생성 핸들러
  const handleCreateProject = async (projectData: ProjectFormData) => {
    try {
      await api.createProject(projectData);
      toast.success('프로젝트가 성공적으로 등록되었습니다');
      
      // 프로젝트 목록 새로고침
      const response = await api.getProjects();
      const transformedData: Project[] = response.projects.map((proj: APIProject) => {
        let status: 'planning' | 'in-progress' | 'completed' = 'planning';
        const projStatus = proj.status?.toLowerCase();
        if (projStatus === '진행중' || projStatus === 'active' || projStatus === 'in-progress') {
          status = 'in-progress';
        } else if (projStatus === '완료' || projStatus === 'completed') {
          status = 'completed';
        }

        const teamMembers = (proj as any).team_members || [];
        const assignedMembers = Array.isArray(teamMembers) ? teamMembers.length : ((proj as any).team_size || 0);
        const requiredMembers = (proj as any).team_size || assignedMembers || 5;

        return {
          id: proj.project_id,
          name: proj.project_name,
          client: (proj as any).client_name || (proj as any).client_industry || '고객사',
          status,
          requiredSkills: proj.required_skills || [],
          assignedMembers: assignedMembers,
          requiredMembers: requiredMembers,
          startDate: proj.start_date || '미정',
          endDate: (proj as any).end_date || proj.start_date || '미정',
          matchRate: undefined,
        };
      });
      setProjects(transformedData);
    } catch (err) {
      console.error('프로젝트 등록 실패:', err);
      toast.error(err instanceof Error ? err.message : '프로젝트 등록에 실패했습니다');
      throw err;
    }
  };

  // AI 인력 추천 받기 핸들러
  const handleGetRecommendations = (projectId: string) => {
    // 추천 기능은 인력 추천 탭에서 프로젝트 ID를 선택하여 사용
    toast.info('인력 추천 탭으로 이동하여 프로젝트를 선택해주세요.');
    console.log('프로젝트 ID:', projectId);
  };

  return (
    <div className="space-y-6">
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h2 className="text-gray-900 mb-2 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">프로젝트 관리</h2>
          <p className="text-gray-600">진행 중인 프로젝트와 투입 인력을 관리하세요 (총 {projects.length}개)</p>
        </div>
        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
          <Button 
            onClick={() => setIsModalOpen(true)}
            className="gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg shadow-blue-500/30"
          >
            <Plus className="w-4 h-4" />
            신규 프로젝트 등록
          </Button>
        </motion.div>
      </motion.div>

      {/* 로딩 및 에러 상태 */}
      {loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">프로젝트 목록을 불러오는 중...</p>
        </motion.div>
      )}

      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700"
        >
          {error}
        </motion.div>
      )}

      {/* Search */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
          <CardContent className="p-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <Input
                placeholder="프로젝트명, 고객사, 기술 스택으로 검색..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 border-0 bg-gray-50 focus:bg-white transition-colors"
              />
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Projects List */}
      {!loading && !error && (
        <div className="space-y-4">
          {filteredProjects.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-600">검색 결과가 없습니다</p>
            </div>
          ) : (
            filteredProjects.map((project, index) => (
          <motion.div
            key={project.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: index * 0.05 }}
            whileHover={{ scale: 1.01, y: -2 }}
          >
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all overflow-hidden">
              <div className="absolute top-0 right-0 w-48 h-48 bg-gradient-to-br from-blue-500/5 to-indigo-500/5 rounded-full blur-2xl" />
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <CardTitle className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">{project.name}</CardTitle>
                      <motion.span 
                        whileHover={{ scale: 1.1 }}
                        className={`px-3 py-1 rounded-full text-xs ${getStatusColor(project.status)}`}
                      >
                        {getStatusText(project.status)}
                      </motion.span>
                    </div>
                    <p className="text-sm text-gray-600">{project.client}</p>
                  </div>
                  {project.matchRate && (
                    <motion.div 
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: index * 0.05 + 0.2 }}
                      className="text-right"
                    >
                      <p className="text-sm text-gray-600">AI 매칭률</p>
                      <p className="text-blue-600">{project.matchRate}%</p>
                    </motion.div>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <div className="flex items-center gap-2 text-gray-600 mb-3">
                      <Calendar className="w-4 h-4" />
                      <span className="text-sm">프로젝트 기간</span>
                    </div>
                    <p className="text-gray-900">{project.startDate} ~ {project.endDate}</p>
                  </div>

                  <div>
                    <div className="flex items-center gap-2 text-gray-600 mb-3">
                      <UsersIcon className="w-4 h-4" />
                      <span className="text-sm">투입 인력</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <p className="text-gray-900">
                        {project.assignedMembers} / {project.requiredMembers}명
                      </p>
                      {project.assignedMembers < project.requiredMembers && (
                        <span className="text-xs text-orange-600">
                          ({project.requiredMembers - project.assignedMembers}명 부족)
                        </span>
                      )}
                    </div>
                    <div className="mt-2 w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${(project.assignedMembers / project.requiredMembers) * 100}%` }}
                        transition={{ duration: 1, delay: index * 0.05, ease: "easeOut" }}
                        className="bg-gradient-to-r from-blue-600 to-indigo-600 h-2 rounded-full"
                      />
                    </div>
                  </div>

                  <div>
                    <p className="text-sm text-gray-600 mb-3">요구 기술</p>
                    <div className="flex flex-wrap gap-2">
                      {project.requiredSkills.map((skill, idx) => (
                        <motion.div
                          key={skill}
                          initial={{ opacity: 0, scale: 0 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: index * 0.05 + idx * 0.03 }}
                        >
                          <Badge variant="outline" className="border-blue-200 text-blue-700">
                            {skill}
                          </Badge>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </div>

                {project.assignedMembers < project.requiredMembers && (
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: index * 0.05 + 0.3 }}
                    className="mt-4 pt-4 border-t border-gray-200"
                  >
                    <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={() => handleGetRecommendations(project.id)}
                        className="w-full md:w-auto border-blue-200 text-blue-700 hover:bg-blue-50"
                      >
                        AI 인력 추천 받기
                      </Button>
                    </motion.div>
                  </motion.div>
                )}
              </CardContent>
            </Card>
          </motion.div>
            ))
          )}
        </div>
      )}

      {/* 프로젝트 등록 모달 */}
      <ProjectRegistrationModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreateProject}
      />
    </div>
  );
}