'use client';

import { useEffect, useState } from 'react';
import { externalAPI } from '@/lib/api';
import { Cloud, CloudRain, Wind, Droplets, Eye, Flame, Satellite, MapPin, AlertTriangle, TrendingUp, RefreshCw, Clock } from 'lucide-react';

export default function WeatherSatellite() {
  const [location, setLocation] = useState<any>(null);
  const [weather, setWeather] = useState<any>(null);
  const [forecast, setForecast] = useState<any[]>([]);
  const [hotspots, setHotspots] = useState<any[]>([]);
  const [riskAssessment, setRiskAssessment] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 300000); // Refresh every 5 minutes
    return () => clearInterval(interval);
  }, []);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      const [locationData, weatherData, forecastData, hotspotsData] = await Promise.all([
        externalAPI.getLocation(),
        externalAPI.getCurrentWeather(),
        externalAPI.getForecast(),
        externalAPI.getFireHotspots(),
      ]);
      
      setLocation(locationData);
      setWeather(weatherData.weather || weatherData);
      setForecast(forecastData.forecast || []);
      setHotspots(hotspotsData.hotspots || []);
      setRiskAssessment(weatherData.fire_risk || null);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Failed to fetch external data:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDateIST = (dateString: string | Date) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-IN', {
      timeZone: 'Asia/Kolkata',
      dateStyle: 'medium',
      timeStyle: 'short'
    });
  };

  const getRelativeTime = (dateString: string | Date) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  };

  const getWindDirection = (degrees: number) => {
    const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
    const index = Math.round(degrees / 45) % 8;
    return directions[index];
  };

  const getFireDangerColor = (level: string) => {
    const colors: any = {
      low: 'bg-green-500',
      moderate: 'bg-yellow-500',
      high: 'bg-orange-500',
      'very high': 'bg-red-500',
      extreme: 'bg-purple-500',
    };
    return colors[level.toLowerCase()] || 'bg-gray-500';
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-green-600';
    if (confidence >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-center py-12">
          <Satellite className="w-8 h-8 text-blue-500 animate-pulse" />
          <span className="ml-3 text-gray-600">Loading external data...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Location */}
      <div className="bg-gradient-to-r from-sky-600 to-blue-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Satellite className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">Weather & Satellite Integration</h2>
              {location && (
                <div className="flex items-center space-x-2 text-sky-100 mt-1">
                  <MapPin className="w-4 h-4" />
                  <span className="text-sm">
                    {location.name} ({location.latitude.toFixed(4)}°N, {location.longitude.toFixed(4)}°E)
                  </span>
                </div>
              )}
              {lastUpdated && (
                <div className="flex items-center space-x-2 text-sky-100 mt-1">
                  <Clock className="w-4 h-4" />
                  <span className="text-xs">
                    Last updated: {formatDateIST(lastUpdated)} ({getRelativeTime(lastUpdated)})
                  </span>
                </div>
              )}
            </div>
          </div>
          <div className="text-right">
            {weather && (
              <>
                <p className="text-sm text-sky-100">Current Temp</p>
                <p className="text-4xl font-bold">{weather.temperature?.toFixed(1)}°C</p>
              </>
            )}
            <button
              onClick={fetchAllData}
              disabled={loading}
              className="mt-2 px-3 py-1 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg text-sm flex items-center space-x-1 transition"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </div>

      {/* Current Weather Conditions */}
      {weather && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-600">Temperature</h3>
              <Cloud className="w-6 h-6 text-orange-500" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{weather.temperature?.toFixed(1)}°C</p>
            {weather.timestamp && (
              <p className="text-xs text-gray-500 mt-1">
                As of {formatDateIST(weather.timestamp)}
              </p>
            )}
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-600">Humidity</h3>
              <Droplets className="w-6 h-6 text-blue-500" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{weather.humidity}%</p>
            <div className="mt-4 w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all"
                style={{ width: `${Math.min(weather.humidity, 100)}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {weather.humidity < 30 ? 'Very Dry - High Fire Risk' : weather.humidity < 60 ? 'Moderate' : 'High - Low Fire Risk'}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-600">Wind</h3>
              <Wind className="w-6 h-6 text-cyan-500" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{weather.wind_speed?.toFixed(1)}</p>
            <p className="text-xs text-gray-500">m/s</p>
            <div className="mt-3 text-sm text-gray-600">
              <div className="flex justify-between">
                <span>Direction:</span>
                <span className="font-semibold">{getWindDirection(weather.wind_direction)} ({weather.wind_direction}°)</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-600">Visibility</h3>
              <Eye className="w-6 h-6 text-purple-500" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{weather.visibility?.toFixed(1) || 'N/A'}</p>
            <p className="text-xs text-gray-500">kilometers</p>
            <div className="mt-3 text-sm text-gray-600">
              <div className="flex justify-between">
                <span>Pressure:</span>
                <span className="font-semibold">{weather.pressure} hPa</span>
              </div>
              <div className="flex justify-between">
                <span>Clouds:</span>
                <span className="font-semibold">{weather.cloud_cover}%</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Weather Description */}
      {weather && weather.weather_description && (
        <div className="bg-gradient-to-r from-blue-50 to-sky-50 rounded-lg p-4 border border-blue-200">
          <div className="flex items-center space-x-3">
            <Cloud className="w-5 h-5 text-blue-600" />
            <p className="text-gray-700">
              <span className="font-semibold">Current Conditions:</span> {weather.weather_description}
            </p>
          </div>
        </div>
      )}

      {/* 3-Day Forecast */}
      {forecast.length > 0 && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="p-6 bg-gray-50 border-b border-gray-200">
            <h3 className="text-lg font-bold text-gray-900 flex items-center">
              <CloudRain className="w-5 h-5 mr-2 text-blue-600" />
              Weather Forecast
            </h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {forecast.slice(0, 8).filter((_, idx) => idx % 2 === 0).map((item, idx) => (
                <div key={idx} className="bg-gradient-to-br from-blue-50 to-sky-50 rounded-lg p-4 text-center border border-blue-200">
                  <p className="text-sm font-semibold text-gray-700">
                    {formatDateIST(item.timestamp)}
                  </p>
                  <div className="my-3">
                    <Cloud className="w-10 h-10 mx-auto text-gray-600" />
                  </div>
                  <p className="text-2xl font-bold text-gray-900">{item.temperature?.toFixed(0)}°C</p>
                  <p className="text-xs text-gray-600 mt-1">{item.description}</p>
                  <div className="mt-3 pt-3 border-t border-blue-200 space-y-1 text-xs text-gray-600">
                    <div className="flex justify-between">
                      <span>💧 Humidity:</span>
                      <span>{item.humidity}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>💨 Wind:</span>
                      <span>{item.wind_speed?.toFixed(1)} m/s</span>
                    </div>
                    {item.precipitation > 0 && (
                      <div className="flex justify-between">
                        <span>🌧️ Rain:</span>
                        <span>{item.precipitation} mm</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* NASA FIRMS Satellite Fire Hotspots */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="p-6 bg-red-50 border-b border-red-200">
          <h3 className="text-lg font-bold text-gray-900 flex items-center">
            <Satellite className="w-5 h-5 mr-2 text-red-600" />
            Satellite Fire Hotspots (NASA FIRMS)
          </h3>
          <p className="text-sm text-gray-600 mt-1">Detected fire hotspots within 50km radius</p>
        </div>
        
        {hotspots.length > 0 ? (
          <div className="p-6">
            <div className="mb-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <AlertTriangle className="w-5 h-5 text-yellow-700 mt-0.5" />
                <div>
                  <p className="text-sm font-semibold text-yellow-900">
                    {hotspots.length} Active Hotspot{hotspots.length !== 1 ? 's' : ''} Detected
                  </p>
                  <p className="text-xs text-yellow-800 mt-1">
                    Satellite data updated regularly. High confidence hotspots require immediate attention.
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              {hotspots.slice(0, 10).map((hotspot, idx) => (
                <div key={idx} className="border border-red-200 rounded-lg p-4 bg-red-50 hover:shadow-md transition">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Flame className="w-5 h-5 text-red-600" />
                      <h4 className="font-semibold text-gray-900">Hotspot #{idx + 1}</h4>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-bold text-white ${
                      hotspot.confidence >= 80 ? 'bg-red-600' : hotspot.confidence >= 50 ? 'bg-orange-500' : 'bg-yellow-500'
                    }`}>
                      {hotspot.confidence}% Confidence
                    </span>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                    <div>
                      <p className="text-xs text-gray-600">Location</p>
                      <div className="flex items-center space-x-1">
                        <MapPin className="w-3 h-3 text-red-600" />
                        <p className="font-semibold text-gray-900">
                          {hotspot.latitude.toFixed(4)}°, {hotspot.longitude.toFixed(4)}°
                        </p>
                      </div>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600">Distance</p>
                      <p className="font-semibold text-gray-900">{hotspot.distance_km?.toFixed(2)} km</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600">Brightness</p>
                      <p className="font-semibold text-orange-600">{hotspot.brightness?.toFixed(0)}K</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600">Detected</p>
                      <p className="font-semibold text-gray-900" title={formatDateIST(hotspot.scan_time)}>
                        {getRelativeTime(hotspot.scan_time)}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="p-12 text-center">
            <Satellite className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600 font-medium">No fire hotspots detected in the area</p>
            <p className="text-sm text-gray-500 mt-1">Satellite monitoring is active</p>
          </div>
        )}
      </div>

      {/* Data Sources Info */}
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <p className="text-xs text-gray-600 text-center">
          📡 Data sources: OpenWeatherMap API • NASA FIRMS (Fire Information for Resource Management System) 
          • Updated every 5 minutes • Times shown in IST (Indian Standard Time)
        </p>
      </div>
    </div>
  );
}
