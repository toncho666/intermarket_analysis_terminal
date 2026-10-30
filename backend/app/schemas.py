from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ===== Enums =====
class AssetClass(str, Enum):
    EQUITY = "equity"
    BOND = "bond"
    CREDIT = "credit"
    VOLATILITY = "volatility"
    FX = "fx"
    COMMODITY = "commodity"
    CRYPTO = "crypto"
    INDEX = "index"


class SignalType(str, Enum):
    MEAN_REVERSION = "mean_reversion"
    MOMENTUM = "momentum"
    LEAD_LAG = "lead_lag"
    CARRY = "carry"


class AnomalyType(str, Enum):
    CORR_BREAK = "corr_break"
    COINT_BREAK = "coint_break"
    DIVERGENCE = "divergence"
    VOL_SPIKE = "vol_spike"
    SPREAD_OUTLIER = "spread_outlier"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UserRole(str, Enum):
    ANALYST = "analyst"
    PM = "pm"
    ADMIN = "admin"


# ===== Auth =====
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


class UserCreate(BaseModel):
    email: str
    password: str
    role: UserRole = UserRole.ANALYST


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str
    password: str


# ===== Assets =====
class AssetResponse(BaseModel):
    id: str
    ticker: str
    name: str
    asset_class: str
    currency: str
    data_source: str
    is_active: bool
    
    class Config:
        from_attributes = True


# ===== Prices =====
class PriceBarResponse(BaseModel):
    asset_id: str
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    frequency: str
    
    class Config:
        from_attributes = True


class PriceQuery(BaseModel):
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    frequency: str = "1d"


# ===== Correlations =====
class CorrelationResponse(BaseModel):
    asset_a_id: str
    asset_b_id: str
    window_days: int
    method: str
    ts: datetime
    value: float
    delta_vs_prev: float
    ci_low: Optional[float] = None
    ci_high: Optional[float] = None
    model_version: str
    
    class Config:
        from_attributes = True


class CorrelationMatrixResponse(BaseModel):
    assets: List[str]
    matrix: List[List[float]]
    window_days: int
    as_of: datetime
    model_version: str


class CorrelationQuery(BaseModel):
    window: int = 60
    asset_class: Optional[str] = None
    method: str = "pearson"


# ===== Cointegration =====
class CointegrationResponse(BaseModel):
    asset_a_id: str
    asset_b_id: str
    window_days: int
    ts: datetime
    method: str
    p_value: Optional[float] = None
    test_statistic: Optional[float] = None
    half_life: Optional[float] = None
    is_cointegrated: bool
    hedge_ratio: Optional[float] = None
    model_version: str
    
    class Config:
        from_attributes = True


# ===== Anomalies =====
class AnomalyResponse(BaseModel):
    id: str
    asset_a_id: str
    asset_b_id: str
    type: str
    z_score: float
    direction: Optional[str] = None
    detected_at: datetime
    severity: str
    status: str
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnomalyQuery(BaseModel):
    type: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    limit: int = 100


# ===== Macro =====
class MacroSeriesResponse(BaseModel):
    id: str
    code: str
    name: str
    unit: str
    frequency: str
    source: str
    
    class Config:
        from_attributes = True


class MacroValueResponse(BaseModel):
    series_id: str
    ts: datetime
    value: float
    
    class Config:
        from_attributes = True


# ===== Regime =====
class RegimeComponent(BaseModel):
    name: str
    value: float
    signal: str  # Risk-On, Risk-Off, Neutral


class RegimeResponse(BaseModel):
    score: float  # 0-100
    regime: str  # Risk-On, Neutral, Risk-Off
    components: List[RegimeComponent]
    as_of: datetime
    model_version: str


# ===== Strategies =====
class StrategyCreate(BaseModel):
    name: str
    asset_a_id: str
    asset_b_id: str
    signal_type: SignalType
    params: Dict[str, Any]


class StrategyResponse(BaseModel):
    id: str
    name: str
    asset_a_id: str
    asset_b_id: str
    signal_type: str
    params: Dict[str, Any]
    created_by: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== Backtests =====
class BacktestMetrics(BaseModel):
    sharpe: float
    sortino: float
    max_drawdown: float
    hit_rate: float
    total_return: float
    turnover: float
    calmar: Optional[float] = None
    profit_factor: Optional[float] = None


class BacktestResponse(BaseModel):
    id: str
    strategy_id: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    status: str
    metrics: Optional[BacktestMetrics] = None
    equity_curve: Optional[List[Dict[str, Any]]] = None
    model_version: str
    
    class Config:
        from_attributes = True


# ===== Alerts =====
class AlertCondition(BaseModel):
    type: str
    asset_a: Optional[str] = None
    asset_b: Optional[str] = None
    threshold: Optional[float] = None


class AlertCreate(BaseModel):
    condition: AlertCondition
    channel: str = "telegram"


class AlertResponse(BaseModel):
    id: str
    user_id: str
    condition: Dict[str, Any]
    channel: str
    is_active: bool
    last_triggered_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    is_active: Optional[bool] = None
    condition: Optional[Dict[str, Any]] = None


# ===== Reports =====
class ReportSnapshot(BaseModel):
    date: str
    regime: RegimeResponse
    top_movers: List[Dict[str, Any]]
    correlation_changes: List[Dict[str, Any]]
    active_anomalies: List[AnomalyResponse]
    macro_indicators: List[Dict[str, Any]]
    generated_at: datetime
    model_version: str


# ===== Generic =====
class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    timestamp: datetime
    database: str = "connected"
    redis: str = "connected"


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
