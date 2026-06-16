import type { ReactNode } from 'react'
import { BrowserRouter, Route, Routes, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store'

// Pages will be implemented by feature agents
// Stubs ensure the routing skeleton compiles
const LoginPage = () => <div>Login page — to be implemented</div>
const DashboardPage = () => <div>Dashboard — to be implemented</div>
const FarmsPage = () => <div>Farms — to be implemented</div>
const LivestockPage = () => <div>Livestock — to be implemented</div>
const InventoryPage = () => <div>Inventory — to be implemented</div>
const FinancePage = () => <div>Finance — to be implemented</div>
const ReportsPage = () => <div>Reports — to be implemented</div>
const NotFoundPage = () => <div>404 — Page not found</div>

function ProtectedRoute({ children }: { children: ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/farms"
          element={
            <ProtectedRoute>
              <FarmsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/livestock"
          element={
            <ProtectedRoute>
              <LivestockPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/inventory"
          element={
            <ProtectedRoute>
              <InventoryPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/finance"
          element={
            <ProtectedRoute>
              <FinancePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/reports"
          element={
            <ProtectedRoute>
              <ReportsPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  )
}
