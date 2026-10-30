from sqlalchemy import Column, String, Float, DateTime, Integer, PrimaryKeyConstraint, Index
from sqlalchemy.sql import func
from app.database import Base


class PriceBar(Base):
    __tablename__ = "price_bars"
    
    asset_id = Column(String, nullable=False, index=True)
    ts = Column(DateTime(timezone=True), nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, default=0)
    frequency = Column(String, default="1d")  # 1d, 1h, 5m, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        PrimaryKeyConstraint('asset_id', 'ts'),
        Index('ix_price_bars_asset_ts', 'asset_id', 'ts'),
    )
