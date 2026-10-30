"""Correlations router"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import Correlation, Asset
from app.schemas import CorrelationResponse, CorrelationMatrixResponse
from app.services.cache_service import cache_service

router = APIRouter()


@router.get("/correlations", response_model=List[CorrelationResponse])
async def get_correlations(
    window: int = Query(60),
    asset_class: Optional[str] = Query(None),
    method: str = Query("pearson"),
    limit: int = Query(1000),
    db: AsyncSession = Depends(get_db)
):
    """Get correlations with optional filtering"""
    query = select(Correlation).where(
        Correlation.window_days == window,
        Correlation.method == method
    )
    
    # Filter by asset class if specified
    if asset_class:
        # Get asset IDs for this class
        asset_result = await db.execute(
            select(Asset.id).where(Asset.asset_class == asset_class)
        )
        asset_ids = [row[0] for row in asset_result.all()]
        
        if asset_ids:
            query = query.where(
                or_(
                    Correlation.asset_a_id.in_(asset_ids),
                    Correlation.asset_b_id.in_(asset_ids)
                )
            )
    
    query = query.order_by(Correlation.ts.desc()).limit(limit)
    
    result = await db.execute(query)
    correlations = result.scalars().all()
    
    return correlations


@router.get("/correlations/matrix", response_model=CorrelationMatrixResponse)
async def get_correlation_matrix(
    window: int = Query(60),
    date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get correlation matrix for all assets"""
    # Check cache
    cached = cache_service.get_correlation_matrix(window)
    if cached and not date:
        return cached
    
    # Get all active assets
    asset_result = await db.execute(
        select(Asset).where(Asset.is_active == True).order_by(Asset.asset_class, Asset.ticker)
    )
    assets = asset_result.scalars().all()
    asset_ids = [a.id for a in assets]
    
    # Initialize matrix
    n = len(asset_ids)
    matrix = [[0.0] * n for _ in range(n)]
    
    # Get latest correlations for each pair
    for i, asset_a in enumerate(asset_ids):
        for j, asset_b in enumerate(asset_ids):
            if i == j:
                matrix[i][j] = 1.0
                continue
            
            if i > j:
                matrix[i][j] = matrix[j][i]
                continue
            
            # Find correlation
            corr_result = await db.execute(
                select(Correlation).where(
                    and_(
                        or_(
                            and_(Correlation.asset_a_id == asset_a, Correlation.asset_b_id == asset_b),
                            and_(Correlation.asset_a_id == asset_b, Correlation.asset_b_id == asset_a)
                        ),
                        Correlation.window_days == window
                    )
                ).order_by(Correlation.ts.desc()).limit(1)
            )
            
            corr = corr_result.scalar_one_or_none()
            if corr:
                matrix[i][j] = corr.value
                matrix[j][i] = corr.value
    
    result = CorrelationMatrixResponse(
        assets=[a.ticker for a in assets],
        matrix=matrix,
        window_days=window,
        as_of=datetime.utcnow(),
        model_version="v2.4.1"
    )
    
    # Cache
    if not date:
        cache_service.set_correlation_matrix(window, result.dict())
    
    return result
