"""
Market regime detection service
- Composite score calculation
- PCA-based regime detection
- Risk-On/Risk-Off classification
- Component signals
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RegimeService:
    """Service for market regime detection"""
    
    @staticmethod
    def calculate_regime_score(
        equity_bond_corr: float,
        vix_level: float,
        vix3m_level: float,
        hy_oas: float,
        ig_oas: float,
        dxy_momentum: float,
        commodity_momentum: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Calculate composite regime score (0-100)
        
        Components:
        - Equity-Bond correlation (negative = risk-on)
        - VIX term structure (contango = risk-on)
        - Credit spreads (tight = risk-on)
        - DXY momentum (weak USD = risk-on)
        - Commodity momentum
        
        Returns:
            dict with score, regime, components
        """
        components = []
        
        # 1. Equity-Bond correlation (weight: 25%)
        # Negative correlation = risk-on (flight to quality works)
        # Score: -1 corr → 100, +1 corr → 0
        eb_score = max(0, min(100, (1 - equity_bond_corr) * 50))
        eb_signal = "Risk-On" if eb_score > 60 else "Risk-Off" if eb_score < 40 else "Neutral"
        components.append({
            'name': 'Equity-Bond Corr',
            'value': round(equity_bond_corr, 3),
            'score': round(eb_score, 1),
            'weight': 0.25,
            'signal': eb_signal,
        })
        
        # 2. VIX term structure (weight: 20%)
        # VIX < VIX3M (contango) = risk-on
        vix_ratio = vix_level / vix3m_level if vix3m_level > 0 else 1.0
        vix_score = max(0, min(100, (1.2 - vix_ratio) * 200))
        vix_signal = "Risk-On" if vix_score > 60 else "Risk-Off" if vix_score < 40 else "Neutral"
        components.append({
            'name': 'VIX Term Structure',
            'value': round(vix_ratio, 3),
            'score': round(vix_score, 1),
            'weight': 0.20,
            'signal': vix_signal,
        })
        
        # 3. Credit spreads (weight: 25%)
        # Tight spreads = risk-on
        # HY OAS: < 300 = risk-on, > 500 = risk-off
        hy_score = max(0, min(100, (600 - hy_oas) / 3))
        hy_signal = "Risk-On" if hy_score > 60 else "Risk-Off" if hy_score < 40 else "Neutral"
        components.append({
            'name': 'Credit Spreads (HY)',
            'value': round(hy_oas, 1),
            'score': round(hy_score, 1),
            'weight': 0.25,
            'signal': hy_signal,
        })
        
        # 4. DXY momentum (weight: 15%)
        # Weak/declining USD = risk-on
        dxy_score = max(0, min(100, (0.05 - dxy_momentum) * 1000))
        dxy_signal = "Risk-On" if dxy_score > 60 else "Risk-Off" if dxy_score < 40 else "Neutral"
        components.append({
            'name': 'DXY Momentum',
            'value': round(dxy_momentum, 4),
            'score': round(dxy_score, 1),
            'weight': 0.15,
            'signal': dxy_signal,
        })
        
        # 5. HY-IG spread (weight: 15%)
        # Tight HY-IG spread = risk-on
        hy_ig_spread = hy_oas - ig_oas
        hig_score = max(0, min(100, (350 - hy_ig_spread) / 2))
        hig_signal = "Risk-On" if hig_score > 60 else "Risk-Off" if hig_score < 40 else "Neutral"
        components.append({
            'name': 'HY-IG Spread',
            'value': round(hy_ig_spread, 1),
            'score': round(hig_score, 1),
            'weight': 0.15,
            'signal': hig_signal,
        })
        
        # Composite score
        total_score = sum(c['score'] * c['weight'] for c in components)
        
        # Determine regime
        if total_score >= 65:
            regime = "Risk-On"
        elif total_score >= 40:
            regime = "Neutral"
        else:
            regime = "Risk-Off"
        
        return {
            'score': round(total_score, 1),
            'regime': regime,
            'components': components,
            'as_of': datetime.utcnow().isoformat(),
        }
    
    @staticmethod
    def pca_regime(
        returns_df: pd.DataFrame,
        n_components: int = 3
    ) -> Dict[str, Any]:
        """
        PCA-based regime detection
        First PC = market factor
        Variance explained indicates regime clarity
        """
        from sklearn.decomposition import PCA
        
        try:
            # Drop NaN
            clean_returns = returns_df.dropna(axis=1)
            
            if clean_returns.shape[1] < 3:
                return {'error': 'Need at least 3 assets for PCA'}
            
            pca = PCA(n_components=n_components)
            pca.fit(clean_returns.values)
            
            # Variance explained
            var_explained = pca.explained_variance_ratio_
            
            # First PC scores (market factor)
            pc1_scores = pca.transform(clean_returns.values)[:, 0]
            
            # Current regime based on PC1
            pc1_mean = np.mean(pc1_scores)
            pc1_std = np.std(pc1_scores)
            current_pc1 = pc1_scores[-1]
            
            # Z-score of current PC1
            pc1_z = (current_pc1 - pc1_mean) / pc1_std if pc1_std > 0 else 0
            
            if pc1_z > 1:
                regime = "Risk-On"
            elif pc1_z < -1:
                regime = "Risk-Off"
            else:
                regime = "Neutral"
            
            return {
                'variance_explained': [round(v, 4) for v in var_explained],
                'pc1_current': round(float(current_pc1), 4),
                'pc1_z_score': round(float(pc1_z), 2),
                'regime': regime,
                'loadings': {
                    clean_returns.columns[i]: round(float(pca.components_[0, i]), 4)
                    for i in range(min(10, len(clean_returns.columns)))
                },
            }
        except Exception as e:
            logger.error(f"PCA regime detection failed: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def risk_appetite_index(
        spx_return: float,
        eem_return: float,
        hy_return: float,
        tlt_return: float,
        gold_return: float,
        jpy_return: float,
    ) -> Dict[str, Any]:
        """
        Calculate risk appetite index
        
        Risk assets: SPX, EEM, HY
        Safe havens: TLT, Gold, JPY
        
        Index = (avg risk asset return) - (avg safe haven return)
        """
        risk_assets = [spx_return, eem_return, hy_return]
        safe_havens = [tlt_return, gold_return, jpy_return]
        
        avg_risk = np.mean(risk_assets)
        avg_safe = np.mean(safe_havens)
        
        index_value = avg_risk - avg_safe
        
        # Normalize to 0-100 scale
        # Typical range: -0.05 to +0.05
        normalized = max(0, min(100, (index_value + 0.05) * 1000))
        
        if normalized >= 60:
            signal = "Risk-On"
        elif normalized >= 40:
            signal = "Neutral"
        else:
            signal = "Risk-Off"
        
        return {
            'index': round(normalized, 1),
            'signal': signal,
            'risk_avg_return': round(float(avg_risk), 6),
            'safe_avg_return': round(float(avg_safe), 6),
            'components': {
                'SPX': round(spx_return, 6),
                'EEM': round(eem_return, 6),
                'HY': round(hy_return, 6),
                'TLT': round(tlt_return, 6),
                'Gold': round(gold_return, 6),
                'JPY': round(jpy_return, 6),
            }
        }
    
    @staticmethod
    def credit_impulse(
        hy_oas_series: pd.Series,
        ig_oas_series: pd.Series,
        window: int = 20
    ) -> Dict[str, Any]:
        """
        Calculate credit impulse
        Rate of change in credit spreads
        """
        hy_change = hy_oas_series.diff(window)
        ig_change = ig_oas_series.diff(window)
        
        # Credit impulse: negative change = easing = risk-on
        current_hy_change = float(hy_change.iloc[-1]) if len(hy_change) > 0 else 0
        current_ig_change = float(ig_change.iloc[-1]) if len(ig_change) > 0 else 0
        
        impulse = -(current_hy_change + current_ig_change) / 2
        
        if impulse > 10:
            signal = "Easing (Risk-On)"
        elif impulse > -10:
            signal = "Neutral"
        else:
            signal = "Tightening (Risk-Off)"
        
        return {
            'impulse': round(impulse, 2),
            'signal': signal,
            'hy_change': round(current_hy_change, 2),
            'ig_change': round(current_ig_change, 2),
        }


# Singleton instance
regime_service = RegimeService()
