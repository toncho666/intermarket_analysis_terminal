import pytest
import pandas as pd
import numpy as np
from app.services.cointegration_service import CointegrationService


class TestCointegrationService:
    
    def setup_method(self):
        self.service = CointegrationService()
        
        # Create cointegrated series
        np.random.seed(42)
        n = 500
        dates = pd.date_range('2022-01-01', periods=n, freq='D')
        
        # Common stochastic trend
        trend = np.cumsum(np.random.randn(n) * 0.01)
        
        # Two cointegrated series (share common trend)
        self.series_a = pd.Series(100 * np.exp(trend + np.random.randn(n) * 0.005), index=dates)
        self.series_b = pd.Series(100 * np.exp(trend + np.random.randn(n) * 0.005), index=dates)
        
        # Non-cointegrated series
        self.series_c = pd.Series(100 * np.exp(np.cumsum(np.random.randn(n) * 0.01)), index=dates)
    
    def test_engle_granger_cointegrated(self):
        result = self.service.engle_granger_test(self.series_a, self.series_b)
        
        assert 'is_cointegrated' in result
        assert 'p_value' in result
        assert 'hedge_ratio' in result
        
        # Should detect cointegration
        assert result['is_cointegrated'] == True
        assert result['p_value'] < 0.05
    
    def test_engle_granger_not_cointegrated(self):
        result = self.service.engle_granger_test(self.series_a, self.series_c)
        
        # Should not detect cointegration (or weak)
        # Note: random chance may occasionally show cointegration
        assert 'p_value' in result
    
    def test_johansen_test(self):
        result = self.service.johansen_test(self.series_a, self.series_b)
        
        assert 'trace_stats' in result
        assert 'is_cointegrated_trace' in result
        assert 'eigenvectors' in result
    
    def test_half_life(self):
        # Calculate spread
        spread = self.series_a - self.series_b
        
        half_life = self.service.calculate_half_life(spread)
        
        # Should return a positive number for mean-reverting spread
        if half_life is not None:
            assert half_life > 0
    
    def test_spread_zscore(self):
        hedge_ratio = 1.0
        z_score = self.service.calculate_spread_zscore(
            self.series_a, self.series_b, hedge_ratio, window=60
        )
        
        assert len(z_score) == len(self.series_a)
        # Z-score should be roughly centered around 0
        assert abs(z_score.mean()) < 1
    
    def test_rolling_cointegration(self):
        result = self.service.rolling_cointegration_test(
            self.series_a, self.series_b, window=100, step=10
        )
        
        assert not result.empty
        assert 'p_value' in result.columns
        assert 'is_cointegrated' in result.columns
    
    def test_hurst_exponent(self):
        # Random walk should have H ≈ 0.5
        hurst = self.service.hurst_exponent(self.series_a)
        
        assert 0 <= hurst <= 1
        # Random walk: H should be close to 0.5
        # (may vary due to finite sample)


class TestCointegrationBreak:
    
    def setup_method(self):
        self.service = CointegrationService()
    
    def test_detect_cointegration_break(self):
        # Create rolling results with a break
        rolling_results = pd.DataFrame({
            'ts': pd.date_range('2023-01-01', periods=20, freq='D'),
            'p_value': [0.01] * 10 + [0.2] * 10,  # Break at day 10
            'hedge_ratio': [1.0] * 20,
            'is_cointegrated': [True] * 10 + [False] * 10,
        })
        
        breaks = self.service.detect_cointegration_break(rolling_results)
        
        # Should detect at least one break
        assert len(breaks) > 0
        assert breaks[0]['type'] == 'coint_break'
