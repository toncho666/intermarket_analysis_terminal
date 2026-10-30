import { useTheme } from '../stores/theme';
import { getLatestPrices, getAssetById } from '../data/marketData';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell } from 'recharts';

export default function LeadersLaggards() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const latestPrices = getLatestPrices();
  
  const sorted = [...latestPrices].sort((a, b) => b.changePct - a.changePct);
  const leaders = sorted.slice(0, 10);
  const laggards = sorted.slice(-10).reverse();
  
  const chartData = [...leaders, ...laggards].map(item => ({
    ticker: getAssetById(item.assetId)?.ticker || item.assetId,
    change: Math.round(item.changePct * 100) / 100,
    class: getAssetById(item.assetId)?.assetClass || '',
  }));

  return (
    <div className={`rounded-2xl p-6 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
      <h3 className={`text-sm font-medium mb-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
        Daily Performance by Asset
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 50 }}>
          <XAxis type="number" tick={{ fontSize: 10, fill: isDark ? '#666' : '#9ca3af' }} />
          <YAxis type="category" dataKey="ticker" tick={{ fontSize: 10, fill: isDark ? '#888' : '#666' }} width={50} />
          <Bar dataKey="change" radius={[0, 4, 4, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={index} fill={entry.change >= 0 ? '#30D158' : '#FF453A'} fillOpacity={0.7} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
