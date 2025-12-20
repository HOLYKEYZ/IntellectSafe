import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import ScanPrompt from './pages/ScanPrompt'
import ScanOutput from './pages/ScanOutput'
import AuditLogs from './pages/AuditLogs'
import RiskScores from './pages/RiskScores'
import Reports from './pages/Reports'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/scan/prompt" element={<ScanPrompt />} />
          <Route path="/scan/output" element={<ScanOutput />} />
          <Route path="/audit/logs" element={<AuditLogs />} />
          <Route path="/audit/risk-scores" element={<RiskScores />} />
          <Route path="/reports" element={<Reports />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App

