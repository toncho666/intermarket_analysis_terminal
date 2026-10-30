"""Anomalies router"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.database import get_db
from app.models import Anomaly
from app.schemas import AnomalyResponse

router = APIRouter()


@router.get("/anomalies", response_model=List[AnomalyResponse])
async def get_anomalies(
    type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100),
    db: AsyncSession = Depends(get_db)
):
    """Get anomalies with filtering"""
    query = select(Anomaly)
    
    if type:
        query = query.where(Anomaly.type == type)
    if severity:
        query = query.where(Anomaly.severity == severity)
    if status:
        query = query.where(Anomaly.status == status)
    
    query = query.order_by(Anomaly.detected_at.desc()).limit(limit)
    
    result = await db.execute(query)
    anomalies = result.scalars().all()
    
    return anomalies
