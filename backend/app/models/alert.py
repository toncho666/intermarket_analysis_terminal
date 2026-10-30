from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    condition = Column(JSONB, nullable=False)  # {type, asset_a, asset_b, threshold, ...}
    channel = Column(String, nullable=False)  # telegram, email, slack
    is_active = Column(Boolean, default=True)
    last_triggered_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
