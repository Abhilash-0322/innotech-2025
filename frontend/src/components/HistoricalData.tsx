'use client';

import { useEffect, useState } from 'react';
import { sensorsAPI } from '@/lib/api';
import SensorChart from '@/components/SensorChart';
import { Calendar, Download } from 'lucide-react';

export default function HistoricalData() {
  const [timeRange, setTimeRange] = useState(24);
  const [loading, setLoading] = useState(false);

  const timeRanges = [
    { label: '6 Hours', value: 6 },
    { label: '24 Hours', value: 24 },
    { label: '48 Hours', value: 48 },
    { label: '1 Week', value: 168 },
  ];

  return (
    <div className="space-y-6">
      {/* Header with Time Range Selector */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Calendar className="w-6 h-6 text-blue-600" />
            <div>
              <h2 className="text-xl font-bold text-gray-900">Historical Sensor Data</h2>
              <p className="text-sm text-gray-600">View trends and patterns over time</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(Number(e.target.value))}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {timeRanges.map((range) => (
                <option key={range.value} value={range.value}>
                  {range.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Charts */}
      <SensorChart hours={timeRange} />
    </div>
  );
}
