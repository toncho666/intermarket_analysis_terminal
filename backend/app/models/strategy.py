from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    asset_a_id = Column(String, ForeignKey("assets.id"), nullable=False)
    asset_b_id = Column(String, ForeignKey("assets.id"), nullable=False)
    signal_type = Column(String, nullable=False)  # mean_reversion, momentum, lead_lag
    params = Column(JSONB, nullable=False)
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(String, default="true")


class Backtest(Base):
    __tablename__ = "backtests"
    
    id = Column(String, primary_key=True)
    strategy_id = Column(String, ForeignKey("strategies.id"), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=False)
    finished_at = Column(DateTime(timezone=True))
    metrics = Column(JSONB)  # sharpe, sortino, max_drawdown, hit_rate, etc.
    equity_curve = Column(JSONB)  # array of {ts, value}
    trades = Column(JSONB)  # array of trades
    model_version = Column(String, default="v1.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
