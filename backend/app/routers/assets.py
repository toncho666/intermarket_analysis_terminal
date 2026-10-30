"""Assets router"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import Asset
from app.schemas import AssetResponse

router = APIRouter()


@router.get("/assets", response_model=List[AssetResponse])
async def get_assets(
    asset_class: str = None,
    is_active: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Get all assets with optional filtering"""
    query = select(Asset)
    
    if asset_class:
        query = query.where(Asset.asset_class == asset_class)
    if is_active is not None:
        query = query.where(Asset.is_active == is_active)
    
    query = query.order_by(Asset.asset_class, Asset.ticker)
    
    result = await db.execute(query)
    assets = result.scalars().all()
    
    return assets
