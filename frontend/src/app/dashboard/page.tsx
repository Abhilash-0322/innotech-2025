'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { Flame, Activity, Database, AlertTriangle, Droplets, LogOut, Brain, FileText, TrendingUp, Map, Satellite, Bell, Settings } from 'lucide-react';
import LiveSensorData from '@/components/LiveSensorData';
import HistoricalData from '@/components/HistoricalData';
import AlertsPanel from '@/components/AlertsPanel';
import SprinklerControl from '@/components/SprinklerControl';
import AIResponsesViewer from '@/components/AIResponsesViewer';
import SensorRecordsViewer from '@/components/SensorRecordsViewer';
import AIRecommendationsSidebar from '@/components/AIRecommendationsSidebar';
import MLPredictions from '@/components/MLPredictions';
import MultiZoneHeatmap from '@/components/MultiZoneHeatmap';
import AdvancedAnalytics from '@/components/AdvancedAnalytics';
import WeatherSatellite from '@/components/WeatherSatellite';
import EnhancedAlertsPanel from '@/components/EnhancedAlertsPanel';
import SystemHealthMonitor from '@/components/SystemHealthMonitor';

type TabType = 'live' | 'ml-predictions' | 'multi-zone' | 'analytics' | 'weather' | 'history' | 'records' | 'ai' | 'alerts' | 'smart-alerts' | 'sprinkler' | 'system';

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
    { id: 'live' as TabType, name: 'Live Data', icon: Activity, color: 'text-green-600', category: 'Core' },
    { id: 'ml-predictions' as TabType, name: 'ML Predictions', icon: Brain, color: 'text-purple-600', category: 'AI' },
    { id: 'multi-zone' as TabType, name: 'Multi-Zone', icon: Map, color: 'text-blue-600', category: 'AI' },
    { id: 'analytics' as TabType, name: 'Analytics', icon: TrendingUp, color: 'text-indigo-600', category: 'AI' },
    { id: 'weather' as TabType, name: 'Weather & Satellite', icon: Satellite, color: 'text-cyan-600', category: 'AI' },
    { id: 'history' as TabType, name: 'Historical Charts', icon: Database, color: 'text-blue-600', category: 'Core' },
    { id: 'records' as TabType, name: 'All Records', icon: FileText, color: 'text-gray-600', category: 'Core' },
    { id: 'ai' as TabType, name: 'AI Responses', icon: Brain, color: 'text-purple-500', category: 'Core' },
    { id: 'alerts' as TabType, name: 'Basic Alerts', icon: AlertTriangle, color: 'text-orange-600', category: 'Core' },
    { id: 'smart-alerts' as TabType, name: 'Smart Alerts', icon: Bell, color: 'text-red-600', category: 'AI' },
    { id: 'sprinkler' as TabType, name: 'Sprinkler', icon: Droplets, color: 'text-cyan-500', category: 'Control' },
    { id: 'system' as TabType, name: 'System Health', icon: Settings, color: 'text-gray-700', category: 'Control' },
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
                <p className="text-sm text-gray-600">AI-Powered Multi-Zone Forest Protection with ML Predictions</p>
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

      {/* Tabs Navigation with Categories */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="overflow-x-auto">
          <nav className="flex min-w-max">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center space-x-2 px-4 py-3 border-b-2 font-medium text-xs transition whitespace-nowrap
                    ${
                      activeTab === tab.id
                        ? `border-orange-500 ${tab.color} bg-orange-50`
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 hover:bg-gray-50'
                    }
                  `}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.name}</span>
                  {tab.category === 'AI' && (
                    <span className="px-1.5 py-0.5 bg-purple-100 text-purple-700 text-[10px] font-bold rounded">AI</span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      <main className="w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content Area */}
          <div className="lg:col-span-2">
            {activeTab === 'live' && <LiveSensorData />}
            {activeTab === 'ml-predictions' && <MLPredictions />}
            {activeTab === 'multi-zone' && <MultiZoneHeatmap />}
            {activeTab === 'analytics' && <AdvancedAnalytics />}
            {activeTab === 'weather' && <WeatherSatellite />}
            {activeTab === 'history' && <HistoricalData />}
            {activeTab === 'records' && <SensorRecordsViewer />}
            {activeTab === 'ai' && <AIResponsesViewer />}
            {activeTab === 'alerts' && <AlertsPanel />}
            {activeTab === 'smart-alerts' && <EnhancedAlertsPanel />}
            {activeTab === 'sprinkler' && <SprinklerControl />}
            {activeTab === 'system' && <SystemHealthMonitor />}
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
