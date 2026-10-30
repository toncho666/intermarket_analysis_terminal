import { useTheme } from '../stores/theme';
import { getAssetById, getLatestPrices } from '../data/marketData';

export default function AssetTicker() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const latestPrices = getLatestPrices();
  
  return (
    <div className={`border-b overflow-hidden ${isDark ? 'border-surface-4 bg-surface-1' : 'border-gray-200 bg-white'}`}>
      <div className="flex items-center gap-6 px-6 py-2 overflow-x-auto whitespace-nowrap">
        {latestPrices.map(item => {
          const asset = getAssetById(item.assetId);
          if (!asset) return null;
          return (
            <div key={item.assetId} className="flex items-center gap-2 shrink-0">
              <span className={`text-xs font-mono font-medium ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                {asset.ticker}
              </span>
              <span className={`text-xs font-mono ${isDark ? 'text-gray-300' : 'text-gray-800'}`}>
                {item.price.toFixed(2)}
              </span>
              <span className={`text-xs font-mono ${item.changePct >= 0 ? 'text-accent-green' : 'text-accent-red'}`}>
                {item.changePct >= 0 ? '▲' : '▼'} {Math.abs(item.changePct).toFixed(2)}%
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
