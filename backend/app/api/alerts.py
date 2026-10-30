from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.database import get_db
from app.models import Alert, User
from app.api.auth import get_current_user

router = APIRouter()


class AlertCreate(BaseModel):
    condition: dict
    channel: str = "telegram"


class AlertUpdate(BaseModel):
    is_active: Optional[bool] = None
    condition: Optional[dict] = None


class AlertResponse(BaseModel):
    id: str
    condition: dict
    channel: str
    is_active: bool
    created_at: datetime


@router.post("/", response_model=AlertResponse)
async def create_alert(
    alert: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_alert = Alert(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        condition=alert.condition,
        channel=alert.channel,
        is_active=True
    )
    db.add(new_alert)
    await db.commit()
    await db.refresh(new_alert)
    
    return AlertResponse(
        id=new_alert.id,
        condition=new_alert.condition,
        channel=new_alert.channel,
        is_active=new_alert.is_active,
        created_at=new_alert.created_at
    )


@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Alert)
        .where(Alert.user_id == current_user.id)
        .order_by(Alert.created_at.desc())
    )
    alerts = result.scalars().all()
    
    return [
        AlertResponse(
            id=a.id,
            condition=a.condition,
            channel=a.channel,
            is_active=a.is_active,
            created_at=a.created_at
        )
        for a in alerts
    ]


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: str,
    update: AlertUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    alert = await db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if alert.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if update.is_active is not None:
        alert.is_active = update.is_active
    if update.condition is not None:
        alert.condition = update.condition
    
    await db.commit()
    await db.refresh(alert)
    
    return AlertResponse(
        id=alert.id,
        condition=alert.condition,
        channel=alert.channel,
        is_active=alert.is_active,
        created_at=alert.created_at
    )


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    alert = await db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if alert.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.delete(alert)
    await db.commit()
    
    return {"status": "deleted"}
