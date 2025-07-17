import React, { useState, useEffect } from 'react';
import { DollarSign, Clock, MapPin, TrendingUp, AlertTriangle, Download, Filter, Search, Eye, BarChart3, PieChart } from 'lucide-react';

const CostAnalysis = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('cost');
  const [sortOrder, setSortOrder] = useState('desc');
  const [filterBy, setFilterBy] = useState('all');
  const [selectedDelivery, setSelectedDelivery] = useState(null);
  const [anomaliesData, setAnomaliesData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCostData();
  }, []);

  const fetchCostData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      

      // Fetch cost anomalies data
      const anomaliesResponse = await fetch('http://127.0.0.1:8000/cost-anomalies');
      if (!anomaliesResponse.ok) {
        throw new Error(`Cost anomalies API failed: ${anomaliesResponse.status}`);
      }

      const anomaliesData = await anomaliesResponse.json();

      // Transform and combine the data
     const transformedData = anomaliesData.map((anomaly, index) => {
     const cost = parseFloat(anomaly.cost);
     const distance = parseFloat(anomaly.distance);
     const duration = parseFloat(anomaly.time_taken ?? anomaly.duration); // fallback if some have `duration`
     const predictionAccuracy = parseFloat(anomaly.prediction_accuracy);

     return {
       orderId: `ORD${String(index + 1).padStart(6, '0')}`,
       cost: isNaN(cost) ? 0 : Number(cost.toFixed(2)),
       distance: isNaN(distance) ? 0 : Number(distance.toFixed(1)),
       duration: isNaN(duration) ? 0 : Number(duration.toFixed(0)),
       costPerKm:
         !isNaN(cost) && !isNaN(distance) && distance !== 0
           ? Number((cost / distance).toFixed(2))
           : 0,
       anomalyType: anomaly.anomaly_type || 'unknown',
       status: 'completed',
       supplier:
         anomaly.supplier_name || `Supplier ${String.fromCharCode(65 + (index % 26))}`,
       predictionAccuracy: isNaN(predictionAccuracy)
         ? 0
         : Number(predictionAccuracy.toFixed(2)),
    };
});



      setAnomaliesData(transformedData);
    } catch (err) {
      console.error('Error fetching cost data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = (delivery) => {
    setSelectedDelivery(delivery);
  };

  const closeModal = () => {
    setSelectedDelivery(null);
  };

  const handleExport = () => {
    const dataToExport = filteredAndSortedData.map(delivery => ({
      'Order ID': delivery.orderId,
      'Cost': `₹${delivery.cost}`,
      'Distance': `${delivery.distance} km`,
      'Duration': `${delivery.duration} min`,
      'Cost Per KM': `₹${delivery.costPerKm}`,
      'Anomaly Type': delivery.anomalyType,
      'Status': delivery.status,
      'Supplier': delivery.supplier
    }))

    // Convert to CSV
    const headers = Object.keys(dataToExport[0])
    const csvContent = [
      headers.join(','),
      ...dataToExport.map(row => headers.map(header => `"${row[header]}"`).join(','))
    ].join('\n')

    // Download file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `cost-analysis-${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  // Loading state component
  const LoadingState = () => (
    <div className="flex items-center justify-center py-20">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading cost analysis data...</p>
      </div>
    </div>
  );

  // Error state component
  const ErrorState = () => (
    <div className="flex items-center justify-center py-20">
      <div className="text-center text-red-600">
        <AlertTriangle className="w-12 h-12 mx-auto mb-4" />
        <p className="font-medium">Failed to load cost data</p>
        <p className="text-sm text-gray-600 mt-2">{error}</p>
      </div>
    </div>
  );

  const handleAnalytics = () => {
    // Mock analytics action
    alert('Opening detailed analytics dashboard...')
  }

  const getAnomalyColor = (type) => {
    switch(type) {
      case 'cost': return 'bg-red-100 text-red-800';
      case 'duration': return 'bg-orange-100 text-orange-800';
      case 'distance': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredAndSortedData = anomaliesData
    .filter(delivery => 
      delivery.orderId.toLowerCase().includes(searchTerm.toLowerCase()) &&
      (filterBy === 'all' || delivery.anomalyType === filterBy)
    )
    .sort((a, b) => {
      const multiplier = sortOrder === 'asc' ? 1 : -1;
      const aValue = sortBy === 'cost' ? parseFloat(a.cost) : 
                     sortBy === 'distance' ? parseFloat(a.distance) : 
                     parseFloat(a.duration);
      const bValue = sortBy === 'cost' ? parseFloat(b.cost) : 
                     sortBy === 'distance' ? parseFloat(b.distance) : 
                     parseFloat(b.duration);
      return (aValue - bValue) * multiplier;
    });
  
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = filteredAndSortedData.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(filteredAndSortedData.length / itemsPerPage);

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent mb-4">
            Cost Analysis Dashboard
          </h1>
          <p className="text-gray-600 text-lg">
            Monitor delivery costs, identify anomalies, and optimize spending
          </p>
        </div>

        {loading && <LoadingState />}
        {error && <ErrorState />}
        
        {!loading && !error && (
        <>
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Average Cost Card */}
          <div className="md:col-span-2 bg-gradient-to-r from-emerald-500 to-teal-600 rounded-xl p-8 text-white relative overflow-hidden shadow-xl">
            <div className="relative z-10">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-white bg-opacity-20 rounded-full">
                  <DollarSign className="w-6 h-6" />
                </div>
                <h2 className="text-xl font-semibold">Average Cost Per Delivery</h2>
              </div>
              <p className="text-4xl font-bold mb-2">₹136.00</p>
              <p className="text-emerald-100 text-sm">+2.3% from last month</p>
            </div>
            <div className="absolute right-0 top-0 w-32 h-32 bg-white bg-opacity-10 rounded-full transform translate-x-8 -translate-y-8"></div>
            <div className="absolute right-8 bottom-0 w-24 h-24 bg-white bg-opacity-10 rounded-full transform translate-y-8"></div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Deliveries</p>
                <p className="text-2xl font-bold text-gray-900">1,247</p>
                <p className="text-xs text-green-600">+12% this week</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <BarChart3 className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Cost Savings</p>
                <p className="text-2xl font-bold text-green-600">₹15.2K</p>
                <p className="text-xs text-green-600">This month</p>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Anomaly Summary */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold text-gray-900">Anomaly Detection</h2>
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-orange-500" />
              <span className="text-sm text-gray-600">25 total anomalies detected</span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Cost Anomalies */}
            <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-xl p-6 border border-red-200">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-red-500 rounded-full">
                  <DollarSign className="w-6 h-6 text-white" />
                </div>
                <div className="text-right">
                  <p className="text-sm text-red-600 font-medium">HIGH PRIORITY</p>
                </div>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Cost Anomalies</h3>
              <p className="text-3xl font-bold text-red-600 mb-2">12</p>
              <p className="text-sm text-gray-600">Avg overspend: ₹45.20</p>
              <div className="mt-4 w-full bg-red-200 rounded-full h-2">
                <div className="bg-red-500 h-2 rounded-full" style={{ width: '75%' }}></div>
              </div>
            </div>

            {/* Duration Anomalies */}
            <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-6 border border-orange-200">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-orange-500 rounded-full">
                  <Clock className="w-6 h-6 text-white" />
                </div>
                <div className="text-right">
                  <p className="text-sm text-orange-600 font-medium">MEDIUM</p>
                </div>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Duration Anomalies</h3>
              <p className="text-3xl font-bold text-orange-600 mb-2">8</p>
              <p className="text-sm text-gray-600">Avg delay: 15 min</p>
              <div className="mt-4 w-full bg-orange-200 rounded-full h-2">
                <div className="bg-orange-500 h-2 rounded-full" style={{ width: '50%' }}></div>
              </div>
            </div>

            {/* Distance Anomalies */}
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-blue-500 rounded-full">
                  <MapPin className="w-6 h-6 text-white" />
                </div>
                <div className="text-right">
                  <p className="text-sm text-blue-600 font-medium">LOW</p>
                </div>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Distance Anomalies</h3>
              <p className="text-3xl font-bold text-blue-600 mb-2">5</p>
              <p className="text-sm text-gray-600">Avg extra: 3.2 km</p>
              <div className="mt-4 w-full bg-blue-200 rounded-full h-2">
                <div className="bg-blue-500 h-2 rounded-full" style={{ width: '25%' }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
            <div className="flex flex-col md:flex-row gap-4 items-center">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search order ID..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              
              <select
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                value={filterBy}
                onChange={(e) => setFilterBy(e.target.value)}
              >
                <option value="all">All Anomalies</option>
                <option value="cost">Cost Anomalies</option>
                <option value="duration">Duration Anomalies</option>
                <option value="distance">Distance Anomalies</option>
              </select>

              <select
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="cost">Sort by Cost</option>
                <option value="distance">Sort by Distance</option>
                <option value="duration">Sort by Duration</option>
              </select>

              <button
                className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              >
                {sortOrder === 'asc' ? '↑' : '↓'}
              </button>
            </div>

            <div className="flex gap-2">
              <button 
                onClick={handleAnalytics}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <PieChart className="w-4 h-4" />
                Analytics
              </button>
              <button 
                onClick={handleExport}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <Download className="w-4 h-4" />
                Export
              </button>
            </div>
          </div>
        </div>

        {/* Enhanced Expensive Deliveries Table */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-100">
          <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100">
            <h2 className="text-xl font-semibold text-gray-900">Most Expensive Deliveries</h2>
            <p className="text-sm text-gray-600 mt-1">Deliveries with highest cost anomalies</p>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Order Details
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Cost Analysis
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Distance & Duration
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Anomaly Type
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {currentItems.map((delivery, index) => {
                  const globalIndex = (currentPage - 1) * itemsPerPage + index + 1;
                  return (
                    <tr key={index} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
                              <span className="text-white font-semibold text-xs">
                                {globalIndex}
                              </span>
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {delivery.orderId}
                            </div>
                            <div className="text-sm text-gray-500">
                              {delivery.supplier}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm">
                          <div className="text-lg font-bold text-gray-900">₹{delivery.cost}</div>
                          <div className="text-gray-500">₹{delivery.costPerKm}/km</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm">
                          <div className="font-medium text-gray-900">{delivery.distance} km</div>
                          <div className="text-gray-500">{delivery.duration} min</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full capitalize ${getAnomalyColor(delivery.anomalyType)}`}>
                          {delivery.anomalyType}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full capitalize ${getStatusColor(delivery.status)}`}>
                          {delivery.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <button 
                          onClick={() => handleViewDetails(delivery)}
                          className="text-emerald-600 hover:text-emerald-800 transition-colors"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>

            </table>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-gray-500 text-sm">
          Showing {filteredAndSortedData.length} of {anomaliesData.length} expensive deliveries
        </div>

        {/* Modal for delivery details */}
        {selectedDelivery && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-96 overflow-y-auto">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-semibold text-gray-900">Delivery Details</h3>
                  <button 
                    onClick={closeModal}
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">Order Information</h4>
                    <div className="space-y-2 text-sm">
                      <div><span className="font-medium">Order ID:</span> {selectedDelivery.orderId}</div>
                      <div><span className="font-medium">Supplier:</span> {selectedDelivery.supplier}</div>
                      <div><span className="font-medium">Status:</span> 
                        <span className={`ml-2 px-2 py-1 rounded-full text-xs ${getStatusColor(selectedDelivery.status)}`}>
                          {selectedDelivery.status}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">Cost Analysis</h4>
                    <div className="space-y-2 text-sm">
                      <div><span className="font-medium">Total Cost:</span> ₹{selectedDelivery.cost}</div>
                      <div><span className="font-medium">Cost per KM:</span> ₹{selectedDelivery.costPerKm}</div>
                      <div><span className="font-medium">Distance:</span> {selectedDelivery.distance} km</div>
                      <div><span className="font-medium">Duration:</span> {selectedDelivery.duration} min</div>
                    </div>
                  </div>
                </div>
                
                <div className="mt-6">
                  <h4 className="font-medium text-gray-900 mb-3">Anomaly Information</h4>
                  <div className="flex items-center gap-2">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getAnomalyColor(selectedDelivery.anomalyType)}`}>
                      {selectedDelivery.anomalyType} anomaly
                    </span>
                    <span className="text-sm text-gray-600">detected in this delivery</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        </>
        )}
      </div>
    </div>
  );
};

export default CostAnalysis;