from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(String, primary_key=True)
    ticker = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    asset_class = Column(String, nullable=False, index=True)  # equity, bond, credit, volatility, fx, commodity, crypto, index
    currency = Column(String, nullable=False)
    data_source = Column(String, default="yfinance")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
