import { useTheme } from '../stores/theme';
import { getRegimeData } from '../data/marketData';
import { TrendingUp, TrendingDown } from 'lucide-react';

export default function RegimeGauge() {
  const { theme } = useTheme();
  const regime = getRegimeData();
  const isDark = theme === 'dark';
  
  const score = regime.score;
  const angle = (score / 100) * 180 - 90; // -90 to 90 degrees
  
  const getColor = () => {
    if (score >= 70) return 'text-accent-green';
    if (score >= 40) return 'text-accent-yellow';
    return 'text-accent-red';
  };
  
  const getLabel = () => {
    if (score >= 70) return 'Risk-On';
    if (score >= 40) return 'Neutral';
    return 'Risk-Off';
  };

  return (
    <div className={`rounded-2xl p-6 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>Market Regime</h3>
        <span className={`text-xs px-2 py-1 rounded-full ${isDark ? 'bg-surface-4' : 'bg-gray-100'}`}>
          As of 2024-12-20
        </span>
      </div>
      
      {/* Gauge */}
      <div className="flex flex-col items-center">
        <div className="relative w-48 h-24 overflow-hidden">
          <svg viewBox="0 0 200 100" className="w-full h-full">
            {/* Background arc */}
            <path
              d="M 20 90 A 80 80 0 0 1 180 90"
              fill="none"
              stroke={isDark ? '#222' : '#e5e7eb'}
              strokeWidth="12"
              strokeLinecap="round"
            />
            {/* Colored arc */}
            <defs>
              <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#FF453A" />
                <stop offset="50%" stopColor="#FFD60A" />
                <stop offset="100%" stopColor="#30D158" />
              </linearGradient>
            </defs>
            <path
              d="M 20 90 A 80 80 0 0 1 180 90"
              fill="none"
              stroke="url(#gaugeGradient)"
              strokeWidth="12"
              strokeLinecap="round"
              opacity="0.3"
            />
            {/* Needle */}
            <g transform={`rotate(${angle}, 100, 90)`}>
              <line x1="100" y1="90" x2="100" y2="25" stroke={isDark ? '#fff' : '#111'} strokeWidth="2" strokeLinecap="round" />
              <circle cx="100" cy="90" r="4" fill={isDark ? '#fff' : '#111'} />
            </g>
          </svg>
        </div>
        
        <div className="text-center mt-2">
          <div className={`text-3xl font-bold ${getColor()}`}>{score}</div>
          <div className={`text-sm font-medium mt-1 flex items-center gap-1.5 justify-center ${getColor()}`}>
            {score >= 70 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            {getLabel()}
          </div>
        </div>
      </div>
      
      {/* Components */}
      <div className="mt-6 space-y-2">
        {regime.components.map((comp, i) => (
          <div key={i} className="flex items-center justify-between">
            <span className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>{comp.name}</span>
            <div className="flex items-center gap-2">
              <div className={`w-16 h-1.5 rounded-full ${isDark ? 'bg-surface-4' : 'bg-gray-200'}`}>
                <div
                  className={`h-full rounded-full ${
                    comp.signal === 'Risk-On' ? 'bg-accent-green' :
                    comp.signal === 'Risk-Off' ? 'bg-accent-red' : 'bg-accent-yellow'
                  }`}
                  style={{ width: `${Math.abs(comp.value) * 100}%` }}
                />
              </div>
              <span className={`text-xs font-mono w-10 text-right ${
                comp.signal === 'Risk-On' ? 'text-accent-green' :
                comp.signal === 'Risk-Off' ? 'text-accent-red' : 'text-accent-yellow'
              }`}>
                {comp.value > 0 ? '+' : ''}{comp.value.toFixed(2)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
