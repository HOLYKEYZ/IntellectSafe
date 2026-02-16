import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import ScanPrompt from './pages/ScanPrompt'
import ScanOutput from './pages/ScanOutput'
import AuditLogs from './pages/AuditLogs'
import RiskScores from './pages/RiskScores'
import Reports from './pages/Reports'
import DeepfakeScan from './pages/DeepfakeScan'
import Settings from './pages/Settings'
import AgentControl from './pages/AgentControl'
import Welcome from './pages/Welcome'
import Docs from './pages/Docs'
import Login from './pages/Login'
import Signup from './pages/Signup'



function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Welcome />} />
        <Route path="/docs" element={<Docs />} />
        <Route path="/login" element={<Login />} />

        <Route path="/signup" element={<Signup />} />

        {/* Protected Dashboard Routes */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard/*" element={
            <Layout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/scan/prompt" element={<ScanPrompt />} />
                <Route path="/scan/output" element={<ScanOutput />} />
                <Route path="/deepfake" element={<DeepfakeScan />} />
                <Route path="/audit/logs" element={<AuditLogs />} />
                <Route path="/audit/risk-scores" element={<RiskScores />} />
                <Route path="/reports" element={<Reports />} />
                <Route path="/agent" element={<AgentControl />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </Layout>
          } />
        </Route>
      </Routes>
    </Router>
  )
}

export default App

