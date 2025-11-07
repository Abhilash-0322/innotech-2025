'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { Flame, Activity, Database, AlertTriangle, Droplets, LogOut, Brain, FileText } from 'lucide-react';
import LiveSensorData from '@/components/LiveSensorData';
import HistoricalData from '@/components/HistoricalData';
import AlertsPanel from '@/components/AlertsPanel';
import SprinklerControl from '@/components/SprinklerControl';
import AIResponsesViewer from '@/components/AIResponsesViewer';
import SensorRecordsViewer from '@/components/SensorRecordsViewer';
import AIRecommendationsSidebar from '@/components/AIRecommendationsSidebar';

type TabType = 'live' | 'history' | 'records' | 'ai' | 'alerts' | 'sprinkler';

export default function DashboardPage() {
  const router = useRouter();
  const { user, clearAuth, isAuthenticated, isHydrated, hydrate } = useAuthStore();
  const [activeTab, setActiveTab] = useState<TabType>('live');

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  useEffect(() => {
    if (isHydrated && !isAuthenticated) {
      router.push('/login');
    }
  }, [isHydrated, isAuthenticated, router]);

  const handleLogout = () => {
    clearAuth();
    router.push('/login');
  };

  const tabs = [
    { id: 'live' as TabType, name: 'Live Data', icon: Activity, color: 'text-green-600' },
    { id: 'history' as TabType, name: 'Historical Charts', icon: Database, color: 'text-blue-600' },
    { id: 'records' as TabType, name: 'All Records', icon: FileText, color: 'text-indigo-600' },
    { id: 'ai' as TabType, name: 'AI Responses', icon: Brain, color: 'text-purple-600' },
    { id: 'alerts' as TabType, name: 'Alerts', icon: AlertTriangle, color: 'text-orange-600' },
    { id: 'sprinkler' as TabType, name: 'Sprinkler Control', icon: Droplets, color: 'text-cyan-600' },
  ];

  if (!isHydrated || !isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Flame className="w-10 h-10 text-orange-500" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Smart Forest Fire Prevention System
                </h1>
                <p className="text-sm text-gray-600">Real-time monitoring & AI-powered alerts</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{user?.full_name}</p>
                <p className="text-xs text-gray-500">{user?.email}</p>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Tabs Navigation */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <nav className="flex w-full">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex-1 flex items-center justify-center space-x-2 px-6 py-4 border-b-2 font-medium text-sm transition
                  ${
                    activeTab === tab.id
                      ? `border-orange-500 ${tab.color} bg-orange-50`
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 hover:bg-gray-50'
                  }
                `}
              >
                <Icon className="w-5 h-5" />
                <span>{tab.name}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <main className="w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content Area */}
          <div className="lg:col-span-2">
            {activeTab === 'live' && <LiveSensorData />}
            {activeTab === 'history' && <HistoricalData />}
            {activeTab === 'records' && <SensorRecordsViewer />}
            {activeTab === 'ai' && <AIResponsesViewer />}
            {activeTab === 'alerts' && <AlertsPanel />}
            {activeTab === 'sprinkler' && <SprinklerControl />}
          </div>

          {/* AI Recommendations Sidebar */}
          <div className="lg:col-span-1">
            <div className="sticky top-8">
              <AIRecommendationsSidebar />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
