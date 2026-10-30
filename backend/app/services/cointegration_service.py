"""
Cointegration analysis service
- Engle-Granger 2-step method
- Johansen test (MLE)
- Half-life calculation (OU process)
- Spread z-score
- Hurst exponent
"""
import numpy as np
import pandas as pd
from typing import Tuple, Optional, Dict, Any
from datetime import datetime
import logging
from statsmodels.tsa.stattools import adfuller, coint
from statsmodels.tsa.vector_ar.vecm import coint_johansen
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant

logger = logging.getLogger(__name__)


class CointegrationService:
    """Service for cointegration analysis"""
    
    @staticmethod
    def engle_granger_test(
        prices_a: pd.Series,
        prices_b: pd.Series,
        significance: float = 0.05
    ) -> Dict[str, Any]:
        """
        Engle-Granger 2-step cointegration test
        
        Step 1: OLS regression to find hedge ratio
        Step 2: ADF test on residuals
        
        Returns:
            dict with p_value, test_statistic, is_cointegrated, hedge_ratio, spread
        """
        # Ensure same length
        min_len = min(len(prices_a), len(prices_b))
        y = prices_a.iloc[-min_len:].values
        x = prices_b.iloc[-min_len:].values
        
        # Step 1: OLS regression y = alpha + beta * x + epsilon
        x_const = add_constant(x)
        model = OLS(y, x_const).fit()
        hedge_ratio = model.params[1]
        residuals = model.resid
        
        # Step 2: ADF test on residuals
        try:
            adf_result = adfuller(residuals, maxlag=1, autolag=None)
            test_stat = adf_result[0]
            p_value = adf_result[1]
        except Exception as e:
            logger.error(f"ADF test failed: {e}")
            return {
                'p_value': 1.0,
                'test_statistic': 0.0,
                'is_cointegrated': False,
                'hedge_ratio': hedge_ratio,
                'spread': None,
                'half_life': None,
            }
        
        # Calculate spread
        spread = y - hedge_ratio * x
        
        # Calculate half-life
        half_life = CointegrationService.calculate_half_life(spread)
        
        return {
            'p_value': float(p_value),
            'test_statistic': float(test_stat),
            'is_cointegrated': p_value < significance,
            'hedge_ratio': float(hedge_ratio),
            'spread': spread.tolist(),
            'half_life': half_life,
        }
    
    @staticmethod
    def johansen_test(
        prices_df: pd.DataFrame,
        det_order: int = 0,
        k_ar_diff: int = 1
    ) -> Dict[str, Any]:
        """
        Johansen cointegration test (MLE-based)
        Tests for multiple cointegrating relationships
        
        Args:
            prices_df: DataFrame with price columns (min 2)
            det_order: -1 (no deterministic), 0 (constant), 1 (linear trend)
            k_ar_diff: number of lags in VAR
        
        Returns:
            dict with trace_stats, max_eigen_stats, coint_vectors
        """
        try:
            # Johansen test requires at least 2 columns
            result = coint_johansen(prices_df.values, det_order=det_order, k_ar_diff=k_ar_diff)
            
            # Trace statistics
            trace_stats = result.lr1  # Trace statistic
            trace_cv = result.cvt     # Critical values (90%, 95%, 99%)
            
            # Maximum eigenvalue statistics
            max_eigen_stats = result.lr2
            max_eigen_cv = result.cvm
            
            # Cointegrating vectors
            coint_vectors = result.eig  # Eigenvectors
            
            # Determine number of cointegrating relationships
            n_coint = 0
            for i in range(len(trace_stats)):
                if trace_stats[i] > trace_cv[i, 1]:  # 95% critical value
                    n_coint += 1
                else:
                    break
            
            return {
                'trace_stats': trace_stats.tolist(),
                'trace_critical_values': trace_cv.tolist(),
                'max_eigen_stats': max_eigen_stats.tolist(),
                'max_eigen_critical_values': max_eigen_cv.tolist(),
                'coint_vectors': coint_vectors.tolist(),
                'n_cointegrating_relations': n_coint,
                'is_cointegrated': n_coint > 0,
            }
        except Exception as e:
            logger.error(f"Johansen test failed: {e}")
            return {
                'trace_stats': [],
                'trace_critical_values': [],
                'max_eigen_stats': [],
                'max_eigen_critical_values': [],
                'coint_vectors': [],
                'n_cointegrating_relations': 0,
                'is_cointegrated': False,
            }
    
    @staticmethod
    def calculate_half_life(spread: np.ndarray) -> Optional[float]:
        """
        Calculate half-life of mean reversion using Ornstein-Uhlenbeck process
        
        Model: dS = theta * (mu - S) * dt + sigma * dW
        Half-life = -log(2) / log(phi)
        where phi is estimated from AR(1): S_t = alpha + phi * S_{t-1} + epsilon
        """
        try:
            spread = np.array(spread)
            if len(spread) < 10:
                return None
            
            # Lag spread
            spread_lag = spread[:-1]
            spread_diff = np.diff(spread)
            
            # OLS: delta_S = alpha + phi * S_{t-1}
            x = add_constant(spread_lag)
            model = OLS(spread_diff, x).fit()
            phi = 1 + model.params[1]  # Convert to level
            
            if phi >= 1 or phi <= 0:
                return None  # Not mean-reverting
            
            half_life = -np.log(2) / np.log(phi)
            return float(max(0, half_life))
        except Exception as e:
            logger.error(f"Half-life calculation failed: {e}")
            return None
    
    @staticmethod
    def spread_z_score(
        prices_a: pd.Series,
        prices_b: pd.Series,
        hedge_ratio: float,
        window: int = 60
    ) -> pd.Series:
        """
        Calculate rolling z-score of the spread
        """
        spread = prices_a - hedge_ratio * prices_b
        
        # Rolling mean and std
        rolling_mean = spread.rolling(window=window).mean()
        rolling_std = spread.rolling(window=window).std()
        
        # Z-score
        z_score = (spread - rolling_mean) / rolling_std
        
        return z_score
    
    @staticmethod
    def hurst_exponent(time_series: np.ndarray, max_lag: int = 20) -> float:
        """
        Calculate Hurst exponent using R/S analysis
        
        H > 0.5: Trending (persistent)
        H = 0.5: Random walk
        H < 0.5: Mean-reverting (anti-persistent)
        """
        try:
            time_series = np.array(time_series)
            lags = range(2, min(max_lag, len(time_series) // 2))
            
            # Calculate R/S for each lag
            rs_values = []
            for lag in lags:
                # Split into chunks
                n_chunks = len(time_series) // lag
                if n_chunks < 1:
                    continue
                
                rs_chunk_list = []
                for i in range(n_chunks):
                    chunk = time_series[i*lag:(i+1)*lag]
                    mean_chunk = np.mean(chunk)
                    deviation = np.cumsum(chunk - mean_chunk)
                    r = np.max(deviation) - np.min(deviation)
                    s = np.std(chunk)
                    if s > 0:
                        rs_chunk_list.append(r / s)
                
                if rs_chunk_list:
                    rs_values.append((np.log(lag), np.log(np.mean(rs_chunk_list))))
            
            if len(rs_values) < 2:
                return 0.5
            
            # Linear regression: log(R/S) = H * log(lag) + c
            x = np.array([v[0] for v in rs_values])
            y = np.array([v[1] for v in rs_values])
            
            model = OLS(y, add_constant(x)).fit()
            hurst = model.params[1]
            
            return float(np.clip(hurst, 0, 1))
        except Exception as e:
            logger.error(f"Hurst exponent calculation failed: {e}")
            return 0.5
    
    @staticmethod
    def rolling_cointegration(
        prices_a: pd.Series,
        prices_b: pd.Series,
        window: int = 250,
        step: int = 5
    ) -> pd.DataFrame:
        """
        Calculate rolling cointegration test results
        """
        results = []
        
        for i in range(window, len(prices_a), step):
            window_a = prices_a.iloc[i-window:i]
            window_b = prices_b.iloc[i-window:i]
            
            eg_result = CointegrationService.engle_granger_test(window_a, window_b)
            
            results.append({
                'ts': prices_a.index[i-1],
                'p_value': eg_result['p_value'],
                'test_statistic': eg_result['test_statistic'],
                'is_cointegrated': eg_result['is_cointegrated'],
                'hedge_ratio': eg_result['hedge_ratio'],
                'half_life': eg_result['half_life'],
            })
        
        return pd.DataFrame(results)


# Singleton instance
cointegration_service = CointegrationService()
