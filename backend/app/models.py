from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime


class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(String, primary_key=True)
    ticker = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    asset_class = Column(String, nullable=False, index=True)  # equity, bond, credit, volatility, fx, commodity, crypto, index
    currency = Column(String, default="USD")
    data_source = Column(String, default="yfinance")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    price_bars = relationship("PriceBar", back_populates="asset", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_assets_class_active', 'asset_class', 'is_active'),
    )


class PriceBar(Base):
    """Hypertable for time-series price data"""
    __tablename__ = "price_bars"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(String, ForeignKey("assets.id"), nullable=False)
    ts = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, default=0)
    frequency = Column(String, default="1d")  # 1d, 1h, 5m, 1m
    
    # Relationships
    asset = relationship("Asset", back_populates="price_bars")
    
    __table_args__ = (
        Index('ix_price_bars_asset_ts', 'asset_id', 'ts'),
        Index('ix_price_bars_ts_desc', 'ts', postgresql_ops={'ts': 'DESC'}),
    )


class MacroSeries(Base):
    __tablename__ = "macro_series"
    
    id = Column(String, primary_key=True)
    code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    unit = Column(String, default="")
    frequency = Column(String, default="daily")  # daily, weekly, monthly
    source = Column(String, default="FRED")
    is_active = Column(Boolean, default=True)
    
    # Relationships
    values = relationship("MacroValue", back_populates="series", cascade="all, delete-orphan")


class MacroValue(Base):
    """Hypertable for macro time-series"""
    __tablename__ = "macro_values"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    series_id = Column(String, ForeignKey("macro_series.id"), nullable=False)
    ts = Column(DateTime, nullable=False, index=True)
    value = Column(Float, nullable=False)
    
    # Relationships
    series = relationship("MacroSeries", back_populates="values")
    
    __table_args__ = (
        Index('ix_macro_values_series_ts', 'series_id', 'ts'),
    )


class Correlation(Base):
    """Hypertable for rolling correlations"""
    __tablename__ = "correlations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_a_id = Column(String, ForeignKey("assets.id"), nullable=False)
    asset_b_id = Column(String, ForeignKey("assets.id"), nullable=False)
    window_days = Column(Integer, nullable=False)  # 20, 60, 250
    method = Column(String, default="pearson")  # pearson, spearman, kendall
    ts = Column(DateTime, nullable=False, index=True)
    value = Column(Float, nullable=False)
    delta_vs_prev = Column(Float, default=0)
    ci_low = Column(Float)
    ci_high = Column(Float)
    model_version = Column(String, default="v2.4.1")
    
    __table_args__ = (
        Index('ix_correlations_pair_window_ts', 'asset_a_id', 'asset_b_id', 'window_days', 'ts'),
        Index('ix_correlations_ts_desc', 'ts', postgresql_ops={'ts': 'DESC'}),
    )


class Cointegration(Base):
    """Cointegration test results"""
    __tablename__ = "cointegration"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_a_id = Column(String, ForeignKey("assets.id"), nullable=False)
    asset_b_id = Column(String, ForeignKey("assets.id"), nullable=False)
    window_days = Column(Integer, nullable=False)
    ts = Column(DateTime, nullable=False, index=True)
    method = Column(String, default="engle_granger")  # engle_granger, johansen
    p_value = Column(Float)
    test_statistic = Column(Float)
    half_life = Column(Float)  # days
    is_cointegrated = Column(Boolean, default=False)
    hedge_ratio = Column(Float)
    model_version = Column(String, default="v2.4.1")
    
    __table_args__ = (
        Index('ix_cointegration_pair_window_ts', 'asset_a_id', 'asset_b_id', 'window_days', 'ts'),
    )


class Anomaly(Base):
    __tablename__ = "anomalies"
    
    id = Column(String, primary_key=True)
    asset_a_id = Column(String, ForeignKey("assets.id"), nullable=False)
    asset_b_id = Column(String, ForeignKey("assets.id"), nullable=False)
    type = Column(String, nullable=False)  # corr_break, coint_break, divergence, vol_spike, spread_outlier
    z_score = Column(Float, nullable=False)
    direction = Column(String)  # positive, negative
    detected_at = Column(DateTime, nullable=False, index=True)
    severity = Column(String, default="medium")  # low, medium, high, critical
    status = Column(String, default="active")  # active, monitoring, resolved
    metadata_json = Column(JSON)  # Additional context
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        Index('ix_anomalies_type_severity', 'type', 'severity'),
        Index('ix_anomalies_status', 'status'),
    )


class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    asset_a_id = Column(String, ForeignKey("assets.id"), nullable=False)
    asset_b_id = Column(String, ForeignKey("assets.id"), nullable=False)
    signal_type = Column(String, nullable=False)  # mean_reversion, momentum, lead_lag, carry
    params = Column(JSON, nullable=False)
    created_by = Column(String, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Backtest(Base):
    __tablename__ = "backtests"
    
    id = Column(String, primary_key=True)
    strategy_id = Column(String, ForeignKey("strategies.id"), nullable=False)
    started_at = Column(DateTime, server_default=func.now())
    finished_at = Column(DateTime)
    status = Column(String, default="pending")  # pending, running, completed, failed
    metrics = Column(JSON)  # sharpe, sortino, max_dd, hit_rate, etc.
    equity_curve = Column(JSON)  # Array of {ts, value}
    trades = Column(JSON)  # Array of trades
    model_version = Column(String, default="v2.4.1")
    error_message = Column(Text)


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    condition = Column(JSON, nullable=False)  # {type, asset_a, asset_b, threshold}
    channel = Column(String, default="telegram")  # telegram, email, slack
    is_active = Column(Boolean, default=True)
    last_triggered_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="alerts")


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="analyst")  # analyst, pm, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")


class AuditLog(Base):
    __tablename__ = "audit_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"))
    action = Column(String, nullable=False)
    payload = Column(JSON)
    ts = Column(DateTime, server_default=func.now(), index=True)
