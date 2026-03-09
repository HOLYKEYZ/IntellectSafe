import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  FileText, BarChart3, Menu, X, Shield, ClipboardList,
  ChevronLeft, ChevronRight, LogOut, ExternalLink, LayoutDashboard,
  ScanSearch, Settings, BookOpen, Code2
} from 'lucide-react'
import { cn } from '@/lib/utils'
import ThemeToggle from './ThemeToggle'

interface LayoutProps {
  children: React.ReactNode
}

interface NavSection {
  title: string
  items: NavItem[]
}

interface NavItem {
  path: string
  label: string
  icon: React.ElementType
  external?: boolean
}

const navSections: NavSection[] = [
  {
    title: 'Main',
    items: [
      { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    ],
  },
  {
    title: 'Tools',
    items: [
      { path: '/dashboard/deepfake', label: 'Deepfake Detector', icon: ScanSearch },
      { path: '/dashboard/agent', label: 'Agent Control', icon: Shield },
    ],
  },
  {
    title: 'Analytics',
    items: [
      { path: '/dashboard/audit/logs', label: 'Audit Logs', icon: ClipboardList },
      { path: '/dashboard/audit/risk-scores', label: 'Risk Scores', icon: BarChart3 },
      { path: '/dashboard/reports', label: 'Reports', icon: FileText },
    ],
  },
  {
    title: 'Other',
    items: [
      { path: '/docs', label: 'Docs', icon: BookOpen },
      {
        path: `${(import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1').replace('/api/v1', '')}/docs`,
        label: 'API Docs',
        icon: Code2,
        external: true,
      },
      { path: '/dashboard/settings', label: 'Settings', icon: Settings },
    ],
  },
]

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('sidebar_collapsed') === 'true'
    }
    return false
  })
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    localStorage.setItem('sidebar_collapsed', String(collapsed))
  }, [collapsed])

  // Close mobile sidebar on route change
  useEffect(() => {
    setMobileOpen(false)
  }, [location.pathname])

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    window.location.href = '/login'
  }

  const isActive = (path: string) => {
    if (path === '/dashboard') return location.pathname === '/dashboard'
    return location.pathname.startsWith(path)
  }

  const renderNavItem = (item: NavItem) => {
    const active = isActive(item.path)
    const Icon = item.icon

    const classes = cn(
      'group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200',
      active
        ? 'bg-primary/10 text-primary dark:bg-primary/20 dark:text-primary-foreground'
        : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
    )

    const content = (
      <>
        <Icon className={cn('h-[18px] w-[18px] shrink-0', active && 'text-primary dark:text-primary-foreground')} />
        <span className={cn(
          'truncate transition-all duration-200',
          collapsed && 'md:hidden'
        )}>
          {item.label}
        </span>
        {item.external && !collapsed && (
          <ExternalLink className="ml-auto h-3 w-3 opacity-50" />
        )}
        {/* Tooltip when collapsed */}
        {collapsed && (
          <span className="pointer-events-none absolute left-full ml-2 hidden rounded-md bg-popover px-2 py-1 text-xs text-popover-foreground shadow-md md:group-hover:block z-50 whitespace-nowrap border border-border">
            {item.label}
          </span>
        )}
      </>
    )

    if (item.external) {
      return (
        <a
          key={item.path}
          href={item.path}
          target="_blank"
          rel="noopener noreferrer"
          className={classes}
        >
          {content}
        </a>
      )
    }

    return (
      <Link key={item.path} to={item.path} className={classes}>
        {content}
      </Link>
    )
  }

  const sidebarContent = (
    <div className="flex h-full flex-col">
      {/* Sidebar Header */}
      <div className={cn(
        'flex items-center border-b border-border px-4 h-16 shrink-0',
        collapsed ? 'md:justify-center' : 'gap-3'
      )}>
        <div className="w-8 h-8 flex items-center justify-center shrink-0">
          <img src="/logo.png" alt="IntellectSafe" className="w-full h-full object-contain filter brightness-0 dark:invert" />
        </div>
        <span className={cn(
          'text-lg font-bold truncate transition-all duration-200',
          collapsed && 'md:hidden'
        )}>
          IntellectSafe
        </span>
        {/* Mobile close button */}
        <button
          className="ml-auto p-1 rounded-md hover:bg-accent md:hidden"
          onClick={() => setMobileOpen(false)}
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* Nav Sections */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {navSections.map((section) => (
          <div key={section.title}>
            {!collapsed && (
              <p className="mb-2 px-3 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground/60">
                {section.title}
              </p>
            )}
            {collapsed && (
              <div className="hidden md:block mb-2 mx-auto w-6 border-t border-border" />
            )}
            <div className="space-y-1">
              {section.items.map(renderNavItem)}
            </div>
          </div>
        ))}
      </nav>

      {/* Sidebar Footer */}
      <div className="shrink-0 border-t border-border p-3 space-y-1">
        <button
          onClick={handleLogout}
          className={cn(
            'flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-red-500 transition-all duration-200 hover:bg-red-500/10',
            collapsed && 'md:justify-center'
          )}
        >
          <LogOut className="h-[18px] w-[18px] shrink-0" />
          <span className={cn('truncate', collapsed && 'md:hidden')}>Logout</span>
        </button>

        {/* Collapse Toggle (desktop only) */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="hidden md:flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground transition-all duration-200 hover:bg-accent hover:text-accent-foreground justify-center"
        >
          {collapsed ? (
            <ChevronRight className="h-[18px] w-[18px]" />
          ) : (
            <>
              <ChevronLeft className="h-[18px] w-[18px]" />
              <span>Collapse</span>
            </>
          )}
        </button>
      </div>
    </div>
  )

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex flex-col border-r border-border bg-card transition-all duration-300 ease-in-out',
          // Mobile: slide in/out
          mobileOpen ? 'translate-x-0' : '-translate-x-full',
          'w-[260px]',
          // Desktop: always visible, width changes
          'md:relative md:translate-x-0',
          collapsed ? 'md:w-[68px]' : 'md:w-[260px]'
        )}
      >
        {sidebarContent}
      </aside>

      {/* Main Content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="flex h-16 shrink-0 items-center justify-between border-b border-border bg-card px-4 md:px-6">
          {/* Mobile hamburger */}
          <button
            className="p-2 rounded-md hover:bg-accent md:hidden"
            onClick={() => setMobileOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </button>

          {/* Page context / breadcrumb area */}
          <div className="hidden md:block" />

          {/* Right actions */}
          <div className="flex items-center gap-2 ml-auto">
            <ThemeToggle />
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          {children}
        </main>
      </div>
    </div>
  )
}
