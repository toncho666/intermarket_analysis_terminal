"""
Backtest engine service
- Mean reversion strategy
- Momentum strategy
- Lead-lag strategy
- Performance metrics (Sharpe, Sortino, MaxDD, Hit Rate, etc.)
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BacktestService:
    """Service for strategy backtesting"""
    
    @staticmethod
    def mean_reversion_backtest(
        prices_a: pd.Series,
        prices_b: pd.Series,
        entry_z: float = 2.0,
        exit_z: float = 0.5,
        window: int = 60,
        transaction_cost: float = 0.001,
        initial_capital: float = 100000,
    ) -> Dict[str, Any]:
        """
        Mean reversion strategy on spread z-score
        
        Entry: |z| > entry_z → open position
        Exit: |z| < exit_z → close position
        """
        # Calculate spread z-score
        spread = prices_a - prices_b  # Simplified; should use hedge ratio
        rolling_mean = spread.rolling(window=window).mean()
        rolling_std = spread.rolling(window=window).std()
        z_score = (spread - rolling_mean) / rolling_std
        
        # Generate signals
        position = 0  # 0 = flat, 1 = long spread, -1 = short spread
        trades = []
        equity = [initial_capital]
        
        for i in range(window, len(z_score)):
            z = z_score.iloc[i]
            
            if pd.isna(z):
                equity.append(equity[-1])
                continue
            
            # Entry signals
            if position == 0:
                if z > entry_z:
                    position = -1  # Short spread (expect mean reversion down)
                    trades.append({
                        'ts': prices_a.index[i],
                        'action': 'entry',
                        'direction': 'short',
                        'z_score': float(z),
                        'price': float(prices_a.iloc[i]),
                    })
                elif z < -entry_z:
                    position = 1  # Long spread
                    trades.append({
                        'ts': prices_a.index[i],
                        'action': 'entry',
                        'direction': 'long',
                        'z_score': float(z),
                        'price': float(prices_a.iloc[i]),
                    })
            
            # Exit signals
            elif position != 0:
                if abs(z) < exit_z:
                    trades.append({
                        'ts': prices_a.index[i],
                        'action': 'exit',
                        'direction': 'close',
                        'z_score': float(z),
                        'price': float(prices_a.iloc[i]),
                    })
                    position = 0
            
            # Calculate P&L
            if i > 0 and position != 0:
                ret_a = prices_a.iloc[i] / prices_a.iloc[i-1] - 1
                ret_b = prices_b.iloc[i] / prices_b.iloc[i-1] - 1
                spread_return = ret_a - ret_b
                pnl = position * spread_return * initial_capital * 0.1  # 10% of capital per trade
                pnl -= abs(pnl) * transaction_cost  # Transaction cost
                equity.append(equity[-1] + pnl)
            else:
                equity.append(equity[-1])
        
        # Calculate metrics
        equity_series = pd.Series(equity, index=prices_a.index[:len(equity)])
        metrics = BacktestService.calculate_metrics(equity_series, trades)
        
        return {
            'equity_curve': [{'ts': str(idx), 'value': round(val, 2)} for idx, val in zip(equity_series.index, equity_series.values)],
            'trades': trades,
            'metrics': metrics,
        }
    
    @staticmethod
    def momentum_backtest(
        prices: pd.Series,
        lookback: int = 20,
        threshold: float = 0.02,
        transaction_cost: float = 0.001,
        initial_capital: float = 100000,
    ) -> Dict[str, Any]:
        """
        Momentum strategy: follow the trend
        
        Entry: ROC > threshold → long
        Exit: ROC < -threshold → close
        """
        # Rate of change
        roc = prices.pct_change(lookback)
        
        position = 0
        trades = []
        equity = [initial_capital]
        
        for i in range(lookback, len(roc)):
            r = roc.iloc[i]
            
            if pd.isna(r):
                equity.append(equity[-1])
                continue
            
            # Entry
            if position == 0 and r > threshold:
                position = 1
                trades.append({
                    'ts': prices.index[i],
                    'action': 'entry',
                    'direction': 'long',
                    'roc': float(r),
                    'price': float(prices.iloc[i]),
                })
            
            # Exit
            elif position == 1 and r < -threshold:
                position = 0
                trades.append({
                    'ts': prices.index[i],
                    'action': 'exit',
                    'direction': 'close',
                    'roc': float(r),
                    'price': float(prices.iloc[i]),
                })
            
            # P&L
            if i > 0 and position == 1:
                ret = prices.iloc[i] / prices.iloc[i-1] - 1
                pnl = ret * initial_capital
                pnl -= abs(pnl) * transaction_cost
                equity.append(equity[-1] + pnl)
            else:
                equity.append(equity[-1])
        
        equity_series = pd.Series(equity, index=prices.index[:len(equity)])
        metrics = BacktestService.calculate_metrics(equity_series, trades)
        
        return {
            'equity_curve': [{'ts': str(idx), 'value': round(val, 2)} for idx, val in zip(equity_series.index, equity_series.values)],
            'trades': trades,
            'metrics': metrics,
        }
    
    @staticmethod
    def lead_lag_backtest(
        prices_leader: pd.Series,
        prices_follower: pd.Series,
        lag_days: int = 2,
        threshold: float = 0.03,
        transaction_cost: float = 0.001,
        initial_capital: float = 100000,
    ) -> Dict[str, Any]:
        """
        Lead-lag strategy: if leader moves > threshold, trade follower in same direction
        """
        leader_returns = prices_leader.pct_change()
        
        position = 0
        trades = []
        equity = [initial_capital]
        
        for i in range(lag_days, len(prices_follower)):
            leader_ret = leader_returns.iloc[i - lag_days]
            
            if pd.isna(leader_ret):
                equity.append(equity[-1])
                continue
            
            # Entry
            if position == 0 and abs(leader_ret) > threshold:
                position = 1 if leader_ret > 0 else -1
                trades.append({
                    'ts': prices_follower.index[i],
                    'action': 'entry',
                    'direction': 'long' if position == 1 else 'short',
                    'leader_return': float(leader_ret),
                    'price': float(prices_follower.iloc[i]),
                })
            
            # Exit after 5 days or reverse signal
            elif position != 0:
                if i >= 5:
                    recent_leader_ret = leader_returns.iloc[i - lag_days - 5:i - lag_days].mean()
                    if (position == 1 and recent_leader_ret < -threshold) or \
                       (position == -1 and recent_leader_ret > threshold):
                        position = 0
                        trades.append({
                            'ts': prices_follower.index[i],
                            'action': 'exit',
                            'direction': 'close',
                            'price': float(prices_follower.iloc[i]),
                        })
            
            # P&L
            if i > 0 and position != 0:
                ret = prices_follower.iloc[i] / prices_follower.iloc[i-1] - 1
                pnl = position * ret * initial_capital
                pnl -= abs(pnl) * transaction_cost
                equity.append(equity[-1] + pnl)
            else:
                equity.append(equity[-1])
        
        equity_series = pd.Series(equity, index=prices_follower.index[:len(equity)])
        metrics = BacktestService.calculate_metrics(equity_series, trades)
        
        return {
            'equity_curve': [{'ts': str(idx), 'value': round(val, 2)} for idx, val in zip(equity_series.index, equity_series.values)],
            'trades': trades,
            'metrics': metrics,
        }
    
    @staticmethod
    def calculate_metrics(
        equity_curve: pd.Series,
        trades: List[Dict[str, Any]],
        risk_free_rate: float = 0.02,
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive performance metrics
        """
        if len(equity_curve) < 2:
            return {
                'sharpe': 0, 'sortino': 0, 'max_drawdown': 0,
                'hit_rate': 0, 'total_return': 0, 'turnover': 0,
            }
        
        # Returns
        returns = equity_curve.pct_change().dropna()
        
        # Annualized metrics
        n_days = len(returns)
        n_years = n_days / 252
        
        # Total return
        total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
        
        # Annualized return
        ann_return = (1 + total_return) ** (1 / n_years) - 1 if n_years > 0 else 0
        
        # Sharpe ratio
        excess_returns = returns - risk_free_rate / 252
        sharpe = np.sqrt(252) * excess_returns.mean() / excess_returns.std() if excess_returns.std() > 0 else 0
        
        # Sortino ratio (downside deviation)
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() if len(downside_returns) > 0 else 0
        sortino = np.sqrt(252) * (returns.mean() - risk_free_rate / 252) / downside_std if downside_std > 0 else 0
        
        # Max drawdown
        cummax = equity_curve.cummax()
        drawdown = (equity_curve - cummax) / cummax
        max_drawdown = drawdown.min()
        
        # Calmar ratio
        calmar = ann_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Hit rate (from trades)
        entry_trades = [t for t in trades if t['action'] == 'entry']
        exit_trades = [t for t in trades if t['action'] == 'exit']
        n_round_trips = min(len(entry_trades), len(exit_trades))
        
        profitable_trades = 0
        for i in range(n_round_trips):
            entry_price = entry_trades[i].get('price', 0)
            exit_price = exit_trades[i].get('price', 0)
            if entry_trades[i]['direction'] == 'long':
                if exit_price > entry_price:
                    profitable_trades += 1
            else:
                if exit_price < entry_price:
                    profitable_trades += 1
        
        hit_rate = profitable_trades / n_round_trips if n_round_trips > 0 else 0
        
        # Profit factor
        gross_profit = sum(
            exit_trades[i].get('price', 0) - entry_trades[i].get('price', 0)
            for i in range(n_round_trips)
            if exit_trades[i].get('price', 0) > entry_trades[i].get('price', 0)
        )
        gross_loss = abs(sum(
            exit_trades[i].get('price', 0) - entry_trades[i].get('price', 0)
            for i in range(n_round_trips)
            if exit_trades[i].get('price', 0) < entry_trades[i].get('price', 0)
        ))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Turnover (approximate)
        turnover = len(trades) / n_days * 100 if n_days > 0 else 0
        
        return {
            'sharpe': round(float(sharpe), 3),
            'sortino': round(float(sortino), 3),
            'max_drawdown': round(float(max_drawdown * 100), 2),
            'hit_rate': round(float(hit_rate * 100), 1),
            'total_return': round(float(total_return * 100), 2),
            'annualized_return': round(float(ann_return * 100), 2),
            'calmar': round(float(calmar), 3),
            'profit_factor': round(float(profit_factor), 2) if profit_factor != float('inf') else 999.99,
            'turnover': round(float(turnover), 1),
            'n_trades': len(trades),
            'n_round_trips': n_round_trips,
        }


# Singleton instance
backtest_service = BacktestService()
