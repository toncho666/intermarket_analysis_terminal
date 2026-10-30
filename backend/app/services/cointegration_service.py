import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller, coint
from statsmodels.tsa.vector_ar.vecm import coint_johansen
from statsmodels.regression.linear_model import OLS
from statsmodels.tsa.ar_model import AutoReg
from typing import Dict, Optional, Tuple
import structlog

logger = structlog.get_logger()


class CointegrationService:
    """Service for cointegration analysis."""
    
    def __init__(self):
        self.model_version = "v1.0"
    
    def engle_granger_test(
        self,
        series_a: pd.Series,
        series_b: pd.Series
    ) -> Dict:
        """
        Perform Engle-Granger 2-step cointegration test.
        
        Step 1: Regress Y on X to get residuals
        Step 2: ADF test on residuals
        
        Returns:
            Dictionary with test results
        """
        try:
            # Ensure same length
            aligned = pd.concat([series_a, series_b], axis=1).dropna()
            aligned.columns = ['y', 'x']
            
            # Step 1: OLS regression
            model = OLS(aligned['y'], aligned['x']).fit()
            residuals = model.resid
            
            # Step 2: ADF test on residuals
            adf_result = adfuller(residuals, maxlag=1)
            
            # Calculate hedge ratio
            hedge_ratio = model.params.iloc[0]
            
            return {
                'is_cointegrated': adf_result[1] < 0.05,
                'p_value': round(adf_result[1], 4),
                'adf_statistic': round(adf_result[0], 4),
                'critical_values': {k: round(v, 4) for k, v in adf_result[4].items()},
                'hedge_ratio': round(hedge_ratio, 4),
                'residuals_mean': round(residuals.mean(), 4),
                'residuals_std': round(residuals.std(), 4),
            }
            
        except Exception as e:
            logger.error("Engle-Granger test failed", error=str(e))
            return {'error': str(e)}
    
    def johansen_test(
        self,
        series_a: pd.Series,
        series_b: pd.Series,
        det_order: int = 0,
        k_ar_diff: int = 1
    ) -> Dict:
        """
        Perform Johansen cointegration test (MLE-based).
        
        Args:
            series_a: First price series
            series_b: Second price series
            det_order: Deterministic trend order (-1, 0, 1)
            k_ar_diff: Number of lags in VAR
        
        Returns:
            Dictionary with test results
        """
        try:
            aligned = pd.concat([series_a, series_b], axis=1).dropna()
            aligned.columns = ['y', 'x']
            
            # Johansen test
            result = coint_johansen(aligned, det_order, k_ar_diff)
            
            # Trace statistics
            trace_stats = result.lr1
            trace_crit = result.cvt[:, 1]  # 95% critical values
            
            # Maximum eigenvalue statistics
            max_eigen_stats = result.lr2
            max_eigen_crit = result.cvt[:, 2]  # 95% critical values
            
            return {
                'trace_stats': [round(s, 4) for s in trace_stats],
                'trace_crit_95': [round(c, 4) for c in trace_crit],
                'max_eigen_stats': [round(s, 4) for s in max_eigen_stats],
                'max_eigen_crit_95': [round(c, 4) for c in max_eigen_crit],
                'is_cointegrated_trace': trace_stats[0] > trace_crit[0],
                'is_cointegrated_max_eigen': max_eigen_stats[0] > max_eigen_crit[0],
                'eigenvectors': result.evec.tolist(),
            }
            
        except Exception as e:
            logger.error("Johansen test failed", error=str(e))
            return {'error': str(e)}
    
    def calculate_half_life(
        self,
        spread: pd.Series
    ) -> Optional[float]:
        """
        Calculate half-life of mean reversion using Ornstein-Uhlenbeck process.
        
        Half-life = -log(2) / log(phi)
        where phi is the AR(1) coefficient of the spread.
        
        Returns:
            Half-life in days, or None if not mean-reverting
        """
        try:
            # Fit AR(1) model
            spread_lag = spread.shift(1).dropna()
            spread_diff = spread.diff().dropna()
            
            # Align
            aligned = pd.concat([spread_diff, spread_lag], axis=1).dropna()
            aligned.columns = ['diff', 'lag']
            
            # OLS: Δy_t = φ * y_{t-1} + ε_t
            model = OLS(aligned['diff'], aligned['lag']).fit()
            phi = 1 + model.params.iloc[0]
            
            if phi >= 1 or phi <= 0:
                return None  # Not mean-reverting
            
            half_life = -np.log(2) / np.log(phi)
            
            return round(half_life, 2)
            
        except Exception as e:
            logger.error("Half-life calculation failed", error=str(e))
            return None
    
    def calculate_spread_zscore(
        self,
        series_a: pd.Series,
        series_b: pd.Series,
        hedge_ratio: float,
        window: int = 60
    ) -> pd.Series:
        """
        Calculate z-score of the cointegration spread.
        
        Spread = Y - hedge_ratio * X
        Z-score = (Spread - rolling_mean) / rolling_std
        """
        spread = series_a - hedge_ratio * series_b
        
        rolling_mean = spread.rolling(window=window).mean()
        rolling_std = spread.rolling(window=window).std()
        
        z_score = (spread - rolling_mean) / rolling_std
        
        return z_score
    
    def rolling_cointegration_test(
        self,
        series_a: pd.Series,
        series_b: pd.Series,
        window: int = 250,
        step: int = 5
    ) -> pd.DataFrame:
        """
        Perform rolling Engle-Granger test.
        
        Returns:
            DataFrame with columns: ts, p_value, hedge_ratio, is_cointegrated
        """
        results = []
        
        for i in range(window, len(series_a), step):
            window_a = series_a.iloc[i-window:i]
            window_b = series_b.iloc[i-window:i]
            
            test_result = self.engle_granger_test(window_a, window_b)
            
            if 'error' not in test_result:
                results.append({
                    'ts': series_a.index[i],
                    'p_value': test_result['p_value'],
                    'hedge_ratio': test_result['hedge_ratio'],
                    'is_cointegrated': test_result['is_cointegrated'],
                })
        
        return pd.DataFrame(results)
    
    def detect_cointegration_break(
        self,
        rolling_results: pd.DataFrame,
        threshold: float = 0.05
    ) -> list:
        """
        Detect breaks in cointegration relationship.
        
        A break is detected when p-value crosses the threshold.
        """
        breaks = []
        
        was_cointegrated = None
        
        for i, row in rolling_results.iterrows():
            is_coint = row['is_cointegrated']
            
            if was_cointegrated is not None and was_cointegrated != is_coint:
                breaks.append({
                    'ts': row['ts'],
                    'type': 'coint_break' if was_cointegrated else 'coint_formed',
                    'p_value': row['p_value'],
                    'hedge_ratio': row['hedge_ratio'],
                })
            
            was_cointegrated = is_coint
        
        return breaks
    
    def hurst_exponent(self, series: pd.Series, max_lag: int = 100) -> float:
        """
        Calculate Hurst exponent using R/S analysis.
        
        H > 0.5: Trending (persistent)
        H = 0.5: Random walk
        H < 0.5: Mean-reverting (anti-persistent)
        """
        lags = range(2, min(max_lag, len(series) // 2))
        
        tau = []
        for lag in lags:
            # Calculate R/S statistic
            returns = series.diff().dropna()
            rolling_mean = returns.rolling(window=lag).mean()
            rolling_std = returns.rolling(window=lag).std()
            
            cumulative_deviation = (returns - rolling_mean).cumsum()
            r = cumulative_deviation.max() - cumulative_deviation.min()
            s = rolling_std
            
            if s.mean() > 0:
                tau.append((lag, r.mean() / s.mean()))
        
        if len(tau) < 2:
            return 0.5
        
        # Log-log regression
        lags_log = np.log([t[0] for t in tau])
        rs_log = np.log([t[1] for t in tau])
        
        model = OLS(rs_log, lags_log).fit()
        hurst = model.params.iloc[0]
        
        return round(hurst, 4)
