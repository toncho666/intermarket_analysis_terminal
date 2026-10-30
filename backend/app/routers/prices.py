"""Prices router"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import PriceBar, Asset
from app.schemas import PriceBarResponse
from app.services.cache_service import cache_service

router = APIRouter()


@router.get("/prices/{ticker}", response_model=List[PriceBarResponse])
async def get_prices(
    ticker: str,
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    frequency: str = Query("1d"),
    db: AsyncSession = Depends(get_db)
):
    """Get price bars for an asset"""
    # Find asset
    result = await db.execute(select(Asset).where(Asset.ticker == ticker.upper()))
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {ticker} not found")
    
    # Check cache
    cached = cache_service.get_prices(asset.id, frequency)
    if cached and not from_date and not to_date:
        return cached
    
    # Query database
    query = select(PriceBar).where(PriceBar.asset_id == asset.id)
    
    if from_date:
        query = query.where(PriceBar.ts >= from_date)
    if to_date:
        query = query.where(PriceBar.ts <= to_date)
    
    query = query.where(PriceBar.frequency == frequency)
    query = query.order_by(PriceBar.ts)
    
    result = await db.execute(query)
    prices = result.scalars().all()
    
    # Cache result
    if not from_date and not to_date:
        cache_service.set_prices(asset.id, [PriceBarResponse.from_orm(p).dict() for p in prices], frequency)
    
    return prices
