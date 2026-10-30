"""Pairs router"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import Dict, Any

from app.database import get_db
from app.models import Asset, PriceBar, Correlation, Cointegration, Anomaly

router = APIRouter()


@router.get("/pairs/{ticker_a}/{ticker_b}")
async def get_pair_analysis(
    ticker_a: str,
    ticker_b: str,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive pair analysis"""
    # Find assets
    result_a = await db.execute(select(Asset).where(Asset.ticker == ticker_a.upper()))
    asset_a = result_a.scalar_one_or_none()
    
    result_b = await db.execute(select(Asset).where(Asset.ticker == ticker_b.upper()))
    asset_b = result_b.scalar_one_or_none()
    
    if not asset_a or not asset_b:
        raise HTTPException(status_code=404, detail="One or both assets not found")
    
    # Get prices
    prices_a_result = await db.execute(
        select(PriceBar).where(PriceBar.asset_id == asset_a.id).order_by(PriceBar.ts)
    )
    prices_a = prices_a_result.scalars().all()
    
    prices_b_result = await db.execute(
        select(PriceBar).where(PriceBar.asset_id == asset_b.id).order_by(PriceBar.ts)
    )
    prices_b = prices_b_result.scalars().all()
    
    # Get latest correlation
    corr_result = await db.execute(
        select(Correlation).where(
            and_(
                or_(
                    and_(Correlation.asset_a_id == asset_a.id, Correlation.asset_b_id == asset_b.id),
                    and_(Correlation.asset_a_id == asset_b.id, Correlation.asset_b_id == asset_a.id)
                ),
                Correlation.window_days == 60
            )
        ).order_by(Correlation.ts.desc()).limit(1)
    )
    latest_corr = corr_result.scalar_one_or_none()
    
    # Get cointegration
    coint_result = await db.execute(
        select(Cointegration).where(
            or_(
                and_(Cointegration.asset_a_id == asset_a.id, Cointegration.asset_b_id == asset_b.id),
                and_(Cointegration.asset_a_id == asset_b.id, Cointegration.asset_b_id == asset_a.id)
            )
        ).order_by(Cointegration.ts.desc()).limit(1)
    )
    cointegration = coint_result.scalar_one_or_none()
    
    # Get anomalies
    anomaly_result = await db.execute(
        select(Anomaly).where(
            or_(
                and_(Anomaly.asset_a_id == asset_a.id, Anomaly.asset_b_id == asset_b.id),
                and_(Anomaly.asset_a_id == asset_b.id, Anomaly.asset_b_id == asset_a.id)
            )
        ).order_by(Anomaly.detected_at.desc()).limit(50)
    )
    anomalies = anomaly_result.scalars().all()
    
    return {
        "asset_a": {"id": asset_a.id, "ticker": asset_a.ticker, "name": asset_a.name},
        "asset_b": {"id": asset_b.id, "ticker": asset_b.ticker, "name": asset_b.name},
        "prices_a": [{"ts": p.ts.isoformat(), "close": p.close} for p in prices_a[-500:]],
        "prices_b": [{"ts": p.ts.isoformat(), "close": p.close} for p in prices_b[-500:]],
        "correlation": {
            "value": latest_corr.value if latest_corr else None,
            "ci_low": latest_corr.ci_low if latest_corr else None,
            "ci_high": latest_corr.ci_high if latest_corr else None,
            "delta": latest_corr.delta_vs_prev if latest_corr else None,
        } if latest_corr else None,
        "cointegration": {
            "p_value": cointegration.p_value,
            "half_life": cointegration.half_life,
            "is_cointegrated": cointegration.is_cointegrated,
            "hedge_ratio": cointegration.hedge_ratio,
        } if cointegration else None,
        "anomalies": [
            {
                "id": a.id,
                "type": a.type,
                "z_score": a.z_score,
                "severity": a.severity,
                "detected_at": a.detected_at.isoformat(),
            }
            for a in anomalies
        ],
    }
