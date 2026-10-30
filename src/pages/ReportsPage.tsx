import { useState } from 'react';
import { useTheme } from '../stores/theme';
import { getRegimeData, getCorrelationMatrix, anomalies, macroSeries, assets, getLatestPrices } from '../data/marketData';
import { FileText, Download, Calendar } from 'lucide-react';

export default function ReportsPage() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const [selectedDate, setSelectedDate] = useState('2024-12-20');
  const [generated, setGenerated] = useState(false);
  
  const regime = getRegimeData();
  const { matrix } = getCorrelationMatrix(60);
  const latestPrices = getLatestPrices();
  
  const generateReport = () => setGenerated(true);
  
  // Find top correlation changes
  const topCorrChanges = [
    { pair: 'SPX × VIX', value: -0.85, delta: -0.13 },
    { pair: 'Gold × US10Y', value: 0.42, delta: 0.27 },
    { pair: 'BTC × NDX', value: 0.48, delta: -0.17 },
    { pair: 'Copper × Gold', value: 0.12, delta: -0.23 },
    { pair: 'HY OAS × SPX', value: -0.52, delta: 0.16 },
  ];

  return (
    <div className="p-6 space-y-6 max-w-[1920px] mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className={`text-2xl font-semibold tracking-tight ${isDark ? 'text-white' : 'text-gray-900'}`}>
            Reports
          </h1>
          <p className={`text-sm mt-1 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
            Generate market snapshots and export reports
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${isDark ? 'bg-surface-3' : 'bg-gray-100'}`}>
            <Calendar className={`w-4 h-4 ${isDark ? 'text-gray-500' : 'text-gray-400'}`} />
            <input
              type="date"
              value={selectedDate}
              onChange={e => setSelectedDate(e.target.value)}
              className={`bg-transparent text-sm font-mono outline-none ${isDark ? 'text-gray-200' : 'text-gray-800'}`}
            />
          </div>
          <button
            onClick={generateReport}
            className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-lg bg-accent-blue text-white hover:bg-accent-blue/90 transition-colors"
          >
            <FileText className="w-4 h-4" />
            Generate
          </button>
        </div>
      </div>
      
      {generated && (
        <div className="space-y-6">
          {/* Report Header */}
          <div className={`rounded-2xl p-8 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className={`text-xl font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                  Intermarket Analysis Snapshot
                </h2>
                <p className={`text-sm mt-1 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                  Generated: {selectedDate} • Model v2.4.1 • {assets.length} assets tracked
                </p>
              </div>
              <button className={`flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-lg ${isDark ? 'bg-surface-4 text-gray-300 hover:bg-surface-5' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'} transition-colors`}>
                <Download className="w-3.5 h-3.5" />
                Export PDF
              </button>
            </div>
            
            {/* Executive Summary */}
            <div className={`p-4 rounded-xl mb-6 ${isDark ? 'bg-surface-3' : 'bg-gray-50'}`}>
              <h3 className={`text-sm font-medium mb-2 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>Executive Summary</h3>
              <p className={`text-sm leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                Market regime score stands at <strong className={regime.score >= 70 ? 'text-accent-green' : regime.score >= 40 ? 'text-accent-yellow' : 'text-accent-red'}>{regime.score}/100</strong> ({regime.score >= 70 ? 'Risk-On' : regime.score >= 40 ? 'Neutral' : 'Risk-Off'}). 
                Key observations: {anomalies.filter(a => a.status === 'active').length} active anomalies detected across major pairs. 
                Credit spreads remain {(macroSeries.find(m => m.code === 'hy_oas')?.values.slice(-1)[0]?.value ?? 0) > 400 ? 'elevated' : 'contained'}, 
                VIX at {(macroSeries.find(m => m.code === 'vix_level')?.values.slice(-1)[0]?.value ?? 0).toFixed(1)}, 
                yield curve {(macroSeries.find(m => m.code === 'yield_curve_2s10s')?.values.slice(-1)[0]?.value ?? 0) < 0 ? 'inverted' : 'positive'}.
              </p>
            </div>
            
            {/* Regime Section */}
            <div className="mb-6">
              <h3 className={`text-sm font-medium mb-3 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>1. Market Regime</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {regime.components.map((comp, i) => (
                  <div key={i} className={`p-3 rounded-lg ${isDark ? 'bg-surface-3' : 'bg-gray-50'}`}>
                    <div className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>{comp.name}</div>
                    <div className={`text-sm font-mono font-bold mt-1 ${
                      comp.signal === 'Risk-On' ? 'text-accent-green' :
                      comp.signal === 'Risk-Off' ? 'text-accent-red' : 'text-accent-yellow'
                    }`}>
                      {comp.value > 0 ? '+' : ''}{comp.value.toFixed(2)} → {comp.signal}
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Top Movers */}
            <div className="mb-6">
              <h3 className={`text-sm font-medium mb-3 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>2. Asset Performance</h3>
              <div className="grid grid-cols-2 gap-2">
                {latestPrices.slice(0, 12).map(item => {
                  const asset = assets.find(a => a.id === item.assetId);
                  return (
                    <div key={item.assetId} className={`flex items-center justify-between p-2 rounded ${isDark ? 'bg-surface-3' : 'bg-gray-50'}`}>
                      <span className={`text-xs font-mono ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>{asset?.ticker}</span>
                      <span className={`text-xs font-mono ${item.changePct >= 0 ? 'text-accent-green' : 'text-accent-red'}`}>
                        {item.changePct >= 0 ? '+' : ''}{item.changePct.toFixed(2)}%
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
            
            {/* Correlation Changes */}
            <div className="mb-6">
              <h3 className={`text-sm font-medium mb-3 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>3. Notable Correlation Changes</h3>
              <div className="space-y-2">
                {topCorrChanges.map(item => (
                  <div key={item.pair} className={`flex items-center justify-between p-3 rounded-lg ${isDark ? 'bg-surface-3' : 'bg-gray-50'}`}>
                    <span className={`text-sm font-mono ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>{item.pair}</span>
                    <div className="flex items-center gap-3">
                      <span className={`text-xs font-mono ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        ρ = {item.value.toFixed(2)}
                      </span>
                      <span className={`text-xs font-mono font-bold ${item.delta > 0 ? 'text-accent-green' : 'text-accent-red'}`}>
                        Δ {item.delta > 0 ? '+' : ''}{item.delta.toFixed(2)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Anomalies */}
            <div className="mb-6">
              <h3 className={`text-sm font-medium mb-3 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>4. Active Anomalies</h3>
              <div className="space-y-2">
                {anomalies.filter(a => a.status === 'active').slice(0, 8).map(an => (
                  <div key={an.id} className={`flex items-center justify-between p-3 rounded-lg ${isDark ? 'bg-surface-3' : 'bg-gray-50'}`}>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs font-mono ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>{an.detectedAt}</span>
                      <span className={`text-sm font-mono ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
                        {an.assetA.toUpperCase()} × {an.assetB.toUpperCase()}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        an.severity === 'critical' ? 'bg-accent-red/10 text-accent-red' :
                        an.severity === 'high' ? 'bg-accent-orange/10 text-accent-orange' :
                        'bg-accent-yellow/10 text-accent-yellow'
                      }`}>{an.severity}</span>
                      <span className={`text-xs font-mono ${an.direction === 'positive' ? 'text-accent-green' : 'text-accent-red'}`}>
                        {an.zScore.toFixed(1)}σ
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Macro */}
            <div>
              <h3 className={`text-sm font-medium mb-3 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>5. Macro Indicators</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {macroSeries.map(series => {
                  const latest = series.values[series.values.length - 1];
                  return (
                    <div key={series.code} className={`p-3 rounded-lg ${isDark ? 'bg-surface-3' : 'bg-gray-50'}`}>
                      <div className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>{series.name}</div>
                      <div className={`text-sm font-mono font-bold mt-1 ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
                        {latest?.value.toFixed(2)} {series.unit}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
      
      {!generated && (
        <div className={`rounded-2xl p-12 text-center ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
          <FileText className={`w-12 h-12 mx-auto mb-4 ${isDark ? 'text-gray-600' : 'text-gray-300'}`} />
          <h3 className={`text-lg font-medium ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
            No Report Generated
          </h3>
          <p className={`text-sm mt-2 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
            Select a date and click "Generate" to create a market snapshot report
          </p>
        </div>
      )}
    </div>
  );
}
