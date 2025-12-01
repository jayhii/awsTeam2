import { useState } from 'react';
import { Users, Briefcase, TrendingUp, UserPlus, BarChart3, Settings } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Dashboard } from './components/Dashboard';
import { PersonnelManagement } from './components/PersonnelManagement';
import { ProjectManagement } from './components/ProjectManagement';
import { PersonnelRecommendation } from './components/PersonnelRecommendation';
import { DomainAnalysis } from './components/DomainAnalysis';
import { PersonnelEvaluation } from './components/PersonnelEvaluation';

type Tab = 'dashboard' | 'personnel' | 'projects' | 'recommendation' | 'domain' | 'evaluation';

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard');

  const navigation = [
    { id: 'dashboard' as Tab, name: '대시보드', icon: BarChart3 },
    { id: 'personnel' as Tab, name: '인력 관리', icon: Users },
    { id: 'projects' as Tab, name: '프로젝트 관리', icon: Briefcase },
    { id: 'recommendation' as Tab, name: '인력 추천', icon: TrendingUp },
    { id: 'domain' as Tab, name: '도메인 분석', icon: TrendingUp },
    { id: 'evaluation' as Tab, name: '인력 평가', icon: UserPlus },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <motion.header 
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="bg-white/80 backdrop-blur-xl border-b border-gray-200/50 shadow-sm sticky top-0 z-50"
      >
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <motion.div 
                whileHover={{ rotate: 360, scale: 1.1 }}
                transition={{ duration: 0.6 }}
                className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30"
              >
                <Users className="w-6 h-6 text-white" />
              </motion.div>
              <div>
                <h1 className="text-gray-900 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">매치마인드</h1>
                <p className="text-sm text-gray-500">AI 기반 역량 관리 및 프로젝트 추천</p>
              </div>
            </div>
            <motion.button 
              whileHover={{ scale: 1.05, rotate: 90 }}
              whileTap={{ scale: 0.95 }}
              className="p-2 hover:bg-gray-100 rounded-xl transition-colors"
            >
              <Settings className="w-5 h-5 text-gray-600" />
            </motion.button>
          </div>
        </div>
      </motion.header>

      <div className="flex">
        {/* Sidebar */}
        <motion.aside 
          initial={{ x: -100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="w-64 bg-white/60 backdrop-blur-xl border-r border-gray-200/50 min-h-[calc(100vh-73px)]"
        >
          <nav className="p-4 space-y-1">
            {navigation.map((item, index) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <motion.button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  initial={{ x: -50, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  whileHover={{ scale: 1.02, x: 4 }}
                  whileTap={{ scale: 0.98 }}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 relative overflow-hidden ${
                    isActive
                      ? 'text-white shadow-lg shadow-blue-500/30'
                      : 'text-gray-700 hover:bg-white/80'
                  }`}
                >
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl"
                      transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                    />
                  )}
                  <Icon className={`w-5 h-5 relative z-10 ${isActive ? 'text-white' : ''}`} />
                  <span className="relative z-10">{item.name}</span>
                </motion.button>
              );
            })}
          </nav>
        </motion.aside>

        {/* Main Content */}
        <main className="flex-1 p-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
            >
              {activeTab === 'dashboard' && <Dashboard />}
              {activeTab === 'personnel' && <PersonnelManagement />}
              {activeTab === 'projects' && <ProjectManagement />}
              {activeTab === 'recommendation' && <PersonnelRecommendation />}
              {activeTab === 'domain' && <DomainAnalysis />}
              {activeTab === 'evaluation' && <PersonnelEvaluation />}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}