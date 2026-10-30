import { useTheme } from '../stores/theme';
import AnomalyTable from '../components/AnomalyTable';

export default function AnomaliesPage() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  
  return (
    <div className="p-6 space-y-6 max-w-[1920px] mx-auto">
      <div>
        <h1 className={`text-2xl font-semibold tracking-tight ${isDark ? 'text-white' : 'text-gray-900'}`}>
          Anomalies
        </h1>
        <p className={`text-sm mt-1 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
          Detected breaks in correlation, cointegration, and divergences
        </p>
      </div>
      
      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Anomalies', value: '200', color: 'text-accent-blue' },
          { label: 'Active', value: '23', color: 'text-accent-red' },
          { label: 'Critical', value: '12', color: 'text-accent-orange' },
          { label: 'Resolved (30D)', value: '45', color: 'text-accent-green' },
        ].map(stat => (
          <div key={stat.label} className={`rounded-2xl p-5 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
            <div className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>{stat.label}</div>
            <div className={`text-2xl font-bold font-mono mt-1 ${stat.color}`}>{stat.value}</div>
          </div>
        ))}
      </div>
      
      <AnomalyTable />
    </div>
  );
}
