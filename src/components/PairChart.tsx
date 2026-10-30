import { useMemo } from 'react';
import { useTheme } from '../stores/theme';
import { getAssetByTicker, getPricesForAsset, getCorrelationsForPair, anomalies } from '../data/marketData';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, ComposedChart, ReferenceLine } from 'recharts';

interface Props {
  tickerA: string;
  tickerB: string;
}

export default function PairChart({ tickerA, tickerB }: Props) {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  
  const assetA = getAssetByTicker(tickerA);
  const assetB = getAssetByTicker(tickerB);
  
  const chartData = useMemo(() => {
    if (!assetA || !assetB) return [];
    
    const pricesA = getPricesForAsset(assetA.id);
    const pricesB = getPricesForAsset(assetB.id);
    const corrs = getCorrelationsForPair(assetA.id, assetB.id, 60);
    const pairAnomalies = anomalies.filter(a => 
      (a.assetA === assetA.id && a.assetB === assetB.id) ||
      (a.assetA === assetB.id && a.assetB === assetA.id)
    );
    
    // Normalize prices to start at 100
    const normA = pricesA.length > 0 ? pricesA.map(p => p.close / pricesA[0].close * 100) : [];
    const normB = pricesB.length > 0 ? pricesB.map(p => p.close / pricesB[0].close * 100) : [];
    
    // Build spread (z-score)
    const spread: number[] = [];
    const window = 60;
    for (let i = 0; i < normA.length; i++) {
      if (i < window) { spread.push(0); continue; }
      const sliceA = normA.slice(i - window, i);
      const sliceB = normB.slice(i - window, i);
      const meanA = sliceA.reduce((s, v) => s + v, 0) / window;
      const meanB = sliceB.reduce((s, v) => s + v, 0) / window;
      const stdA = Math.sqrt(sliceA.reduce((s, v) => s + (v - meanA) ** 2, 0) / window);
      const stdB = Math.sqrt(sliceB.reduce((s, v) => s + (v - meanB) ** 2, 0) / window);
      const zA = stdA > 0 ? (normA[i] - meanA) / stdA : 0;
      const zB = stdB > 0 ? (normB[i] - meanB) / stdB : 0;
      spread.push(zA - zB);
    }
    
    // Build chart data (sample every 3 days for performance)
    const data = [];
    for (let i = 0; i < pricesA.length; i += 3) {
      const corr = corrs.find(c => c.ts === pricesA[i].ts);
      const anomaly = pairAnomalies.find(a => a.detectedAt === pricesA[i].ts);
      data.push({
        ts: pricesA[i].ts,
        priceA: Math.round(normA[i] * 100) / 100,
        priceB: Math.round(normB[i] * 100) / 100,
        spread: Math.round(spread[i] * 100) / 100,
        correlation: corr?.value ?? null,
        ciLow: corr?.ciLow ?? null,
        ciHigh: corr?.ciHigh ?? null,
        anomaly: anomaly?.severity ?? null,
      });
    }
    
    return data;
  }, [assetA, assetB]);
  
  if (!assetA || !assetB) return <div>Assets not found</div>;
  
  const gridColor = isDark ? '#1a1a1a' : '#f3f4f6';
  const textColor = isDark ? '#666' : '#9ca3af';
  
  // Show last 250 data points
  const visibleData = chartData.slice(-250);

  return (
    <div className="space-y-6">
      {/* Normalized Prices */}
      <div className={`rounded-2xl p-6 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
        <h3 className={`text-sm font-medium mb-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
          Normalized Prices (base=100)
        </h3>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={visibleData}>
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
            <XAxis dataKey="ts" tick={{ fontSize: 10, fill: textColor }} tickFormatter={(v) => v.slice(5)} interval={30} />
            <YAxis tick={{ fontSize: 10, fill: textColor }} />
            <Tooltip
              contentStyle={{ backgroundColor: isDark ? '#1a1a1a' : '#fff', border: 'none', borderRadius: 8, fontSize: 12 }}
              labelStyle={{ color: isDark ? '#999' : '#666' }}
            />
            <Line type="monotone" dataKey="priceA" stroke="#007AFF" strokeWidth={1.5} dot={false} name={assetA.ticker} />
            <Line type="monotone" dataKey="priceB" stroke="#BF5AF2" strokeWidth={1.5} dot={false} name={assetB.ticker} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      {/* Z-Score Spread */}
      <div className={`rounded-2xl p-6 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
        <h3 className={`text-sm font-medium mb-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
          Spread Z-Score (60D)
        </h3>
        <ResponsiveContainer width="100%" height={200}>
          <ComposedChart data={visibleData}>
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
            <XAxis dataKey="ts" tick={{ fontSize: 10, fill: textColor }} tickFormatter={(v) => v.slice(5)} interval={30} />
            <YAxis tick={{ fontSize: 10, fill: textColor }} domain={[-4, 4]} />
            <Tooltip
              contentStyle={{ backgroundColor: isDark ? '#1a1a1a' : '#fff', border: 'none', borderRadius: 8, fontSize: 12 }}
            />
            <ReferenceLine y={2} stroke="#FF453A" strokeDasharray="3 3" strokeOpacity={0.5} />
            <ReferenceLine y={-2} stroke="#30D158" strokeDasharray="3 3" strokeOpacity={0.5} />
            <ReferenceLine y={0} stroke={isDark ? '#333' : '#ddd'} />
            <Area type="monotone" dataKey="spread" fill="#007AFF" fillOpacity={0.1} stroke="#007AFF" strokeWidth={1.5} />
            {visibleData.filter(d => d.anomaly).map((d, i) => (
              <ReferenceLine key={i} x={d.ts} stroke="#FF9F0A" strokeOpacity={0.6} />
            ))}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      
      {/* Rolling Correlation */}
      <div className={`rounded-2xl p-6 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
        <h3 className={`text-sm font-medium mb-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
          Rolling Correlation (60D) with 95% CI
        </h3>
        <ResponsiveContainer width="100%" height={200}>
          <ComposedChart data={visibleData.filter(d => d.correlation !== null)}>
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
            <XAxis dataKey="ts" tick={{ fontSize: 10, fill: textColor }} tickFormatter={(v) => v.slice(5)} interval={30} />
            <YAxis tick={{ fontSize: 10, fill: textColor }} domain={[-1, 1]} />
            <Tooltip
              contentStyle={{ backgroundColor: isDark ? '#1a1a1a' : '#fff', border: 'none', borderRadius: 8, fontSize: 12 }}
            />
            <ReferenceLine y={0} stroke={isDark ? '#333' : '#ddd'} />
            <Area type="monotone" dataKey="ciHigh" fill="#007AFF" fillOpacity={0.08} stroke="none" />
            <Area type="monotone" dataKey="ciLow" fill="#007AFF" fillOpacity={0.08} stroke="none" />
            <Line type="monotone" dataKey="correlation" stroke="#007AFF" strokeWidth={1.5} dot={false} name="Correlation" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
