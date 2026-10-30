import { useState } from 'react';
import { useTheme } from '../stores/theme';
import CorrelationHeatmap from '../components/CorrelationHeatmap';

export default function CorrelationsPage() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const [window, setWindow] = useState(60);
  
  return (
    <div className="p-6 space-y-6 max-w-[1920px] mx-auto">
      <div>
        <h1 className={`text-2xl font-semibold tracking-tight ${isDark ? 'text-white' : 'text-gray-900'}`}>
          Correlation Matrix
        </h1>
        <p className={`text-sm mt-1 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
          Cross-asset correlations • Click any cell to drill into pair analysis
        </p>
      </div>
      
      <CorrelationHeatmap windowDays={window} onWindowChange={setWindow} />
      
      {/* Top Correlation Changes */}
      <div className={`rounded-2xl p-6 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
        <h3 className={`text-sm font-medium mb-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
          Notable Correlation Changes (Δ vs previous period)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[
            { pair: 'SPX × VIX', from: -0.72, to: -0.85, delta: -0.13 },
            { pair: 'Gold × US10Y', from: 0.15, to: 0.42, delta: 0.27 },
            { pair: 'BTC × NDX', from: 0.65, to: 0.48, delta: -0.17 },
            { pair: 'Copper × Gold', from: 0.35, to: 0.12, delta: -0.23 },
            { pair: 'DXY × EURUSD', from: -0.95, to: -0.98, delta: -0.03 },
            { pair: 'HY OAS × SPX', from: -0.68, to: -0.52, delta: 0.16 },
          ].map(item => (
            <div key={item.pair} className={`flex items-center justify-between p-3 rounded-xl ${isDark ? 'bg-surface-3' : 'bg-gray-50'}`}>
              <span className={`text-sm font-mono ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>{item.pair}</span>
              <div className="flex items-center gap-3">
                <span className={`text-xs font-mono ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                  {item.from.toFixed(2)} → {item.to.toFixed(2)}
                </span>
                <span className={`text-xs font-mono font-bold ${item.delta > 0 ? 'text-accent-green' : 'text-accent-red'}`}>
                  {item.delta > 0 ? '+' : ''}{item.delta.toFixed(2)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
