import pytest
import pandas as pd
import numpy as np
from app.services.backtest_service import BacktestService


class TestBacktestService:
    
    def setup_method(self):
        self.service = BacktestService()
        
        # Create test price data
        np.random.seed(42)
        n = 500
        dates = pd.date_range('2022-01-01', periods=n, freq='D')
        
        # Mean-reverting spread
        trend = np.cumsum(np.random.randn(n) * 0.01)
        self.series_a = pd.Series(100 * np.exp(trend + np.random.randn(n) * 0.005), index=dates)
        self.series_b = pd.Series(100 * np.exp(trend + np.random.randn(n) * 0.005), index=dates)
        
        # Trending series for momentum
        self.series_trend = pd.Series(
            100 * np.exp(np.cumsum(np.random.randn(n) * 0.005 + 0.0002)),
            index=dates
        )
    
    def test_mean_reversion_backtest(self):
        result = self.service.mean_reversion_backtest(
            self.series_a, self.series_b,
            entry_z=2.0, exit_z=0.5, window=60
        )
        
        assert 'equity_curve' in result
        assert 'trades' in result
        assert 'metrics' in result
        
        # Check metrics
        metrics = result['metrics']
        assert 'sharpe' in metrics
        assert 'sortino' in metrics
        assert 'max_drawdown' in metrics
        assert 'hit_rate' in metrics
        assert 'total_return' in metrics
        
        # Equity curve should start at 100
        assert result['equity_curve'][0]['value'] == 100.0
    
    def test_momentum_backtest(self):
        result = self.service.momentum_backtest(
            self.series_trend,
            lookback=20,
            threshold=0.02
        )
        
        assert 'equity_curve' in result
        assert 'trades' in result
        assert 'metrics' in result
        
        metrics = result['metrics']
        assert metrics['num_trades'] >= 0
    
    def test_lead_lag_backtest(self):
        result = self.service.lead_lag_backtest(
            self.series_a, self.series_b,
            lag_days=2, threshold=0.03
        )
        
        assert 'equity_curve' in result
        assert 'trades' in result
        assert 'metrics' in result
    
    def test_metrics_calculation(self):
        # Create simple equity curve
        equity = pd.Series([100, 102, 101, 105, 103, 108], 
                          index=pd.date_range('2023-01-01', periods=6))
        trades = [
            {'pnl': 2.0},
            {'pnl': -1.0},
            {'pnl': 4.0},
            {'pnl': -2.0},
            {'pnl': 5.0},
        ]
        
        metrics = self.service._calculate_metrics(equity, trades)
        
        assert 'sharpe' in metrics
        assert 'sortino' in metrics
        assert 'max_drawdown' in metrics
        assert 'hit_rate' in metrics
        assert 'total_return' in metrics
        
        # Total return should be positive
        assert metrics['total_return'] > 0
        
        # Hit rate: 3 profitable out of 5 = 60%
        assert metrics['hit_rate'] == 60.0
    
    def test_max_drawdown_calculation(self):
        # Create equity curve with known drawdown
        equity = pd.Series([100, 110, 105, 95, 100, 120],
                          index=pd.date_range('2023-01-01', periods=6))
        
        metrics = self.service._calculate_metrics(equity, [])
        
        # Max drawdown from 110 to 95 = -13.6%
        assert metrics['max_drawdown'] < 0
        assert metrics['max_drawdown'] > -20
    
    def test_transaction_costs(self):
        # Run with and without transaction costs
        result_no_cost = self.service.mean_reversion_backtest(
            self.series_a, self.series_b,
            entry_z=2.0, exit_z=0.5, window=60,
            transaction_cost=0.0
        )
        
        result_with_cost = self.service.mean_reversion_backtest(
            self.series_a, self.series_b,
            entry_z=2.0, exit_z=0.5, window=60,
            transaction_cost=0.005
        )
        
        # With costs should have lower or equal return
        assert result_with_cost['metrics']['total_return'] <= result_no_cost['metrics']['total_return']
    
    def test_empty_trades(self):
        # Series that won't generate trades
        flat_series = pd.Series([100] * 200, 
                               index=pd.date_range('2023-01-01', periods=200))
        
        result = self.service.mean_reversion_backtest(
            flat_series, flat_series,
            entry_z=2.0, exit_z=0.5, window=60
        )
        
        # Should handle gracefully
        assert 'metrics' in result
        assert result['metrics']['num_trades'] == 0
        assert result['metrics']['hit_rate'] == 0
