# Intermarket Analysis Terminal

> Macro-economic intermarket analysis dashboard for hedge fund portfolio managers and analysts.

![Status](https://img.shields.io/badge/status-demo-green)
![React](https://img.shields.io/badge/React-18-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)
![Tailwind](https://img.shields.io/badge/Tailwind-4-blue)

## Overview

A comprehensive intermarket analysis terminal that provides real-time visibility into cross-asset correlations, market regime detection, anomaly identification, and strategy backtesting.

### Features

- **🎯 Market Regime Detection** — Real-time risk-on/risk-off gauge with component breakdown
- **📊 Correlation Matrix** — 32×32 interactive heatmap with 20/60/250-day windows
- **🔗 Pair Analysis** — Deep-dive into any asset pair with normalized prices, z-scores, rolling correlations with CI bands
- **⚡ Anomaly Detection** — 200+ detected correlation breaks, cointegration failures, and divergences
- **📈 Strategy Builder** — Create and backtest mean-reversion, momentum, and lead-lag strategies
- **🔔 Alerts** — Configurable alerts for correlation breaks and regime changes
- **📋 Reports** — Generate comprehensive market snapshots with export capability

### Asset Coverage (32 instruments)

| Class | Assets |
|-------|--------|
| **Equities** | SPX, NDX, EEM, DAX, NKY, RTY |
| **Bonds/Rates** | US10Y, US2Y, TLT, US30Y, BUND |
| **Credit** | HY OAS, IG OAS, CDX IG |
| **Volatility** | VIX, MOVE, VVIX, VIX3M |
| **FX** | DXY, EURUSD, USDJPY, AUDJPY, GBPUSD |
| **Commodities** | Brent, WTI, Gold, Copper, Silver, NatGas |
| **Crypto** | BTC, ETH |
| **Indices** | BCOM |

## Экраны и блоки

### 📊 Dashboard (`/`)

**Назначение:** Главная панель мониторинга, предоставляющая мгновенный обзор состояния рынка и межрыночных связей.

**Что видит пользователь:**
- **Regime Gauge** — полукруглый индикатор текущего режима рынка (Risk-On/Neutral/Risk-Off) с композитной оценкой 0-100. Компоненты включают: корреляцию акций и облигаций, терм-структуру VIX, кредитные спреды, динамику DXY и индекс аппетита к риску.
- **Correlation Heatmap** — интерактивная матрица корреляций 32×32 с возможностью переключения окон (20/60/250 дней). Цветовая кодировка: зелёный (положительная корреляция), красный (отрицательная), серый (нейтральная). Клик по ячейке открывает детальный анализ пары.
- **Top Leaders & Laggards** — два виджета с топ-8 активами-лидерами (зелёный) и лаггерами (красный) за день, показывающие процентное изменение.
- **Macro Panel** — сетка из 8 макроиндикаторов: 2s10s spread, 3m10y spread, HY OAS, IG OAS, VIX, DXY, Fed Funds Rate, Real Yield. Каждый индикатор показывает текущее значение, изменение и спарклайн за последние 50 дней.
- **Yield Curve Visualization** — визуализация кривой доходности (3M, 2Y, 5Y, 10Y, 30Y) с цветовой кодировкой.
- **Leaders & Laggards Chart** — горизонтальный столбчатый график дневной производительности всех активов.
- **Quick Stats** — 4 карточки с ключевой статистикой: количество отслеживаемых активов, активных аномалий, корреляций (60D) и версия модели.
- **Asset Ticker** — бегущая строка вверху экрана с текущими ценами и изменениями всех 32 активов.

**Ключевые компоненты:** `RegimeGauge`, `CorrelationHeatmap`, `MacroPanel`, `LeadersLaggards`, `AssetTicker`

---

### 🔗 Correlations (`/correlations`)

**Назначение:** Детальный анализ межрыночных корреляций с возможностью фильтрации и drill-down в пары активов.

**Что видит пользователь:**
- **Multi-select Class Filter** — чипсы с мульти-выбором классов активов (Equity, Bond, Credit, Volatility, FX, Commodity, Crypto, Index). Можно выбрать несколько классов одновременно (например, Equity + Crypto). Кнопки "Select All" и "Clear" для быстрого управления.
- **Window Selector** — переключатель окон корреляции: 20D (краткосрочная), 60D (среднесрочная), 250D (долгосрочная).
- **Interactive Heatmap** — динамическая матрица корреляций, размер которой меняется в зависимости от выбранных классов. При наведении на ячейку показывается tooltip с точным значением корреляции. Клик открывает страницу Pair Analysis для этой пары.
- **Notable Correlation Changes** — таблица с 6 наиболее значимыми изменениями корреляций за период. Показывает пару активов, предыдущее и текущее значение корреляции, дельту (изменение). Цветовая кодировка: зелёный (рост корреляции), красный (падение).
- **Legend** — легенда с градиентом от -1.0 (красный) через 0.0 (серый) до +1.0 (зелёный).

**Ключевые компоненты:** `CorrelationHeatmap` с расширенным фильтром

**Примеры использования:**
- Выбрать "Equity" + "Crypto" чтобы увидеть корреляции между акциями и криптовалютами
- Переключить окно на 250D для анализа долгосрочных структурных связей
- Кликнуть на ячейку SPX × VIX для детального анализа этой пары

---

### 📈 Pair Analysis (`/pair/:a/:b`)

**Назначение:** Глубокий анализ конкретной пары активов с визуализацией спреда, z-score и rolling корреляции.

**Что видит пользователь:**
- **Header** — название пары (например, "SPX × US10Y") с иконкой обмена и описанием активов.
- **Quick Stats** — 5 карточек с ключевыми метриками:
  - Correlation (60D) — текущая корреляция с цветовой индикацией
  - 95% CI — доверительный интервал [lower, upper]
  - Δ vs Prev — изменение корреляции относительно предыдущего периода
  - Anomalies — количество обнаруженных аномалий для этой пары
  - Cointegration — p-value теста на коинтеграцию
- **Normalized Prices Chart** — график нормализованных цен обоих активов (база = 100). Две линии разных цветов (синяя для Asset A, фиолетовая для Asset B) позволяют визуально оценить расхождение/схождение.
- **Z-Score Spread Chart** — график z-score спреда между активами с горизонтальными референсными линиями на ±2σ. Область под графиком залита полупрозрачным цветом. Вертикальные оранжевые линии отмечают моменты обнаружения аномалий.
- **Rolling Correlation Chart** — график скользящей корреляции (60D) с 95% доверительным интервалом (заливка). Горизонтальная линия на 0 для ориентира. Позволяет увидеть, как корреляция меняется во времени и выходит ли за пределы исторического диапазона.
- **Anomaly Events Table** — таблица до 10 последних аномалий для этой пары с датой, типом (corr_break/coint_break/divergence), z-score и severity.

**Ключевые компоненты:** `PairChart`

**Методология:**
- Нормализация цен: `price / price[0] * 100`
- Z-score спреда: `(spread - rolling_mean) / rolling_std` с окном 60 дней
- Rolling correlation: Pearson correlation с окном 60 дней, Fisher z-transform для CI

---

### ⚡ Anomalies (`/anomalies`)

**Назначение:** Мониторинг и управление обнаруженными аномалиями в межрыночных связях.

**Что видит пользователь:**
- **Summary Cards** — 4 карточки со сводной статистикой:
  - Total Anomalies — общее количество обнаруженных аномалий (200+)
  - Active — количество активных (требующих внимания) аномалий
  - Critical — количество критических аномалий (z-score > 4σ)
  - Resolved (30D) — количество разрешённых за последние 30 дней
- **Filter Controls** — три выпадающих списка для фильтрации:
  - Type: All Types, Corr Break, Coint Break, Divergence
  - Severity: All Severity, Critical, High, Medium, Low
  - Status: All Status, Active, Monitoring, Resolved
- **Anomaly Table** — таблица с до 100 аномалий (с пагинацией), колонки:
  - Date — дата обнаружения
  - Pair — пара активов (например, "SPX × VIX")
  - Type — тип аномалии с цветовой кодировкой (синий = corr_break, фиолетовый = coint_break, оранжевый = divergence)
  - Z-Score — величина отклонения с направлением (+/-) и σ
  - Severity — уровень серьёзности с цветовой индикацией (красный = critical, оранжевый = high, жёлтый = medium, серый = low)
  - Status — текущий статус (красный = active, жёлтый = monitoring, зелёный = resolved)
  - Actions — кнопка "View" для просмотра деталей

**Типы аномалий:**
- **Correlation Break** — резкое изменение корреляции (z-score > 2σ от rolling mean)
- **Cointegration Break** — нарушение коинтеграционной связи (p-value > 0.1)
- **Divergence** — расхождение в поведении активов (например, цены растут, а корреляция падает)

**Ключевые компоненты:** `AnomalyTable`

---

### 🎯 Strategies (`/strategies`)

**Назначение:** Конструктор и бэктестер межрыночных стратегий.

**Что видит пользователь:**
- **Strategy List** — сетка из 7 предустановленных стратегий в виде карточек. Каждая карточка показывает:
  - Название стратегии (например, "SPX-VIX Mean Reversion")
  - Тип сигнала с цветовой кодировкой (фиолетовый = mean_reversion, зелёный = momentum, оранжевый = lead_lag)
  - Пару активов (например, "SPX × VIX")
  - Ключевые метрики: Sharpe ratio и Total Return
  - Активная стратегия подсвечивается синей рамкой
- **Strategy Builder** — форма создания новой стратегии (открывается по кнопке "New Strategy"):
  - Name — название стратегии
  - Asset A / Asset B — выпадающие списки с 32 активами
  - Signal Type — тип сигнала: Mean Reversion, Momentum, Lead-Lag
  - Entry Z-Score — порог входа (например, 2.0σ)
  - Exit Z-Score — порог выхода (например, 0.5σ)
  - Window (days) — окно расчёта (например, 60)
  - Кнопка "Run Backtest" для запуска бэктеста
- **Backtest Results** — панель с результатами бэктеста выбранной стратегии:
  - **Metrics Grid** — 6 карточек с ключевыми метриками:
    - Sharpe — отношение доходности к волатильности (>1 = хорошо)
    - Sortino — отношение доходности к downside risk (>1.5 = хорошо)
    - Max DD — максимальная просадка (<-10% = плохо)
    - Hit Rate — процент прибыльных сделок (>55% = хорошо)
    - Total Return — общая доходность за период
    - Turnover — годовая оборачиваемость (<30% = низкие транзакционные издержки)
  - **Equity Curve** — график кривой капитала (начальное значение = 100), показывающий рост/падение портфеля во времени.

**Типы стратегий:**
- **Mean Reversion** — вход при z-score > entry_z, выход при z-score < exit_z. Используется для коинтегрированных пар.
- **Momentum** — вход при ROC(lookback) > threshold, выход при развороте. Ловит тренды.
- **Lead-Lag** — вход в lagger после движения leader на > threshold. Использует опережающие связи.

**Ключевые компоненты:** `StrategyBuilder`

---

### 🔔 Alerts (`/alerts`)

**Назначение:** Управление алертами для мониторинга критических событий и автоматических уведомлений.

**Что видит пользователь:**
- **Alert List** — список из 7 предустановленных алертов в виде карточек. Каждая карточка показывает:
  - Зелёный пульсирующий индикатор для активных алертов, серый для неактивных
  - Условие алерта (например, "Correlation Break • SPX × VIX")
  - Детали: пороговое значение, канал уведомлений (Email/Slack), дата создания
  - Переключатель активности (ToggleRight/ToggleLeft)
  - Кнопка удаления (иконка колокольчика с перечёркиванием)
- **Create Alert Form** — форма создания нового алерта (открывается по кнопке "New Alert"):
  - Condition Type — тип условия: Correlation Break, Cointegration Break, Divergence, Regime Change
  - Asset A / Asset B — выбор активов (для парных условий)
  - Channel — канал уведомлений: Email, Slack, Web Push
  - Кнопка "Create Alert"

**Типы алертов:**
- **Correlation Break** — уведомление при изменении корреляции ниже порога (например, SPX-VIX < -0.7)
- **Divergence** — уведомление при расхождении активов (например, Gold-DXY z-score > 2.0)
- **Regime Change** — уведомление при смене режима рынка (Risk-On ↔ Risk-Off)

**Ключевые компоненты:** Встроенный UI в `AlertsPage`

---

### 📋 Reports (`/reports`)

**Назначение:** Генерация комплексных отчётов о состоянии рынка за выбранную дату.

**Что видит пользователь:**
- **Controls** — панель управления:
  - Date Picker — выбор даты для отчёта
  - Generate Button — кнопка генерации отчёта
- **Report Content** (появляется после генерации):
  - **Header** — заголовок "Intermarket Analysis Snapshot" с датой, версией модели и количеством активов
  - **Export Button** — кнопка экспорта в PDF (UI готов, реализация TODO)
  - **Executive Summary** — текстовое резюме с ключевыми выводами: режим рынка, количество активных аномалий, состояние кредитных спредов, уровень VIX, форма кривой доходности
  - **1. Market Regime** — 6 карточек с компонентами режима: название, значение, сигнал (Risk-On/Neutral/Risk-Off) с цветовой кодировкой
  - **2. Asset Performance** — сетка из 12 активов с тикером и процентным изменением (зелёный/красный)
  - **3. Notable Correlation Changes** — список из 5 наиболее значимых изменений корреляций с парой, текущим значением ρ и дельтой Δ
  - **4. Active Anomalies** — список из 8 активных аномалий с датой, парой, severity и z-score
  - **5. Macro Indicators** — сетка из 8 макроиндикаторов с названием, значением и единицей измерения

**Ключевые компоненты:** Встроенный UI в `ReportsPage`

**Экспорт:** UI для экспорта в PDF и Excel готов, реализация планируется через WeasyPrint и openpyxl на бэкенде.

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite
- **Styling**: Tailwind CSS v4, Apple-inspired dark theme
- **Charts**: Recharts
- **Routing**: React Router v6 (HashRouter)
- **State**: React hooks + context
- **Data**: Deterministic seed-based mock data (32 assets × 1260 days)
- **Fonts**: Inter (UI) + JetBrains Mono (data)

## Architecture

```
src/
├── App.tsx                    # Root with routing
├── main.tsx                   # Entry point
├── index.css                  # Tailwind v4 config + global styles
├── data/
│   └── marketData.ts          # Data generator (GBM + regime switching)
├── stores/
│   └── theme.tsx              # Theme context (dark/light)
├── components/
│   ├── Layout.tsx             # Sidebar + ticker bar layout
│   ├── AssetTicker.tsx        # Scrolling price ticker
│   ├── RegimeGauge.tsx        # SVG gauge + regime components
│   ├── CorrelationHeatmap.tsx # Interactive N×N heatmap
│   ├── PairChart.tsx          # Multi-panel pair analysis
│   ├── MacroPanel.tsx         # Macro indicators grid
│   ├── AnomalyTable.tsx       # Filterable anomaly table
│   ├── StrategyBuilder.tsx    # Strategy CRUD + backtest
│   └── LeadersLaggards.tsx    # Performance bar chart
└── pages/
    ├── Dashboard.tsx
    ├── CorrelationsPage.tsx
    ├── PairPage.tsx
    ├── AnomaliesPage.tsx
    ├── StrategiesPage.tsx
    ├── AlertsPage.tsx
    └── ReportsPage.tsx
```

## Data Generation

The mock data is generated deterministically (seed=42) using:
- **Geometric Brownian Motion** with regime switching (risk-on/risk-off)
- **Seasonality** adjustments
- **Volatility clustering** per regime
- **Realistic start prices** for each instrument
- **Rolling Pearson correlations** with Fisher z confidence intervals
- **200 synthetic anomalies** across major pairs

### Data Volumes
- 32 assets × 1,260 trading days = ~40,320 price bars
- 30 key pairs × 3 windows × ~250 points = ~22,500 correlations
- 200 anomalies
- 8 macro series × 252 points
- 7 strategies with backtests

## Design

- **Apple-inspired** minimal aesthetic
- **Light theme** by default with dark toggle
- **Inter** font for UI, **JetBrains Mono** for data
- **Divergent palette** for correlations (red ↔ green)
- **Semantic colors** for regime (green = risk-on, red = risk-off)
- Responsive for 1440px and 1920px displays
- Smooth transitions and hover states

## Demo Users

| Role | Email | Password |
|------|-------|----------|
| Analyst | analyst@demo.local | demo1234 |
| PM | pm@demo.local | demo1234 |
| Admin | admin@demo.local | demo1234 |

## Backend Architecture

Полноценный бэкенд на FastAPI с расчётным слоем и Telegram-уведомлениями расположен в директории `backend/`.

### Структура бэкенда

```
backend/
├── app/
│   ├── main.py                    # FastAPI приложение
│   ├── config.py                  # Настройки (Pydantic Settings)
│   ├── database.py                # SQLAlchemy async engine
│   ├── models/                    # SQLAlchemy модели
│   │   ├── asset.py               # Активы
│   │   ├── price.py               # Ценовые данные
│   │   ├── correlation.py         # Корреляции
│   │   ├── anomaly.py             # Аномалии
│   │   ├── strategy.py            # Стратегии и бэктесты
│   │   ├── alert.py               # Алерты
│   │   └── user.py                # Пользователи
│   ├── api/                       # FastAPI роутеры
│   │   ├── auth.py                # JWT аутентификация
│   │   ├── assets.py              # CRUD активов
│   │   ├── prices.py              # Ценовые данные
│   │   ├── correlations.py        # Запросы корреляций
│   │   ├── anomalies.py           # Запросы аномалий
│   │   ├── strategies.py          # CRUD стратегий + бэктест
│   │   ├── alerts.py              # CRUD алертов
│   │   └── reports.py             # Генерация отчётов
│   ├── services/                  # Бизнес-логика
│   │   ├── data_ingestion.py      # yfinance, FRED, Binance
│   │   ├── correlation_service.py # Расчёт корреляций
│   │   ├── cointegration_service.py # Коинтеграция
│   │   ├── anomaly_service.py     # Детекция аномалий
│   │   ├── regime_service.py      # Режимы рынка
│   │   ├── backtest_service.py    # Бэктест стратегий
│   │   └── telegram_service.py    # Telegram уведомления
│   ├── tasks/                     # Celery фоновые задачи
│   │   ├── celery_app.py          # Конфигурация Celery
│   │   ├── data_tasks.py          # Загрузка данных
│   │   └── calc_tasks.py          # Расчёты и алерты
│   ├── schemas/                   # Pydantic схемы
│   └── utils/                     # Утилиты (кэш, безопасность)
├── tests/                         # Тесты (pytest)
├── alembic/                       # Миграции БД
├── requirements.txt
├── Dockerfile
└── .env.example
```

### Источники данных

| Источник | Данные | Стоимость |
|----------|--------|-----------|
| **yfinance** | Акции, ETF, FX, commodities | Бесплатно |
| **FRED API** | Макроиндикаторы (ставки, CPI, GDP) | Бесплатно (нужен API key) |
| **Binance API** | Криптовалюты (BTC, ETH) | Бесплатно |

### Расчётные сервисы

#### CorrelationService
- Rolling Pearson/Spearman/Kendall корреляции
- Fisher z-transform доверительные интервалы
- Partial correlation (precision matrix)
- Lead-lag cross-correlation
- Детекция аномалий корреляций (z-score)

#### CointegrationService
- Engle-Granger 2-step тест
- Johansen MLE тест
- Half-life calculation (OU process)
- Spread z-score
- Rolling cointegration
- Hurst exponent (R/S analysis)

#### AnomalyService
- Z-score based detection
- Volatility spike detection
- Spread outlier detection
- Isolation Forest (multivariate)
- CUSUM structural break detection
- Ensemble anomaly detection

#### RegimeService
- Composite regime score (0-100)
- Компоненты: equity-bond corr, VIX term structure, credit spreads, DXY momentum, risk appetite
- Regime change detection
- Volatility regime classification
- Credit regime classification

#### BacktestService
- Mean reversion strategy (z-score based)
- Momentum strategy (ROC based)
- Lead-lag strategy (cross-asset)
- Метрики: Sharpe, Sortino, MaxDD, Hit Rate, Total Return, Turnover

#### TelegramService
- Алерты об аномалиях
- Уведомления о смене режима
- Алерты о breaking correlations
- Уведомления о завершении бэктеста
- Ежедневная сводка рынка

### API Endpoints

#### Аутентификация
- `POST /api/auth/login` — Получить JWT токен
- `GET /api/auth/me` — Информация о текущем пользователе

#### Активы
- `GET /api/assets` — Список всех активов
- `GET /api/assets/{id}` — Детали актива

#### Цены
- `GET /api/prices/{ticker}?from=&to=&freq=` — Исторические цены

#### Корреляции
- `GET /api/correlations?window=60` — Последние корреляции
- `GET /api/correlations/matrix?window=60` — Полная матрица корреляций
- `GET /api/correlations/pairs/{a}/{b}?window=60` — Корреляции для пары

#### Аномалии
- `GET /api/anomalies?type=&severity=&limit=` — Список аномалий

#### Стратегии
- `POST /api/strategies` — Создать стратегию
- `GET /api/strategies` — Список стратегий
- `POST /api/strategies/{id}/backtest` — Запустить бэктест
- `GET /api/strategies/backtests/{id}` — Результаты бэктеста

#### Алерты
- `POST /api/alerts` — Создать алерт
- `GET /api/alerts` — Список алертов пользователя
- `PATCH /api/alerts/{id}` — Обновить алерт
- `DELETE /api/alerts/{id}` — Удалить алерт

#### Отчёты
- `GET /api/reports/snapshot?date=` — Снапшот рынка
- `GET /api/reports/export/pdf` — Экспорт PDF (TODO)
- `GET /api/reports/export/excel` — Экспорт Excel (TODO)

### Запуск бэкенда

```bash
cd backend
cp .env.example .env
# Отредактируйте .env с вашими API ключами:
# - FRED_API_KEY: https://fred.stlouisfed.org/docs/api/api_key.html
# - TELEGRAM_BOT_TOKEN: Создайте бота через @BotFather
# - TELEGRAM_CHAT_ID: Ваш Telegram chat ID

# Запуск через Docker Compose
docker compose up --build

# Сервисы:
# - PostgreSQL + TimescaleDB: localhost:5432
# - Redis: localhost:6379
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Настройка Telegram

1. **Создайте бота:**
   - Откройте Telegram, найдите `@BotFather`
   - Отправьте `/newbot` и следуйте инструкциям
   - Скопируйте токен бота

2. **Получите Chat ID:**
   - Откройте вашего бота и отправьте `/start`
   - Перейдите на `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Найдите `chat.id` в ответе

3. **Настройте .env:**
   ```bash
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_CHAT_ID=123456789
   ```

### Celery Tasks

#### Data Tasks
- `fetch_all_prices` — Загрузка последних цен для всех активов
- `fetch_macro_data` — Загрузка макро данных из FRED
- `initialize_assets` — Создание дефолтных активов в БД

#### Calculation Tasks
- `calculate_correlations` — Rolling корреляции для ключевых пар
- `detect_anomalies` — Детекция аномалий корреляций/волатильности
- `calculate_regime` — Расчёт режима рынка
- `send_daily_summary` — Отправка ежедневной сводки в Telegram

### Тестирование

```bash
cd backend
pytest tests/
pytest --cov=app tests/  # С покрытием
```

Тесты покрывают:
- CorrelationService (rolling correlation, CI, anomaly detection)
- CointegrationService (Engle-Granger, Johansen, half-life)
- BacktestService (mean reversion, momentum, metrics)

## Development

### Frontend

```bash
npm install
npm run dev      # Start dev server (http://localhost:5173)
npm run build    # Production build
npm run preview  # Preview production build
```

### Backend

```bash
cd backend
cp .env.example .env
# Edit .env with your API keys

# Using Docker Compose (recommended)
docker compose up --build

# Or manually
pip install -r requirements.txt
uvicorn app.main:app --reload
celery -A app.tasks.celery_app worker --loglevel=info
```

## Model Version

All calculations tagged with `model_version: v2.4.1`

---

*Intermarket Analysis Terminal — Built for macro analysts who need to see the forest AND the trees.*
