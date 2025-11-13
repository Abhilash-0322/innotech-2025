'use client';

import { useEffect, useState } from 'react';
import { smartAlertsAPI } from '@/lib/api';
import { Bell, AlertTriangle, CheckCircle, XCircle, Mail, MessageSquare, Phone, Radio, Clock, TrendingUp } from 'lucide-react';

export default function EnhancedAlertsPanel() {
  const [activeAlerts, setActiveAlerts] = useState<any[]>([]);
  const [alertHistory, setAlertHistory] = useState<any[]>([]);
  const [channelStatus, setChannelStatus] = useState<any>(null);
  const [alertStats, setAlertStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPriority, setSelectedPriority] = useState('all');

  useEffect(() => {
    fetchAllAlerts();
    const interval = setInterval(fetchAllAlerts, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, [selectedPriority]);

  const fetchAllAlerts = async () => {
    try {
      setLoading(true);
      const [active, stats] = await Promise.all([
        smartAlertsAPI.getActiveAlerts(),
        smartAlertsAPI.getStatistics(),
      ]);
      
      const filteredActive = selectedPriority === 'all' 
        ? active.alerts || []
        : (active.alerts || []).filter((a: any) => a.priority === selectedPriority);
      
      setActiveAlerts(filteredActive);
      setAlertHistory(stats.recent_alerts || []);
      setChannelStatus(stats.channel_status || null);
      setAlertStats(stats);
    } catch (err) {
      console.error('Failed to fetch alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledge = async (alertId: string) => {
    try {
      await smartAlertsAPI.acknowledgeAlert(alertId);
      await fetchAllAlerts();
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    }
  };

  const getPriorityColor = (priority: string) => {
    const colors: any = {
      low: 'bg-blue-500',
      medium: 'bg-yellow-500',
      high: 'bg-orange-500',
      critical: 'bg-red-500',
    };
    return colors[priority] || 'bg-gray-500';
  };

  const getPriorityBorder = (priority: string) => {
    const borders: any = {
      low: 'border-blue-500',
      medium: 'border-yellow-500',
      high: 'border-orange-500',
      critical: 'border-red-500',
    };
    return borders[priority] || 'border-gray-500';
  };

  const getChannelIcon = (channel: string) => {
    const icons: any = {
      email: <Mail className="w-4 h-4" />,
      sms: <MessageSquare className="w-4 h-4" />,
      push: <Bell className="w-4 h-4" />,
      webhook: <Radio className="w-4 h-4" />,
      voice: <Phone className="w-4 h-4" />,
      dashboard: <TrendingUp className="w-4 h-4" />,
    };
    return icons[channel] || <Bell className="w-4 h-4" />;
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-center py-12">
          <Bell className="w-8 h-8 text-blue-500 animate-bounce" />
          <span className="ml-3 text-gray-600">Loading alerts...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Stats */}
      <div className="bg-gradient-to-r from-red-600 to-orange-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Bell className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">Smart Alert System</h2>
              <p className="text-red-100">Multi-channel intelligent notifications</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-red-100">Active Alerts</p>
            <p className="text-4xl font-bold">{activeAlerts.length}</p>
          </div>
        </div>

        {alertStats && (
          <div className="grid grid-cols-4 gap-4 mt-4">
            <div className="bg-white/20 rounded-lg p-3 text-center">
              <p className="text-xs text-red-100 mb-1">Total Today</p>
              <p className="text-2xl font-bold">{alertStats.total_today || 0}</p>
            </div>
            <div className="bg-white/20 rounded-lg p-3 text-center">
              <p className="text-xs text-red-100 mb-1">Critical</p>
              <p className="text-2xl font-bold">{alertStats.critical_count || 0}</p>
            </div>
            <div className="bg-white/20 rounded-lg p-3 text-center">
              <p className="text-xs text-red-100 mb-1">Acknowledged</p>
              <p className="text-2xl font-bold">{alertStats.acknowledged_count || 0}</p>
            </div>
            <div className="bg-white/20 rounded-lg p-3 text-center">
              <p className="text-xs text-red-100 mb-1">Avg Response</p>
              <p className="text-xl font-bold">{alertStats.avg_response_time || '0'}m</p>
            </div>
          </div>
        )}
      </div>

      {/* Priority Filter */}
      <div className="bg-white rounded-lg shadow-md p-4">
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-gray-700">Filter by Priority:</p>
          <div className="flex space-x-2">
            {['all', 'critical', 'high', 'medium', 'low'].map((priority) => (
              <button
                key={priority}
                onClick={() => setSelectedPriority(priority)}
                className={`px-4 py-2 rounded-lg text-sm font-semibold transition ${
                  selectedPriority === priority
                    ? `${getPriorityColor(priority)} text-white`
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {priority.charAt(0).toUpperCase() + priority.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Active Alerts */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="p-6 bg-red-50 border-b border-red-200">
          <h3 className="text-lg font-bold text-gray-900 flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2 text-red-600" />
            Active Alerts ({activeAlerts.length})
          </h3>
        </div>
        
        {activeAlerts.length > 0 ? (
          <div className="p-6 space-y-4">
            {activeAlerts.map((alert) => (
              <div
                key={alert.id}
                className={`border-l-4 ${getPriorityBorder(alert.priority)} bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`px-3 py-1 rounded-full text-white text-xs font-bold ${getPriorityColor(alert.priority)}`}>
                        {alert.priority.toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-500">
                        {alert.rule_type && `Rule: ${alert.rule_type}`}
                      </span>
                    </div>
                    <h4 className="font-bold text-gray-900 text-lg mb-1">{alert.title}</h4>
                    <p className="text-sm text-gray-700">{alert.message}</p>
                  </div>
                  {!alert.acknowledged && (
                    <button
                      onClick={() => handleAcknowledge(alert.id)}
                      className="ml-4 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-sm font-semibold flex items-center space-x-1"
                    >
                      <CheckCircle className="w-4 h-4" />
                      <span>Acknowledge</span>
                    </button>
                  )}
                </div>

                {/* Alert Details */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm mb-3">
                  {alert.sensor_id && (
                    <div>
                      <p className="text-xs text-gray-600">Sensor</p>
                      <p className="font-semibold text-gray-900">{alert.sensor_id}</p>
                    </div>
                  )}
                  {alert.zone && (
                    <div>
                      <p className="text-xs text-gray-600">Zone</p>
                      <p className="font-semibold text-gray-900">{alert.zone}</p>
                    </div>
                  )}
                  <div>
                    <p className="text-xs text-gray-600">Triggered</p>
                    <div className="flex items-center space-x-1">
                      <Clock className="w-3 h-3 text-gray-500" />
                      <p className="font-semibold text-gray-900">
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Status</p>
                    <p className="font-semibold text-gray-900">
                      {alert.acknowledged ? (
                        <span className="text-green-600 flex items-center">
                          <CheckCircle className="w-4 h-4 mr-1" />
                          Acknowledged
                        </span>
                      ) : (
                        <span className="text-orange-600 flex items-center">
                          <AlertTriangle className="w-4 h-4 mr-1" />
                          Pending
                        </span>
                      )}
                    </p>
                  </div>
                </div>

                {/* Delivery Channels */}
                <div className="pt-3 border-t border-gray-200">
                  <p className="text-xs text-gray-600 mb-2">Sent via:</p>
                  <div className="flex flex-wrap gap-2">
                    {alert.channels && alert.channels.map((channel: string) => (
                      <span key={channel} className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-semibold flex items-center space-x-1">
                        {getChannelIcon(channel)}
                        <span>{channel.toUpperCase()}</span>
                      </span>
                    ))}
                  </div>
                </div>

                {/* Action Taken */}
                {alert.action_taken && (
                  <div className="mt-3 pt-3 border-t border-gray-200 bg-green-50 rounded p-2">
                    <p className="text-xs text-gray-600 mb-1">🤖 Automated Action:</p>
                    <p className="text-sm text-green-800 font-medium">{alert.action_taken}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="p-12 text-center">
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <p className="text-gray-600 font-medium">No active alerts</p>
            <p className="text-sm text-gray-500 mt-1">All systems operating normally</p>
          </div>
        )}
      </div>

      {/* Channel Status */}
      {channelStatus && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="p-6 bg-gray-50 border-b border-gray-200">
            <h3 className="text-lg font-bold text-gray-900 flex items-center">
              <Radio className="w-5 h-5 mr-2 text-blue-600" />
              Notification Channels Status
            </h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {Object.entries(channelStatus.channels || {}).map(([channel, status]: [string, any]) => (
                <div key={channel} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      {getChannelIcon(channel)}
                      <h4 className="font-semibold text-gray-900 capitalize">{channel}</h4>
                    </div>
                    {status.enabled ? (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-600" />
                    )}
                  </div>
                  <div className="text-sm text-gray-600 space-y-1">
                    <div className="flex justify-between">
                      <span>Status:</span>
                      <span className={`font-semibold ${status.enabled ? 'text-green-600' : 'text-red-600'}`}>
                        {status.enabled ? 'Active' : 'Disabled'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Sent Today:</span>
                      <span className="font-semibold text-gray-900">{status.sent_today || 0}</span>
                    </div>
                    {status.last_sent && (
                      <div className="flex justify-between">
                        <span>Last Sent:</span>
                        <span className="font-semibold text-gray-900">
                          {new Date(status.last_sent).toLocaleTimeString()}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Alert History */}
      {alertHistory.length > 0 && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="p-6 bg-gray-50 border-b border-gray-200">
            <h3 className="text-lg font-bold text-gray-900 flex items-center">
              <Clock className="w-5 h-5 mr-2 text-gray-600" />
              Recent Alert History
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Priority</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sensor/Zone</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Response Time</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {alertHistory.slice(0, 10).map((alert, idx) => (
                  <tr key={idx} className="hover:bg-gray-50 transition">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs font-semibold rounded-full text-white ${getPriorityColor(alert.priority)}`}>
                        {alert.priority}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">{alert.title}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {alert.sensor_id || alert.zone || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(alert.timestamp).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {alert.acknowledged ? (
                        <span className="text-green-600 text-xs flex items-center">
                          <CheckCircle className="w-4 h-4 mr-1" />
                          Resolved
                        </span>
                      ) : (
                        <span className="text-orange-600 text-xs flex items-center">
                          <AlertTriangle className="w-4 h-4 mr-1" />
                          Open
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {alert.response_time || 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
