import pandas as pd
import numpy as np
from typing import Dict, List
import structlog

logger = structlog.get_logger()


class RegimeService:
    """Service for market regime detection."""
    
    def __init__(self):
        self.model_version = "v1.0"
    
    def calculate_regime_score(
        self,
        data: Dict[str, pd.Series]
    ) -> Dict:
        """
        Calculate composite regime score (0-100).
        
        Components:
        - Equity-Bond correlation (negative = risk-on)
        - VIX term structure (contango = risk-on)
        - Credit spreads (tight = risk-on)
        - DXY momentum (weak = risk-on)
        - Risk appetite index
        
        Returns:
            Dictionary with score and components
        """
        components = []
        
        # 1. Equity-Bond correlation (SPX vs US10Y)
        if 'spx' in data and 'us10y' in data:
            corr = data['spx'].tail(60).corr(data['us10y'].tail(60))
            # Negative correlation is risk-on (flight to quality)
            score = self._normalize_score(-corr, -1, 1)
            components.append({
                'name': 'Equity-Bond Corr',
                'value': round(corr, 3),
                'score': round(score, 1),
                'signal': 'Risk-On' if score > 60 else ('Risk-Off' if score < 40 else 'Neutral')
            })
        
        # 2. VIX term structure (VIX3M / VIX ratio)
        if 'vix' in data and 'vix3m' in data:
            vix = data['vix'].iloc[-1]
            vix3m = data['vix3m'].iloc[-1]
            ratio = vix3m / vix if vix > 0 else 1
            # Contango (ratio > 1) is risk-on
            score = self._normalize_score(ratio, 0.8, 1.3)
            components.append({
                'name': 'VIX Term Structure',
                'value': round(ratio, 3),
                'score': round(score, 1),
                'signal': 'Risk-On' if score > 60 else ('Risk-Off' if score < 40 else 'Neutral')
            })
        
        # 3. Credit spreads (HY OAS level)
        if 'hy_oas' in data:
            hy_oas = data['hy_oas'].iloc[-1]
            # Lower spreads = risk-on
            score = self._normalize_score(-hy_oas, -800, -200)
            components.append({
                'name': 'Credit Spreads',
                'value': round(hy_oas, 1),
                'score': round(score, 1),
                'signal': 'Risk-On' if score > 60 else ('Risk-Off' if score < 40 else 'Neutral')
            })
        
        # 4. DXY momentum (20-day ROC)
        if 'dxy' in data:
            dxy = data['dxy']
            roc_20d = (dxy.iloc[-1] / dxy.iloc[-20] - 1) * 100 if len(dxy) >= 20 else 0
            # Weak dollar = risk-on
            score = self._normalize_score(-roc_20d, -5, 5)
            components.append({
                'name': 'DXY Momentum',
                'value': round(roc_20d, 2),
                'score': round(score, 1),
                'signal': 'Risk-On' if score > 60 else ('Risk-Off' if score < 40 else 'Neutral')
            })
        
        # 5. Risk appetite index (SPX+EEM+HY vs TLT+Gold+JPY)
        if all(k in data for k in ['spx', 'eem', 'tlt', 'gold']):
            risk_assets = data['spx'].tail(20).pct_change().sum() + \
                         data['eem'].tail(20).pct_change().sum()
            safe_assets = data['tlt'].tail(20).pct_change().sum() + \
                         data['gold'].tail(20).pct_change().sum()
            
            risk_appetite = risk_assets - safe_assets
            score = self._normalize_score(risk_appetite, -0.1, 0.1)
            components.append({
                'name': 'Risk Appetite',
                'value': round(risk_appetite, 4),
                'score': round(score, 1),
                'signal': 'Risk-On' if score > 60 else ('Risk-Off' if score < 40 else 'Neutral')
            })
        
        # Calculate composite score (weighted average)
        if components:
            weights = [0.25, 0.20, 0.25, 0.15, 0.15]  # Sum = 1.0
            composite = sum(c['score'] * w for c, w in zip(components, weights[:len(components)]))
            composite = min(100, max(0, composite))
        else:
            composite = 50
        
        return {
            'score': round(composite, 1),
            'regime': self._get_regime_label(composite),
            'components': components,
            'timestamp': pd.Timestamp.now().isoformat(),
            'model_version': self.model_version
        }
    
    def _normalize_score(self, value: float, min_val: float, max_val: float) -> float:
        """Normalize value to 0-100 scale."""
        normalized = (value - min_val) / (max_val - min_val)
        return min(100, max(0, normalized * 100))
    
    def _get_regime_label(self, score: float) -> str:
        """Get regime label based on score."""
        if score >= 70:
            return 'Risk-On'
        elif score >= 40:
            return 'Neutral'
        else:
            return 'Risk-Off'
    
    def detect_regime_change(
        self,
        scores: pd.Series,
        window: int = 10,
        threshold: float = 15
    ) -> List[Dict]:
        """
        Detect regime changes based on score movement.
        
        Args:
            scores: Series of regime scores
            window: Smoothing window
            threshold: Minimum score change to trigger
        
        Returns:
            List of regime change events
        """
        smoothed = scores.rolling(window=window, min_periods=1).mean()
        
        changes = []
        prev_regime = None
        
        for i in range(len(smoothed)):
            current_regime = self._get_regime_label(smoothed.iloc[i])
            
            if prev_regime is not None and current_regime != prev_regime:
                changes.append({
                    'ts': scores.index[i],
                    'from_regime': prev_regime,
                    'to_regime': current_regime,
                    'score': round(smoothed.iloc[i], 1)
                })
            
            prev_regime = current_regime
        
        return changes
    
    def calculate_volatility_regime(
        self,
        vix: pd.Series,
        window: int = 250
    ) -> str:
        """
        Classify volatility regime based on VIX level and percentile.
        """
        current_vix = vix.iloc[-1]
        percentile = (vix < current_vix).mean() * 100
        
        if current_vix < 15:
            return 'Low Vol'
        elif current_vix < 20:
            return 'Normal Vol'
        elif current_vix < 30:
            return 'Elevated Vol'
        else:
            return 'High Vol'
    
    def calculate_credit_regime(
        self,
        hy_oas: pd.Series,
        ig_oas: pd.Series
    ) -> str:
        """
        Classify credit regime based on spread levels.
        """
        current_hy = hy_oas.iloc[-1]
        
        if current_hy < 300:
            return 'Tight Credit'
        elif current_hy < 500:
            return 'Normal Credit'
        elif current_hy < 800:
            return 'Wide Credit'
        else:
            return 'Stress Credit'
