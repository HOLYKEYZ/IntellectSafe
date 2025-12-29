import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import ScanPrompt from './pages/ScanPrompt'
import ScanOutput from './pages/ScanOutput'
import AuditLogs from './pages/AuditLogs'
import RiskScores from './pages/RiskScores'
import Reports from './pages/Reports'
import Welcome from './pages/Welcome'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Research from './pages/Research'
import Docs from './pages/Docs'

function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Welcome />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/research" element={<Research />} />
        <Route path="/docs" element={<Docs />} />

        {/* Protected Dashboard Routes */}
        <Route path="/dashboard/*" element={
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
        } />
      </Routes>
    </Router>
  )
}

export default App

