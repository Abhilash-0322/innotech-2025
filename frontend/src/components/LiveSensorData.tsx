'use client';

import { useEffect, useState } from 'react';
import { Thermometer, Droplets, Wind, Cloud, Flame, Activity, Download } from 'lucide-react';
import { api } from '@/lib/api';

interface SensorReading {
  temperature: number;
  humidity: number;
  smoke_level: number;
  rain_level: number;
  rain_detected: boolean;
  fire_risk_score: number;
  risk_level: string;
  timestamp: string;
  recommendations?: string[];
}

export default function LiveSensorData() {
  const [sensorData, setSensorData] = useState<SensorReading | null>(null);
  const [connected, setConnected] = useState(false);
  const [history, setHistory] = useState<SensorReading[]>([]);

  const handleExportCSV = async (type: 'sensor' | 'ai') => {
    try {
      const endpoint = type === 'sensor' 
        ? '/export/sensor-data/csv?hours=24'
        : '/export/ai-responses/csv?hours=24';
      
      const response = await api.get(endpoint, {
        responseType: 'blob',
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${type}_data_${new Date().toISOString().slice(0, 10)}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to export CSV:', error);
      alert('Failed to export data. Please try again.');
    }
  };

  useEffect(() => {
    // Connect to WebSocket
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onopen = () => {
      console.log('✅ WebSocket connected');
      setConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        
        if (message.type === 'sensor_update') {
          const newData = message.data;
          setSensorData(newData);
          
          // Add to history (keep last 20 readings)
          setHistory((prev) => {
            const updated = [newData, ...prev].slice(0, 20);
            return updated;
          });
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };

    ws.onclose = () => {
      console.log('🔌 WebSocket disconnected');
      setConnected(false);
    };

    return () => {
      ws.close();
    };
  }, []);

  const getRiskColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'critical':
        return 'bg-red-500';
      case 'high':
        return 'bg-orange-500';
      case 'medium':
        return 'bg-yellow-500';
      case 'low':
        return 'bg-green-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getRiskTextColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'critical':
        return 'text-red-600';
      case 'high':
        return 'text-orange-600';
      case 'medium':
        return 'text-yellow-600';
      case 'low':
        return 'text-green-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* Connection Status with Export Buttons */}
      <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-blue-500">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Activity className={`w-6 h-6 ${connected ? 'text-green-500 animate-pulse' : 'text-gray-400'}`} />
            <div>
              <h3 className="font-semibold text-gray-900">
                {connected ? 'Live Stream Active' : 'Connecting...'}
              </h3>
              <p className="text-sm text-gray-600">
                {connected ? 'Receiving real-time sensor data from ESP32' : 'Waiting for sensor data...'}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {sensorData && (
              <div className="text-right mr-4">
                <p className="text-xs text-gray-500">Last Update</p>
                <p className="text-sm font-medium text-gray-900">
                  {new Date(sensorData.timestamp).toLocaleTimeString()}
                </p>
              </div>
            )}
            <button
              onClick={() => handleExportCSV('sensor')}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
              title="Export Sensor Data as CSV"
            >
              <Download className="w-4 h-4" />
              <span className="hidden sm:inline">Sensor CSV</span>
            </button>
            <button
              onClick={() => handleExportCSV('ai')}
              className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
              title="Export AI Responses as CSV"
            >
              <Download className="w-4 h-4" />
              <span className="hidden sm:inline">AI CSV</span>
            </button>
          </div>
        </div>
      </div>

      {/* Current Sensor Readings */}
      {sensorData && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Temperature */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <Thermometer className="w-8 h-8 text-red-500" />
                <span className="text-3xl font-bold text-gray-900">
                  {sensorData.temperature.toFixed(1)}°C
                </span>
              </div>
              <p className="mt-2 text-sm text-gray-600">Temperature</p>
            </div>

            {/* Humidity */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <Droplets className="w-8 h-8 text-blue-500" />
                <span className="text-3xl font-bold text-gray-900">
                  {sensorData.humidity.toFixed(1)}%
                </span>
              </div>
              <p className="mt-2 text-sm text-gray-600">Humidity</p>
            </div>

            {/* Smoke Level */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <Wind className="w-8 h-8 text-gray-500" />
                <span className="text-3xl font-bold text-gray-900">
                  {sensorData.smoke_level}
                </span>
              </div>
              <p className="mt-2 text-sm text-gray-600">Smoke Level</p>
            </div>

            {/* Rain Status */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <Cloud className="w-8 h-8 text-cyan-500" />
                <div className="text-right">
                  <span className="text-3xl font-bold text-gray-900">
                    {sensorData.rain_detected ? 'Yes' : 'No'}
                  </span>
                  <p className="text-sm text-gray-600 mt-1">
                    Level: {sensorData.rain_level.toFixed(1)}
                  </p>
                </div>
              </div>
              <p className="mt-2 text-sm text-gray-600">Rain Detected</p>
            </div>
          </div>

          {/* Fire Risk Assessment */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <Flame className="w-8 h-8 text-orange-500" />
                <div>
                  <h3 className="text-xl font-bold text-gray-900">Fire Risk Assessment</h3>
                  <p className="text-sm text-gray-600">AI-powered risk analysis</p>
                </div>
              </div>
              <div className="text-right">
                <p className={`text-3xl font-bold ${getRiskTextColor(sensorData.risk_level)}`}>
                  {sensorData.risk_level.toUpperCase()}
                </p>
                <p className="text-sm text-gray-600">Risk Score: {sensorData.fire_risk_score}/100</p>
              </div>
            </div>

            {/* Risk Progress Bar */}
            <div className="mt-4">
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div
                  className={`h-4 rounded-full transition-all duration-500 ${getRiskColor(sensorData.risk_level)}`}
                  style={{ width: `${sensorData.fire_risk_score}%` }}
                />
              </div>
            </div>

            {/* Recommendations */}
            {sensorData.recommendations && sensorData.recommendations.length > 0 && (
              <div className="mt-6">
                <h4 className="font-semibold text-gray-900 mb-2">AI Recommendations:</h4>
                <ul className="space-y-2">
                  {sensorData.recommendations.map((rec, idx) => (
                    <li key={idx} className="flex items-start space-x-2">
                      <span className="text-orange-500 mt-1">•</span>
                      <span className="text-sm text-gray-700">{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Recent Readings History */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Recent Readings</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Temp (°C)</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Humidity (%)</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Smoke</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rain</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rain Lvl</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Risk</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {history.map((reading, idx) => (
                    <tr key={idx} className={idx === 0 ? 'bg-blue-50' : ''}>
                      <td className="px-4 py-3 text-sm text-gray-900">
                        {new Date(reading.timestamp).toLocaleTimeString()}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900">{reading.temperature.toFixed(1)}</td>
                      <td className="px-4 py-3 text-sm text-gray-900">{reading.humidity.toFixed(1)}</td>
                      <td className="px-4 py-3 text-sm text-gray-900">{reading.smoke_level}</td>
                      <td className="px-4 py-3 text-sm text-gray-900">
                        {reading.rain_detected ? '✓' : '✗'}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900">
                        {reading.rain_level.toFixed(1)}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <span className={`font-semibold ${getRiskTextColor(reading.risk_level)}`}>
                          {reading.risk_level}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* No Data State */}
      {!sensorData && connected && (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <Activity className="w-16 h-16 text-gray-400 mx-auto mb-4 animate-pulse" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Waiting for Sensor Data</h3>
          <p className="text-gray-600">
            Ensure your ESP32 is connected and the sensor stream is running.
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Run: <code className="bg-gray-100 px-2 py-1 rounded">python3 start_sensor_stream.py</code>
          </p>
        </div>
      )}

      {/* Disconnected State */}
      {!connected && (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <Activity className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Connection Lost</h3>
          <p className="text-gray-600">
            Unable to connect to WebSocket server. Please check if the backend is running.
          </p>
        </div>
      )}
    </div>
  );
}
