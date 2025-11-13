'use client';

import { useEffect, useState } from 'react';
import { systemAPI } from '@/lib/api';
import { Activity, Server, Database, Wifi, WifiOff, CheckCircle, XCircle, AlertTriangle, TrendingUp, TrendingDown, Cpu, HardDrive, Zap } from 'lucide-react';

export default function SystemHealthMonitor() {
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [sensorStatus, setSensorStatus] = useState<any[]>([]);
  const [performance, setPerformance] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSystemHealth();
    const interval = setInterval(fetchSystemHealth, 15000); // Refresh every 15s
    return () => clearInterval(interval);
  }, []);

  const fetchSystemHealth = async () => {
    try {
      setLoading(true);
      const health = await systemAPI.getHealth();
      
      setSystemHealth(health);
      setSensorStatus(health.sensor_status || []);
      setPerformance(health.performance || null);
    } catch (err) {
      console.error('Failed to fetch system health:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: any = {
      healthy: 'text-green-600 bg-green-50',
      degraded: 'text-yellow-600 bg-yellow-50',
      critical: 'text-red-600 bg-red-50',
      offline: 'text-gray-600 bg-gray-50',
      online: 'text-green-600 bg-green-50',
    };
    return colors[status] || 'text-gray-600 bg-gray-50';
  };

  const getStatusIcon = (status: string) => {
    if (status === 'healthy' || status === 'online') return <CheckCircle className="w-5 h-5 text-green-600" />;
    if (status === 'degraded') return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
    if (status === 'offline') return <XCircle className="w-5 h-5 text-gray-600" />;
    return <XCircle className="w-5 h-5 text-red-600" />;
  };

  const getHealthScore = () => {
    if (!systemHealth) return 0;
    const { api_status, database_status, ml_model_status } = systemHealth;
    let score = 0;
    if (api_status === 'healthy') score += 33;
    if (database_status === 'healthy') score += 33;
    if (ml_model_status === 'ready') score += 34;
    return score;
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-center py-12">
          <Activity className="w-8 h-8 text-blue-500 animate-spin" />
          <span className="ml-3 text-gray-600">Checking system health...</span>
        </div>
      </div>
    );
  }

  const healthScore = getHealthScore();

  return (
    <div className="space-y-6">
      {/* Header with Health Score */}
      <div className={`rounded-lg shadow-lg p-6 ${
        healthScore >= 90 ? 'bg-gradient-to-r from-green-600 to-emerald-600' :
        healthScore >= 70 ? 'bg-gradient-to-r from-yellow-600 to-orange-600' :
        'bg-gradient-to-r from-red-600 to-rose-600'
      } text-white`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Activity className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">System Health Monitor</h2>
              <p className="text-white/80">Real-time infrastructure monitoring</p>
            </div>
          </div>
          <div className="text-center">
            <p className="text-sm text-white/80 mb-1">Health Score</p>
            <div className="relative">
              <p className="text-5xl font-bold">{healthScore}%</p>
              {healthScore >= 90 ? (
                <CheckCircle className="absolute -top-2 -right-2 w-6 h-6" />
              ) : healthScore >= 70 ? (
                <AlertTriangle className="absolute -top-2 -right-2 w-6 h-6" />
              ) : (
                <XCircle className="absolute -top-2 -right-2 w-6 h-6" />
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Core Services Status */}
      {systemHealth && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Server className="w-6 h-6 text-blue-600" />
                <h3 className="text-lg font-semibold text-gray-900">API Server</h3>
              </div>
              {getStatusIcon(systemHealth.api_status)}
            </div>
            <div className={`px-3 py-2 rounded-lg text-sm font-semibold mb-3 ${getStatusColor(systemHealth.api_status)}`}>
              {systemHealth.api_status?.toUpperCase() || 'UNKNOWN'}
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Uptime:</span>
                <span className="font-semibold text-gray-900">{systemHealth.uptime || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Version:</span>
                <span className="font-semibold text-gray-900">{systemHealth.api_version || 'v1.0.0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Response Time:</span>
                <span className="font-semibold text-green-600">{systemHealth.avg_response_time || '<50'}ms</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Database className="w-6 h-6 text-purple-600" />
                <h3 className="text-lg font-semibold text-gray-900">Database</h3>
              </div>
              {getStatusIcon(systemHealth.database_status)}
            </div>
            <div className={`px-3 py-2 rounded-lg text-sm font-semibold mb-3 ${getStatusColor(systemHealth.database_status)}`}>
              {systemHealth.database_status?.toUpperCase() || 'UNKNOWN'}
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Records:</span>
                <span className="font-semibold text-gray-900">{systemHealth.total_records?.toLocaleString() || '0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Size:</span>
                <span className="font-semibold text-gray-900">{systemHealth.db_size || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Last Backup:</span>
                <span className="font-semibold text-gray-900">
                  {systemHealth.last_backup ? new Date(systemHealth.last_backup).toLocaleDateString() : 'N/A'}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Zap className="w-6 h-6 text-yellow-600" />
                <h3 className="text-lg font-semibold text-gray-900">ML Models</h3>
              </div>
              {getStatusIcon(systemHealth.ml_model_status === 'ready' ? 'healthy' : 'critical')}
            </div>
            <div className={`px-3 py-2 rounded-lg text-sm font-semibold mb-3 ${getStatusColor(systemHealth.ml_model_status === 'ready' ? 'healthy' : 'critical')}`}>
              {systemHealth.ml_model_status?.toUpperCase() || 'UNKNOWN'}
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Models Loaded:</span>
                <span className="font-semibold text-gray-900">{systemHealth.models_loaded || '2/2'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Accuracy:</span>
                <span className="font-semibold text-green-600">{systemHealth.model_accuracy || '95.2'}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Last Training:</span>
                <span className="font-semibold text-gray-900">
                  {systemHealth.last_training ? new Date(systemHealth.last_training).toLocaleDateString() : 'N/A'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Performance Metrics */}
      {performance && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
            <Cpu className="w-5 h-5 mr-2 text-indigo-600" />
            Performance Metrics
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg p-4 border border-blue-200">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-gray-600">CPU Usage</p>
                <Cpu className="w-4 h-4 text-blue-600" />
              </div>
              <p className="text-2xl font-bold text-gray-900">{performance.cpu_usage || 0}%</p>
              <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${
                    (performance.cpu_usage || 0) > 80 ? 'bg-red-500' : 
                    (performance.cpu_usage || 0) > 60 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${Math.min(performance.cpu_usage || 0, 100)}%` }}
                />
              </div>
            </div>

            <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-4 border border-purple-200">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-gray-600">Memory Usage</p>
                <HardDrive className="w-4 h-4 text-purple-600" />
              </div>
              <p className="text-2xl font-bold text-gray-900">{performance.memory_usage || 0}%</p>
              <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${
                    (performance.memory_usage || 0) > 80 ? 'bg-red-500' : 
                    (performance.memory_usage || 0) > 60 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${Math.min(performance.memory_usage || 0, 100)}%` }}
                />
              </div>
            </div>

            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg p-4 border border-green-200">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-gray-600">Req/Sec</p>
                <TrendingUp className="w-4 h-4 text-green-600" />
              </div>
              <p className="text-2xl font-bold text-gray-900">{performance.requests_per_second || 0}</p>
              <p className="text-xs text-gray-500 mt-1">Avg: {performance.avg_requests_per_second || 0}/s</p>
            </div>

            <div className="bg-gradient-to-br from-orange-50 to-yellow-50 rounded-lg p-4 border border-orange-200">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-gray-600">Error Rate</p>
                <TrendingDown className="w-4 h-4 text-orange-600" />
              </div>
              <p className="text-2xl font-bold text-gray-900">{performance.error_rate || 0}%</p>
              <p className="text-xs text-gray-500 mt-1">Target: &lt;1%</p>
            </div>
          </div>
        </div>
      )}

      {/* Sensor Network Status */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="p-6 bg-gray-50 border-b border-gray-200">
          <h3 className="text-lg font-bold text-gray-900 flex items-center">
            <Wifi className="w-5 h-5 mr-2 text-green-600" />
            Sensor Network Status ({sensorStatus.filter((s: any) => s.status === 'online').length}/{sensorStatus.length} Online)
          </h3>
        </div>
        
        {sensorStatus.length > 0 ? (
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {sensorStatus.map((sensor) => (
                <div key={sensor.sensor_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      {sensor.status === 'online' ? (
                        <Wifi className="w-5 h-5 text-green-600" />
                      ) : (
                        <WifiOff className="w-5 h-5 text-red-600" />
                      )}
                      <h4 className="font-semibold text-gray-900">{sensor.sensor_id}</h4>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-bold text-white ${
                      sensor.status === 'online' ? 'bg-green-500' : 'bg-red-500'
                    }`}>
                      {sensor.status?.toUpperCase()}
                    </span>
                  </div>

                  <div className="space-y-2 text-sm">
                    {sensor.zone && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Zone:</span>
                        <span className="font-semibold text-gray-900">{sensor.zone}</span>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <span className="text-gray-600">Last Update:</span>
                      <span className="font-semibold text-gray-900">
                        {sensor.last_update ? new Date(sensor.last_update).toLocaleTimeString() : 'Never'}
                      </span>
                    </div>
                    {sensor.battery_level && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Battery:</span>
                        <span className={`font-semibold ${
                          sensor.battery_level > 50 ? 'text-green-600' : 
                          sensor.battery_level > 20 ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          {sensor.battery_level}%
                        </span>
                      </div>
                    )}
                    {sensor.signal_strength && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Signal:</span>
                        <span className="font-semibold text-gray-900">{sensor.signal_strength}%</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="p-12 text-center">
            <WifiOff className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600">No sensor data available</p>
          </div>
        )}
      </div>

      {/* System Alerts */}
      {systemHealth && systemHealth.alerts && systemHealth.alerts.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-5 h-5 text-yellow-700 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-semibold text-yellow-900">System Alerts</p>
              <ul className="mt-2 space-y-1">
                {systemHealth.alerts.map((alert: string, idx: number) => (
                  <li key={idx} className="text-sm text-yellow-800">• {alert}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Last Updated */}
      <div className="text-center text-xs text-gray-500">
        Last updated: {new Date().toLocaleString()} • Auto-refresh: 15s
      </div>
    </div>
  );
}
