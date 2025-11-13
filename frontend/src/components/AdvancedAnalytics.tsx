'use client';

import { useEffect, useState } from 'react';
import { analyticsAPI } from '@/lib/api';
import { TrendingUp, TrendingDown, Activity, Target, AlertCircle, BarChart3, Calendar } from 'lucide-react';

export default function AdvancedAnalytics() {
  const [trends, setTrends] = useState<any>(null);
  const [patterns, setPatterns] = useState<any[]>([]);
  const [forecast, setForecast] = useState<any>(null);
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('7d');

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [timeRange]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const [trendsData, patternsData, forecastData, insightsData] = await Promise.all([
        analyticsAPI.getTrends(),
        analyticsAPI.getPatterns(),
        analyticsAPI.getForecast(),
        analyticsAPI.getInsights(),
      ]);
      
      setTrends(trendsData);
      setPatterns(patternsData.patterns || []);
      setForecast(forecastData);
      setAnomalies(insightsData.anomalies || []);
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (direction: string) => {
    if (direction === 'increasing') return <TrendingUp className="w-5 h-5 text-red-600" />;
    if (direction === 'decreasing') return <TrendingDown className="w-5 h-5 text-green-600" />;
    return <Activity className="w-5 h-5 text-blue-600" />;
  };

  const getTrendColor = (direction: string) => {
    if (direction === 'increasing') return 'text-red-600 bg-red-50';
    if (direction === 'decreasing') return 'text-green-600 bg-green-50';
    return 'text-blue-600 bg-blue-50';
  };

  const getPatternColor = (type: string) => {
    const colors: any = {
      temporal: 'bg-purple-100 text-purple-700',
      spatial: 'bg-cyan-100 text-cyan-700',
      seasonal: 'bg-orange-100 text-orange-700',
      correlation: 'bg-green-100 text-green-700',
    };
    return colors[type] || 'bg-gray-100 text-gray-700';
  };

  const getSeverityColor = (severity: string) => {
    const colors: any = {
      low: 'bg-green-500',
      medium: 'bg-yellow-500',
      high: 'bg-orange-500',
      critical: 'bg-red-500',
    };
    return colors[severity] || 'bg-gray-500';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-center py-12">
          <Activity className="w-8 h-8 text-blue-500 animate-spin" />
          <span className="ml-3 text-gray-600">Analyzing data...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Time Range Selector */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <BarChart3 className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">Advanced Analytics & Insights</h2>
              <p className="text-purple-100">AI-powered trend analysis and pattern detection</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Calendar className="w-5 h-5" />
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="bg-white/20 text-white px-4 py-2 rounded-lg border border-white/30 focus:outline-none focus:ring-2 focus:ring-white/50"
            >
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
            </select>
          </div>
        </div>
      </div>

      {/* Trends Overview */}
      {trends && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {Object.entries(trends.trends || {}).map(([metric, data]: [string, any]) => (
            <div key={metric} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-gray-600 capitalize">
                  {metric.replace('_', ' ')}
                </h3>
                {getTrendIcon(data.direction)}
              </div>
              
              <div className="mb-4">
                <p className="text-3xl font-bold text-gray-900">
                  {data.current_value?.toFixed(2)}
                </p>
                <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold mt-2 ${getTrendColor(data.direction)}`}>
                  {data.change_percent > 0 ? '+' : ''}{data.change_percent?.toFixed(1)}%
                </div>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Slope:</span>
                  <span className="font-semibold text-gray-900">{data.slope?.toFixed(4)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">R² Score:</span>
                  <span className="font-semibold text-gray-900">{data.r2_score?.toFixed(3)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Confidence:</span>
                  <span className="font-semibold text-green-600">{(data.confidence * 100)?.toFixed(0)}%</span>
                </div>
              </div>

              {data.prediction_24h !== undefined && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="text-xs text-gray-600 mb-1">24h Prediction</p>
                  <p className="text-lg font-bold text-indigo-600">{data.prediction_24h?.toFixed(2)}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Detected Patterns */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="p-6 bg-gray-50 border-b border-gray-200">
          <h3 className="text-lg font-bold text-gray-900 flex items-center">
            <Target className="w-5 h-5 mr-2 text-purple-600" />
            Detected Patterns ({patterns.length})
          </h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {patterns.map((pattern, idx) => (
              <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                <div className="flex items-start justify-between mb-3">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getPatternColor(pattern.type)}`}>
                    {pattern.type.toUpperCase()}
                  </span>
                  <span className="text-xs text-gray-500">
                    Confidence: {(pattern.confidence * 100)?.toFixed(0)}%
                  </span>
                </div>
                
                <h4 className="font-semibold text-gray-900 mb-2">{pattern.description}</h4>
                
                <div className="space-y-1 text-sm">
                  {pattern.details && Object.entries(pattern.details).map(([key, value]: [string, any]) => (
                    <div key={key} className="flex justify-between">
                      <span className="text-gray-600 capitalize">{key.replace('_', ' ')}:</span>
                      <span className="font-medium text-gray-900">
                        {typeof value === 'number' ? value.toFixed(2) : value}
                      </span>
                    </div>
                  ))}
                </div>

                {pattern.recommendation && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-xs text-gray-600 mb-1">Recommendation:</p>
                    <p className="text-sm text-indigo-700">{pattern.recommendation}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 24-Hour Forecast */}
      {forecast && (
        <div className="bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg shadow-md p-6 border border-blue-200">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
            <Calendar className="w-5 h-5 mr-2 text-blue-600" />
            24-Hour Risk Forecast
          </h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg p-4 text-center">
              <p className="text-xs text-gray-600 mb-1">Avg Predicted Risk</p>
              <p className="text-2xl font-bold text-blue-600">{forecast.average_predicted_risk?.toFixed(1)}%</p>
            </div>
            <div className="bg-white rounded-lg p-4 text-center">
              <p className="text-xs text-gray-600 mb-1">Peak Risk</p>
              <p className="text-2xl font-bold text-red-600">{forecast.peak_risk?.toFixed(1)}%</p>
            </div>
            <div className="bg-white rounded-lg p-4 text-center">
              <p className="text-xs text-gray-600 mb-1">Lowest Risk</p>
              <p className="text-2xl font-bold text-green-600">{forecast.lowest_risk?.toFixed(1)}%</p>
            </div>
            <div className="bg-white rounded-lg p-4 text-center">
              <p className="text-xs text-gray-600 mb-1">Model Confidence</p>
              <p className="text-2xl font-bold text-purple-600">{(forecast.confidence * 100)?.toFixed(0)}%</p>
            </div>
          </div>

          {forecast.peak_time && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <AlertCircle className="w-5 h-5 text-yellow-700 mt-0.5" />
                <div>
                  <p className="text-sm font-semibold text-yellow-900">Peak Risk Alert</p>
                  <p className="text-sm text-yellow-800">
                    Highest risk expected at <strong>{new Date(forecast.peak_time).toLocaleTimeString()}</strong>
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Recent Anomalies */}
      {anomalies.length > 0 && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="p-6 bg-red-50 border-b border-red-200">
            <h3 className="text-lg font-bold text-gray-900 flex items-center">
              <AlertCircle className="w-5 h-5 mr-2 text-red-600" />
              Detected Anomalies ({anomalies.length})
            </h3>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {anomalies.slice(0, 5).map((anomaly, idx) => (
                <div key={idx} className="flex items-start space-x-4 p-4 bg-red-50 rounded-lg border border-red-200">
                  <div className={`w-2 h-2 rounded-full mt-2 ${getSeverityColor(anomaly.severity)}`} />
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-semibold text-gray-900">{anomaly.sensor_id || 'Unknown Sensor'}</h4>
                      <span className="text-xs text-gray-500">
                        {new Date(anomaly.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">{anomaly.description}</p>
                    <div className="grid grid-cols-3 gap-2 text-xs">
                      <div>
                        <span className="text-gray-600">Metric: </span>
                        <span className="font-semibold">{anomaly.metric}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Value: </span>
                        <span className="font-semibold text-red-600">{anomaly.value?.toFixed(2)}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Expected: </span>
                        <span className="font-semibold">{anomaly.expected_range}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Statistical Summary */}
      {trends && trends.summary && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Statistical Summary</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-xs text-gray-600 mb-1">Total Data Points</p>
              <p className="text-xl font-bold text-gray-900">{trends.summary.total_records}</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-600 mb-1">Time Period</p>
              <p className="text-xl font-bold text-gray-900">{timeRange}</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-600 mb-1">Sensors Monitored</p>
              <p className="text-xl font-bold text-gray-900">{trends.summary.sensors_count || 'N/A'}</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-600 mb-1">Analysis Updated</p>
              <p className="text-sm font-semibold text-gray-900">
                {new Date().toLocaleTimeString()}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
