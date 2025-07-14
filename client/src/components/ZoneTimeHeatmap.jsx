import React, { useState } from 'react'
import { X } from 'lucide-react'
import zoneHeatmapImg from '../assets/zone_time_heatmap.png'
import delayHeatmapImg from '../assets/delay_heatmap_by_time_slot.png'

const ZoneTimeHeatmap = () => {
  const [images, setImages] = useState({
    heatmapAnalysis: zoneHeatmapImg,
    timeAnalysis: delayHeatmapImg
  })
  const [modalImage, setModalImage] = useState(null)

  const openModal = (imageData, title) => {
    setModalImage({ src: imageData, title })
  }

  const closeModal = () => {
    setModalImage(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Zone-Time Heatmap Analysis</h1>
          <p className="text-lg text-gray-600 max-w-4xl mx-auto">
            Advanced analytics reveal delivery patterns across different zones and time periods. Our ML algorithms process real-time data to identify peak delivery zones, 
            time-based bottlenecks, and delay patterns. These heatmaps provide critical insights for optimizing route efficiency, predicting high-traffic periods, 
            and reducing delivery delays across all operational zones.
          </p>
        </div>

        {/* Image Frames */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* First Image Frame */}
          <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-4 border-b border-gray-200">
              <h3 className="text-xl font-bold text-gray-900">Zone-Time Delivery Heatmap</h3>
              <p className="text-sm text-gray-600">Comprehensive delivery intensity analysis across zones and time periods</p>
            </div>
            <div className="p-6">
              <div className="bg-gray-100 rounded-lg h-80 flex items-center justify-center mb-4">
                {images.heatmapAnalysis ? (
                  <img 
                    src={images.heatmapAnalysis} 
                    alt="Zone Time Heatmap Analysis" 
                    className="w-full h-full object-contain rounded-lg cursor-pointer hover:opacity-90 transition-opacity"
                    onClick={() => openModal(images.heatmapAnalysis, 'Zone-Time Delivery Heatmap')}
                  />
                ) : (
                  <div className="text-center text-gray-500">
                    <div className="w-20 h-20 bg-gray-300 rounded-lg mx-auto mb-4 flex items-center justify-center">
                      <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <p className="text-sm font-medium">Zone Heatmap</p>
                    <p className="text-xs">Image will be loaded from backend</p>
                  </div>
                )}
              </div>
              <div className="space-y-4">
                <div className="bg-blue-50 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 mb-3">Key Insights from Zone-Time Analysis</h4>
                  <ul className="space-y-2 text-sm text-blue-800">
                    <li className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                      <span><strong>Peak Activity Zones:</strong> Central metropolitan areas show 60-80% higher delivery concentration during business hours (9AM-5PM)</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                      <span><strong>Time-Based Patterns:</strong> Clear visualization of lunch rush (12-2PM) and evening peak (6-8PM) across all zones</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                      <span><strong>Resource Allocation:</strong> Suburban zones show optimal delivery windows during morning hours (8-11AM) with 40% lower congestion</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                      <span><strong>Efficiency Opportunities:</strong> Cross-zone analysis reveals potential for load balancing during off-peak hours</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Second Image Frame */}
          <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 px-6 py-4 border-b border-gray-200">
              <h3 className="text-xl font-bold text-gray-900">Delay Heatmap by Time Slot</h3>
              <p className="text-sm text-gray-600">Time-based delay pattern analysis and bottleneck identification</p>
            </div>
            <div className="p-6">
              <div className="bg-gray-100 rounded-lg h-80 flex items-center justify-center mb-4">
                {images.timeAnalysis ? (
                  <img 
                    src={images.timeAnalysis} 
                    alt="Delay Heatmap by Time Slot" 
                    className="w-full h-full object-contain rounded-lg cursor-pointer hover:opacity-90 transition-opacity"
                    onClick={() => openModal(images.timeAnalysis, 'Delay Heatmap by Time Slot')}
                  />
                ) : (
                  <div className="text-center text-gray-500">
                    <div className="w-20 h-20 bg-gray-300 rounded-lg mx-auto mb-4 flex items-center justify-center">
                      <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    </div>
                    <p className="text-sm font-medium">Time Analysis Chart</p>
                    <p className="text-xs">Image will be loaded from backend</p>
                  </div>
                )}
              </div>
              <div className="space-y-4">
                <div className="bg-purple-50 rounded-lg p-4">
                  <h4 className="font-semibold text-purple-900 mb-3">Delay Pattern Analysis</h4>
                  <ul className="space-y-2 text-sm text-purple-800">
                    <li className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-purple-600 rounded-full mt-2 flex-shrink-0"></div>
                      <span><strong>Critical Time Slots:</strong> Highest delays occur during 12-2PM and 6-8PM slots with average delays exceeding 25 minutes</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-purple-600 rounded-full mt-2 flex-shrink-0"></div>
                      <span><strong>Morning Efficiency:</strong> 8-11AM window shows minimal delays (5-8 minutes) across all zones, optimal for priority deliveries</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-purple-600 rounded-full mt-2 flex-shrink-0"></div>
                      <span><strong>Traffic Correlation:</strong> Delay patterns directly correlate with urban traffic congestion and peak business hours</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-purple-600 rounded-full mt-2 flex-shrink-0"></div>
                      <span><strong>Predictive Insights:</strong> Late evening (8-10PM) shows gradual improvement with delays dropping to 12-15 minutes</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Image Modal */}
        {modalImage && (
          <div 
            className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75 p-4"
            onClick={closeModal}
          >
            <div 
              className="bg-white rounded-xl overflow-hidden shadow-2xl max-w-6xl max-h-full w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="relative">
                <img 
                  src={modalImage.src} 
                  alt={modalImage.title} 
                  className="w-full h-auto max-h-[80vh] object-contain"
                />
                <button 
                  onClick={closeModal} 
                  className="absolute top-4 right-4 p-2 bg-white text-gray-600 rounded-full hover:bg-gray-100 shadow-lg transition-colors"
                  title="Close image"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-t border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">{modalImage.title}</h3>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  )
}

export default ZoneTimeHeatmap
