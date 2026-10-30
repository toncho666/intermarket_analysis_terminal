import pytest
import pandas as pd
import numpy as np
from app.services.correlation_service import CorrelationService


class TestCorrelationService:
    
    def setup_method(self):
        self.service = CorrelationService()
        
        # Create test data
        np.random.seed(42)
        n = 200
        dates = pd.date_range('2023-01-01', periods=n, freq='D')
        
        # Two correlated series
        base = np.cumsum(np.random.randn(n) * 0.01)
        noise_a = np.cumsum(np.random.randn(n) * 0.005)
        noise_b = np.cumsum(np.random.randn(n) * 0.005)
        
        self.series_a = pd.Series(100 * np.exp(base + noise_a), index=dates)
        self.series_b = pd.Series(100 * np.exp(base + noise_b), index=dates)
        
        # Uncorrelated series
        self.series_c = pd.Series(100 * np.exp(np.cumsum(np.random.randn(n) * 0.01)), index=dates)
    
    def test_rolling_correlation_pearson(self):
        result = self.service.calculate_rolling_correlation(
            self.series_a, self.series_b, window=60, method='pearson'
        )
        
        assert not result.empty
        assert 'correlation' in result.columns
        assert 'ci_low' in result.columns
        assert 'ci_high' in result.columns
        
        # Correlated series should have high correlation
        assert result['correlation'].mean() > 0.5
    
    def test_rolling_correlation_spearman(self):
        result = self.service.calculate_rolling_correlation(
            self.series_a, self.series_b, window=60, method='spearman'
        )
        
        assert not result.empty
        assert result['correlation'].mean() > 0.5
    
    def test_uncorrelated_series(self):
        result = self.service.calculate_rolling_correlation(
            self.series_a, self.series_c, window=60, method='pearson'
        )
        
        # Uncorrelated series should have low correlation
        assert abs(result['correlation'].mean()) < 0.3
    
    def test_confidence_intervals(self):
        result = self.service.calculate_rolling_correlation(
            self.series_a, self.series_b, window=60
        )
        
        # CI should contain the correlation value
        for _, row in result.iterrows():
            assert row['ci_low'] <= row['correlation'] <= row['ci_high']
    
    def test_correlation_delta(self):
        delta = self.service.calculate_correlation_delta(0.8, 0.6)
        assert delta == 0.2
        
        delta = self.service.calculate_correlation_delta(-0.5, -0.3)
        assert delta == -0.2
    
    def test_detect_correlation_anomaly(self):
        # Create series with an anomaly
        correlations = pd.Series(
            [0.5] * 100 + [0.9] + [0.5] * 99,
            index=pd.date_range('2023-01-01', periods=200, freq='D')
        )
        
        anomalies = self.service.detect_correlation_anomaly(
            correlations, window=50, threshold=2.0
        )
        
        # Should detect at least one anomaly
        assert len(anomalies) > 0
    
    def test_lead_lag_correlation(self):
        result = self.service.calculate_lead_lag_correlation(
            self.series_a, self.series_b, max_lag=5
        )
        
        assert isinstance(result, dict)
        assert len(result) == 11  # -5 to +5
        assert 0 in result  # Zero lag should exist
    
    def test_insufficient_data(self):
        short_series = self.series_a.iloc[:10]
        result = self.service.calculate_rolling_correlation(
            short_series, self.series_b.iloc[:10], window=60
        )
        
        assert result.empty


class TestCorrelationMatrix:
    
    def setup_method(self):
        self.service = CorrelationService()
        
        np.random.seed(42)
        n = 200
        dates = pd.date_range('2023-01-01', periods=n, freq='D')
        
        # Create returns DataFrame
        returns = pd.DataFrame({
            'SPX': np.random.randn(n) * 0.01,
            'NDX': np.random.randn(n) * 0.012,
            'VIX': np.random.randn(n) * 0.02,
            'GOLD': np.random.randn(n) * 0.008,
        }, index=dates)
        
        self.returns_df = returns
    
    def test_correlation_matrix(self):
        matrix = self.service.calculate_correlation_matrix(
            self.returns_df, window=60
        )
        
        assert not matrix.empty
        # Should be square
        assert matrix.shape[0] == matrix.shape[1]
    
    def test_partial_correlation(self):
        partial = self.service.calculate_partial_correlation(
            self.returns_df, 'SPX', 'NDX'
        )
        
        assert isinstance(partial, float)
        assert -1 <= partial <= 1
