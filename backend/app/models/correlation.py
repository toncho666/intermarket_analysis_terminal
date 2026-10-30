from sqlalchemy import Column, String, Float, DateTime, Integer, PrimaryKeyConstraint, Index
from sqlalchemy.sql import func
from app.database import Base


class Correlation(Base):
    __tablename__ = "correlations"
    
    asset_a_id = Column(String, nullable=False, index=True)
    asset_b_id = Column(String, nullable=False, index=True)
    window_days = Column(Integer, nullable=False, index=True)
    method = Column(String, default="pearson")  # pearson, spearman, kendall
    ts = Column(DateTime(timezone=True), nullable=False, index=True)
    value = Column(Float, nullable=False)
    delta_vs_prev = Column(Float)
    ci_low = Column(Float)
    ci_high = Column(Float)
    model_version = Column(String, default="v1.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        PrimaryKeyConstraint('asset_a_id', 'asset_b_id', 'window_days', 'method', 'ts'),
        Index('ix_correlations_pair_window', 'asset_a_id', 'asset_b_id', 'window_days', 'ts'),
    )
