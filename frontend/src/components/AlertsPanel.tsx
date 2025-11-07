'use client';

import { useEffect, useState } from 'react';
import { alertsAPI, Alert } from '@/lib/api';
import { AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { getRiskColor, formatRelativeTime } from '@/lib/utils';

export default function AlertsPanel() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 15000); // Refresh every 15s
    return () => clearInterval(interval);
  }, []);

  const fetchAlerts = async () => {
    try {
      const data = await alertsAPI.getActive();
      setAlerts(data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
      setLoading(false);
    }
  };

  const handleAcknowledge = async (alertId: string) => {
    try {
      await alertsAPI.acknowledge(alertId);
      fetchAlerts();
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  const handleResolve = async (alertId: string) => {
    try {
      await alertsAPI.resolve(alertId);
      fetchAlerts();
    } catch (error) {
      console.error('Failed to resolve alert:', error);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className="flex items-center mb-4">
        <AlertTriangle className="w-6 h-6 text-red-600 mr-2" />
        <h2 className="text-xl font-bold text-gray-900">Active Alerts</h2>
      </div>

      {loading ? (
        <p className="text-gray-500">Loading alerts...</p>
      ) : alerts.length === 0 ? (
        <div className="text-center py-8">
          <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-2" />
          <p className="text-gray-600">No active alerts</p>
          <p className="text-sm text-gray-500">System is operating normally</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-4 rounded-lg border-l-4 ${getRiskColor(alert.severity)}`}
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold text-sm">{alert.title}</h3>
                <span className="text-xs px-2 py-1 rounded bg-white">
                  {alert.severity.toUpperCase()}
                </span>
              </div>
              <p className="text-sm text-gray-700 mb-2">{alert.message}</p>
              <div className="flex items-center justify-between text-xs text-gray-500">
                <div className="flex items-center">
                  <Clock className="w-3 h-3 mr-1" />
                  {formatRelativeTime(alert.timestamp)}
                </div>
                <div className="space-x-2">
                  {alert.status === 'active' && (
                    <>
                      <button
                        onClick={() => handleAcknowledge(alert.id)}
                        className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded hover:bg-yellow-200"
                      >
                        Acknowledge
                      </button>
                      <button
                        onClick={() => handleResolve(alert.id)}
                        className="px-2 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200"
                      >
                        Resolve
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
