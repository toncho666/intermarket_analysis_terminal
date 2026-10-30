"""
Anomaly detection service
- Z-score based correlation break detection
- CUSUM test for structural breaks
- Isolation Forest for multivariate outliers
- Spread outlier detection
- Volatility spike detection
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from sklearn.ensemble import IsolationForest
import logging

logger = logging.getLogger(__name__)


class AnomalyService:
    """Service for detecting market anomalies"""
    
    @staticmethod
    def correlation_break_zscore(
        correlation_series: pd.Series,
        lookback: int = 250,
        threshold: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Detect correlation breaks using z-score
        An anomaly is when current correlation deviates from historical mean by > threshold σ
        """
        anomalies = []
        
        rolling_mean = correlation_series.rolling(window=lookback, min_periods=60).mean()
        rolling_std = correlation_series.rolling(window=lookback, min_periods=60).std()
        
        z_scores = (correlation_series - rolling_mean) / rolling_std
        
        for i in range(len(z_scores)):
            if pd.isna(z_scores.iloc[i]):
                continue
            
            z = z_scores.iloc[i]
            if abs(z) > threshold:
                severity = AnomalyService._calculate_severity(abs(z))
                anomalies.append({
                    'index': i,
                    'ts': correlation_series.index[i],
                    'z_score': float(z),
                    'correlation': float(correlation_series.iloc[i]),
                    'mean': float(rolling_mean.iloc[i]) if not pd.isna(rolling_mean.iloc[i]) else None,
                    'std': float(rolling_std.iloc[i]) if not pd.isna(rolling_std.iloc[i]) else None,
                    'severity': severity,
                    'direction': 'positive' if z > 0 else 'negative',
                })
        
        return anomalies
    
    @staticmethod
    def cusum_test(
        series: pd.Series,
        significance: float = 0.05
    ) -> Dict[str, Any]:
        """
        CUSUM test for structural break detection
        
        Returns:
            dict with break_detected, break_point, p_value
        """
        try:
            n = len(series)
            if n < 20:
                return {'break_detected': False, 'break_point': None, 'p_value': 1.0}
            
            # Calculate CUSUM
            mean = series.mean()
            std = series.std()
            
            cusum = np.cumsum(series - mean) / (std * np.sqrt(n))
            
            # Critical values (approximate)
            # For significance = 0.05, critical value ≈ 0.948
            critical_value = 0.948 if significance == 0.05 else 1.143  # 0.01
            
            # Find first crossing
            break_idx = None
            for i in range(len(cusum)):
                if abs(cusum[i]) > critical_value:
                    break_idx = i
                    break
            
            break_detected = break_idx is not None
            
            return {
                'break_detected': break_detected,
                'break_point': break_idx,
                'break_date': series.index[break_idx] if break_idx is not None else None,
                'max_cusum': float(np.max(np.abs(cusum))),
                'critical_value': critical_value,
                'cusum_series': cusum.tolist(),
            }
        except Exception as e:
            logger.error(f"CUSUM test failed: {e}")
            return {'break_detected': False, 'break_point': None, 'p_value': 1.0}
    
    @staticmethod
    def isolation_forest_detection(
        features_df: pd.DataFrame,
        contamination: float = 0.01,
        random_state: int = 42
    ) -> pd.DataFrame:
        """
        Use Isolation Forest for multivariate anomaly detection
        
        Args:
            features_df: DataFrame with features (returns, volatilities, etc.)
            contamination: expected proportion of outliers
            random_state: for reproducibility
        
        Returns:
            DataFrame with anomaly_score and is_anomaly columns
        """
        try:
            # Drop NaN rows
            clean_df = features_df.dropna()
            
            # Fit Isolation Forest
            iso_forest = IsolationForest(
                contamination=contamination,
                random_state=random_state,
                n_estimators=100,
            )
            
            # Predict: -1 for anomaly, 1 for normal
            predictions = iso_forest.fit_predict(clean_df)
            
            # Anomaly scores (lower = more anomalous)
            scores = iso_forest.decision_function(clean_df)
            
            results = pd.DataFrame(index=clean_df.index)
            results['anomaly_score'] = scores
            results['is_anomaly'] = predictions == -1
            
            return results
        except Exception as e:
            logger.error(f"Isolation Forest failed: {e}")
            return pd.DataFrame({'anomaly_score': [], 'is_anomaly': []})
    
    @staticmethod
    def spread_outlier_detection(
        spread: pd.Series,
        window: int = 60,
        threshold: float = 3.0
    ) -> List[Dict[str, Any]]:
        """
        Detect spread outliers using rolling z-score
        """
        anomalies = []
        
        rolling_mean = spread.rolling(window=window, min_periods=30).mean()
        rolling_std = spread.rolling(window=window, min_periods=30).std()
        
        z_scores = (spread - rolling_mean) / rolling_std
        
        for i in range(len(z_scores)):
            if pd.isna(z_scores.iloc[i]):
                continue
            
            z = z_scores.iloc[i]
            if abs(z) > threshold:
                severity = AnomalyService._calculate_severity(abs(z))
                anomalies.append({
                    'index': i,
                    'ts': spread.index[i],
                    'z_score': float(z),
                    'spread_value': float(spread.iloc[i]),
                    'mean': float(rolling_mean.iloc[i]) if not pd.isna(rolling_mean.iloc[i]) else None,
                    'std': float(rolling_std.iloc[i]) if not pd.isna(rolling_std.iloc[i]) else None,
                    'severity': severity,
                    'direction': 'positive' if z > 0 else 'negative',
                })
        
        return anomalies
    
    @staticmethod
    def volatility_spike_detection(
        prices: pd.Series,
        window: int = 60,
        threshold_multiplier: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Detect volatility spikes (realized vol > threshold × historical average)
        """
        anomalies = []
        
        # Calculate log returns
        returns = np.log(prices / prices.shift(1)).dropna()
        
        # Realized volatility (rolling)
        realized_vol = returns.rolling(window=20).std() * np.sqrt(252)
        
        # Historical average vol
        historical_vol = realized_vol.rolling(window=window, min_periods=30).mean()
        
        # Ratio
        vol_ratio = realized_vol / historical_vol
        
        for i in range(len(vol_ratio)):
            if pd.isna(vol_ratio.iloc[i]):
                continue
            
            ratio = vol_ratio.iloc[i]
            if ratio > threshold_multiplier:
                severity = AnomalyService._calculate_severity(ratio - 1)
                anomalies.append({
                    'index': i,
                    'ts': realized_vol.index[i],
                    'vol_ratio': float(ratio),
                    'realized_vol': float(realized_vol.iloc[i]),
                    'historical_vol': float(historical_vol.iloc[i]) if not pd.isna(historical_vol.iloc[i]) else None,
                    'severity': severity,
                })
        
        return anomalies
    
    @staticmethod
    def divergence_detection(
        prices_a: pd.Series,
        prices_b: pd.Series,
        correlation_series: pd.Series,
        price_threshold: float = 0.05,
        corr_threshold: float = -0.3
    ) -> List[Dict[str, Any]]:
        """
        Detect divergences: prices moving apart while correlation was high
        """
        anomalies = []
        
        # Calculate rolling returns
        returns_a = prices_a.pct_change(20)
        returns_b = prices_b.pct_change(20)
        
        # Correlation change
        corr_change = correlation_series.diff(20)
        
        for i in range(20, len(prices_a)):
            if pd.isna(returns_a.iloc[i]) or pd.isna(returns_b.iloc[i]):
                continue
            if pd.isna(corr_change.iloc[i]):
                continue
            
            # Check for divergence: prices moving in opposite directions
            # while correlation was decreasing
            ret_a = returns_a.iloc[i]
            ret_b = returns_b.iloc[i]
            delta_corr = corr_change.iloc[i]
            
            if (ret_a > price_threshold and ret_b < -price_threshold and delta_corr < corr_threshold) or \
               (ret_a < -price_threshold and ret_b > price_threshold and delta_corr < corr_threshold):
                
                anomalies.append({
                    'index': i,
                    'ts': prices_a.index[i],
                    'return_a': float(ret_a),
                    'return_b': float(ret_b),
                    'corr_change': float(delta_corr),
                    'severity': 'high' if abs(delta_corr) > 0.5 else 'medium',
                })
        
        return anomalies
    
    @staticmethod
    def _calculate_severity(z_score: float) -> str:
        """Map z-score to severity level"""
        if z_score >= 4.0:
            return 'critical'
        elif z_score >= 3.0:
            return 'high'
        elif z_score >= 2.0:
            return 'medium'
        else:
            return 'low'
    
    @staticmethod
    def detect_all_anomalies(
        prices_a: pd.Series,
        prices_b: pd.Series,
        correlation_series: pd.Series,
        hedge_ratio: Optional[float] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Run all anomaly detection methods and return combined results
        """
        results = {
            'correlation_breaks': AnomalyService.correlation_break_zscore(correlation_series),
            'cusum_breaks': [],
            'spread_outliers': [],
            'volatility_spikes_a': AnomalyService.volatility_spike_detection(prices_a),
            'volatility_spikes_b': AnomalyService.volatility_spike_detection(prices_b),
            'divergences': AnomalyService.divergence_detection(prices_a, prices_b, correlation_series),
        }
        
        # CUSUM on correlation
        cusum_result = AnomalyService.cusum_test(correlation_series)
        if cusum_result['break_detected']:
            results['cusum_breaks'] = [cusum_result]
        
        # Spread outliers if hedge ratio available
        if hedge_ratio is not None:
            spread = prices_a - hedge_ratio * prices_b
            results['spread_outliers'] = AnomalyService.spread_outlier_detection(spread)
        
        return results


# Singleton instance
anomaly_service = AnomalyService()
