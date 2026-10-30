import { useState } from 'react';
import { useTheme } from '../stores/theme';
import { assets, getCorrelationMatrix } from '../data/marketData';
import { useNavigate } from 'react-router-dom';

interface Props {
  windowDays?: number;
  onWindowChange?: (w: number) => void;
}

export default function CorrelationHeatmap({ windowDays = 60, onWindowChange }: Props) {
  const { theme } = useTheme();
  const navigate = useNavigate();
  const isDark = theme === 'dark';
  const [hoveredCell, setHoveredCell] = useState<{ i: number; j: number } | null>(null);
  const [filterClass, setFilterClass] = useState<string>('all');
  
  const windows = [20, 60, 250];
  const { matrix } = getCorrelationMatrix(windowDays);
  
  // Filter assets by class
  const filteredAssets = filterClass === 'all' 
    ? assets 
    : assets.filter(a => a.assetClass === filterClass);
  
  const filteredIndices = filteredAssets.map(a => assets.findIndex(ia => ia.id === a.id));
  
  const getColor = (value: number) => {
    if (value >= 0.7) return isDark ? 'bg-green-500/80' : 'bg-green-500/70';
    if (value >= 0.4) return isDark ? 'bg-green-500/50' : 'bg-green-400/50';
    if (value >= 0.1) return isDark ? 'bg-green-500/25' : 'bg-green-300/40';
    if (value >= -0.1) return isDark ? 'bg-gray-500/20' : 'bg-gray-300/40';
    if (value >= -0.4) return isDark ? 'bg-red-500/25' : 'bg-red-300/40';
    if (value >= -0.7) return isDark ? 'bg-red-500/50' : 'bg-red-400/50';
    return isDark ? 'bg-red-500/80' : 'bg-red-500/70';
  };
  
  const classes = ['all', 'equity', 'bond', 'credit', 'volatility', 'fx', 'commodity', 'crypto'];

  return (
    <div className={`rounded-2xl p-6 ${isDark ? 'bg-surface-2' : 'bg-white shadow-sm'}`}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>Correlation Matrix</h3>
          <p className={`text-xs mt-0.5 ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>
            {filteredAssets.length}×{filteredAssets.length} • {windowDays}D window
          </p>
        </div>
        <div className="flex items-center gap-2">
          {/* Window selector */}
          <div className={`flex rounded-lg overflow-hidden ${isDark ? 'bg-surface-4' : 'bg-gray-100'}`}>
            {windows.map(w => (
              <button
                key={w}
                onClick={() => onWindowChange?.(w)}
                className={`px-3 py-1.5 text-xs font-medium transition-colors ${
                  w === windowDays
                    ? isDark ? 'bg-surface-3 text-white' : 'bg-white text-gray-900 shadow-sm'
                    : isDark ? 'text-gray-500 hover:text-gray-300' : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {w}D
              </button>
            ))}
          </div>
        </div>
      </div>
      
      {/* Class filter */}
      <div className="flex gap-1.5 mb-4 flex-wrap">
        {classes.map(c => (
          <button
            key={c}
            onClick={() => setFilterClass(c)}
            className={`px-2.5 py-1 text-xs rounded-full transition-colors ${
              filterClass === c
                ? 'bg-accent-blue text-white'
                : isDark ? 'bg-surface-4 text-gray-400 hover:text-gray-200' : 'bg-gray-100 text-gray-600 hover:text-gray-900'
            }`}
          >
            {c === 'all' ? 'All' : c.charAt(0).toUpperCase() + c.slice(1)}
          </button>
        ))}
      </div>
      
      {/* Heatmap */}
      <div className="overflow-x-auto">
        <div className="min-w-fit">
          {/* Header */}
          <div className="flex">
            <div className="w-12 shrink-0" />
            {filteredAssets.map(asset => (
              <div
                key={asset.id}
                className={`w-8 h-8 flex items-center justify-center text-[9px] font-mono rotate-[-45deg] origin-center ${
                  isDark ? 'text-gray-500' : 'text-gray-400'
                }`}
                title={asset.ticker}
              >
                {asset.ticker.slice(0, 4)}
              </div>
            ))}
          </div>
          
          {/* Rows */}
          {filteredAssets.map((rowAsset, ri) => (
            <div key={rowAsset.id} className="flex items-center">
              <div className={`w-12 shrink-0 text-[9px] font-mono text-right pr-2 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                {rowAsset.ticker.slice(0, 5)}
              </div>
              {filteredAssets.map((colAsset, ci) => {
                const val = matrix[filteredIndices[ri]]?.[filteredIndices[ci]] ?? 0;
                const isHovered = hoveredCell?.i === ri && hoveredCell?.j === ci;
                return (
                  <div
                    key={colAsset.id}
                    className={`w-8 h-8 rounded-sm cursor-pointer transition-all ${getColor(val)} ${
                      isHovered ? 'ring-2 ring-accent-blue scale-110 z-10' : ''
                    }`}
                    onMouseEnter={() => setHoveredCell({ i: ri, j: ci })}
                    onMouseLeave={() => setHoveredCell(null)}
                    onClick={() => navigate(`/pair/${rowAsset.ticker}/${colAsset.ticker}`)}
                    title={`${rowAsset.ticker} × ${colAsset.ticker}: ${val.toFixed(3)}`}
                  />
                );
              })}
            </div>
          ))}
        </div>
      </div>
      
      {/* Legend */}
      <div className="flex items-center gap-4 mt-4">
        <span className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Legend:</span>
        <div className="flex items-center gap-1">
          <div className="w-4 h-3 rounded-sm bg-red-500/60" />
          <span className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>-1.0</span>
        </div>
        <div className="flex items-center gap-1">
          <div className={`w-4 h-3 rounded-sm ${isDark ? 'bg-gray-500/20' : 'bg-gray-300/40'}`} />
          <span className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>0.0</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-4 h-3 rounded-sm bg-green-500/60" />
          <span className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>+1.0</span>
        </div>
        {hoveredCell && (
          <span className={`text-xs ml-auto font-mono ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
            {filteredAssets[hoveredCell.i]?.ticker} × {filteredAssets[hoveredCell.j]?.ticker}: {
              (matrix[filteredIndices[hoveredCell.i]]?.[filteredIndices[hoveredCell.j]] ?? 0).toFixed(3)
            }
          </span>
        )}
      </div>
    </div>
  );
}
