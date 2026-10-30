import { useState } from 'react';
import { useTheme } from '../stores/theme';
import { anomalies, getAssetById } from '../data/marketData';
import { AlertTriangle, Filter, Eye } from 'lucide-react';

export default function AnomalyTable() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  
  const filtered = anomalies.filter(a => {
    if (typeFilter !== 'all' && a.type !== typeFilter) return false;
    if (severityFilter !== 'all' && a.severity !== severityFilter) return false;
    if (statusFilter !== 'all' && a.status !== statusFilter) return false;
    return true;
  });
  
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-accent-red bg-accent-red/10';
      case 'high': return 'text-accent-orange bg-accent-orange/10';
      case 'medium': return 'text-accent-yellow bg-accent-yellow/10';
      default: return 'text-gray-400 bg-gray-500/10';
    }
  };
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-accent-red';
      case 'monitoring': return 'text-accent-yellow';
      default: return 'text-accent-green';
    }
  };

  return (
    <div className={`rounded-2xl p-6 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-accent-orange" />
          <h3 className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
            Anomalies ({filtered.length})
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <Filter className={`w-3.5 h-3.5 ${isDark ? 'text-gray-500' : 'text-gray-400'}`} />
          <select
            value={typeFilter}
            onChange={e => setTypeFilter(e.target.value)}
            className={`text-xs rounded-lg px-2 py-1.5 ${isDark ? 'bg-surface-4 text-gray-300 border-surface-5' : 'bg-gray-100 text-gray-700 border-gray-200'} border`}
          >
            <option value="all">All Types</option>
            <option value="corr_break">Corr Break</option>
            <option value="coint_break">Coint Break</option>
            <option value="divergence">Divergence</option>
          </select>
          <select
            value={severityFilter}
            onChange={e => setSeverityFilter(e.target.value)}
            className={`text-xs rounded-lg px-2 py-1.5 ${isDark ? 'bg-surface-4 text-gray-300 border-surface-5' : 'bg-gray-100 text-gray-700 border-gray-200'} border`}
          >
            <option value="all">All Severity</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <select
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value)}
            className={`text-xs rounded-lg px-2 py-1.5 ${isDark ? 'bg-surface-4 text-gray-300 border-surface-5' : 'bg-gray-100 text-gray-700 border-gray-200'} border`}
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="monitoring">Monitoring</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
      </div>
      
      {/* Table */}
      <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
        <table className="w-full text-xs">
          <thead className={`sticky top-0 ${isDark ? 'bg-surface-3' : 'bg-gray-50'}`}>
            <tr>
              <th className={`text-left py-2 px-3 font-medium ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Date</th>
              <th className={`text-left py-2 px-3 font-medium ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Pair</th>
              <th className={`text-left py-2 px-3 font-medium ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Type</th>
              <th className={`text-right py-2 px-3 font-medium ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Z-Score</th>
              <th className={`text-center py-2 px-3 font-medium ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Severity</th>
              <th className={`text-center py-2 px-3 font-medium ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Status</th>
              <th className={`text-center py-2 px-3 font-medium ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.slice(0, 100).map(anomaly => (
              <tr key={anomaly.id} className={`border-t ${isDark ? 'border-surface-4 hover:bg-surface-3' : 'border-gray-100 hover:bg-gray-50'} transition-colors`}>
                <td className={`py-2.5 px-3 font-mono ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                  {anomaly.detectedAt}
                </td>
                <td className="py-2.5 px-3">
                  <span className={`font-mono ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
                    {getAssetById(anomaly.assetA)?.ticker} × {getAssetById(anomaly.assetB)?.ticker}
                  </span>
                </td>
                <td className="py-2.5 px-3">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] ${
                    anomaly.type === 'corr_break' ? 'bg-accent-blue/10 text-accent-blue' :
                    anomaly.type === 'coint_break' ? 'bg-accent-purple/10 text-accent-purple' :
                    'bg-accent-orange/10 text-accent-orange'
                  }`}>
                    {anomaly.type.replace('_', ' ')}
                  </span>
                </td>
                <td className={`py-2.5 px-3 text-right font-mono ${
                  anomaly.direction === 'positive' ? 'text-accent-green' : 'text-accent-red'
                }`}>
                  {anomaly.direction === 'positive' ? '+' : '-'}{anomaly.zScore.toFixed(2)}σ
                </td>
                <td className="py-2.5 px-3 text-center">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] ${getSeverityColor(anomaly.severity)}`}>
                    {anomaly.severity}
                  </span>
                </td>
                <td className={`py-2.5 px-3 text-center ${getStatusColor(anomaly.status)}`}>
                  {anomaly.status}
                </td>
                <td className="py-2.5 px-3 text-center">
                  <button className={`p-1 rounded ${isDark ? 'hover:bg-surface-4 text-gray-500' : 'hover:bg-gray-200 text-gray-400'}`}>
                    <Eye className="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {filtered.length > 100 && (
        <p className={`text-xs mt-3 text-center ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>
          Showing 100 of {filtered.length} anomalies
        </p>
      )}
    </div>
  );
}
