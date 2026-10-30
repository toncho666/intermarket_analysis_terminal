from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List


# Asset schemas
class AssetBase(BaseModel):
    ticker: str
    name: str
    asset_class: str
    currency: str


class AssetCreate(AssetBase):
    id: str
    data_source: str = "yfinance"


class AssetResponse(AssetBase):
    id: str
    data_source: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Price schemas
class PriceBarBase(BaseModel):
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0


class PriceBarResponse(PriceBarBase):
    asset_id: str
    frequency: str = "1d"
    
    class Config:
        from_attributes = True


# Correlation schemas
class CorrelationBase(BaseModel):
    asset_a_id: str
    asset_b_id: str
    window_days: int
    method: str = "pearson"
    value: float


class CorrelationResponse(CorrelationBase):
    ts: datetime
    delta_vs_prev: Optional[float] = None
    ci_low: Optional[float] = None
    ci_high: Optional[float] = None
    model_version: str = "v1.0"
    
    class Config:
        from_attributes = True


class CorrelationMatrixResponse(BaseModel):
    assets: List[str]
    matrix: List[List[float]]
    window: int
    model_version: str


# Anomaly schemas
class AnomalyBase(BaseModel):
    asset_a_id: str
    asset_b_id: str
    type: str
    z_score: float
    direction: str
    severity: str


class AnomalyResponse(AnomalyBase):
    id: str
    detected_at: datetime
    status: str
    model_version: str = "v1.0"
    
    class Config:
        from_attributes = True


# Strategy schemas
class StrategyCreate(BaseModel):
    name: str
    asset_a_id: str
    asset_b_id: str
    signal_type: str
    params: Dict[str, Any]


class StrategyResponse(BaseModel):
    id: str
    name: str
    asset_a_id: str
    asset_b_id: str
    signal_type: str
    params: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Backtest schemas
class BacktestResponse(BaseModel):
    id: str
    strategy_id: str
    metrics: Dict[str, float]
    equity_curve: List[Dict[str, Any]]
    model_version: str = "v1.0"


# Alert schemas
class AlertCreate(BaseModel):
    condition: Dict[str, Any]
    channel: str = "telegram"


class AlertUpdate(BaseModel):
    is_active: Optional[bool] = None
    condition: Optional[Dict[str, Any]] = None


class AlertResponse(BaseModel):
    id: str
    condition: Dict[str, Any]
    channel: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Auth schemas
class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: str
    email: str
    role: str


# Regime schemas
class RegimeComponent(BaseModel):
    name: str
    value: float
    score: float
    signal: str


class RegimeResponse(BaseModel):
    score: float
    regime: str
    components: List[RegimeComponent]
    timestamp: str
    model_version: str


# Report schemas
class SnapshotResponse(BaseModel):
    date: str
    regime: Dict[str, Any]
    top_movers: List[Dict[str, Any]]
    anomalies_count: int
    model_version: str
