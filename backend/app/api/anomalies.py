from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models import Anomaly

router = APIRouter()


class AnomalyResponse(BaseModel):
    id: str
    asset_a_id: str
    asset_b_id: str
    type: str
    z_score: float
    direction: str
    detected_at: datetime
    severity: str
    status: str


@router.get("/", response_model=List[AnomalyResponse])
async def get_anomalies(
    type: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
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
    
    return [
        AnomalyResponse(
            id=a.id,
            asset_a_id=a.asset_a_id,
            asset_b_id=a.asset_b_id,
            type=a.type,
            z_score=a.z_score,
            direction=a.direction,
            detected_at=a.detected_at,
            severity=a.severity,
            status=a.status
        )
        for a in anomalies
    ]
