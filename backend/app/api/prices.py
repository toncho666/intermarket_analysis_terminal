from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.database import get_db
from app.models import PriceBar

router = APIRouter()


class PriceBarResponse(BaseModel):
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@router.get("/{ticker}", response_model=List[PriceBarResponse])
async def get_prices(
    ticker: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    freq: str = "1d",
    db: AsyncSession = Depends(get_db)
):
    query = select(PriceBar).where(PriceBar.asset_id == ticker.lower())
    
    if from_date:
        query = query.where(PriceBar.ts >= datetime.fromisoformat(from_date))
    if to_date:
        query = query.where(PriceBar.ts <= datetime.fromisoformat(to_date))
    
    query = query.order_by(PriceBar.ts.desc()).limit(1000)
    
    result = await db.execute(query)
    prices = result.scalars().all()
    
    return [
        PriceBarResponse(
            ts=p.ts,
            open=p.open,
            high=p.high,
            low=p.low,
            close=p.close,
            volume=p.volume
        )
        for p in prices
    ]
