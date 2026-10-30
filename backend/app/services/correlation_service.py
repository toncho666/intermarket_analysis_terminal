"""
Correlation calculation service
- Rolling Pearson/Spearman correlations
- Fisher z confidence intervals
- Delta vs previous period
- Correlation matrix generation
"""
import numpy as np
import pandas as pd
from typing import List, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CorrelationService:
    """Service for calculating cross-asset correlations"""
    
    @staticmethod
    def pearson_correlation(x: np.ndarray, y: np.ndarray) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(x) != len(y) or len(x) < 3:
            return 0.0
        return float(np.corrcoef(x, y)[0, 1])
    
    @staticmethod
    def spearman_correlation(x: np.ndarray, y: np.ndarray) -> float:
        """Calculate Spearman rank correlation"""
        from scipy.stats import spearmanr
        if len(x) != len(y) or len(x) < 3:
            return 0.0
        corr, _ = spearmanr(x, y)
        return float(corr)
    
    @staticmethod
    def fisher_z_ci(r: float, n: int, confidence: float = 0.95) -> Tuple[float, float]:
        """
        Calculate Fisher z-transform confidence interval for correlation
        """
        if n < 4:
            return (-1.0, 1.0)
        
        # Fisher z-transform
        z = np.arctanh(r)
        
        # Standard error
        se = 1.0 / np.sqrt(n - 3)
        
        # Z-score for confidence level
        from scipy.stats import norm
        z_score = norm.ppf((1 + confidence) / 2)
        
        # CI in z-space
        z_low = z - z_score * se
        z_high = z + z_score * se
        
        # Transform back to correlation space
        r_low = np.tanh(z_low)
        r_high = np.tanh(z_high)
        
        return (float(r_low), float(r_high))
    
    @staticmethod
    def rolling_correlation(
        prices_a: pd.Series,
        prices_b: pd.Series,
        window: int = 60,
        method: str = "pearson"
    ) -> pd.DataFrame:
        """
        Calculate rolling correlation between two price series
        
        Returns DataFrame with columns: ts, correlation, ci_low, ci_high
        """
        # Calculate log returns
        returns_a = np.log(prices_a / prices_a.shift(1)).dropna()
        returns_b = np.log(prices_b / prices_b.shift(1)).dropna()
        
        # Align indices
        common_idx = returns_a.index.intersection(returns_b.index)
        returns_a = returns_a.loc[common_idx]
        returns_b = returns_b.loc[common_idx]
        
        results = []
        
        for i in range(window, len(returns_a)):
            window_a = returns_a.iloc[i-window:i].values
            window_b = returns_b.iloc[i-window:i].values
            
            # Remove NaN
            mask = ~(np.isnan(window_a) | np.isnan(window_b))
            window_a = window_a[mask]
            window_b = window_b[mask]
            
            if len(window_a) < 10:
                continue
            
            # Calculate correlation
            if method == "spearman":
                corr = CorrelationService.spearman_correlation(window_a, window_b)
            else:
                corr = CorrelationService.pearson_correlation(window_a, window_b)
            
            # Calculate CI
            ci_low, ci_high = CorrelationService.fisher_z_ci(corr, len(window_a))
            
            results.append({
                'ts': returns_a.index[i],
                'correlation': corr,
                'ci_low': ci_low,
                'ci_high': ci_high,
                'n_obs': len(window_a)
            })
        
        return pd.DataFrame(results)
    
    @staticmethod
    def correlation_matrix(
        returns_df: pd.DataFrame,
        window: int = 60,
        method: str = "pearson"
    ) -> pd.DataFrame:
        """
        Calculate correlation matrix for multiple assets
        
        Args:
            returns_df: DataFrame with asset returns (columns = assets)
            window: rolling window size
            method: pearson or spearman
        
        Returns:
            Correlation matrix (DataFrame)
        """
        # Use last `window` observations
        recent_returns = returns_df.iloc[-window:]
        
        if method == "spearman":
            corr_matrix = recent_returns.corr(method='spearman')
        else:
            corr_matrix = recent_returns.corr(method='pearson')
        
        return corr_matrix
    
    @staticmethod
    def correlation_delta(
        current_corr: float,
        previous_corr: float
    ) -> float:
        """Calculate change in correlation"""
        return current_corr - previous_corr
    
    @staticmethod
    def exponential_weighted_correlation(
        prices_a: pd.Series,
        prices_b: pd.Series,
        span: int = 60
    ) -> pd.Series:
        """
        Calculate exponentially weighted moving correlation
        """
        returns_a = np.log(prices_a / prices_a.shift(1))
        returns_b = np.log(prices_b / prices_b.shift(1))
        
        # EWMA correlation
        ewm_corr = returns_a.ewm(span=span).corr(returns_b.ewm(span=span))
        
        return ewm_corr
    
    @staticmethod
    def partial_correlation(
        returns_df: pd.DataFrame,
        asset_a: str,
        asset_b: str
    ) -> float:
        """
        Calculate partial correlation between two assets controlling for all others
        Uses inverse of correlation matrix
        """
        corr_matrix = returns_df.corr()
        
        try:
            # Precision matrix (inverse of correlation matrix)
            precision_matrix = np.linalg.inv(corr_matrix.values)
            
            # Get indices
            idx_a = list(corr_matrix.columns).index(asset_a)
            idx_b = list(corr_matrix.columns).index(asset_b)
            
            # Partial correlation
            partial_corr = -precision_matrix[idx_a, idx_b] / np.sqrt(
                precision_matrix[idx_a, idx_a] * precision_matrix[idx_b, idx_b]
            )
            
            return float(partial_corr)
        except np.linalg.LinAlgError:
            logger.warning("Singular matrix in partial correlation calculation")
            return 0.0
    
    @staticmethod
    def lead_lag_correlation(
        prices_a: pd.Series,
        prices_b: pd.Series,
        max_lag: int = 5,
        window: int = 60
    ) -> pd.DataFrame:
        """
        Calculate cross-correlation with lags
        Positive lag: B leads A
        Negative lag: A leads B
        """
        returns_a = np.log(prices_a / prices_a.shift(1)).dropna()
        returns_b = np.log(prices_b / prices_b.shift(1)).dropna()
        
        results = []
        
        for lag in range(-max_lag, max_lag + 1):
            if lag > 0:
                # B leads A
                shifted_b = returns_b.shift(lag)
            elif lag < 0:
                # A leads B
                shifted_a = returns_a.shift(-lag)
                shifted_b = returns_b
            else:
                shifted_a = returns_a
                shifted_b = returns_b
            
            # Calculate correlation on rolling window
            rolling_corr = shifted_a.rolling(window).corr(shifted_b)
            
            results.append({
                'lag': lag,
                'mean_correlation': rolling_corr.mean(),
                'last_correlation': rolling_corr.iloc[-1] if len(rolling_corr) > 0 else 0
            })
        
        return pd.DataFrame(results)


# Singleton instance
correlation_service = CorrelationService()
