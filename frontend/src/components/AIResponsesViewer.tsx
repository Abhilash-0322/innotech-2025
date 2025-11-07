'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Brain, Download, RefreshCw } from 'lucide-react';

interface AIResponse {
  _id: string;
  timestamp: string;
  risk_score: number;
  risk_level: string;
  reasoning: string;
  recommendations: string[];
  should_activate_sprinkler: boolean;
  sensor_data_id: string;
}

export default function AIResponsesViewer() {
  const [responses, setResponses] = useState<AIResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    fetchAIResponses();
  }, []);

  const fetchAIResponses = async () => {
    try {
      setLoading(true);
      const response = await api.get('/sensors/ai-responses?limit=50');
      setResponses(response.data);
    } catch (error) {
      console.error('Failed to fetch AI responses:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExportCSV = async () => {
    try {
      const response = await api.get('/export/ai-responses/csv?hours=168', {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `ai_responses_${new Date().toISOString().slice(0, 10)}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to export CSV:', error);
      alert('Failed to export data. Please try again.');
    }
  };

  const getRiskColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-300';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low': return 'bg-green-100 text-green-800 border-green-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const filteredResponses = responses.filter(r => 
    filter === 'all' || r.risk_level.toLowerCase() === filter
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <RefreshCw className="w-8 h-8 animate-spin text-purple-600" />
        <span className="ml-3 text-gray-600">Loading AI responses...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Brain className="w-8 h-8 text-purple-600" />
            <div>
              <h2 className="text-xl font-bold text-gray-900">AI Risk Assessment History</h2>
              <p className="text-sm text-gray-600">View all AI-generated fire risk analyses</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={fetchAIResponses}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>
            <button
              onClick={handleExportCSV}
              className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
            >
              <Download className="w-4 h-4" />
              <span>Export CSV</span>
            </button>
          </div>
        </div>

        {/* Filter */}
        <div className="mt-4 flex items-center space-x-2">
          <span className="text-sm text-gray-600">Filter:</span>
          {['all', 'critical', 'high', 'medium', 'low'].map((level) => (
            <button
              key={level}
              onClick={() => setFilter(level)}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition ${
                filter === level
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {level.charAt(0).toUpperCase() + level.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* AI Responses List */}
      <div className="space-y-4">
        {filteredResponses.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <Brain className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No AI responses found</p>
          </div>
        ) : (
          filteredResponses.map((response) => (
            <div key={response._id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${getRiskColor(response.risk_level)}`}>
                      {response.risk_level.toUpperCase()}
                    </span>
                    <span className="text-2xl font-bold text-gray-900">
                      {response.risk_score}/100
                    </span>
                    {response.should_activate_sprinkler && (
                      <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold">
                        💧 Sprinkler Recommended
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500">
                    {new Date(response.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>

              {/* Reasoning */}
              <div className="mb-4">
                <h4 className="text-sm font-semibold text-gray-700 mb-2">AI Reasoning:</h4>
                <p className="text-gray-900 bg-gray-50 p-3 rounded-lg">
                  {response.reasoning}
                </p>
              </div>

              {/* Recommendations */}
              {response.recommendations && response.recommendations.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Recommendations:</h4>
                  <ul className="space-y-1">
                    {response.recommendations.map((rec, idx) => (
                      <li key={idx} className="flex items-start space-x-2 text-sm text-gray-700">
                        <span className="text-purple-600 mt-1">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Metadata */}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-xs text-gray-500">
                  Sensor Data ID: <code className="bg-gray-100 px-2 py-1 rounded">{response.sensor_data_id}</code>
                </p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
