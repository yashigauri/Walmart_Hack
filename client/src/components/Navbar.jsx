import React from 'react'
import { useState } from 'react'
import {
  User,
  Settings,
} from 'lucide-react'

const Navbar = ({ currentPage, onPageChange }) => {
  const [showSettings, setShowSettings] = useState(false)

  const navigation = [
    { id: 'cost-analysis', label: 'Cost Analysis' },
    { id: 'prediction', label: 'Prediction & Rerouting' },
    { id: 'supplier', label: 'Supplier Score Engine' },
    { id: 'heatmap', label: 'Zone-Time Heatmap' }
  ]


  return (
    <header className="bg-white/90 backdrop-blur-sm border-b border-gray-200/50 px-6 py-4 shadow-sm">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        {/* Logo + Title */}
        <div className="flex items-center space-x-3">
          <div className="relative">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl transform rotate-45 shadow-lg"></div>
            <div className="absolute inset-0 w-10 h-10 bg-gradient-to-r from-blue-400 to-purple-400 rounded-xl transform rotate-45 opacity-50 blur-sm"></div>
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
              Delivery Intelligence
            </h1>
            <p className="text-xs text-gray-500 -mt-1">
              Smart Logistics Platform
            </p>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center space-x-1">
          {navigation.map((item) => {
            return (
              <button
                key={item.id}
                onClick={() => onPageChange(item.id)}
                className={`flex items-center space-x-2 px-4 py-2 text-sm font-medium rounded-xl transition-all duration-200 ${
                  currentPage === item.id
                    ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg shadow-blue-500/25'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100/80'
                }`}
              >
                <span className="hidden sm:inline">{item.label}</span>
              </button>
            )
          })}
        </div>

        {/* Right-side icons */}
        <div className="flex items-center space-x-4">

          {/* Settings */}
          <button 
            onClick={() => setShowSettings(true)}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Settings className="w-5 h-5" />
          </button>

          {/* User Profile */}
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center shadow-lg">
              <User className="w-5 h-5 text-white" />
            </div>
            <div className="hidden md:block">
              <p className="text-sm font-medium text-gray-900">Admin User</p>
              <p className="text-xs text-gray-500">admin@delivery.com</p>
            </div>
          </div>
        </div>
      </div>

      {/* Settings Modal */}
      {showSettings && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-900">Settings</h3>
                <button 
                  onClick={() => setShowSettings(false)}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Application Settings</h4>
                  <div className="space-y-3">
                    <label className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">Dark Mode</span>
                      <input type="checkbox" className="rounded" />
                    </label>
                    <label className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">Notifications</span>
                      <input type="checkbox" className="rounded" defaultChecked />
                    </label>
                    <label className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">Auto-refresh Data</span>
                      <input type="checkbox" className="rounded" defaultChecked />
                    </label>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Data Preferences</h4>
                  <div className="space-y-3">
                    <label className="block">
                      <span className="text-sm text-gray-700">Refresh Interval</span>
                      <select className="mt-1 block w-full rounded-md border-gray-300 text-sm">
                        <option>30 seconds</option>
                        <option>1 minute</option>
                        <option>5 minutes</option>
                        <option>10 minutes</option>
                      </select>
                    </label>
                  </div>
                </div>
              </div>
              
              <div className="mt-6 flex justify-end space-x-3">
                <button 
                  onClick={() => setShowSettings(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Cancel
                </button>
                <button 
                  onClick={() => setShowSettings(false)}
                  className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </header>
  )
}

export default Navbar
