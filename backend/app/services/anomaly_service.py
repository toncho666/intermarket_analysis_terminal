import pandas as pd
import numpy as np
from typing import List, Dict
import structlog
from sklearn.ensemble import IsolationForest

from app.config import settings

logger = structlog.get_logger()


class AnomalyService:
    """Service for anomaly detection."""
    
    def __init__(self):
        self.model_version = "v1.0"
        self.z_threshold = settings.ANOMALY_Z_THRESHOLD
    
    def detect_correlation_anomaly(
        self,
        correlations: pd.Series,
        window: int = 250,
        threshold: float = None
    ) -> List[Dict]:
        """
        Detect anomalies in correlation series using z-score.
        """
        threshold = threshold or self.z_threshold
        
        rolling_mean = correlations.rolling(window=window, min_periods=60).mean()
        rolling_std = correlations.rolling(window=window, min_periods=60).std()
        
        z_scores = (correlations - rolling_mean) / rolling_std
        
        anomalies = []
        
        for i in range(len(z_scores)):
            if pd.notna(z_scores.iloc[i]) and abs(z_scores.iloc[i]) > threshold:
                anomalies.append({
                    'ts': correlations.index[i],
                    'value': round(correlations.iloc[i], 4),
                    'z_score': round(z_scores.iloc[i], 2),
                    'direction': 'positive' if z_scores.iloc[i] > 0 else 'negative',
                    'severity': self._get_severity(abs(z_scores.iloc[i])),
                    'type': 'corr_break'
                })
        
        return anomalies
    
    def detect_volatility_anomaly(
        self,
        volatility: pd.Series,
        window: int = 60,
        threshold: float = 2.0
    ) -> List[Dict]:
        """
        Detect volatility spikes.
        """
        rolling_mean = volatility.rolling(window=window).mean()
        rolling_std = volatility.rolling(window=window).std()
        
        z_scores = (volatility - rolling_mean) / rolling_std
        
        anomalies = []
        
        for i in range(len(z_scores)):
            if pd.notna(z_scores.iloc[i]) and z_scores.iloc[i] > threshold:
                anomalies.append({
                    'ts': volatility.index[i],
                    'value': round(volatility.iloc[i], 4),
                    'z_score': round(z_scores.iloc[i], 2),
                    'direction': 'positive',
                    'severity': self._get_severity(z_scores.iloc[i]),
                    'type': 'vol_spike'
                })
        
        return anomalies
    
    def detect_spread_anomaly(
        self,
        spread: pd.Series,
        window: int = 60,
        threshold: float = 3.0
    ) -> List[Dict]:
        """
        Detect spread outliers (for cointegration pairs).
        """
        rolling_mean = spread.rolling(window=window).mean()
        rolling_std = spread.rolling(window=window).std()
        
        z_scores = (spread - rolling_mean) / rolling_std
        
        anomalies = []
        
        for i in range(len(z_scores)):
            if pd.notna(z_scores.iloc[i]) and abs(z_scores.iloc[i]) > threshold:
                anomalies.append({
                    'ts': spread.index[i],
                    'value': round(spread.iloc[i], 4),
                    'z_score': round(z_scores.iloc[i], 2),
                    'direction': 'positive' if z_scores.iloc[i] > 0 else 'negative',
                    'severity': self._get_severity(abs(z_scores.iloc[i])),
                    'type': 'divergence'
                })
        
        return anomalies
    
    def detect_multivariate_anomaly(
        self,
        returns_df: pd.DataFrame,
        contamination: float = 0.01
    ) -> List[Dict]:
        """
        Detect multivariate anomalies using Isolation Forest.
        """
        # Drop NaN rows
        clean_data = returns_df.dropna()
        
        if len(clean_data) < 100:
            return []
        
        # Fit Isolation Forest
        model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        
        predictions = model.fit_predict(clean_data)
        scores = model.score_samples(clean_data)
        
        anomalies = []
        
        for i, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:  # Anomaly
                anomalies.append({
                    'ts': clean_data.index[i],
                    'anomaly_score': round(-score, 4),  # Negative score = more anomalous
                    'severity': self._get_severity(-score * 10),
                    'type': 'multivariate',
                    'values': {col: round(clean_data.iloc[i][col], 4) for col in clean_data.columns}
                })
        
        return anomalies
    
    def detect_cusum_anomaly(
        self,
        series: pd.Series,
        threshold: float = 1.0
    ) -> List[Dict]:
        """
        Detect structural breaks using CUSUM test.
        """
        # Standardize series
        mean = series.mean()
        std = series.std()
        standardized = (series - mean) / std
        
        # Calculate CUSUM
        cusum = standardized.cumsum()
        
        # Detect when CUSUM exceeds threshold * std * sqrt(n)
        n = len(series)
        boundary = threshold * std * np.sqrt(np.arange(1, n + 1))
        
        anomalies = []
        
        for i in range(len(cusum)):
            if abs(cusum.iloc[i]) > boundary[i]:
                anomalies.append({
                    'ts': series.index[i],
                    'cusum_value': round(cusum.iloc[i], 4),
                    'boundary': round(boundary[i], 4),
                    'severity': 'high' if abs(cusum.iloc[i]) > 2 * boundary[i] else 'medium',
                    'type': 'structural_break'
                })
        
        return anomalies
    
    def _get_severity(self, magnitude: float) -> str:
        """Determine severity based on magnitude."""
        if magnitude > 4:
            return 'critical'
        elif magnitude > 3:
            return 'high'
        elif magnitude > 2.5:
            return 'medium'
        else:
            return 'low'
    
    def ensemble_anomaly_detection(
        self,
        correlations: pd.Series,
        volatility: pd.Series,
        spread: pd.Series = None
    ) -> List[Dict]:
        """
        Combine multiple anomaly detection methods.
        """
        all_anomalies = []
        
        # Correlation anomalies
        corr_anomalies = self.detect_correlation_anomaly(correlations)
        all_anomalies.extend(corr_anomalies)
        
        # Volatility anomalies
        vol_anomalies = self.detect_volatility_anomaly(volatility)
        all_anomalies.extend(vol_anomalies)
        
        # Spread anomalies
        if spread is not None:
            spread_anomalies = self.detect_spread_anomaly(spread)
            all_anomalies.extend(spread_anomalies)
        
        # Sort by timestamp
        all_anomalies.sort(key=lambda x: x['ts'])
        
        return all_anomalies
