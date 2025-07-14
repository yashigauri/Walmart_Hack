import React, { useMemo } from 'react'
import { TrendingUp, Clock, MapPin } from 'lucide-react'

// Static data arrays moved outside component to avoid re-renders
const zones = ['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E']
const timeSlots = ['6AM-8AM', '8AM-10AM', '10AM-12PM', '12PM-2PM', '2PM-4PM', '4PM-6PM', '6PM-8PM', '8PM-10PM']

const ZoneTimeHeatmap = () => {
  
  // Generate consistent mock heatmap data (delivery intensity)
  const heatmapData = useMemo(() => {
    return zones.map((zone, zoneIndex) => 
      timeSlots.map((timeSlot, timeIndex) => {
        // Create more realistic patterns - higher during lunch and evening
        let baseIntensity = 30
        if (timeIndex >= 3 && timeIndex <= 4) baseIntensity = 70 // Lunch hours
        if (timeIndex >= 6 && timeIndex <= 7) baseIntensity = 80 // Evening hours
        if (zoneIndex === 2) baseIntensity += 20 // Zone C is busiest
        
        const variation = Math.floor(Math.random() * 30) - 15
        return Math.max(0, Math.min(100, baseIntensity + variation))
      })
    )
  }, [])
  
  const getColorClass = (intensity) => {
    if (intensity >= 80) return 'bg-gradient-to-br from-red-400 to-red-600 text-white shadow-lg'
    if (intensity >= 60) return 'bg-gradient-to-br from-orange-400 to-orange-500 text-white shadow-md'
    if (intensity >= 40) return 'bg-gradient-to-br from-yellow-300 to-yellow-400 text-gray-800 shadow-sm'
    if (intensity >= 20) return 'bg-gradient-to-br from-green-300 to-green-400 text-gray-800 shadow-sm'
    return 'bg-gradient-to-br from-blue-200 to-blue-300 text-gray-700 shadow-sm'
  }
  
  const getTextColor = (intensity) => {
    return intensity >= 60 ? 'text-white' : 'text-gray-800'
  }

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Zone-Time Heatmap</h1>
        <p className="text-lg text-gray-600">Real-time delivery intensity across zones and time slots</p>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm font-medium">Peak Hours</p>
              <p className="text-2xl font-bold">12PM-2PM & 6PM-8PM</p>
            </div>
            <Clock className="w-10 h-10 text-blue-200" />
          </div>
        </div>
        <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm font-medium">Busiest Zone</p>
              <p className="text-2xl font-bold">Zone C (Metro)</p>
            </div>
            <MapPin className="w-10 h-10 text-green-200" />
          </div>
        </div>
        <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm font-medium">Avg Daily Deliveries</p>
              <p className="text-2xl font-bold">1,247</p>
            </div>
            <TrendingUp className="w-10 h-10 text-purple-200" />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-8 py-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-3">Delivery Intensity Matrix</h2>
          
          {/* Legend */}
          <div className="flex flex-wrap items-center gap-4">
            <span className="text-sm font-medium text-gray-700 mr-2">Intensity Level:</span>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-gradient-to-br from-blue-200 to-blue-300 rounded-full shadow-sm"></div>
              <span className="text-xs text-gray-600 font-medium">Low (0-20)</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-gradient-to-br from-green-300 to-green-400 rounded-full shadow-sm"></div>
              <span className="text-xs text-gray-600 font-medium">Medium (20-40)</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-gradient-to-br from-yellow-300 to-yellow-400 rounded-full shadow-sm"></div>
              <span className="text-xs text-gray-600 font-medium">High (40-60)</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-gradient-to-br from-orange-400 to-orange-500 rounded-full shadow-sm"></div>
              <span className="text-xs text-gray-600 font-medium">Very High (60-80)</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-gradient-to-br from-red-400 to-red-600 rounded-full shadow-sm"></div>
              <span className="text-xs text-gray-600 font-medium">Critical (80-100)</span>
            </div>
          </div>
        </div>

        {/* Heatmap Grid */}
        <div className="p-8">
          <div className="overflow-x-auto">
            <div className="inline-block min-w-full">
              <div className="grid grid-cols-9 gap-3">
                {/* Header row */}
                <div className="p-4"></div>
                {timeSlots.map((time, index) => (
                  <div key={index} className="p-4 text-center">
                    <div className="text-xs font-bold text-gray-600 mb-1">TIME SLOT</div>
                    <div className="text-sm font-semibold text-gray-900">{time}</div>
                  </div>
                ))}
                
                {/* Data rows */}
                {zones.map((zone, zoneIndex) => (
                  <React.Fragment key={zoneIndex}>
                    <div className="p-4 flex items-center justify-center">
                      <div className="text-center">
                        <div className="text-xs font-bold text-gray-600 mb-1">ZONE</div>
                        <div className="text-lg font-bold text-gray-900">{zone}</div>
                      </div>
                    </div>
                    {timeSlots.map((_, timeIndex) => {
                      const intensity = heatmapData[zoneIndex][timeIndex]
                      return (
                        <div
                          key={timeIndex}
                          className={`relative w-20 h-16 rounded-xl ${getColorClass(intensity)} flex items-center justify-center cursor-pointer transform hover:scale-110 transition-all duration-200 hover:z-10 border border-white/20`}
                          title={`${zone} at ${timeSlots[timeIndex]}: ${intensity}% intensity`}
                        >
                          <div className="text-center">
                            <div className={`text-lg font-bold ${getTextColor(intensity)}`}>
                              {intensity}
                            </div>
                            <div className={`text-xs ${getTextColor(intensity)} opacity-75`}>
                              %
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </React.Fragment>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Additional Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Zone Performance Summary</h3>
          <div className="space-y-4">
            {zones.map((zone, index) => {
              const avgIntensity = Math.round(heatmapData[index].reduce((a, b) => a + b, 0) / timeSlots.length)
              return (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="font-medium text-gray-900">{zone}</span>
                  <div className="flex items-center space-x-3">
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-500" 
                        style={{ width: `${avgIntensity}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-semibold text-gray-700 w-8">{avgIntensity}%</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Time Slot Analysis</h3>
          <div className="space-y-4">
            {timeSlots.map((timeSlot, index) => {
              const avgIntensity = Math.round(heatmapData.reduce((sum, zone) => sum + zone[index], 0) / zones.length)
              return (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="font-medium text-gray-900 text-sm">{timeSlot}</span>
                  <div className="flex items-center space-x-3">
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-green-600 h-2 rounded-full transition-all duration-500" 
                        style={{ width: `${avgIntensity}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-semibold text-gray-700 w-8">{avgIntensity}%</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ZoneTimeHeatmap
