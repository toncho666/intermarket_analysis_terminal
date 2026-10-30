"""Regime router"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.database import get_db
from app.schemas import RegimeResponse
from app.services.cache_service import cache_service

router = APIRouter()


@router.get("/regime", response_model=RegimeResponse)
async def get_regime(db: AsyncSession = Depends(get_db)):
    """Get current market regime"""
    # Check cache
    cached = cache_service.get_regime()
    if cached:
        return cached
    
    # Calculate regime (simplified - should use actual data)
    # In production, this would fetch real data and calculate
    regime_data = {
        "score": 62.0,
        "regime": "Neutral",
        "components": [
            {"name": "Equity-Bond Corr", "value": -0.35, "signal": "Risk-On"},
            {"name": "VIX Term Structure", "value": 0.72, "signal": "Risk-On"},
            {"name": "Credit Spreads", "value": 0.55, "signal": "Neutral"},
            {"name": "DXY Momentum", "value": -0.28, "signal": "Risk-On"},
            {"name": "HY-IG Spread", "value": 0.65, "signal": "Risk-On"},
        ],
        "as_of": datetime.utcnow(),
        "model_version": "v2.4.1",
    }
    
    # Cache
    cache_service.set_regime(regime_data)
    
    return regime_data
