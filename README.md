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

## Screens

### Dashboard (`/`)
- Market regime gauge with composite score (0-100)
- Correlation heatmap (32×32, switchable 20/60/250D windows)
- Top leaders & laggards
- Macro indicators panel (yield curve, VIX, DXY, credit spreads)
- Daily performance bar chart

### Correlations (`/correlations`)
- Full interactive correlation matrix
- Filter by asset class
- Click any cell to drill into pair analysis
- Notable correlation changes table

### Pair Analysis (`/pair/:a/:b`)
- Normalized price comparison (base=100)
- Z-score spread with ±2σ reference lines
- Rolling correlation with 95% confidence interval
- Anomaly event markers
- Cointegration statistics

### Anomalies (`/anomalies`)
- 200+ detected anomalies
- Filterable by type (corr_break, coint_break, divergence)
- Filterable by severity (critical, high, medium, low)
- Filterable by status (active, monitoring, resolved)

### Strategies (`/strategies`)
- 7 pre-built strategies
- Strategy builder with parameter configuration
- Backtest results with equity curve
- Metrics: Sharpe, Sortino, MaxDD, Hit Rate, Total Return, Turnover

### Alerts (`/alerts`)
- 7 pre-configured alerts
- Toggle active/inactive
- Create new alerts with condition builder

### Reports (`/reports`)
- Date-selectable market snapshot
- Executive summary
- Regime breakdown
- Asset performance
- Correlation changes
- Active anomalies
- Macro indicators
- PDF export (UI ready)

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
- **Dark theme** by default with light toggle
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

## Development

```bash
npm install
npm run dev      # Start dev server
npm run build    # Production build
```

## Model Version

All calculations tagged with `model_version: v2.4.1`

---

*Intermarket Analysis Terminal — Built for macro analysts who need to see the forest AND the trees.*
