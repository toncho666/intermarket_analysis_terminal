import { NavLink, Outlet } from 'react-router-dom';
import { useTheme } from '../stores/theme';
import {
  LayoutDashboard, GitBranch, Link2, AlertTriangle,
  TrendingUp, Bell, FileText, Sun, Moon, Activity
} from 'lucide-react';
import AssetTicker from './AssetTicker';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/correlations', icon: GitBranch, label: 'Correlations' },
  { to: '/pair/SPX/US10Y', icon: Link2, label: 'Pair Analysis' },
  { to: '/anomalies', icon: AlertTriangle, label: 'Anomalies' },
  { to: '/strategies', icon: TrendingUp, label: 'Strategies' },
  { to: '/alerts', icon: Bell, label: 'Alerts' },
  { to: '/reports', icon: FileText, label: 'Reports' },
];

export default function Layout() {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className={`flex h-screen ${theme === 'dark' ? 'bg-surface-1 text-gray-100' : 'bg-gray-50 text-gray-900'}`}>
      {/* Sidebar */}
      <aside className={`w-64 flex flex-col border-r ${theme === 'dark' ? 'bg-surface-2 border-surface-4' : 'bg-white border-gray-200'}`}>
        {/* Logo */}
        <div className="p-6 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-blue to-accent-purple flex items-center justify-center">
            <Activity className="w-4 h-4 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-semibold tracking-tight">Intermarket</h1>
            <p className={`text-xs ${theme === 'dark' ? 'text-gray-500' : 'text-gray-400'}`}>Analysis Terminal</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 space-y-1">
          {navItems.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? theme === 'dark'
                      ? 'bg-surface-4 text-white'
                      : 'bg-gray-100 text-gray-900'
                    : theme === 'dark'
                      ? 'text-gray-400 hover:text-gray-200 hover:bg-surface-3'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`
              }
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className={`p-4 border-t ${theme === 'dark' ? 'border-surface-4' : 'border-gray-200'}`}>
          <button
            onClick={toggleTheme}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm w-full transition-colors ${
              theme === 'dark' ? 'text-gray-400 hover:bg-surface-3' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
          </button>
          <div className={`mt-3 px-3 text-xs ${theme === 'dark' ? 'text-gray-600' : 'text-gray-400'}`}>
            <p>analyst@demo.local</p>
            <p className="mt-0.5">Model v2.4.1 • As of 2024-12-20</p>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <AssetTicker />
        <div className="flex-1 overflow-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
