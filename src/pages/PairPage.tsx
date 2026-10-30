import { useParams } from 'react-router-dom';
import { useTheme } from '../stores/theme';
import PairChart from '../components/PairChart';
import { getAssetByTicker, getCorrelationsForPair, anomalies } from '../data/marketData';
import { ArrowLeftRight } from 'lucide-react';

export default function PairPage() {
  const { a, b } = useParams<{ a: string; b: string }>();
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  
  const tickerA = a || 'SPX';
  const tickerB = b || 'US10Y';
  const assetA = getAssetByTicker(tickerA);
  const assetB = getAssetByTicker(tickerB);
  
  const corr60 = getCorrelationsForPair(assetA?.id || '', assetB?.id || '', 60);
  const latestCorr = corr60.length > 0 ? corr60[corr60.length - 1] : null;
  
  const pairAnomalies = anomalies.filter(an =>
    (an.assetA === assetA?.id && an.assetB === assetB?.id) ||
    (an.assetA === assetB?.id && an.assetB === assetA?.id)
  );

  return (
    <div className="p-6 space-y-6 max-w-[1920px] mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className={`text-2xl font-bold font-mono ${isDark ? 'text-white' : 'text-gray-900'}`}>
              {tickerA}
            </span>
            <ArrowLeftRight className={`w-5 h-5 ${isDark ? 'text-gray-500' : 'text-gray-400'}`} />
            <span className={`text-2xl font-bold font-mono ${isDark ? 'text-white' : 'text-gray-900'}`}>
              {tickerB}
            </span>
          </div>
        </div>
        <div className={`text-xs px-3 py-1.5 rounded-lg ${isDark ? 'bg-surface-3' : 'bg-gray-100'}`}>
          <span className={isDark ? 'text-gray-500' : 'text-gray-400'}>
            {assetA?.name} × {assetB?.name}
          </span>
        </div>
      </div>
      
      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className={`rounded-xl p-4 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
          <div className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Correlation (60D)</div>
          <div className={`text-xl font-bold font-mono mt-1 ${
            latestCorr && latestCorr.value > 0 ? 'text-accent-green' : 'text-accent-red'
          }`}>
            {latestCorr?.value.toFixed(3) || 'N/A'}
          </div>
        </div>
        <div className={`rounded-xl p-4 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
          <div className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>95% CI</div>
          <div className={`text-xl font-bold font-mono mt-1 ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
            [{latestCorr?.ciLow.toFixed(3)}, {latestCorr?.ciHigh.toFixed(3)}]
          </div>
        </div>
        <div className={`rounded-xl p-4 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
          <div className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Δ vs Prev</div>
          <div className={`text-xl font-bold font-mono mt-1 ${
            latestCorr && latestCorr.deltaVsPrev > 0 ? 'text-accent-green' : 'text-accent-red'
          }`}>
            {latestCorr && latestCorr.deltaVsPrev > 0 ? '+' : ''}{latestCorr?.deltaVsPrev?.toFixed(3) ?? 'N/A'}
          </div>
        </div>
        <div className={`rounded-xl p-4 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
          <div className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Anomalies</div>
          <div className={`text-xl font-bold font-mono mt-1 text-accent-orange`}>
            {pairAnomalies.length}
          </div>
        </div>
        <div className={`rounded-xl p-4 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
          <div className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Cointegration</div>
          <div className={`text-xl font-bold font-mono mt-1 ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
            p=0.032
          </div>
        </div>
      </div>
      
      {/* Charts */}
      <PairChart tickerA={tickerA} tickerB={tickerB} />
      
      {/* Anomaly Markers for this pair */}
      {pairAnomalies.length > 0 && (
        <div className={`rounded-2xl p-6 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
          <h3 className={`text-sm font-medium mb-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
            Anomaly Events ({pairAnomalies.length})
          </h3>
          <div className="space-y-2">
            {pairAnomalies.slice(0, 10).map(an => (
              <div key={an.id} className={`flex items-center justify-between p-3 rounded-xl ${isDark ? 'bg-surface-3' : 'bg-gray-50'}`}>
                <div className="flex items-center gap-3">
                  <span className={`text-xs font-mono ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>{an.detectedAt}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    an.type === 'corr_break' ? 'bg-accent-blue/10 text-accent-blue' :
                    an.type === 'coint_break' ? 'bg-accent-purple/10 text-accent-purple' :
                    'bg-accent-orange/10 text-accent-orange'
                  }`}>
                    {an.type.replace('_', ' ')}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-xs font-mono ${an.direction === 'positive' ? 'text-accent-green' : 'text-accent-red'}`}>
                    {an.direction === 'positive' ? '+' : '-'}{an.zScore.toFixed(2)}σ
                  </span>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    an.severity === 'critical' ? 'bg-accent-red/10 text-accent-red' :
                    an.severity === 'high' ? 'bg-accent-orange/10 text-accent-orange' :
                    an.severity === 'medium' ? 'bg-accent-yellow/10 text-accent-yellow' :
                    'bg-gray-500/10 text-gray-400'
                  }`}>
                    {an.severity}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
