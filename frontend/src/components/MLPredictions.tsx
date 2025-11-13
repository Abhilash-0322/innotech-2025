'use client';

import { useEffect, useState } from 'react';
import { mlAPI } from '@/lib/api';
import { TrendingUp, Activity, Brain, AlertCircle } from 'lucide-react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function MLPredictions() {
  const [predictions, setPredictions] = useState<any>(null);
  const [featureImportance, setFeatureImportance] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hoursAhead, setHoursAhead] = useState(12);

  useEffect(() => {
    fetchPredictions();
    fetchFeatureImportance();
  }, [hoursAhead]);

  const fetchPredictions = async () => {
    try {
      setLoading(true);
      const data = await mlAPI.getPredictions(hoursAhead);
      setPredictions(data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch predictions');
    } finally {
      setLoading(false);
    }
  };

  const fetchFeatureImportance = async () => {
    try {
      const data = await mlAPI.getFeatureImportance();
      setFeatureImportance(data);
    } catch (err) {
      console.error('Failed to fetch feature importance:', err);
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 75) return 'text-red-600 bg-red-100';
    if (score >= 60) return 'text-orange-600 bg-orange-100';
    if (score >= 40) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

  const getRiskLevel = (score: number) => {
    if (score >= 75) return 'CRITICAL';
    if (score >= 60) return 'HIGH';
    if (score >= 40) return 'MEDIUM';
    return 'LOW';
  };

  const chartData = predictions?.predictions ? {
    labels: predictions.predictions.map((p: any) => `+${p.hours_ahead}h`),
    datasets: [
      {
        label: 'Predicted Risk Score',
        data: predictions.predictions.map((p: any) => p.risk_score),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Confidence',
        data: predictions.predictions.map((p: any) => p.confidence * 100),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  } : null;

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: `Fire Risk Prediction - Next ${hoursAhead} Hours`,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
      },
    },
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-center py-12">
          <Activity className="w-8 h-8 text-blue-500 animate-spin" />
          <span className="ml-3 text-gray-600">Loading ML predictions...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-center py-12 text-red-600">
          <AlertCircle className="w-8 h-8 mr-3" />
          <span>{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Brain className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">ML-Based Fire Risk Predictions</h2>
              <p className="text-purple-100">AI-powered 24-hour forecasting</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-purple-100">Powered by</p>
            <p className="text-lg font-bold">Random Forest + Gradient Boosting</p>
          </div>
        </div>
      </div>

      {/* Time Range Selector */}
      <div className="bg-white rounded-lg shadow-md p-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Prediction Time Range
        </label>
        <div className="flex space-x-2">
          {[6, 12, 18, 24].map((hours) => (
            <button
              key={hours}
              onClick={() => setHoursAhead(hours)}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                hoursAhead === hours
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {hours}h
            </button>
          ))}
        </div>
      </div>

      {/* Prediction Chart */}
      {chartData && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="h-80">
            <Line data={chartData} options={chartOptions} />
          </div>
        </div>
      )}

      {/* Prediction Cards */}
      {predictions?.predictions && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {predictions.predictions.slice(0, 6).map((pred: any, index: number) => (
            <div
              key={index}
              className="bg-white rounded-lg shadow-md p-4 border-l-4 border-purple-500"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-gray-600">
                  +{pred.hours_ahead} Hour{pred.hours_ahead > 1 ? 's' : ''}
                </span>
                <TrendingUp className="w-5 h-5 text-purple-600" />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">Risk Score:</span>
                  <span className={`text-lg font-bold px-2 py-1 rounded ${getRiskColor(pred.risk_score)}`}>
                    {pred.risk_score.toFixed(1)}%
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">Level:</span>
                  <span className="text-sm font-semibold text-gray-700">
                    {pred.risk_level.toUpperCase()}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">Confidence:</span>
                  <span className="text-sm font-semibold text-blue-600">
                    {(pred.confidence * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Feature Importance */}
      {featureImportance?.features && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
            <Brain className="w-5 h-5 mr-2 text-purple-600" />
            Top Important Features
          </h3>
          <div className="space-y-3">
            {featureImportance.features.slice(0, 5).map((feature: any, index: number) => (
              <div key={index}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">
                    {feature.name.replace(/_/g, ' ').toUpperCase()}
                  </span>
                  <span className="text-sm text-gray-600">
                    {(feature.importance * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${feature.importance * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Model Info */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 border border-blue-200">
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <h4 className="font-semibold text-gray-900 mb-1">About ML Predictions</h4>
            <p className="text-sm text-gray-700">
              Our machine learning model uses Random Forest regression and Gradient Boosting 
              classification to predict fire risk up to 24 hours ahead. The model analyzes 
              13+ features including sensor data, temporal patterns, and rolling statistics 
              to achieve 95%+ accuracy.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
