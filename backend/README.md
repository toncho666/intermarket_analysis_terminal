# Intermarket Analysis Terminal — Backend

FastAPI-based backend for intermarket analysis with real-time data ingestion, correlation/cointegration calculations, anomaly detection, regime analysis, and Telegram notifications.

## Architecture

```
backend/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Settings (Pydantic)
│   ├── database.py             # SQLAlchemy async engine
│   ├── models/                 # SQLAlchemy models
│   │   ├── asset.py
│   │   ├── price.py
│   │   ├── correlation.py
│   │   ├── anomaly.py
│   │   ├── strategy.py
│   │   ├── alert.py
│   │   └── user.py
│   ├── api/                    # FastAPI routers
│   │   ├── auth.py             # JWT authentication
│   │   ├── assets.py           # Asset CRUD
│   │   ├── prices.py           # Price data
│   │   ├── correlations.py     # Correlation queries
│   │   ├── anomalies.py        # Anomaly queries
│   │   ├── strategies.py       # Strategy CRUD + backtest
│   │   ├── alerts.py           # Alert CRUD
│   │   └── reports.py          # Report generation
│   ├── services/               # Business logic
│   │   ├── data_ingestion.py   # yfinance, FRED, Binance
│   │   ├── correlation_service.py
│   │   ├── cointegration_service.py
│   │   ├── anomaly_service.py
│   │   ├── regime_service.py
│   │   ├── backtest_service.py
│   │   └── telegram_service.py
│   └── tasks/                  # Celery background tasks
│       ├── celery_app.py
│       ├── data_tasks.py       # Price fetching
│       └── calc_tasks.py       # Correlation/anomaly/regime calcs
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Quick Start

### 1. Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)

### 2. Environment Setup

```bash
cd backend
cp .env.example .env
# Edit .env with your API keys:
# - FRED_API_KEY: https://fred.stlouisfed.org/docs/api/api_key.html
# - TELEGRAM_BOT_TOKEN: Create via @BotFather
# - TELEGRAM_CHAT_ID: Your Telegram chat ID
# - SECRET_KEY: Generate with `openssl rand -hex 32`
```

### 3. Run with Docker Compose

```bash
# From project root
docker compose up --build
```

Services:
- **PostgreSQL + TimescaleDB**: `localhost:5432`
- **Redis**: `localhost:6379`
- **Backend API**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs`
- **Frontend**: `http://localhost:3000`

### 4. Initialize Data

```bash
# Enter backend container
docker compose exec backend bash

# Initialize assets
python -c "from app.tasks.data_tasks import initialize_assets; initialize_assets()"

# Fetch historical prices (5 years)
python -c "from app.tasks.data_tasks import fetch_all_prices; fetch_all_prices()"

# Calculate correlations
python -c "from app.tasks.calc_tasks import calculate_correlations; calculate_correlations()"

# Detect anomalies
python -c "from app.tasks.calc_tasks import detect_anomalies; detect_anomalies()"

# Test Telegram connection
python -c "
import asyncio
from app.services.telegram_service import TelegramService
async def test():
    svc = TelegramService()
    result = await svc.test_connection()
    print('Telegram connected!' if result else 'Telegram failed!')
asyncio.run(test())
"
```

## API Endpoints

### Authentication
- `POST /api/auth/login` — Get JWT token
- `GET /api/auth/me` — Current user info

### Assets
- `GET /api/assets` — List all assets
- `GET /api/assets/{id}` — Get asset details

### Prices
- `GET /api/prices/{ticker}?from=&to=&freq=` — Get price history

### Correlations
- `GET /api/correlations?window=60` — Latest correlations
- `GET /api/correlations/matrix?window=60` — Full correlation matrix
- `GET /api/correlations/pairs/{a}/{b}?window=60` — Pair correlations

### Anomalies
- `GET /api/anomalies?type=&severity=&limit=` — List anomalies

### Strategies
- `POST /api/strategies` — Create strategy
- `GET /api/strategies` — List strategies
- `POST /api/strategies/{id}/backtest` — Run backtest
- `GET /api/strategies/backtests/{id}` — Get backtest results

### Alerts
- `POST /api/alerts` — Create alert
- `GET /api/alerts` — List user alerts
- `PATCH /api/alerts/{id}` — Update alert
- `DELETE /api/alerts/{id}` — Delete alert

### Reports
- `GET /api/reports/snapshot?date=` — Market snapshot
- `GET /api/reports/export/pdf` — Export PDF (TODO)
- `GET /api/reports/export/excel` — Export Excel (TODO)

## Data Sources

| Source | Data | Configuration |
|--------|------|---------------|
| **yfinance** | Stocks, ETFs, FX, commodities | Free, no key needed |
| **FRED** | Macro indicators (rates, CPI, GDP) | `FRED_API_KEY` |
| **Binance API** | Crypto (BTC, ETH) | Free, no key needed |

## Calculation Services

### CorrelationService
- Rolling Pearson/Spearman/Kendall correlation
- Fisher z-transform confidence intervals
- Partial correlation (precision matrix)
- Lead-lag cross-correlation
- Correlation anomaly detection (z-score)

### CointegrationService
- Engle-Granger 2-step test
- Johansen MLE test
- Half-life calculation (OU process)
- Spread z-score
- Rolling cointegration
- Hurst exponent (R/S analysis)

### AnomalyService
- Z-score based detection
- Volatility spike detection
- Spread outlier detection
- Isolation Forest (multivariate)
- CUSUM structural break detection
- Ensemble anomaly detection

### RegimeService
- Composite regime score (0-100)
- Components: equity-bond corr, VIX term structure, credit spreads, DXY momentum, risk appetite
- Regime change detection
- Volatility regime classification
- Credit regime classification

### BacktestService
- Mean reversion strategy (z-score based)
- Momentum strategy (ROC based)
- Lead-lag strategy (cross-asset)
- Metrics: Sharpe, Sortino, MaxDD, Hit Rate, Total Return, Turnover

### TelegramService
- Anomaly alerts
- Regime change alerts
- Correlation break alerts
- Backtest completion alerts
- Daily market summary

## Celery Tasks

### Data Tasks
- `fetch_all_prices` — Fetch latest prices for all assets
- `fetch_macro_data` — Fetch FRED macro series
- `initialize_assets` — Create default assets in DB

### Calculation Tasks
- `calculate_correlations` — Rolling correlations for key pairs
- `detect_anomalies` — Detect correlation/volatility anomalies
- `calculate_regime` — Calculate regime score
- `send_daily_summary` — Send daily Telegram summary

### Scheduled (Celery Beat)
```python
# Example schedule (add to celery_app.py)
celery_app.conf.beat_schedule = {
    'fetch-prices-hourly': {
        'task': 'app.tasks.data_tasks.fetch_all_prices',
        'schedule': 3600.0,  # Every hour
    },
    'calculate-correlations-daily': {
        'task': 'app.tasks.calc_tasks.calculate_correlations',
        'schedule': 86400.0,  # Every day
    },
    'detect-anomalies-hourly': {
        'task': 'app.tasks.calc_tasks.detect_anomalies',
        'schedule': 3600.0,
    },
    'daily-summary': {
        'task': 'app.tasks.calc_tasks.send_daily_summary',
        'schedule': crontab(hour=17, minute=0),  # 5 PM daily
    },
}
```

## Telegram Setup

1. **Create Bot:**
   - Open Telegram, search for `@BotFather`
   - Send `/newbot` and follow instructions
   - Copy the bot token

2. **Get Chat ID:**
   - Open your new bot and send `/start`
   - Visit `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Find your `chat.id` in the response

3. **Configure:**
   ```bash
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_CHAT_ID=123456789
   ```

4. **Test:**
   ```python
   from app.services.telegram_service import TelegramService
   import asyncio
   
   async def test():
       svc = TelegramService()
       await svc.send_message("Hello from Intermarket Terminal! 🚀")
   
   asyncio.run(test())
   ```

## Demo Users

After initialization, create demo users:

```python
from app.api.auth import get_password_hash
from app.models import User
from app.database import async_session
import asyncio

async def create_users():
    async with async_session() as session:
        users = [
            User(id="analyst_1", email="analyst@demo.local", 
                 hashed_password=get_password_hash("demo1234"), role="analyst"),
            User(id="pm_1", email="pm@demo.local",
                 hashed_password=get_password_hash("demo1234"), role="pm"),
            User(id="admin_1", email="admin@demo.local",
                 hashed_password=get_password_hash("demo1234"), role="admin"),
        ]
        for user in users:
            session.add(user)
        await session.commit()

asyncio.run(create_users())
```

## Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

## Model Version

All calculations are tagged with `model_version` for reproducibility:
- Correlation: `v1.0`
- Cointegration: `v1.0`
- Anomaly: `v1.0`
- Regime: `v1.0`
- Backtest: `v1.0`

---

*Built with FastAPI, SQLAlchemy, Celery, and love for macro analysis.*
