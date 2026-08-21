import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar.jsx'
import { ProcurementProvider } from './context/ProcurementContext.jsx'

import Dashboard from './pages/Dashboard.jsx'
import CreateRFQ from './pages/CreateRFQ.jsx'
import QuoteComparison from './pages/QuoteComparison.jsx'
import AIAnalysis from './pages/AIAnalysis.jsx'
import PurchaseOrder from './pages/PurchaseOrder.jsx'
import Vendors from './pages/Vendors.jsx'
import RFQList from './pages/RFQList.jsx'

export default function App() {
  return (
    <ProcurementProvider>
      <div className="flex min-h-screen bg-slate-50">
        <Sidebar />
        <main className="flex-1 min-w-0 px-5 py-6 md:px-10 md:py-8 max-w-[1400px]">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/rfqs" element={<RFQList />} />
            <Route path="/rfqs/new" element={<CreateRFQ />} />
            <Route path="/quotes" element={<QuoteComparison />} />
            <Route path="/ai-analysis" element={<AIAnalysis />} />
            <Route path="/vendors" element={<Vendors />} />
            <Route path="/purchase-orders" element={<PurchaseOrder />} />
            <Route path="*" element={<Dashboard />} />
          </Routes>
        </main>
      </div>
    </ProcurementProvider>
  )
}
