import React, { useState } from 'react'
import CostAnalysis from './components/CostAnalysis'
import DeliveryPrediction from './components/DeliveryPrediction'
import SupplierPerformance from './components/SupplierPerformance'
import ZoneTimeHeatmap from './components/ZoneTimeHeatmap'
import Navbar from './components/Navbar' // use correct name

function App() {
  const [currentPage, setCurrentPage] = useState('prediction')

  const renderPage = () => {
    switch (currentPage) {
      case 'cost-analysis':
        return <CostAnalysis />
      case 'prediction':
        return <DeliveryPrediction />
      case 'supplier':
        return <SupplierPerformance />
      case 'heatmap':
        return <ZoneTimeHeatmap />
      default:
        return <CostAnalysis />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar currentPage={currentPage} onPageChange={setCurrentPage} />
      <main className="p-6">{renderPage()}</main>
    </div>
  )
}

export default App
