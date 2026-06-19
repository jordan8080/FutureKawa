import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { Dashboard } from './pages/Dashboard'
import { CountryPage } from './pages/CountryPage'
import { LotDetailPage } from './pages/LotDetailPage'
import { AlertsPage } from './pages/AlertsPage'

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/pays/:countryId" element={<CountryPage />} />
          <Route path="/lots/:lotId" element={<LotDetailPage />} />
          <Route path="/alertes" element={<AlertsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
