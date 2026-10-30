import { useTheme } from '../stores/theme';
import StrategyBuilder from '../components/StrategyBuilder';

export default function StrategiesPage() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  
  return (
    <div className="p-6 space-y-6 max-w-[1920px] mx-auto">
      <div>
        <h1 className={`text-2xl font-semibold tracking-tight ${isDark ? 'text-white' : 'text-gray-900'}`}>
          Strategies
        </h1>
        <p className={`text-sm mt-1 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
          Build, backtest, and monitor cross-asset strategies
        </p>
      </div>
      
      <StrategyBuilder />
    </div>
  );
}
