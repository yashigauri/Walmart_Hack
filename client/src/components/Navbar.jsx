import React from 'react'
import {
  User,
  Settings,
} from 'lucide-react'

const Navbar = ({ currentPage, onPageChange }) => {

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
          <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
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
    </header>
  )
}

export default Navbar
