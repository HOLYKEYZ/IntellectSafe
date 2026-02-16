import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Scan, FileText, BarChart3, Home, Menu, X, Shield, ClipboardList } from 'lucide-react'
import { cn } from '@/lib/utils'
import ThemeToggle from './ThemeToggle'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  const navItems = [
    { path: '/', label: 'Home', icon: Home },
    { path: '/dashboard', label: 'Dashboard', icon: Menu },
    { path: '/dashboard/scan/prompt', label: 'Scan Prompt', icon: Scan },
    { path: '/dashboard/scan/output', label: 'Scan Output', icon: Scan },
    { path: '/dashboard/deepfake', label: 'Deepfake Detector', icon: FileText },
    { path: '/dashboard/agent', label: 'Agent Control', icon: Shield },
    { path: '/dashboard/audit/logs', label: 'Audit Logs', icon: ClipboardList },
    { path: '/dashboard/audit/risk-scores', label: 'Risk Scores', icon: BarChart3 },
    { path: '/dashboard/reports', label: 'Reports', icon: BarChart3 },
    { path: '/docs', label: 'Docs', icon: FileText },
    { path: `${(import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1').replace('/api/v1', '')}/docs`, label: 'API Docs', icon: BarChart3, external: true },
    { path: '/dashboard/settings', label: 'Settings', icon: Menu },
  ]


  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    window.location.href = '/login';
  };

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b bg-card">
        <div className="container mx-auto px-4">
          <div className="flex h-16 items-center justify-between">
            {/* Logo */}
             <div className="flex items-center space-x-2">
              <div className="w-8 h-8 flex items-center justify-center">
                 <img src="/logo.png" alt="IntellectSafe Logo" className="w-full h-full object-contain filter brightness-0 dark:invert" />
              </div>
              <span className="text-xl font-bold">IntellectSafe</span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex space-x-1 items-center">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.path
                const linkClasses = cn(
                  "flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                )
                if (item.external) {
                  return (
                    <a key={item.path} href={item.path} target="_blank" rel="noopener noreferrer" className={linkClasses}>
                      <Icon className="h-4 w-4" />
                      <span>{item.label}</span>
                    </a>
                  )
                }
                return (
                  <Link key={item.path} to={item.path} className={linkClasses}>
                    <Icon className="h-4 w-4" />
                    <span>{item.label}</span>
                  </Link>
                )
              })}

              <div className="ml-4 flex items-center space-x-2">
                <ThemeToggle />
                <button 
                  onClick={handleLogout}
                  className="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium text-red-500 hover:bg-red-50 transition-colors"
                >
                  <span>Logout</span>
                </button>
              </div>
            </div>

            {/* Mobile Menu Toggle */}
            <button 
              className="md:hidden p-2 text-muted-foreground hover:bg-accent rounded-md"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t p-4 space-y-2 bg-card">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              const linkClasses = cn(
                "flex items-center space-x-3 px-4 py-3 rounded-md text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )
              if (item.external) {
                return (
                  <a key={item.path} href={item.path} target="_blank" rel="noopener noreferrer" onClick={() => setIsMobileMenuOpen(false)} className={linkClasses}>
                    <Icon className="h-5 w-5" />
                    <span>{item.label}</span>
                  </a>
                )
              }
              return (
                <Link key={item.path} to={item.path} onClick={() => setIsMobileMenuOpen(false)} className={linkClasses}>
                  <Icon className="h-5 w-5" />
                  <span>{item.label}</span>
                </Link>
              )
            })}

          </div>
        )}
      </nav>
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  )
}

