'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Database, ChevronLeft, ChevronRight, Download, RefreshCw } from 'lucide-react';

interface SensorRecord {
  _id: string;
  temperature: number;
  humidity: number;
  smoke_level: number;
  rain_level: number;
  rain_detected: boolean;
  fire_risk_score: number;
  risk_level: string;
  timestamp: string;
}

export default function SensorRecordsViewer() {
  const [records, setRecords] = useState<SensorRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  const [recordsPerPage] = useState(20);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    fetchRecords();
  }, [currentPage, filter]);

  const fetchRecords = async () => {
    try {
      setLoading(true);
      const skip = (currentPage - 1) * recordsPerPage;
      
      let url = `/sensors/records?skip=${skip}&limit=${recordsPerPage}`;
      if (filter !== 'all') {
        url += `&risk_level=${filter}`;
      }
      
      const response = await api.get(url);
      setRecords(response.data.records);
      setTotalRecords(response.data.total);
    } catch (error) {
      console.error('Failed to fetch sensor records:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExportCSV = async () => {
    try {
      const response = await api.get('/export/sensor-data/csv?hours=720', {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `all_sensor_records_${new Date().toISOString().slice(0, 10)}.csv`);
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
      case 'critical': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const totalPages = Math.ceil(totalRecords / recordsPerPage);

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  const handlePageClick = (page: number) => {
    setCurrentPage(page);
  };

  const getPageNumbers = () => {
    const pages = [];
    const maxPagesToShow = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxPagesToShow / 2));
    let endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);

    if (endPage - startPage + 1 < maxPagesToShow) {
      startPage = Math.max(1, endPage - maxPagesToShow + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }

    return pages;
  };

  if (loading && records.length === 0) {
    return (
      <div className="flex items-center justify-center p-12">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-3 text-gray-600">Loading sensor records...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Database className="w-8 h-8 text-blue-600" />
            <div>
              <h2 className="text-xl font-bold text-gray-900">All Sensor Records</h2>
              <p className="text-sm text-gray-600">
                Showing {records.length} of {totalRecords.toLocaleString()} total records
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={fetchRecords}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>
            <button
              onClick={handleExportCSV}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
            >
              <Download className="w-4 h-4" />
              <span>Export All</span>
            </button>
          </div>
        </div>

        {/* Filter */}
        <div className="mt-4 flex items-center space-x-2">
          <span className="text-sm text-gray-600">Filter by risk:</span>
          {['all', 'critical', 'high', 'medium', 'low'].map((level) => (
            <button
              key={level}
              onClick={() => {
                setFilter(level);
                setCurrentPage(1);
              }}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition ${
                filter === level
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {level.charAt(0).toUpperCase() + level.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Records Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Temp (°C)
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Humidity (%)
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Smoke
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rain Level
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rain
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Risk Score
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Risk Level
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {records.map((record) => (
                <tr key={record._id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                    {new Date(record.timestamp).toLocaleString()}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                    {record.temperature.toFixed(1)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                    {record.humidity.toFixed(1)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                    {record.smoke_level}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                    {record.rain_level.toFixed(1)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                    {record.rain_detected ? (
                      <span className="text-blue-600">✓ Yes</span>
                    ) : (
                      <span className="text-gray-400">✗ No</span>
                    )}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-semibold text-gray-900">
                    {record.fire_risk_score.toFixed(1)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getRiskColor(record.risk_level)}`}>
                      {record.risk_level.toUpperCase()}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="bg-gray-50 px-4 py-3 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Page <span className="font-semibold">{currentPage}</span> of{' '}
              <span className="font-semibold">{totalPages}</span>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={handlePreviousPage}
                disabled={currentPage === 1}
                className={`flex items-center px-3 py-1 rounded-lg text-sm font-medium transition ${
                  currentPage === 1
                    ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                }`}
              >
                <ChevronLeft className="w-4 h-4" />
                Previous
              </button>

              {/* Page Numbers */}
              <div className="hidden sm:flex items-center space-x-1">
                {currentPage > 3 && (
                  <>
                    <button
                      onClick={() => handlePageClick(1)}
                      className="px-3 py-1 rounded-lg text-sm font-medium bg-white text-gray-700 hover:bg-gray-100 border border-gray-300"
                    >
                      1
                    </button>
                    {currentPage > 4 && <span className="text-gray-500">...</span>}
                  </>
                )}

                {getPageNumbers().map((page) => (
                  <button
                    key={page}
                    onClick={() => handlePageClick(page)}
                    className={`px-3 py-1 rounded-lg text-sm font-medium transition ${
                      page === currentPage
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                    }`}
                  >
                    {page}
                  </button>
                ))}

                {currentPage < totalPages - 2 && (
                  <>
                    {currentPage < totalPages - 3 && <span className="text-gray-500">...</span>}
                    <button
                      onClick={() => handlePageClick(totalPages)}
                      className="px-3 py-1 rounded-lg text-sm font-medium bg-white text-gray-700 hover:bg-gray-100 border border-gray-300"
                    >
                      {totalPages}
                    </button>
                  </>
                )}
              </div>

              <button
                onClick={handleNextPage}
                disabled={currentPage === totalPages}
                className={`flex items-center px-3 py-1 rounded-lg text-sm font-medium transition ${
                  currentPage === totalPages
                    ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                }`}
              >
                Next
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Empty State */}
      {records.length === 0 && !loading && (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <Database className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Records Found</h3>
          <p className="text-gray-600">
            {filter !== 'all' 
              ? `No sensor records found with ${filter} risk level.`
              : 'No sensor records available yet. Start the sensor stream to collect data.'}
          </p>
        </div>
      )}
    </div>
  );
}
