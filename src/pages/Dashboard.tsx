import { useTheme } from '../stores/theme';
import RegimeGauge from '../components/RegimeGauge';
import CorrelationHeatmap from '../components/CorrelationHeatmap';
import MacroPanel from '../components/MacroPanel';
import LeadersLaggards from '../components/LeadersLaggards';
import { getLatestPrices, getAssetById, assets } from '../data/marketData';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';
import { useState } from 'react';

export default function Dashboard() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const [corrWindow, setCorrWindow] = useState(60);
  const latestPrices = getLatestPrices();
  
  // Leaders & Laggards
  const sorted = [...latestPrices].sort((a, b) => b.changePct - a.changePct);
  const leaders = sorted.slice(0, 8);
  const laggards = sorted.slice(-8).reverse();
  
  return (
    <div className="p-6 space-y-6 max-w-[1920px] mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className={`text-2xl font-semibold tracking-tight ${isDark ? 'text-white' : 'text-gray-900'}`}>
            Dashboard
          </h1>
          <p className={`text-sm mt-1 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
            Intermarket regime & correlation overview
          </p>
        </div>
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${isDark ? 'bg-surface-3' : 'bg-gray-100'}`}>
          <Activity className="w-3.5 h-3.5 text-accent-green" />
          <span className={`text-xs font-mono ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            Live • 2024-12-20 16:00 EST
          </span>
        </div>
      </div>
      
      {/* Top row: Regime + Leaders/Laggards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <RegimeGauge />
        
        {/* Leaders */}
        <div className={`rounded-2xl p-6 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-4 h-4 text-accent-green" />
            <h3 className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>Top Leaders</h3>
          </div>
          <div className="space-y-2">
            {leaders.map(item => {
              const asset = getAssetById(item.assetId);
              return (
                <div key={item.assetId} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-1.5 py-0.5 rounded ${isDark ? 'bg-surface-4' : 'bg-gray-100'}`}>
                      {asset?.assetClass?.slice(0, 3)}
                    </span>
                    <span className={`text-sm font-mono font-medium ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
                      {asset?.ticker}
                    </span>
                  </div>
                  <span className="text-sm font-mono text-accent-green">
                    +{item.changePct.toFixed(2)}%
                  </span>
                </div>
              );
            })}
          </div>
        </div>
        
        {/* Laggards */}
        <div className={`rounded-2xl p-6 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
          <div className="flex items-center gap-2 mb-4">
            <TrendingDown className="w-4 h-4 text-accent-red" />
            <h3 className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>Top Laggards</h3>
          </div>
          <div className="space-y-2">
            {laggards.map(item => {
              const asset = getAssetById(item.assetId);
              return (
                <div key={item.assetId} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-1.5 py-0.5 rounded ${isDark ? 'bg-surface-4' : 'bg-gray-100'}`}>
                      {asset?.assetClass?.slice(0, 3)}
                    </span>
                    <span className={`text-sm font-mono font-medium ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
                      {asset?.ticker}
                    </span>
                  </div>
                  <span className="text-sm font-mono text-accent-red">
                    {item.changePct.toFixed(2)}%
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
      
      {/* Correlation Heatmap */}
      <CorrelationHeatmap windowDays={corrWindow} onWindowChange={setCorrWindow} />
      
      {/* Leaders & Laggards Chart */}
      <LeadersLaggards />
      
      {/* Macro Panel */}
      <MacroPanel />
      
      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Assets Tracked', value: assets.length.toString(), color: 'text-accent-blue' },
          { label: 'Active Anomalies', value: '23', color: 'text-accent-orange' },
          { label: 'Correlations (60D)', value: '496', color: 'text-accent-purple' },
          { label: 'Model Version', value: 'v2.4.1', color: 'text-accent-teal' },
        ].map(stat => (
          <div key={stat.label} className={`rounded-2xl p-5 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
            <div className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>{stat.label}</div>
            <div className={`text-2xl font-bold font-mono mt-1 ${stat.color}`}>{stat.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
