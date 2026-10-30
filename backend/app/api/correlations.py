from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models import Correlation

router = APIRouter()


class CorrelationResponse(BaseModel):
    asset_a_id: str
    asset_b_id: str
    window_days: int
    ts: datetime
    value: float
    delta_vs_prev: Optional[float]
    ci_low: Optional[float]
    ci_high: Optional[float]


@router.get("/", response_model=List[CorrelationResponse])
async def get_correlations(
    window: int = 60,
    asset_class: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Correlation)
        .where(Correlation.window_days == window)
        .order_by(Correlation.ts.desc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    correlations = result.scalars().all()
    
    return [
        CorrelationResponse(
            asset_a_id=c.asset_a_id,
            asset_b_id=c.asset_b_id,
            window_days=c.window_days,
            ts=c.ts,
            value=c.value,
            delta_vs_prev=c.delta_vs_prev,
            ci_low=c.ci_low,
            ci_high=c.ci_high
        )
        for c in correlations
    ]


@router.get("/matrix")
async def get_correlation_matrix(
    window: int = 60,
    date: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    # Get latest correlations for each pair
    query = (
        select(Correlation)
        .where(Correlation.window_days == window)
        .order_by(Correlation.ts.desc())
    )
    
    result = await db.execute(query)
    correlations = result.scalars().all()
    
    # Build matrix (simplified)
    assets = set()
    for c in correlations:
        assets.add(c.asset_a_id)
        assets.add(c.asset_b_id)
    
    assets = sorted(list(assets))
    matrix = [[0.0] * len(assets) for _ in range(len(assets))]
    
    asset_idx = {a: i for i, a in enumerate(assets)}
    
    for c in correlations[:100]:  # Limit for performance
        i = asset_idx.get(c.asset_a_id)
        j = asset_idx.get(c.asset_b_id)
        if i is not None and j is not None:
            matrix[i][j] = c.value
            matrix[j][i] = c.value
    
    # Diagonal = 1
    for i in range(len(assets)):
        matrix[i][i] = 1.0
    
    return {
        "assets": assets,
        "matrix": matrix,
        "window": window,
        "model_version": "v1.0"
    }


@router.get("/pairs/{asset_a}/{asset_b}", response_model=List[CorrelationResponse])
async def get_pair_correlations(
    asset_a: str,
    asset_b: str,
    window: int = 60,
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Correlation)
        .where(
            ((Correlation.asset_a_id == asset_a.lower()) & (Correlation.asset_b_id == asset_b.lower())) |
            ((Correlation.asset_a_id == asset_b.lower()) & (Correlation.asset_b_id == asset_a.lower()))
        )
        .where(Correlation.window_days == window)
        .order_by(Correlation.ts.desc())
        .limit(500)
    )
    
    result = await db.execute(query)
    correlations = result.scalars().all()
    
    return [
        CorrelationResponse(
            asset_a_id=c.asset_a_id,
            asset_b_id=c.asset_b_id,
            window_days=c.window_days,
            ts=c.ts,
            value=c.value,
            delta_vs_prev=c.delta_vs_prev,
            ci_low=c.ci_low,
            ci_high=c.ci_high
        )
        for c in correlations
    ]
