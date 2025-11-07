'use client';

import { useEffect, useState } from 'react';
import { Brain, AlertTriangle, CheckCircle, Clock, TrendingUp } from 'lucide-react';

interface AIRecommendation {
  risk_score: number;
  risk_level: string;
  reasoning: string;
  recommendations: string[];
  should_activate_sprinkler: boolean;
  timestamp: string;
}

export default function AIRecommendationsSidebar() {
  const [latestAI, setLatestAI] = useState<AIRecommendation | null>(null);
  const [previousRisk, setPreviousRisk] = useState<number | null>(null);

  useEffect(() => {
    // Connect to WebSocket for real-time updates
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        
        if (message.type === 'sensor_update' && message.data) {
          const data = message.data;
          
          // Only update if we have AI data with recommendations
          if (data.recommendations && data.recommendations.length > 0) {
            setPreviousRisk(latestAI?.risk_score || null);
            
            setLatestAI({
              risk_score: data.fire_risk_score,
              risk_level: data.risk_level,
              reasoning: data.reasoning || '',
              recommendations: data.recommendations,
              should_activate_sprinkler: data.should_activate_sprinkler || false,
              timestamp: data.timestamp,
            });
          }
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    return () => {
      ws.close();
    };
  }, [latestAI]);

  const getRiskColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const getRiskTextColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'critical': return 'text-red-600';
      case 'high': return 'text-orange-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  const getRiskTrend = () => {
    if (previousRisk === null || latestAI === null) return null;
    if (latestAI.risk_score > previousRisk) {
      return <span className="text-red-600 flex items-center">↑ Increasing</span>;
    } else if (latestAI.risk_score < previousRisk) {
      return <span className="text-green-600 flex items-center">↓ Decreasing</span>;
    }
    return <span className="text-gray-600">→ Stable</span>;
  };

  if (!latestAI) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Brain className="w-6 h-6 text-purple-600 animate-pulse" />
          <h3 className="text-lg font-bold text-gray-900">AI Recommendations</h3>
        </div>
        <div className="text-center py-8">
          <Brain className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-sm text-gray-600">Waiting for AI analysis...</p>
          <p className="text-xs text-gray-500 mt-1">
            AI runs every 30 seconds
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <Brain className="w-6 h-6 text-purple-600" />
          <h3 className="text-lg font-bold text-gray-900">AI Recommendations</h3>
        </div>
        <div className="flex items-center space-x-2 text-xs text-gray-500">
          <Clock className="w-3 h-3" />
          <span>{new Date(latestAI.timestamp).toLocaleTimeString()}</span>
        </div>
      </div>

      {/* Risk Score */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Current Risk</span>
          {getRiskTrend() && (
            <div className="flex items-center space-x-1 text-xs">
              <TrendingUp className="w-3 h-3" />
              {getRiskTrend()}
            </div>
          )}
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex-1">
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all duration-500 ${getRiskColor(latestAI.risk_level)}`}
                style={{ width: `${latestAI.risk_score}%` }}
              />
            </div>
          </div>
          <span className="text-2xl font-bold text-gray-900">
            {latestAI.risk_score}
          </span>
        </div>
        <div className="mt-2">
          <span className={`text-sm font-semibold ${getRiskTextColor(latestAI.risk_level)}`}>
            {latestAI.risk_level?.toUpperCase()}
          </span>
        </div>
      </div>

      {/* Sprinkler Alert */}
      {latestAI.should_activate_sprinkler && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-start space-x-2">
            <AlertTriangle className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-blue-900">Sprinkler Activation Recommended</p>
              <p className="text-xs text-blue-700 mt-1">AI suggests activating fire suppression system</p>
            </div>
          </div>
        </div>
      )}

      {/* AI Reasoning */}
      {latestAI.reasoning && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
            <Brain className="w-4 h-4 mr-1" />
            AI Analysis
          </h4>
          <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg leading-relaxed">
            {latestAI.reasoning}
          </p>
        </div>
      )}

      {/* Recommendations */}
      {latestAI.recommendations && latestAI.recommendations.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
            <CheckCircle className="w-4 h-4 mr-1 text-green-600" />
            Recommended Actions
          </h4>
          <ul className="space-y-2">
            {latestAI.recommendations.map((rec, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <span className="text-purple-600 mt-1 flex-shrink-0">•</span>
                <span className="text-sm text-gray-700 leading-relaxed">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Update Indicator */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          Updates every 30 seconds with new AI analysis
        </p>
      </div>
    </div>
  );
}
