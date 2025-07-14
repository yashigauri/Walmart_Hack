import React from 'react'
import { useState } from 'react'
import CostAnalysis from './components/CostAnalysis'
import DeliveryPrediction from './components/DeliveryPrediction'
import SupplierPerformance from './components/SupplierPerformance'
import ZoneTimeHeatmap from './components/ZoneTimeHeatmap'
import Navbar from './components/Navbar'
import ErrorBoundary from './components/ErrorBoundary'

function App() {
  const [currentPage, setCurrentPage] = useState('cost-analysis')

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

  const handleNavigateHome = () => {
    setCurrentPage('cost-analysis')
  }

  return (
    <ErrorBoundary onNavigateHome={handleNavigateHome}>
      <div className="min-h-screen bg-gray-50">
        <Navbar currentPage={currentPage} onPageChange={setCurrentPage} />
        <main className="p-6">
          <ErrorBoundary>
            {renderPage()}
          </ErrorBoundary>
        </main>
      </div>
    </ErrorBoundary>
  )
}

export default App
