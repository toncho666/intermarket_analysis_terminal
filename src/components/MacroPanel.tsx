import { useTheme } from '../stores/theme';
import { macroSeries } from '../data/marketData';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function MacroPanel() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  
  const colors = ['#007AFF', '#30D158', '#FF9F0A', '#BF5AF2', '#FF453A', '#64D2FF', '#FFD60A', '#FF6482'];

  return (
    <div className={`rounded-2xl p-6 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>Macro Dashboard</h3>
          <p className={`text-xs mt-0.5 ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>
            Key macro indicators • Updated 2024-12-20
          </p>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        {macroSeries.map((series, idx) => {
          const latest = series.values[series.values.length - 1];
          const prev = series.values[series.values.length - 2];
          const change = latest && prev ? latest.value - prev.value : 0;
          const changePct = prev && prev.value !== 0 ? (change / Math.abs(prev.value)) * 100 : 0;
          const isPositive = change >= 0;
          
          // Sample data for mini chart
          const chartData = series.values.slice(-50).map(v => ({ ts: v.ts, value: v.value }));
          
          return (
            <div key={series.code} className={`rounded-xl p-4 ${isDark ? 'bg-surface-3' : 'bg-gray-50'}`}>
              <div className="flex items-center justify-between mb-2">
                <span className={`text-xs font-medium ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                  {series.name}
                </span>
                <span className={`text-xs ${isPositive ? 'text-accent-green' : 'text-accent-red'}`}>
                  {isPositive ? '+' : ''}{change.toFixed(2)}
                </span>
              </div>
              <div className="flex items-end justify-between">
                <div>
                  <span className={`text-lg font-bold font-mono ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    {latest?.value.toFixed(2)}
                  </span>
                  <span className={`text-xs ml-1 ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>
                    {series.unit}
                  </span>
                </div>
                <div className="w-20 h-8">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                      <Line
                        type="monotone"
                        dataKey="value"
                        stroke={colors[idx % colors.length]}
                        strokeWidth={1.5}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      {/* Yield Curve Visualization */}
      <div className={`mt-6 rounded-xl p-4 ${isDark ? 'bg-surface-3' : 'bg-gray-50'}`}>
        <h4 className={`text-xs font-medium mb-3 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
          Yield Curve Shape
        </h4>
        <div className="flex items-end gap-3 h-20">
          {[
            { label: '3M', value: 4.5, color: '#007AFF' },
            { label: '2Y', value: 4.3, color: '#30D158' },
            { label: '5Y', value: 4.1, color: '#FF9F0A' },
            { label: '10Y', value: 4.2, color: '#BF5AF2' },
            { label: '30Y', value: 4.4, color: '#FF453A' },
          ].map(point => (
            <div key={point.label} className="flex-1 flex flex-col items-center gap-1">
              <span className={`text-xs font-mono ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                {point.value}%
              </span>
              <div
                className="w-full rounded-t-sm transition-all"
                style={{
                  height: `${(point.value / 5) * 100}%`,
                  backgroundColor: point.color,
                  opacity: 0.7,
                }}
              />
              <span className={`text-[10px] ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                {point.label}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
