'use client';

import { useEffect, useState } from 'react';
import { zoneAPI } from '@/lib/api';
import { Map, Flame, Activity, AlertTriangle, Droplets, Wifi, WifiOff } from 'lucide-react';

export default function MultiZoneHeatmap() {
  const [zones, setZones] = useState<any[]>([]);
  const [heatmapData, setHeatmapData] = useState<any[]>([]);
  const [comparison, setComparison] = useState<any[]>([]);
  const [selectedZone, setSelectedZone] = useState<string | null>(null);
  const [fireSpread, setFireSpread] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedZone) {
      fetchFireSpread(selectedZone);
    }
  }, [selectedZone]);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      const [zonesData, heatmap, comp] = await Promise.all([
        zoneAPI.getAllZones(),
        zoneAPI.getHeatmap(),
        zoneAPI.getComparison(),
      ]);
      
      setZones(zonesData.zones || []);
      setHeatmapData(heatmap.heatmap || []);
      setComparison(comp.comparison || []);
    } catch (err) {
      console.error('Failed to fetch zone data:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchFireSpread = async (zoneId: string) => {
    try {
      const data = await zoneAPI.getFireSpread(zoneId);
      setFireSpread(data);
    } catch (err) {
      console.error('Failed to fetch fire spread:', err);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: any = {
      safe: 'bg-green-500',
      monitoring: 'bg-blue-500',
      warning: 'bg-yellow-500',
      danger: 'bg-orange-500',
      critical: 'bg-red-500',
      offline: 'bg-gray-500',
    };
    return colors[status] || 'bg-gray-500';
  };

  const getStatusBorder = (status: string) => {
    const borders: any = {
      safe: 'border-green-500',
      monitoring: 'border-blue-500',
      warning: 'border-yellow-500',
      danger: 'border-orange-500',
      critical: 'border-red-500',
      offline: 'border-gray-500',
    };
    return borders[status] || 'border-gray-500';
  };

  const getRiskColor = (score: number) => {
    if (score >= 75) return 'bg-red-500';
    if (score >= 60) return 'bg-orange-500';
    if (score >= 40) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-center py-12">
          <Activity className="w-8 h-8 text-blue-500 animate-spin" />
          <span className="ml-3 text-gray-600">Loading zone data...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-cyan-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Map className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">Multi-Zone Forest Network</h2>
              <p className="text-blue-100">Real-time monitoring across all sectors</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-blue-100">Total Zones</p>
            <p className="text-3xl font-bold">{zones.length}</p>
          </div>
        </div>
      </div>

      {/* Zone Grid/Heatmap */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {heatmapData.map((zone) => (
          <div
            key={zone.zone_id}
            onClick={() => setSelectedZone(zone.zone_id)}
            className={`bg-white rounded-lg shadow-lg p-6 cursor-pointer transition transform hover:scale-105 border-l-4 ${getStatusBorder(zone.status)}`}
          >
            {/* Zone Header */}
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-bold text-gray-900">{zone.zone_name}</h3>
                <p className="text-sm text-gray-600">{zone.zone_id}</p>
              </div>
              <div className={`px-3 py-1 rounded-full text-white text-xs font-bold ${getStatusColor(zone.status)}`}>
                {zone.status.toUpperCase()}
              </div>
            </div>

            {/* Risk Visualization */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Current Risk</span>
                <span className="text-2xl font-bold text-gray-900">{zone.risk_score.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div
                  className={`h-4 rounded-full transition-all duration-500 ${getRiskColor(zone.risk_score)}`}
                  style={{ width: `${Math.min(zone.risk_score, 100)}%` }}
                />
              </div>
            </div>

            {/* Zone Stats */}
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-xs text-gray-600">Area</p>
                <p className="text-lg font-bold text-gray-900">{zone.area}</p>
                <p className="text-xs text-gray-500">hectares</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Nodes</p>
                <div className="flex items-center justify-center space-x-1">
                  <Wifi className="w-4 h-4 text-green-600" />
                  <p className="text-lg font-bold text-gray-900">{zone.online_nodes}/{zone.nodes}</p>
                </div>
              </div>
              <div>
                <p className="text-xs text-gray-600">Max Risk</p>
                <p className="text-lg font-bold text-red-600">{zone.max_risk.toFixed(1)}%</p>
              </div>
            </div>

            {/* Coordinates */}
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-xs text-gray-500">
                📍 {zone.latitude.toFixed(4)}°, {zone.longitude.toFixed(4)}°
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Zone Comparison Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="p-6 bg-gray-50 border-b border-gray-200">
          <h3 className="text-lg font-bold text-gray-900 flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2 text-orange-600" />
            Zone Risk Comparison
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Zone
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg Risk
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Max Risk
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Nodes
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Area
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {comparison.map((zone) => (
                <tr key={zone.zone_id} className="hover:bg-gray-50 transition">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{zone.zone_name}</div>
                    <div className="text-xs text-gray-500">{zone.zone_id}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full text-white ${getStatusColor(zone.status)}`}>
                      {zone.status.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{zone.avg_risk.toFixed(1)}%</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-bold text-red-600">{zone.max_risk.toFixed(1)}%</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {zone.online_nodes}/{zone.total_nodes}
                      {zone.online_nodes === zone.total_nodes ? (
                        <Wifi className="inline w-4 h-4 ml-1 text-green-600" />
                      ) : (
                        <WifiOff className="inline w-4 h-4 ml-1 text-red-600" />
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {zone.area_hectares} ha
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Fire Spread Prediction (if zone selected) */}
      {selectedZone && fireSpread && !fireSpread.error && (
        <div className="bg-gradient-to-r from-red-50 to-orange-50 rounded-lg shadow-lg p-6 border-2 border-red-300">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-900 flex items-center">
              <Flame className="w-6 h-6 mr-2 text-red-600" />
              Fire Spread Prediction - {selectedZone}
            </h3>
            <button
              onClick={() => setSelectedZone(null)}
              className="text-sm text-gray-600 hover:text-gray-800"
            >
              ✕ Close
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg p-4">
              <p className="text-xs text-gray-600 mb-1">Origin Node</p>
              <p className="text-lg font-bold text-gray-900">{fireSpread.origin_node}</p>
              <p className="text-xs text-gray-500 mt-1">
                📍 {fireSpread.origin_coords?.latitude.toFixed(4)}°, {fireSpread.origin_coords?.longitude.toFixed(4)}°
              </p>
            </div>

            <div className="bg-white rounded-lg p-4">
              <p className="text-xs text-gray-600 mb-1">Spread Rate</p>
              <p className="text-2xl font-bold text-red-600">{fireSpread.spread_rate_m_per_min}</p>
              <p className="text-xs text-gray-500">meters/minute</p>
            </div>

            <div className="bg-white rounded-lg p-4">
              <p className="text-xs text-gray-600 mb-1">Predicted Radius (30 min)</p>
              <p className="text-2xl font-bold text-orange-600">{fireSpread.predicted_radius_30min}</p>
              <p className="text-xs text-gray-500">meters</p>
            </div>
          </div>

          <div className="mt-4 bg-white rounded-lg p-4">
            <p className="text-sm font-medium text-gray-700 mb-2">At-Risk Nodes:</p>
            <div className="flex flex-wrap gap-2">
              {fireSpread.at_risk_nodes && fireSpread.at_risk_nodes.map((node: string) => (
                <span key={node} className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs font-semibold">
                  {node}
                </span>
              ))}
            </div>
          </div>

          <div className="mt-4 bg-yellow-100 border border-yellow-300 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="w-5 h-5 text-yellow-700 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-yellow-900">Recommendation</p>
                <p className="text-sm text-yellow-800 mt-1">
                  Fire may affect {fireSpread.affected_area_hectares} hectares in 30 minutes. 
                  Consider pre-activating sprinklers in adjacent zones.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
