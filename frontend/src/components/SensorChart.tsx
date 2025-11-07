'use client';

import { useEffect, useState } from 'react';
import { dashboardAPI } from '@/lib/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp } from 'lucide-react';

interface SensorChartProps {
  hours?: number;
}

export default function SensorChart({ hours = 24 }: SensorChartProps) {
  const [chartData, setChartData] = useState<any[]>([]);
  const [timeRange, setTimeRange] = useState(hours);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setTimeRange(hours);
  }, [hours]);

  useEffect(() => {
    fetchChartData();
    const interval = setInterval(fetchChartData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, [timeRange]);

  const fetchChartData = async () => {
    try {
      const response = await dashboardAPI.getChartData(timeRange);
      const formatted = response.data.map((item: any) => ({
        time: new Date(item.timestamp).toLocaleTimeString(),
        temperature: item.temperature,
        humidity: item.humidity,
        smoke: item.smoke_level,
        risk: item.risk_score,
      }));
      setChartData(formatted);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch chart data:', error);
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <TrendingUp className="w-6 h-6 text-green-600 mr-2" />
          <h2 className="text-xl font-bold text-gray-900">Sensor Trends</h2>
        </div>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(Number(e.target.value))}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
        >
          <option value={6}>Last 6 hours</option>
          <option value={24}>Last 24 hours</option>
          <option value={48}>Last 48 hours</option>
          <option value={168}>Last week</option>
        </select>
      </div>

      {loading ? (
        <div className="h-96 flex items-center justify-center">
          <p className="text-gray-500">Loading chart data...</p>
        </div>
      ) : chartData.length === 0 ? (
        <div className="h-96 flex items-center justify-center">
          <p className="text-gray-500">No data available</p>
        </div>
      ) : (
        <div className="space-y-8">
          {/* Temperature & Humidity Chart */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Temperature & Humidity</h3>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="temperature" stroke="#f97316" name="Temperature (°C)" strokeWidth={2} />
                <Line type="monotone" dataKey="humidity" stroke="#3b82f6" name="Humidity (%)" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Smoke Level Chart */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Smoke Level</h3>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="smoke" stroke="#6b7280" name="Smoke Level" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Risk Score Chart */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Fire Risk Score</h3>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="risk" stroke="#ef4444" name="Risk Score" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
