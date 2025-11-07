'use client';

import { useState, useEffect } from 'react';
import { sprinklerAPI } from '@/lib/api';
import { Droplet, Play, Square, RefreshCw } from 'lucide-react';

interface SprinklerControlProps {
  currentStatus?: string;
}

export default function SprinklerControl({ currentStatus = 'STANDBY' }: SprinklerControlProps) {
  const [status, setStatus] = useState(currentStatus);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setStatus(currentStatus);
  }, [currentStatus]);

  const handleControl = async (action: string, reason?: string) => {
    setLoading(true);
    try {
      await sprinklerAPI.control(action, reason);
      setStatus(action);
    } catch (error) {
      console.error('Failed to control sprinkler:', error);
      alert('Failed to control sprinkler system');
    } finally {
      setLoading(false);
    }
  };

  const handleAuto = async () => {
    setLoading(true);
    try {
      await sprinklerAPI.setAuto();
      setStatus('auto');
    } catch (error) {
      console.error('Failed to set auto mode:', error);
      alert('Failed to set auto mode');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'on':
        return 'bg-blue-100 text-blue-700 border-blue-300';
      case 'off':
        return 'bg-gray-100 text-gray-700 border-gray-300';
      case 'auto':
        return 'bg-green-100 text-green-700 border-green-300';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className="flex items-center mb-4">
        <Droplet className="w-6 h-6 text-blue-600 mr-2" />
        <h2 className="text-xl font-bold text-gray-900">Sprinkler Control</h2>
      </div>

      {/* Current Status */}
      <div className={`p-4 rounded-lg border-2 mb-6 ${getStatusColor()}`}>
        <p className="text-sm font-medium mb-1">Current Status</p>
        <p className="text-2xl font-bold uppercase">{status}</p>
      </div>

      {/* Control Buttons */}
      <div className="space-y-3">
        <button
          onClick={() => handleControl('on', 'Manual activation from dashboard')}
          disabled={loading || status === 'on'}
          className="w-full flex items-center justify-center px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Play className="w-5 h-5 mr-2" />
          Turn ON
        </button>

        <button
          onClick={() => handleControl('off', 'Manual deactivation from dashboard')}
          disabled={loading || status === 'off'}
          className="w-full flex items-center justify-center px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Square className="w-5 h-5 mr-2" />
          Turn OFF
        </button>

        <button
          onClick={handleAuto}
          disabled={loading || status === 'auto'}
          className="w-full flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <RefreshCw className="w-5 h-5 mr-2" />
          Set AUTO Mode
        </button>
      </div>

      {/* Info */}
      <div className="mt-6 p-3 bg-blue-50 rounded-lg">
        <p className="text-xs text-blue-800">
          <strong>AUTO Mode:</strong> System will automatically activate sprinklers based on AI risk assessment.
        </p>
      </div>

      {loading && (
        <div className="mt-4 text-center">
          <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        </div>
      )}
    </div>
  );
}
