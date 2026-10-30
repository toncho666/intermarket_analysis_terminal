import { useState } from 'react';
import { useTheme } from '../stores/theme';
import { alerts } from '../data/marketData';
import { Bell, BellOff, Plus, ToggleLeft, ToggleRight } from 'lucide-react';

export default function AlertsPage() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const [alertList, setAlertList] = useState(alerts);
  const [showCreate, setShowCreate] = useState(false);
  
  const toggleAlert = (id: string) => {
    setAlertList(prev => prev.map(a => a.id === id ? { ...a, isActive: !a.isActive } : a));
  };
  
  const deleteAlert = (id: string) => {
    setAlertList(prev => prev.filter(a => a.id !== id));
  };

  return (
    <div className="p-6 space-y-6 max-w-[1920px] mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className={`text-2xl font-semibold tracking-tight ${isDark ? 'text-white' : 'text-gray-900'}`}>
            Alerts
          </h1>
          <p className={`text-sm mt-1 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
            Monitor correlation breaks, regime changes, and anomalies
          </p>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-lg bg-accent-blue text-white hover:bg-accent-blue/90 transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Alert
        </button>
      </div>
      
      {/* Create Alert */}
      {showCreate && (
        <div className={`rounded-2xl p-6 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
          <h3 className={`text-sm font-medium mb-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>Create Alert</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <label className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Condition Type</label>
              <select className={`w-full mt-1 px-3 py-2 text-sm rounded-lg ${isDark ? 'bg-surface-4 text-gray-200 border-surface-5' : 'bg-gray-100 text-gray-800 border-gray-200'} border`}>
                <option>Correlation Break</option>
                <option>Cointegration Break</option>
                <option>Divergence</option>
                <option>Regime Change</option>
              </select>
            </div>
            <div>
              <label className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Asset A</label>
              <select className={`w-full mt-1 px-3 py-2 text-sm rounded-lg ${isDark ? 'bg-surface-4 text-gray-200 border-surface-5' : 'bg-gray-100 text-gray-800 border-gray-200'} border`}>
                <option>SPX</option>
                <option>VIX</option>
                <option>GOLD</option>
                <option>BTC</option>
              </select>
            </div>
            <div>
              <label className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Asset B</label>
              <select className={`w-full mt-1 px-3 py-2 text-sm rounded-lg ${isDark ? 'bg-surface-4 text-gray-200 border-surface-5' : 'bg-gray-100 text-gray-800 border-gray-200'} border`}>
                <option>VIX</option>
                <option>US10Y</option>
                <option>DXY</option>
                <option>NDX</option>
              </select>
            </div>
            <div>
              <label className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Channel</label>
              <select className={`w-full mt-1 px-3 py-2 text-sm rounded-lg ${isDark ? 'bg-surface-4 text-gray-200 border-surface-5' : 'bg-gray-100 text-gray-800 border-gray-200'} border`}>
                <option>Email</option>
                <option>Slack</option>
                <option>Web Push</option>
              </select>
            </div>
          </div>
          <button className="mt-4 px-4 py-2 text-sm font-medium rounded-lg bg-accent-green text-white hover:bg-accent-green/90 transition-colors">
            Create Alert
          </button>
        </div>
      )}
      
      {/* Alert List */}
      <div className={`rounded-2xl p-6 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
        <div className="flex items-center gap-2 mb-4">
          <Bell className="w-4 h-4 text-accent-blue" />
          <h3 className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
            Active Alerts ({alertList.filter(a => a.isActive).length})
          </h3>
        </div>
        
        <div className="space-y-3">
          {alertList.map(alert => (
            <div key={alert.id} className={`flex items-center justify-between p-4 rounded-xl ${isDark ? 'bg-surface-3' : 'bg-gray-50'}`}>
              <div className="flex items-center gap-4">
                <div className={`w-2 h-2 rounded-full ${alert.isActive ? 'bg-accent-green animate-pulse' : 'bg-gray-500'}`} />
                <div>
                  <div className={`text-sm font-medium ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
                    {alert.condition.type.replace('_', ' ')}
                    {alert.condition.assetA && ` • ${alert.condition.assetA.toUpperCase()} × ${alert.condition.assetB?.toUpperCase()}`}
                  </div>
                  <div className={`text-xs mt-0.5 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                    Threshold: {alert.condition.threshold} • Channel: {alert.channel} • Created: {alert.createdAt}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => toggleAlert(alert.id)}
                  className={`p-1.5 rounded-lg transition-colors ${isDark ? 'hover:bg-surface-4' : 'hover:bg-gray-200'}`}
                >
                  {alert.isActive ? (
                    <ToggleRight className="w-5 h-5 text-accent-green" />
                  ) : (
                    <ToggleLeft className="w-5 h-5 text-gray-500" />
                  )}
                </button>
                <button
                  onClick={() => deleteAlert(alert.id)}
                  className={`p-1.5 rounded-lg transition-colors ${isDark ? 'hover:bg-surface-4 text-gray-500' : 'hover:bg-gray-200 text-gray-400'}`}
                >
                  <BellOff className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
