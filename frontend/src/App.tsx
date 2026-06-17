import type { ReactNode } from 'react'
import { BrowserRouter, Route, Routes, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store'
import { Layout } from '@/components/layout/Layout'
import { ToastContainer } from '@/components/ui/Toast'
import LoginPage from '@/pages/Login'
import BatchListPage from '@/pages/livestock/BatchListPage'
import NewBatchPage from '@/pages/livestock/NewBatchPage'
import BatchDetailPage from '@/pages/livestock/BatchDetailPage'
import FarmListPage from '@/pages/farms/FarmListPage'
import FarmDetailPage from '@/pages/farms/FarmDetailPage'
import InventoryPage from '@/pages/inventory/InventoryPage'
import BatchReportPage from '@/pages/reports/BatchReportPage'
import DashboardPage from '@/pages/dashboard/DashboardPage'
import FinancePage from '@/pages/finance/FinancePage'
import ReportsPage from '@/pages/reports/ReportsPage'

const NotFoundPage = () => <div className="p-6 text-gray-600">404 — Sahifa topilmadi</div>

function ProtectedRoute({ children }: { children: ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

function AppLayout({ children }: { children: ReactNode }) {
  return (
    <ProtectedRoute>
      <Layout>{children}</Layout>
    </ProtectedRoute>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <ToastContainer />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/"               element={<AppLayout><DashboardPage /></AppLayout>} />
        <Route path="/farms"          element={<AppLayout><FarmListPage /></AppLayout>} />
        <Route path="/farms/:id"      element={<AppLayout><FarmDetailPage /></AppLayout>} />
        <Route path="/livestock"      element={<AppLayout><BatchListPage /></AppLayout>} />
        <Route path="/livestock/new"  element={<AppLayout><NewBatchPage /></AppLayout>} />
        <Route path="/livestock/:id"  element={<AppLayout><BatchDetailPage /></AppLayout>} />
        <Route path="/inventory"          element={<AppLayout><InventoryPage /></AppLayout>} />
        <Route path="/finance"            element={<AppLayout><FinancePage /></AppLayout>} />
        <Route path="/reports"            element={<AppLayout><ReportsPage /></AppLayout>} />
        <Route path="/reports/batch/:id"  element={<AppLayout><BatchReportPage /></AppLayout>} />
        <Route path="*"               element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  )
}
