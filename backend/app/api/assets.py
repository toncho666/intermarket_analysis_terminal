from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app.models import Asset

router = APIRouter()


class AssetResponse(BaseModel):
    id: str
    ticker: str
    name: str
    asset_class: str
    currency: str
    is_active: bool


@router.get("/", response_model=List[AssetResponse])
async def get_assets(
    asset_class: str = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Asset).where(Asset.is_active == True)
    
    if asset_class:
        query = query.where(Asset.asset_class == asset_class)
    
    result = await db.execute(query)
    assets = result.scalars().all()
    
    return [
        AssetResponse(
            id=a.id,
            ticker=a.ticker,
            name=a.name,
            asset_class=a.asset_class,
            currency=a.currency,
            is_active=a.is_active
        )
        for a in assets
    ]


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: str, db: AsyncSession = Depends(get_db)):
    asset = await db.get(Asset, asset_id)
    if not asset:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return AssetResponse(
        id=asset.id,
        ticker=asset.ticker,
        name=asset.name,
        asset_class=asset.asset_class,
        currency=asset.currency,
        is_active=asset.is_active
    )
