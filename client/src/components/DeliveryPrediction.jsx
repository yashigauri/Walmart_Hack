import React from 'react'
import { useState } from 'react'
import { ChevronDown, Package, Clock, MapPin, Cloud, Weight, Route, Truck } from 'lucide-react'

const DeliveryPrediction = () => {
  const [formData, setFormData] = useState({
    fromZone: '',
    toZone: '',
    timeSlot: '',
    trafficLevel: '',
    weatherConditions: '',
    weight: '',
    distance: ''
  })

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handlePredict = () => {
    // Handle prediction logic here
    alert('Prediction submitted!')
  }

  const isFormValid = Object.values(formData).every(value => value !== '')

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header Section */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl mb-6">
            <Truck className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent mb-4">
            Delivery Delay Predictor
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Get accurate delivery time predictions based on real-time factors and historical data
          </p>
        </div>
        
        {/* Main Form Card */}
        <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-xl border border-white/20 p-8 lg:p-12">
          <div className="flex items-center gap-3 mb-8">
            <Package className="w-6 h-6 text-blue-600" />
            <h2 className="text-2xl font-semibold text-gray-900">Delivery Parameters</h2>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8">
            {/* From Zone */}
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
                <MapPin className="w-4 h-4 text-blue-500" />
                From Zone
              </label>
              <div className="relative">
                <select 
                  className="w-full px-4 py-4 border border-gray-200 rounded-xl bg-white/90 text-gray-900 appearance-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-300"
                  value={formData.fromZone}
                  onChange={(e) => handleInputChange('fromZone', e.target.value)}
                >
                  <option value="">Select Origin Zone</option>
                  <option value="zone-a">Zone A - Central Business District</option>
                  <option value="zone-b">Zone B - Residential North</option>
                  <option value="zone-c">Zone C - Industrial South</option>
                  <option value="zone-d">Zone D - Suburban East</option>
                </select>
                <ChevronDown className="absolute right-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              </div>
            </div>

            {/* To Zone */}
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
                <MapPin className="w-4 h-4 text-green-500" />
                To Zone
              </label>
              <div className="relative">
                <select 
                  className="w-full px-4 py-4 border border-gray-200 rounded-xl bg-white/90 text-gray-900 appearance-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-300"
                  value={formData.toZone}
                  onChange={(e) => handleInputChange('toZone', e.target.value)}
                >
                  <option value="">Select Destination Zone</option>
                  <option value="zone-a">Zone A - Central Business District</option>
                  <option value="zone-b">Zone B - Residential North</option>
                  <option value="zone-c">Zone C - Industrial South</option>
                  <option value="zone-d">Zone D - Suburban East</option>
                </select>
                <ChevronDown className="absolute right-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              </div>
            </div>

            {/* Time Slot */}
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
                <Clock className="w-4 h-4 text-purple-500" />
                Delivery Time Slot
              </label>
              <div className="relative">
                <select 
                  className="w-full px-4 py-4 border border-gray-200 rounded-xl bg-white/90 text-gray-900 appearance-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-300"
                  value={formData.timeSlot}
                  onChange={(e) => handleInputChange('timeSlot', e.target.value)}
                >
                  <option value="">Select Time Slot</option>
                  <option value="morning">🌅 Morning (6AM - 12PM)</option>
                  <option value="afternoon">☀️ Afternoon (12PM - 6PM)</option>
                  <option value="evening">🌆 Evening (6PM - 10PM)</option>
                </select>
                <ChevronDown className="absolute right-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              </div>
            </div>

            {/* Traffic Level */}
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
                <Route className="w-4 h-4 text-orange-500" />
                Traffic Level
              </label>
              <div className="relative">
                <select 
                  className="w-full px-4 py-4 border border-gray-200 rounded-xl bg-white/90 text-gray-900 appearance-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-300"
                  value={formData.trafficLevel}
                  onChange={(e) => handleInputChange('trafficLevel', e.target.value)}
                >
                  <option value="">Select Traffic Level</option>
                  <option value="low">🟢 Low - Smooth traffic</option>
                  <option value="medium">🟡 Medium - Moderate traffic</option>
                  <option value="high">🟠 High - Heavy traffic</option>
                  <option value="very-high">🔴 Very High - Congested</option>
                </select>
                <ChevronDown className="absolute right-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              </div>
            </div>

            {/* Weather Conditions */}
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
                <Cloud className="w-4 h-4 text-blue-500" />
                Weather Conditions
              </label>
              <div className="relative">
                <select 
                  className="w-full px-4 py-4 border border-gray-200 rounded-xl bg-white/90 text-gray-900 appearance-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-300"
                  value={formData.weatherConditions}
                  onChange={(e) => handleInputChange('weatherConditions', e.target.value)}
                >
                  <option value="">Select Weather Conditions</option>
                  <option value="clear">☀️ Clear - Perfect conditions</option>
                  <option value="rain">🌧️ Rain - Wet roads</option>
                  <option value="snow">❄️ Snow - Icy conditions</option>
                  <option value="fog">🌫️ Fog - Limited visibility</option>
                  <option value="storm">⛈️ Storm - Severe weather</option>
                </select>
                <ChevronDown className="absolute right-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              </div>
            </div>

            {/* Weight */}
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
                <Weight className="w-4 h-4 text-red-500" />
                Package Weight
              </label>
              <div className="relative">
                <input
                  type="text"
                  placeholder="Enter weight in kg"
                  className="w-full px-4 py-4 border border-gray-200 rounded-xl bg-white/90 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-300"
                  value={formData.weight}
                  onChange={(e) => handleInputChange('weight', e.target.value)}
                />
                <div className="absolute right-4 top-1/2 transform -translate-y-1/2 text-sm text-gray-400">
                  kg
                </div>
              </div>
            </div>

            {/* Distance */}
            <div className="space-y-2 md:col-span-2">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
                <Route className="w-4 h-4 text-indigo-500" />
                Delivery Distance
              </label>
              <div className="relative max-w-md">
                <input
                  type="text"
                  placeholder="Enter distance in km"
                  className="w-full px-4 py-4 border border-gray-200 rounded-xl bg-white/90 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-300"
                  value={formData.distance}
                  onChange={(e) => handleInputChange('distance', e.target.value)}
                />
                <div className="absolute right-4 top-1/2 transform -translate-y-1/2 text-sm text-gray-400">
                  km
                </div>
              </div>
            </div>
          </div>

          {/* Predict Button */}
          <div className="mt-12 text-center">
            <button
              onClick={handlePredict}
              disabled={!isFormValid}
              className={`
                px-12 py-4 rounded-2xl font-semibold text-lg transition-all duration-200 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
                ${isFormValid 
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl' 
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }
              `}
            >
              {isFormValid ? (
                <span className="flex items-center gap-2">
                  <Package className="w-5 h-5" />
                  Predict Delivery Time
                </span>
              ) : (
                'Fill all fields to predict'
              )}
            </button>
          </div>
        </div>

        {/* Additional Info Cards */}
        <div className="grid md:grid-cols-3 gap-6 mt-8">
          <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-6 text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-xl mx-auto mb-4 flex items-center justify-center">
              <Clock className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Real-time Analysis</h3>
            <p className="text-sm text-gray-600">AI-powered predictions based on current conditions</p>
          </div>
          
          <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-6 text-center">
            <div className="w-12 h-12 bg-green-100 rounded-xl mx-auto mb-4 flex items-center justify-center">
              <Route className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Route Optimization</h3>
            <p className="text-sm text-gray-600">Smart routing to minimize delivery delays</p>
          </div>
          
          <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-6 text-center">
            <div className="w-12 h-12 bg-purple-100 rounded-xl mx-auto mb-4 flex items-center justify-center">
              <Package className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Accurate Predictions</h3>
            <p className="text-sm text-gray-600">95% accuracy rate for delivery time estimates</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DeliveryPrediction