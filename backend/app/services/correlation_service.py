import pandas as pd
import numpy as np
from scipy import stats
from typing import List, Dict, Tuple, Optional
import structlog

logger = structlog.get_logger()


class CorrelationService:
    """Service for calculating cross-asset correlations."""
    
    def __init__(self):
        self.model_version = "v1.0"
    
    def calculate_rolling_correlation(
        self,
        series_a: pd.Series,
        series_b: pd.Series,
        window: int = 60,
        method: str = "pearson"
    ) -> pd.DataFrame:
        """
        Calculate rolling correlation between two series.
        
        Args:
            series_a: First price/return series
            series_b: Second price/return series
            window: Rolling window size in days
            method: 'pearson', 'spearman', or 'kendall'
        
        Returns:
            DataFrame with columns: ts, correlation, ci_low, ci_high
        """
        # Calculate log returns
        returns_a = np.log(series_a / series_a.shift(1)).dropna()
        returns_b = np.log(series_b / series_b.shift(1)).dropna()
        
        # Align series
        aligned = pd.concat([returns_a, returns_b], axis=1).dropna()
        aligned.columns = ['a', 'b']
        
        if len(aligned) < window:
            logger.warning("Insufficient data for correlation calculation")
            return pd.DataFrame()
        
        results = []
        
        for i in range(window, len(aligned)):
            window_data = aligned.iloc[i-window:i]
            
            if method == "pearson":
                corr, p_value = stats.pearsonr(window_data['a'], window_data['b'])
            elif method == "spearman":
                corr, p_value = stats.spearmanr(window_data['a'], window_data['b'])
            elif method == "kendall":
                corr, p_value = stats.kendalltau(window_data['a'], window_data['b'])
            else:
                raise ValueError(f"Unknown method: {method}")
            
            # Fisher z-transform for confidence interval
            z = np.arctanh(corr)
            se = 1 / np.sqrt(window - 3)
            z_low = z - 1.96 * se
            z_high = z + 1.96 * se
            ci_low = np.tanh(z_low)
            ci_high = np.tanh(z_high)
            
            results.append({
                'ts': aligned.index[i],
                'correlation': round(corr, 4),
                'p_value': round(p_value, 4),
                'ci_low': round(ci_low, 4),
                'ci_high': round(ci_high, 4),
            })
        
        return pd.DataFrame(results)
    
    def calculate_correlation_matrix(
        self,
        returns_df: pd.DataFrame,
        window: int = 60,
        method: str = "pearson"
    ) -> pd.DataFrame:
        """
        Calculate correlation matrix for multiple assets.
        
        Args:
            returns_df: DataFrame with asset returns as columns
            window: Rolling window size
            method: Correlation method
        
        Returns:
            Correlation matrix as DataFrame
        """
        if method == "pearson":
            return returns_df.rolling(window=window).corr()
        elif method == "spearman":
            return returns_df.rolling(window=window).corr(method='spearman')
        else:
            raise ValueError(f"Matrix correlation not supported for {method}")
    
    def calculate_partial_correlation(
        self,
        returns_df: pd.DataFrame,
        asset_a: str,
        asset_b: str
    ) -> float:
        """
        Calculate partial correlation between two assets controlling for all others.
        
        Uses precision matrix (inverse of covariance matrix).
        """
        cov_matrix = returns_df.cov()
        
        try:
            precision_matrix = np.linalg.inv(cov_matrix)
            
            # Partial correlation = -precision[i,j] / sqrt(precision[i,i] * precision[j,j])
            i = list(returns_df.columns).index(asset_a)
            j = list(returns_df.columns).index(asset_b)
            
            partial_corr = -precision_matrix.iloc[i, j] / np.sqrt(
                precision_matrix.iloc[i, i] * precision_matrix.iloc[j, j]
            )
            
            return round(partial_corr, 4)
            
        except np.linalg.LinAlgError:
            logger.warning("Singular covariance matrix, cannot compute partial correlation")
            return np.nan
    
    def calculate_lead_lag_correlation(
        self,
        series_a: pd.Series,
        series_b: pd.Series,
        max_lag: int = 5
    ) -> Dict[int, float]:
        """
        Calculate cross-correlation at different lags.
        
        Returns:
            Dict mapping lag to correlation
        """
        returns_a = np.log(series_a / series_a.shift(1)).dropna()
        returns_b = np.log(series_b / series_b.shift(1)).dropna()
        
        aligned = pd.concat([returns_a, returns_b], axis=1).dropna()
        aligned.columns = ['a', 'b']
        
        results = {}
        
        for lag in range(-max_lag, max_lag + 1):
            if lag > 0:
                # A leads B
                corr = aligned['a'].iloc[:-lag].corr(aligned['b'].iloc[lag:])
            elif lag < 0:
                # B leads A
                corr = aligned['a'].iloc[-lag:].corr(aligned['b'].iloc[:lag])
            else:
                corr = aligned['a'].corr(aligned['b'])
            
            results[lag] = round(corr, 4)
        
        return results
    
    def calculate_correlation_delta(
        self,
        current_corr: float,
        previous_corr: float
    ) -> float:
        """Calculate change in correlation."""
        return round(current_corr - previous_corr, 4)
    
    def detect_correlation_anomaly(
        self,
        correlations: pd.Series,
        window: int = 250,
        threshold: float = 2.0
    ) -> List[Dict]:
        """
        Detect anomalies in correlation series using z-score.
        
        Args:
            correlations: Series of correlation values
            window: Lookback window for mean/std calculation
            threshold: Z-score threshold for anomaly detection
        
        Returns:
            List of anomaly dictionaries
        """
        rolling_mean = correlations.rolling(window=window, min_periods=60).mean()
        rolling_std = correlations.rolling(window=window, min_periods=60).std()
        
        z_scores = (correlations - rolling_mean) / rolling_std
        
        anomalies = []
        
        for i in range(len(z_scores)):
            if pd.notna(z_scores.iloc[i]) and abs(z_scores.iloc[i]) > threshold:
                anomalies.append({
                    'index': i,
                    'ts': correlations.index[i],
                    'value': correlations.iloc[i],
                    'z_score': round(z_scores.iloc[i], 2),
                    'direction': 'positive' if z_scores.iloc[i] > 0 else 'negative',
                    'severity': self._get_severity(abs(z_scores.iloc[i]))
                })
        
        return anomalies
    
    def _get_severity(self, z_score: float) -> str:
        """Determine severity based on z-score magnitude."""
        if z_score > 4:
            return 'critical'
        elif z_score > 3:
            return 'high'
        elif z_score > 2.5:
            return 'medium'
        else:
            return 'low'
