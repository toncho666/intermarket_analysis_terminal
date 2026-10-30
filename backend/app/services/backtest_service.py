import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import structlog

logger = structlog.get_logger()


class BacktestService:
    """Service for strategy backtesting."""
    
    def __init__(self):
        self.model_version = "v1.0"
    
    def mean_reversion_backtest(
        self,
        series_a: pd.Series,
        series_b: pd.Series,
        entry_z: float = 2.0,
        exit_z: float = 0.5,
        window: int = 60,
        transaction_cost: float = 0.001
    ) -> Dict:
        """
        Backtest mean reversion strategy on spread z-score.
        
        Logic:
        - Enter long spread when z > entry_z
        - Enter short spread when z < -entry_z
        - Exit when |z| < exit_z
        """
        # Calculate spread z-score
        spread = series_a - series_b
        rolling_mean = spread.rolling(window=window).mean()
        rolling_std = spread.rolling(window=window).std()
        z_score = (spread - rolling_mean) / rolling_std
        
        # Generate signals
        position = 0
        trades = []
        equity = [100.0]
        dates = [series_a.index[window]]
        
        for i in range(window + 1, len(series_a)):
            z = z_score.iloc[i]
            
            if pd.isna(z):
                equity.append(equity[-1])
                dates.append(series_a.index[i])
                continue
            
            # Entry signals
            if position == 0:
                if z > entry_z:
                    position = -1  # Short spread
                    trades.append({
                        'entry_date': series_a.index[i],
                        'entry_z': round(z, 2),
                        'direction': 'short',
                        'entry_price_a': series_a.iloc[i],
                        'entry_price_b': series_b.iloc[i],
                    })
                elif z < -entry_z:
                    position = 1  # Long spread
                    trades.append({
                        'entry_date': series_a.index[i],
                        'entry_z': round(z, 2),
                        'direction': 'long',
                        'entry_price_a': series_a.iloc[i],
                        'entry_price_b': series_b.iloc[i],
                    })
            
            # Exit signals
            elif position == 1 and z > -exit_z:
                # Close long
                pnl = (series_a.iloc[i] - series_a.iloc[i-1]) - (series_b.iloc[i] - series_b.iloc[i-1])
                pnl -= transaction_cost * 2
                equity.append(equity[-1] * (1 + pnl / 100))
                trades[-1]['exit_date'] = series_a.index[i]
                trades[-1]['exit_z'] = round(z, 2)
                trades[-1]['pnl'] = round(pnl, 4)
                position = 0
            
            elif position == -1 and z < exit_z:
                # Close short
                pnl = (series_b.iloc[i] - series_b.iloc[i-1]) - (series_a.iloc[i] - series_a.iloc[i-1])
                pnl -= transaction_cost * 2
                equity.append(equity[-1] * (1 + pnl / 100))
                trades[-1]['exit_date'] = series_a.index[i]
                trades[-1]['exit_z'] = round(z, 2)
                trades[-1]['pnl'] = round(pnl, 4)
                position = 0
            
            else:
                # Hold position
                if position == 1:
                    daily_pnl = (series_a.iloc[i] - series_a.iloc[i-1]) - (series_b.iloc[i] - series_b.iloc[i-1])
                elif position == -1:
                    daily_pnl = (series_b.iloc[i] - series_b.iloc[i-1]) - (series_a.iloc[i] - series_a.iloc[i-1])
                else:
                    daily_pnl = 0
                
                equity.append(equity[-1] * (1 + daily_pnl / 100))
            
            dates.append(series_a.index[i])
        
        # Close any open position at end
        if position != 0 and trades:
            trades[-1]['exit_date'] = series_a.index[-1]
            trades[-1]['exit_z'] = round(z_score.iloc[-1], 2)
            trades[-1]['pnl'] = 0
        
        # Calculate metrics
        equity_series = pd.Series(equity, index=dates)
        metrics = self._calculate_metrics(equity_series, trades)
        
        return {
            'equity_curve': [{'ts': d.isoformat(), 'value': round(v, 2)} for d, v in zip(dates, equity)],
            'trades': trades,
            'metrics': metrics,
            'model_version': self.model_version
        }
    
    def momentum_backtest(
        self,
        series: pd.Series,
        lookback: int = 20,
        threshold: float = 0.02,
        transaction_cost: float = 0.001
    ) -> Dict:
        """
        Backtest momentum strategy.
        
        Logic:
        - Long when ROC(lookback) > threshold
        - Short when ROC(lookback) < -threshold
        - Flat otherwise
        """
        returns = series.pct_change()
        roc = series.pct_change(lookback)
        
        position = 0
        trades = []
        equity = [100.0]
        dates = [series.index[lookback]]
        
        for i in range(lookback + 1, len(series)):
            r = roc.iloc[i]
            
            if pd.isna(r):
                equity.append(equity[-1])
                dates.append(series.index[i])
                continue
            
            # Entry
            if position == 0:
                if r > threshold:
                    position = 1
                    trades.append({
                        'entry_date': series.index[i],
                        'direction': 'long',
                        'entry_price': series.iloc[i],
                    })
                elif r < -threshold:
                    position = -1
                    trades.append({
                        'entry_date': series.index[i],
                        'direction': 'short',
                        'entry_price': series.iloc[i],
                    })
            
            # Exit (reverse signal or flat)
            elif position == 1 and r < 0:
                pnl = returns.iloc[i] - transaction_cost
                equity.append(equity[-1] * (1 + pnl))
                trades[-1]['exit_date'] = series.index[i]
                trades[-1]['pnl'] = round(pnl * 100, 4)
                position = 0
            
            elif position == -1 and r > 0:
                pnl = -returns.iloc[i] - transaction_cost
                equity.append(equity[-1] * (1 + pnl))
                trades[-1]['exit_date'] = series.index[i]
                trades[-1]['pnl'] = round(pnl * 100, 4)
                position = 0
            
            else:
                if position == 1:
                    daily_pnl = returns.iloc[i] - transaction_cost / lookback
                elif position == -1:
                    daily_pnl = -returns.iloc[i] - transaction_cost / lookback
                else:
                    daily_pnl = 0
                
                equity.append(equity[-1] * (1 + daily_pnl))
            
            dates.append(series.index[i])
        
        equity_series = pd.Series(equity, index=dates)
        metrics = self._calculate_metrics(equity_series, trades)
        
        return {
            'equity_curve': [{'ts': d.isoformat(), 'value': round(v, 2)} for d, v in zip(dates, equity)],
            'trades': trades,
            'metrics': metrics,
            'model_version': self.model_version
        }
    
    def lead_lag_backtest(
        self,
        leader: pd.Series,
        lagger: pd.Series,
        lag_days: int = 2,
        threshold: float = 0.03,
        transaction_cost: float = 0.001
    ) -> Dict:
        """
        Backtest lead-lag strategy.
        
        Logic:
        - If leader moved > threshold, trade lagger in same direction after lag_days
        """
        leader_returns = leader.pct_change()
        lagger_returns = lagger.pct_change()
        
        position = 0
        trades = []
        equity = [100.0]
        dates = [leader.index[lag_days]]
        
        for i in range(lag_days + 1, len(leader)):
            leader_signal = leader_returns.iloc[i - lag_days]
            
            if pd.isna(leader_signal):
                equity.append(equity[-1])
                dates.append(leader.index[i])
                continue
            
            # Entry based on leader's signal
            if position == 0:
                if leader_signal > threshold:
                    position = 1
                    trades.append({
                        'entry_date': leader.index[i],
                        'direction': 'long',
                        'leader_signal': round(leader_signal * 100, 2),
                    })
                elif leader_signal < -threshold:
                    position = -1
                    trades.append({
                        'entry_date': leader.index[i],
                        'direction': 'short',
                        'leader_signal': round(leader_signal * 100, 2),
                    })
            
            # Exit after 1 day or reverse signal
            elif position != 0:
                pnl = lagger_returns.iloc[i] * position - transaction_cost
                equity.append(equity[-1] * (1 + pnl))
                trades[-1]['exit_date'] = leader.index[i]
                trades[-1]['pnl'] = round(pnl * 100, 4)
                position = 0
                continue
            
            else:
                equity.append(equity[-1])
            
            dates.append(leader.index[i])
        
        equity_series = pd.Series(equity, index=dates)
        metrics = self._calculate_metrics(equity_series, trades)
        
        return {
            'equity_curve': [{'ts': d.isoformat(), 'value': round(v, 2)} for d, v in zip(dates, equity)],
            'trades': trades,
            'metrics': metrics,
            'model_version': self.model_version
        }
    
    def _calculate_metrics(self, equity: pd.Series, trades: List[Dict]) -> Dict:
        """Calculate performance metrics from equity curve."""
        returns = equity.pct_change().dropna()
        
        # Sharpe ratio (annualized)
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
        
        # Sortino ratio
        downside_returns = returns[returns < 0]
        sortino = (returns.mean() / downside_returns.std()) * np.sqrt(252) if len(downside_returns) > 0 and downside_returns.std() > 0 else 0
        
        # Max drawdown
        rolling_max = equity.cummax()
        drawdown = (equity - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100
        
        # Hit rate
        if trades:
            profitable = [t for t in trades if t.get('pnl', 0) > 0]
            hit_rate = len(profitable) / len(trades) * 100
        else:
            hit_rate = 0
        
        # Total return
        total_return = (equity.iloc[-1] / equity.iloc[0] - 1) * 100
        
        # Turnover (approximate)
        turnover = len(trades) / len(equity) * 252 * 100  # Annualized %
        
        return {
            'sharpe': round(sharpe, 2),
            'sortino': round(sortino, 2),
            'max_drawdown': round(max_drawdown, 2),
            'hit_rate': round(hit_rate, 1),
            'total_return': round(total_return, 2),
            'turnover': round(turnover, 1),
            'num_trades': len(trades),
        }
