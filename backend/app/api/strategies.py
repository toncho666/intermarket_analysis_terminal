from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.database import get_db
from app.models import Strategy, Backtest, User
from app.api.auth import get_current_user

router = APIRouter()


class StrategyCreate(BaseModel):
    name: str
    asset_a_id: str
    asset_b_id: str
    signal_type: str
    params: dict


class StrategyResponse(BaseModel):
    id: str
    name: str
    asset_a_id: str
    asset_b_id: str
    signal_type: str
    params: dict
    created_at: datetime


class BacktestResponse(BaseModel):
    id: str
    strategy_id: str
    metrics: dict
    equity_curve: list


@router.post("/", response_model=StrategyResponse)
async def create_strategy(
    strategy: StrategyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_strategy = Strategy(
        id=str(uuid.uuid4()),
        name=strategy.name,
        asset_a_id=strategy.asset_a_id,
        asset_b_id=strategy.asset_b_id,
        signal_type=strategy.signal_type,
        params=strategy.params,
        created_by=current_user.id
    )
    db.add(new_strategy)
    await db.commit()
    await db.refresh(new_strategy)
    
    return StrategyResponse(
        id=new_strategy.id,
        name=new_strategy.name,
        asset_a_id=new_strategy.asset_a_id,
        asset_b_id=new_strategy.asset_b_id,
        signal_type=new_strategy.signal_type,
        params=new_strategy.params,
        created_at=new_strategy.created_at
    )


@router.get("/", response_model=List[StrategyResponse])
async def get_strategies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Strategy).order_by(Strategy.created_at.desc()))
    strategies = result.scalars().all()
    
    return [
        StrategyResponse(
            id=s.id,
            name=s.name,
            asset_a_id=s.asset_a_id,
            asset_b_id=s.asset_b_id,
            signal_type=s.signal_type,
            params=s.params,
            created_at=s.created_at
        )
        for s in strategies
    ]


@router.post("/{strategy_id}/backtest", response_model=BacktestResponse)
async def run_backtest(
    strategy_id: str,
    db: AsyncSession = Depends(get_db)
):
    strategy = await db.get(Strategy, strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # TODO: Run actual backtest using BacktestService
    # For now, return mock result
    
    backtest = Backtest(
        id=str(uuid.uuid4()),
        strategy_id=strategy_id,
        started_at=datetime.utcnow(),
        finished_at=datetime.utcnow(),
        metrics={
            "sharpe": 1.2,
            "sortino": 1.8,
            "max_drawdown": -8.5,
            "hit_rate": 55.0,
            "total_return": 12.3,
            "turnover": 25.0
        },
        equity_curve=[
            {"ts": "2024-01-01", "value": 100},
            {"ts": "2024-06-01", "value": 106},
            {"ts": "2024-12-01", "value": 112}
        ]
    )
    db.add(backtest)
    await db.commit()
    await db.refresh(backtest)
    
    return BacktestResponse(
        id=backtest.id,
        strategy_id=backtest.strategy_id,
        metrics=backtest.metrics,
        equity_curve=backtest.equity_curve
    )


@router.get("/backtests/{backtest_id}", response_model=BacktestResponse)
async def get_backtest(backtest_id: str, db: AsyncSession = Depends(get_db)):
    backtest = await db.get(Backtest, backtest_id)
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")
    
    return BacktestResponse(
        id=backtest.id,
        strategy_id=backtest.strategy_id,
        metrics=backtest.metrics,
        equity_curve=backtest.equity_curve
    )
