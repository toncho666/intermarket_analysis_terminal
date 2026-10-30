import { useState } from 'react';
import { useTheme } from '../stores/theme';
import { strategies, backtests, assets } from '../data/marketData';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Play, Plus, TrendingUp } from 'lucide-react';

export default function StrategyBuilder() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const [selectedStrategy, setSelectedStrategy] = useState<string>(strategies[0]?.id || '');
  const [showBuilder, setShowBuilder] = useState(false);
  
  const selectedBT = backtests.find(b => b.strategyId === selectedStrategy);
  const selectedStrat = strategies.find(s => s.id === selectedStrategy);
  
  const [newStrat, setNewStrat] = useState({
    name: '',
    assetA: 'spx',
    assetB: 'vix',
    signalType: 'mean_reversion' as const,
    entryZ: 2.0,
    exitZ: 0.5,
    window: 60,
  });

  return (
    <div className="space-y-6">
      {/* Strategy List */}
      <div className={`rounded-2xl p-6 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-accent-blue" />
            <h3 className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>Strategies</h3>
          </div>
          <button
            onClick={() => setShowBuilder(!showBuilder)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-accent-blue text-white hover:bg-accent-blue/90 transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            New Strategy
          </button>
        </div>
        
        {/* Strategy selector */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {strategies.map(strat => {
            const bt = backtests.find(b => b.strategyId === strat.id);
            const isSelected = strat.id === selectedStrategy;
            return (
              <button
                key={strat.id}
                onClick={() => setSelectedStrategy(strat.id)}
                className={`text-left p-4 rounded-xl border transition-all ${
                  isSelected
                    ? isDark ? 'border-accent-blue bg-accent-blue/5' : 'border-accent-blue bg-blue-50'
                    : isDark ? 'border-surface-4 hover:border-surface-5 bg-surface-3' : 'border-gray-200 hover:border-gray-300 bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-sm font-medium ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
                    {strat.name}
                  </span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                    strat.signalType === 'mean_reversion' ? 'bg-accent-purple/10 text-accent-purple' :
                    strat.signalType === 'momentum' ? 'bg-accent-green/10 text-accent-green' :
                    'bg-accent-orange/10 text-accent-orange'
                  }`}>
                    {strat.signalType.replace('_', '-')}
                  </span>
                </div>
                <div className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                  {assets.find(a => a.id === strat.assetA)?.ticker} × {assets.find(a => a.id === strat.assetB)?.ticker}
                </div>
                {bt && (
                  <div className="flex items-center gap-3 mt-2">
                    <span className={`text-xs font-mono ${bt.metrics.sharpe > 1 ? 'text-accent-green' : 'text-accent-yellow'}`}>
                      Sharpe: {bt.metrics.sharpe.toFixed(2)}
                    </span>
                    <span className={`text-xs font-mono ${bt.metrics.totalReturn > 0 ? 'text-accent-green' : 'text-accent-red'}`}>
                      {bt.metrics.totalReturn > 0 ? '+' : ''}{bt.metrics.totalReturn.toFixed(1)}%
                    </span>
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>
      
      {/* Strategy Builder Modal */}
      {showBuilder && (
        <div className={`rounded-2xl p-6 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
          <h3 className={`text-sm font-medium mb-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
            New Strategy Builder
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <label className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Name</label>
              <input
                type="text"
                value={newStrat.name}
                onChange={e => setNewStrat({ ...newStrat, name: e.target.value })}
                placeholder="Strategy name"
                className={`w-full mt-1 px-3 py-2 text-sm rounded-lg ${isDark ? 'bg-surface-4 text-gray-200 border-surface-5' : 'bg-gray-100 text-gray-800 border-gray-200'} border`}
              />
            </div>
            <div>
              <label className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Asset A</label>
              <select
                value={newStrat.assetA}
                onChange={e => setNewStrat({ ...newStrat, assetA: e.target.value })}
                className={`w-full mt-1 px-3 py-2 text-sm rounded-lg ${isDark ? 'bg-surface-4 text-gray-200 border-surface-5' : 'bg-gray-100 text-gray-800 border-gray-200'} border`}
              >
                {assets.map(a => <option key={a.id} value={a.id}>{a.ticker}</option>)}
              </select>
            </div>
            <div>
              <label className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Asset B</label>
              <select
                value={newStrat.assetB}
                onChange={e => setNewStrat({ ...newStrat, assetB: e.target.value })}
                className={`w-full mt-1 px-3 py-2 text-sm rounded-lg ${isDark ? 'bg-surface-4 text-gray-200 border-surface-5' : 'bg-gray-100 text-gray-800 border-gray-200'} border`}
              >
                {assets.map(a => <option key={a.id} value={a.id}>{a.ticker}</option>)}
              </select>
            </div>
            <div>
              <label className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Signal Type</label>
              <select
                value={newStrat.signalType}
                onChange={e => setNewStrat({ ...newStrat, signalType: e.target.value as any })}
                className={`w-full mt-1 px-3 py-2 text-sm rounded-lg ${isDark ? 'bg-surface-4 text-gray-200 border-surface-5' : 'bg-gray-100 text-gray-800 border-gray-200'} border`}
              >
                <option value="mean_reversion">Mean Reversion</option>
                <option value="momentum">Momentum</option>
                <option value="lead_lag">Lead-Lag</option>
              </select>
            </div>
            <div>
              <label className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Entry Z-Score</label>
              <input
                type="number"
                step="0.1"
                value={newStrat.entryZ}
                onChange={e => setNewStrat({ ...newStrat, entryZ: parseFloat(e.target.value) })}
                className={`w-full mt-1 px-3 py-2 text-sm rounded-lg ${isDark ? 'bg-surface-4 text-gray-200 border-surface-5' : 'bg-gray-100 text-gray-800 border-gray-200'} border`}
              />
            </div>
            <div>
              <label className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Exit Z-Score</label>
              <input
                type="number"
                step="0.1"
                value={newStrat.exitZ}
                onChange={e => setNewStrat({ ...newStrat, exitZ: parseFloat(e.target.value) })}
                className={`w-full mt-1 px-3 py-2 text-sm rounded-lg ${isDark ? 'bg-surface-4 text-gray-200 border-surface-5' : 'bg-gray-100 text-gray-800 border-gray-200'} border`}
              />
            </div>
            <div>
              <label className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Window (days)</label>
              <input
                type="number"
                value={newStrat.window}
                onChange={e => setNewStrat({ ...newStrat, window: parseInt(e.target.value) })}
                className={`w-full mt-1 px-3 py-2 text-sm rounded-lg ${isDark ? 'bg-surface-4 text-gray-200 border-surface-5' : 'bg-gray-100 text-gray-800 border-gray-200'} border`}
              />
            </div>
            <div className="flex items-end">
              <button className="w-full flex items-center justify-center gap-1.5 px-4 py-2 text-sm font-medium rounded-lg bg-accent-green text-white hover:bg-accent-green/90 transition-colors">
                <Play className="w-3.5 h-3.5" />
                Run Backtest
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Backtest Results */}
      {selectedBT && selectedStrat && (
        <div className={`rounded-2xl p-6 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
          <h3 className={`text-sm font-medium mb-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
            Backtest: {selectedStrat.name}
          </h3>
          
          {/* Metrics */}
          <div className="grid grid-cols-3 md:grid-cols-6 gap-4 mb-6">
            {[
              { label: 'Sharpe', value: selectedBT.metrics.sharpe.toFixed(2), good: selectedBT.metrics.sharpe > 1 },
              { label: 'Sortino', value: selectedBT.metrics.sortino.toFixed(2), good: selectedBT.metrics.sortino > 1.5 },
              { label: 'Max DD', value: `${selectedBT.metrics.maxDrawdown.toFixed(1)}%`, good: selectedBT.metrics.maxDrawdown > -10 },
              { label: 'Hit Rate', value: `${selectedBT.metrics.hitRate.toFixed(1)}%`, good: selectedBT.metrics.hitRate > 55 },
              { label: 'Total Return', value: `${selectedBT.metrics.totalReturn > 0 ? '+' : ''}${selectedBT.metrics.totalReturn.toFixed(1)}%`, good: selectedBT.metrics.totalReturn > 0 },
              { label: 'Turnover', value: `${selectedBT.metrics.turnover.toFixed(0)}%`, good: selectedBT.metrics.turnover < 30 },
            ].map(m => (
              <div key={m.label} className={`p-3 rounded-xl ${isDark ? 'bg-surface-3' : 'bg-gray-50'}`}>
                <div className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>{m.label}</div>
                <div className={`text-lg font-bold font-mono mt-1 ${m.good ? 'text-accent-green' : 'text-accent-red'}`}>
                  {m.value}
                </div>
              </div>
            ))}
          </div>
          
          {/* Equity Curve */}
          <div>
            <h4 className={`text-xs font-medium mb-3 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Equity Curve</h4>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={selectedBT.equityCurve}>
                <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#1a1a1a' : '#f3f4f6'} />
                <XAxis dataKey="ts" tick={{ fontSize: 10, fill: isDark ? '#666' : '#9ca3af' }} tickFormatter={(v) => v.slice(5)} interval={50} />
                <YAxis tick={{ fontSize: 10, fill: isDark ? '#666' : '#9ca3af' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: isDark ? '#1a1a1a' : '#fff', border: 'none', borderRadius: 8, fontSize: 12 }}
                />
                <Line type="monotone" dataKey="value" stroke="#007AFF" strokeWidth={2} dot={false} name="Equity" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
