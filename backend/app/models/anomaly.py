from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.sql import func
from app.database import Base


class Anomaly(Base):
    __tablename__ = "anomalies"
    
    id = Column(String, primary_key=True)
    asset_a_id = Column(String, nullable=False, index=True)
    asset_b_id = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False, index=True)  # corr_break, coint_break, divergence, vol_spike
    z_score = Column(Float, nullable=False)
    direction = Column(String, nullable=False)  # positive, negative
    detected_at = Column(DateTime(timezone=True), nullable=False, index=True)
    severity = Column(String, nullable=False)  # low, medium, high, critical
    status = Column(String, default="active", index=True)  # active, monitoring, resolved
    metadata_json = Column(String)  # JSON string for additional data
    model_version = Column(String, default="v1.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))
