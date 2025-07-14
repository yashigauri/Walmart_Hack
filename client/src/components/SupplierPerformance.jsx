import React, { useState } from 'react';
import { Search, Filter, Download, TrendingUp, AlertCircle, Award, Eye } from 'lucide-react';

const SupplierPerformance = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTier, setSelectedTier] = useState('All');
  const [sortBy, setSortBy] = useState('reliabilityScore');
  const [sortOrder, setSortOrder] = useState('desc');
  const [selectedSupplier, setSelectedSupplier] = useState(null);
  const [isDetailedView, setIsDetailedView] = useState(true);

  const handleViewDetails = (supplier) => {
    setSelectedSupplier(supplier);
  };

  const closeModal = () => {
    setSelectedSupplier(null);
  };

  const handleExport = () => {
    const dataToExport = filteredAndSortedData.map(supplier => ({
      'Supplier Name': supplier.name,
      'Reliability Score': supplier.reliabilityScore,
      'On-Time Rate': `${supplier.onTimeRate}%`,
      'Avg Actual Delay': `${supplier.avgActualDelay} min`,
      'Order Volume': supplier.orderVolume.toLocaleString(),
      'Distance Efficiency': `${supplier.distanceEfficiency}%`,
      'Tier': supplier.tier,
      'Zones Served': supplier.zonesServed,
      'Time Saved (RL)': `${supplier.totalRLTimeSaved} hrs`
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
    link.setAttribute('download', `supplier-performance-${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const supplierData = [
    {
      name: 'Supplier A',
      avgPredictedDelay: 15,
      avgActualDelay: 20,
      totalRLTimeSaved: 300,
      orderVolume: 5000,
      avgDistance: 10,
      avgWeight: 5,
      highTrafficDeliveries: 100,
      zonesServed: 5,
      onTimeRate: 85,
      severeDelayRate: 5,
      weatherResilience: 90,
      distanceEfficiency: 88,
      rlOptimizationRate: 92,
      reliabilityScore: 88.5,
      tier: 'Gold'
    },
    {
      name: 'Supplier B',
      avgPredictedDelay: 10,
      avgActualDelay: 12,
      totalRLTimeSaved: 250,
      orderVolume: 4500,
      avgDistance: 8,
      avgWeight: 4,
      highTrafficDeliveries: 80,
      zonesServed: 4,
      onTimeRate: 92,
      severeDelayRate: 3,
      weatherResilience: 85,
      distanceEfficiency: 91,
      rlOptimizationRate: 89,
      reliabilityScore: 92.3,
      tier: 'Gold'
    },
    {
      name: 'Supplier C',
      avgPredictedDelay: 25,
      avgActualDelay: 30,
      totalRLTimeSaved: 200,
      orderVolume: 4000,
      avgDistance: 12,
      avgWeight: 6,
      highTrafficDeliveries: 120,
      zonesServed: 6,
      onTimeRate: 75,
      severeDelayRate: 8,
      weatherResilience: 78,
      distanceEfficiency: 82,
      rlOptimizationRate: 85,
      reliabilityScore: 78.2,
      tier: 'Silver'
    },
    {
      name: 'Supplier D',
      avgPredictedDelay: 18,
      avgActualDelay: 22,
      totalRLTimeSaved: 280,
      orderVolume: 4800,
      avgDistance: 9,
      avgWeight: 4.5,
      highTrafficDeliveries: 90,
      zonesServed: 5,
      onTimeRate: 88,
      severeDelayRate: 4,
      weatherResilience: 87,
      distanceEfficiency: 89,
      rlOptimizationRate: 91,
      reliabilityScore: 86.7,
      tier: 'Silver'
    },
    {
      name: 'Supplier E',
      avgPredictedDelay: 12,
      avgActualDelay: 15,
      totalRLTimeSaved: 220,
      orderVolume: 4200,
      avgDistance: 7,
      avgWeight: 3.5,
      highTrafficDeliveries: 70,
      zonesServed: 3,
      onTimeRate: 90,
      severeDelayRate: 2,
      weatherResilience: 92,
      distanceEfficiency: 94,
      rlOptimizationRate: 88,
      reliabilityScore: 91.8,
      tier: 'Gold'
    },
    {
      name: 'Supplier F',
      avgPredictedDelay: 22,
      avgActualDelay: 28,
      totalRLTimeSaved: 180,
      orderVolume: 3800,
      avgDistance: 11,
      avgWeight: 5.5,
      highTrafficDeliveries: 110,
      zonesServed: 4,
      onTimeRate: 72,
      severeDelayRate: 10,
      weatherResilience: 75,
      distanceEfficiency: 80,
      rlOptimizationRate: 83,
      reliabilityScore: 75.4,
      tier: 'Bronze'
    },
    {
      name: 'Supplier G',
      avgPredictedDelay: 16,
      avgActualDelay: 20,
      totalRLTimeSaved: 260,
      orderVolume: 4600,
      avgDistance: 8.5,
      avgWeight: 4.2,
      highTrafficDeliveries: 85,
      zonesServed: 4,
      onTimeRate: 86,
      severeDelayRate: 5,
      weatherResilience: 89,
      distanceEfficiency: 87,
      rlOptimizationRate: 90,
      reliabilityScore: 87.1,
      tier: 'Silver'
    },
    {
      name: 'Supplier H',
      avgPredictedDelay: 11,
      avgActualDelay: 14,
      totalRLTimeSaved: 240,
      orderVolume: 4400,
      avgDistance: 7.5,
      avgWeight: 3.8,
      highTrafficDeliveries: 75,
      zonesServed: 3,
      onTimeRate: 91,
      severeDelayRate: 3,
      weatherResilience: 88,
      distanceEfficiency: 93,
      rlOptimizationRate: 87,
      reliabilityScore: 90.5,
      tier: 'Gold'
    },
    {
      name: 'Supplier I',
      avgPredictedDelay: 24,
      avgActualDelay: 30,
      totalRLTimeSaved: 180,
      orderVolume: 3900,
      avgDistance: 11.5,
      avgWeight: 5.8,
      highTrafficDeliveries: 115,
      zonesServed: 5,
      onTimeRate: 70,
      severeDelayRate: 12,
      weatherResilience: 72,
      distanceEfficiency: 78,
      rlOptimizationRate: 82,
      reliabilityScore: 73.8,
      tier: 'Critical Review'
    },
    {
      name: 'Supplier J',
      avgPredictedDelay: 17,
      avgActualDelay: 21,
      totalRLTimeSaved: 270,
      orderVolume: 4700,
      avgDistance: 9.5,
      avgWeight: 4.7,
      highTrafficDeliveries: 95,
      zonesServed: 4,
      onTimeRate: 84,
      severeDelayRate: 6,
      weatherResilience: 86,
      distanceEfficiency: 85,
      rlOptimizationRate: 89,
      reliabilityScore: 85.3,
      tier: 'Silver'
    },
    {
      name: 'Supplier K',
      avgPredictedDelay: 8,
      avgActualDelay: 9,
      totalRLTimeSaved: 420,
      orderVolume: 5200,
      avgDistance: 6.5,
      avgWeight: 3.2,
      highTrafficDeliveries: 65,
      zonesServed: 3,
      onTimeRate: 95,
      severeDelayRate: 1,
      weatherResilience: 96,
      distanceEfficiency: 97,
      rlOptimizationRate: 94,
      reliabilityScore: 95.2,
      tier: 'Gold'
    },
    {
      name: 'Supplier L',
      avgPredictedDelay: 28,
      avgActualDelay: 35,
      totalRLTimeSaved: 150,
      orderVolume: 3200,
      avgDistance: 14,
      avgWeight: 6.8,
      highTrafficDeliveries: 140,
      zonesServed: 6,
      onTimeRate: 65,
      severeDelayRate: 15,
      weatherResilience: 68,
      distanceEfficiency: 72,
      rlOptimizationRate: 78,
      reliabilityScore: 68.5,
      tier: 'Critical Review'
    }
  ];

  const getTierColor = (tier) => {
    switch(tier) {
      case 'Gold': return 'bg-gradient-to-r from-yellow-400 to-yellow-600 text-white';
      case 'Silver': return 'bg-gradient-to-r from-gray-400 to-gray-600 text-white';
      case 'Bronze': return 'bg-gradient-to-r from-orange-400 to-orange-600 text-white';
      case 'Critical Review': return 'bg-gradient-to-r from-red-500 to-red-700 text-white';
      default: return 'bg-gradient-to-r from-gray-400 to-gray-600 text-white';
    }
  };

  const getTierIcon = (tier) => {
    switch(tier) {
      case 'Gold': return <Award className="w-4 h-4" />;
      case 'Silver': return <Award className="w-4 h-4" />;
      case 'Bronze': return <Award className="w-4 h-4" />;
      case 'Critical Review': return <AlertCircle className="w-4 h-4" />;
      default: return <Award className="w-4 h-4" />;
    }
  };

  const getPerformanceColor = (value, type) => {
    switch(type) {
      case 'onTime':
        return value >= 90 ? 'text-green-600' : value >= 80 ? 'text-yellow-600' : 'text-red-600';
      case 'delay':
        return value <= 10 ? 'text-green-600' : value <= 20 ? 'text-yellow-600' : 'text-red-600';
      case 'efficiency':
        return value >= 90 ? 'text-green-600' : value >= 80 ? 'text-yellow-600' : 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const filteredAndSortedData = supplierData
    .filter(supplier => 
      supplier.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
      (selectedTier === 'All' || supplier.tier === selectedTier)
    )
    .sort((a, b) => {
      const multiplier = sortOrder === 'asc' ? 1 : -1;
      return (a[sortBy] - b[sortBy]) * multiplier;
    });

  const tierCounts = supplierData.reduce((acc, supplier) => {
    acc[supplier.tier] = (acc[supplier.tier] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            Supplier Performance Dashboard
          </h1>
          <p className="text-gray-600 text-lg">
            Advanced analytics and reliability metrics for supply chain optimization
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Suppliers</p>
                <p className="text-2xl font-bold text-gray-900">{supplierData.length}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Gold Tier</p>
                <p className="text-2xl font-bold text-yellow-600">{tierCounts['Gold'] || 0}</p>
              </div>
              <div className="p-3 bg-yellow-100 rounded-full">
                <Award className="w-6 h-6 text-yellow-600" />
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Reliability</p>
                <p className="text-2xl font-bold text-green-600">
                  {(supplierData.reduce((sum, s) => sum + s.reliabilityScore, 0) / supplierData.length).toFixed(1)}
                </p>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Critical Review</p>
                <p className="text-2xl font-bold text-red-600">{tierCounts['Critical Review'] || 0}</p>
              </div>
              <div className="p-3 bg-red-100 rounded-full">
                <AlertCircle className="w-6 h-6 text-red-600" />
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
                  placeholder="Search suppliers..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              
              <select
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={selectedTier}
                onChange={(e) => setSelectedTier(e.target.value)}
              >
                <option value="All">All Tiers</option>
                <option value="Gold">Gold</option>
                <option value="Silver">Silver</option>
                <option value="Bronze">Bronze</option>
                <option value="Critical Review">Critical Review</option>
              </select>

              <select
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="reliabilityScore">Reliability Score</option>
                <option value="onTimeRate">On-Time Rate</option>
                <option value="orderVolume">Order Volume</option>
                <option value="avgActualDelay">Avg Delay</option>
                <option value="weatherResilience">Weather Resilience</option>
                <option value="distanceEfficiency">Distance Efficiency</option>
                <option value="rlOptimizationRate">RL Optimization</option>
                <option value="totalRLTimeSaved">Time Saved</option>
              </select>

              <button
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              >
                {sortOrder === 'asc' ? '↑' : '↓'}
              </button>
            </div>

            <div className="flex gap-2">
              <button 
                onClick={() => setIsDetailedView(!isDetailedView)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  isDetailedView 
                    ? 'bg-blue-600 text-white hover:bg-blue-700' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                <Filter className="w-4 h-4" />
                {isDetailedView ? 'Detailed View' : 'Compact View'}
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

        {/* Table */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-100">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Supplier
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Reliability Score
                  </th>
                  {isDetailedView ? (
                    <>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Delay Analysis
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Performance Rates
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Weather & Distance
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        RL Optimization
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Volume & Operations
                      </th>
                    </>
                  ) : (
                    <>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Performance
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Orders & Efficiency
                      </th>
                    </>
                  )}
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Tier
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredAndSortedData.map((supplier, index) => (
                  <tr key={index} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center">
                            <span className="text-white font-semibold text-sm">
                              {supplier.name.split(' ')[1]}
                            </span>
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {supplier.name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {supplier.zonesServed} zones
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="text-lg font-bold text-gray-900">
                          {supplier.reliabilityScore}
                        </div>
                        <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${supplier.reliabilityScore}%` }}
                          ></div>
                        </div>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        Tier: {supplier.tier}
                      </div>
                    </td>
                    
                    {/* Conditional columns based on view mode */}
                    {isDetailedView ? (
                      <>
                        {/* Delay Analysis Column */}
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm space-y-1">
                            <div className="flex justify-between items-center">
                              <span className="text-gray-600">Predicted:</span>
                              <span className={`font-medium ${getPerformanceColor(supplier.avgPredictedDelay, 'delay')}`}>
                                {supplier.avgPredictedDelay}m
                              </span>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="text-gray-600">Actual:</span>
                              <span className={`font-medium ${getPerformanceColor(supplier.avgActualDelay, 'delay')}`}>
                                {supplier.avgActualDelay}m
                              </span>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="text-gray-600">Severe:</span>
                              <span className={`font-medium ${supplier.severeDelayRate <= 3 ? 'text-green-600' : supplier.severeDelayRate <= 6 ? 'text-yellow-600' : 'text-red-600'}`}>
                                {supplier.severeDelayRate}%
                              </span>
                            </div>
                          </div>
                        </td>

                        {/* Performance Rates Column */}
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm space-y-1">
                            <div className="flex justify-between items-center">
                              <span className="text-gray-600">On-Time:</span>
                              <span className={`font-medium ${getPerformanceColor(supplier.onTimeRate, 'onTime')}`}>
                                {supplier.onTimeRate}%
                              </span>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="text-gray-600">High Traffic:</span>
                              <span className="font-medium text-gray-700">
                                {supplier.highTrafficDeliveries}
                              </span>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="text-gray-600">Zones:</span>
                              <span className="font-medium text-gray-700">
                                {supplier.zonesServed}
                              </span>
                            </div>
                          </div>
                        </td>

                        {/* Weather & Distance Column */}
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm space-y-1">
                            <div className="flex justify-between items-center">
                              <span className="text-gray-600">Weather:</span>
                              <span className={`font-medium ${getPerformanceColor(supplier.weatherResilience, 'efficiency')}`}>
                                {supplier.weatherResilience}%
                              </span>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="text-gray-600">Distance:</span>
                              <span className={`font-medium ${getPerformanceColor(supplier.distanceEfficiency, 'efficiency')}`}>
                                {supplier.distanceEfficiency}%
                              </span>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="text-gray-600">Avg Dist:</span>
                              <span className="font-medium text-gray-700">
                                {supplier.avgDistance}km
                              </span>
                            </div>
                          </div>
                        </td>

                        {/* RL Optimization Column */}
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm space-y-1">
                            <div className="flex justify-between items-center">
                              <span className="text-gray-600">RL Rate:</span>
                              <span className={`font-medium ${getPerformanceColor(supplier.rlOptimizationRate, 'efficiency')}`}>
                                {supplier.rlOptimizationRate}%
                              </span>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="text-gray-600">Time Saved:</span>
                              <span className="font-medium text-green-600">
                                {supplier.totalRLTimeSaved}h
                              </span>
                            </div>
                            <div className="text-xs text-gray-500 mt-1">
                              ML Optimized
                            </div>
                          </div>
                        </td>

                        {/* Volume & Operations Column */}
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm space-y-1">
                            <div className="flex justify-between items-center">
                              <span className="text-gray-600">Orders:</span>
                              <span className="font-medium text-gray-900">
                                {(supplier.orderVolume / 1000).toFixed(1)}k
                              </span>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="text-gray-600">Avg Weight:</span>
                              <span className="font-medium text-gray-700">
                                {supplier.avgWeight}kg
                              </span>
                            </div>
                            <div className="text-xs text-gray-500 mt-1">
                              Volume Score
                            </div>
                          </div>
                        </td>
                      </>
                    ) : (
                      <>
                        {/* Compact Performance Column */}
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center space-x-3">
                            <div className="flex-1">
                              <div className="text-sm font-medium text-gray-900">
                                <span className={getPerformanceColor(supplier.onTimeRate, 'onTime')}>
                                  {supplier.onTimeRate}%
                                </span> On-time
                              </div>
                              <div className="text-sm text-gray-500">
                                {supplier.avgPredictedDelay}m avg delay
                              </div>
                            </div>
                          </div>
                        </td>

                        {/* Compact Orders & Efficiency Column */}
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm">
                            <div className="text-gray-900 font-medium">
                              {(supplier.orderVolume / 1000).toFixed(1)}k orders
                            </div>
                            <div className="text-gray-500">
                              <span className={getPerformanceColor(supplier.rlOptimizationRate, 'efficiency')}>
                                {supplier.rlOptimizationRate}%
                              </span> efficiency
                            </div>
                          </div>
                        </td>
                      </>
                    )}

                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold ${getTierColor(supplier.tier)}`}>
                        {getTierIcon(supplier.tier)}
                        {supplier.tier}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <button 
                        onClick={() => handleViewDetails(supplier)}
                        className="text-blue-600 hover:text-blue-800 transition-colors"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-gray-500 text-sm">
          Showing {filteredAndSortedData.length} of {supplierData.length} suppliers
        </div>

        {/* Modal for supplier details */}
        {selectedSupplier && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-96 overflow-y-auto">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-semibold text-gray-900">Supplier Performance Details</h3>
                  <button 
                    onClick={closeModal}
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">Basic Information</h4>
                    <div className="space-y-2 text-sm">
                      <div><span className="font-medium">Name:</span> {selectedSupplier.name}</div>
                      <div><span className="font-medium">Tier:</span> 
                        <span className={`ml-2 px-2 py-1 rounded-full text-xs ${getTierColor(selectedSupplier.tier)}`}>
                          {selectedSupplier.tier}
                        </span>
                      </div>
                      <div><span className="font-medium">Zones Served:</span> {selectedSupplier.zonesServed}</div>
                      <div><span className="font-medium">Order Volume:</span> {selectedSupplier.orderVolume.toLocaleString()}</div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">Performance Metrics</h4>
                    <div className="space-y-2 text-sm">
                      <div><span className="font-medium">Reliability Score:</span> {selectedSupplier.reliabilityScore}</div>
                      <div><span className="font-medium">On-Time Rate:</span> {selectedSupplier.onTimeRate}%</div>
                      <div><span className="font-medium">Severe Delay Rate:</span> {selectedSupplier.severeDelayRate}%</div>
                      <div><span className="font-medium">Distance Efficiency:</span> {selectedSupplier.distanceEfficiency}%</div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">Operational Data</h4>
                    <div className="space-y-2 text-sm">
                      <div><span className="font-medium">Avg Distance:</span> {selectedSupplier.avgDistance} km</div>
                      <div><span className="font-medium">Avg Weight:</span> {selectedSupplier.avgWeight} kg</div>
                      <div><span className="font-medium">Weather Resilience:</span> {selectedSupplier.weatherResilience}%</div>
                      <div><span className="font-medium">RL Time Saved:</span> {selectedSupplier.totalRLTimeSaved} hrs</div>
                    </div>
                  </div>
                </div>
                
                <div className="mt-6">
                  <h4 className="font-medium text-gray-900 mb-3">Delivery Analysis</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div><span className="font-medium">Avg Predicted Delay:</span> {selectedSupplier.avgPredictedDelay} min</div>
                    <div><span className="font-medium">Avg Actual Delay:</span> {selectedSupplier.avgActualDelay} min</div>
                    <div><span className="font-medium">High Traffic Deliveries:</span> {selectedSupplier.highTrafficDeliveries}</div>
                    <div><span className="font-medium">RL Optimization Rate:</span> {selectedSupplier.rlOptimizationRate}%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SupplierPerformance;