// ASSUMPTION: All data is generated deterministically with seed 42
// to simulate 5 years of daily data for 30+ intermarket assets

export type AssetClass = 'equity' | 'bond' | 'credit' | 'volatility' | 'fx' | 'commodity' | 'crypto' | 'index';

export interface Asset {
  id: string;
  ticker: string;
  name: string;
  assetClass: AssetClass;
  currency: string;
  isActive: boolean;
}

export interface PriceBar {
  assetId: string;
  ts: string; // ISO date
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Correlation {
  assetA: string;
  assetB: string;
  windowDays: number;
  ts: string;
  value: number;
  deltaVsPrev: number;
  ciLow: number;
  ciHigh: number;
}

export interface Anomaly {
  id: string;
  assetA: string;
  assetB: string;
  type: 'corr_break' | 'coint_break' | 'divergence';
  zScore: number;
  direction: 'positive' | 'negative';
  detectedAt: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'active' | 'resolved' | 'monitoring';
}

export interface MacroSeries {
  code: string;
  name: string;
  unit: string;
  values: { ts: string; value: number }[];
}

export interface Strategy {
  id: string;
  name: string;
  assetA: string;
  assetB: string;
  signalType: 'mean_reversion' | 'momentum' | 'lead_lag';
  params: Record<string, number>;
  createdAt: string;
}

export interface Backtest {
  strategyId: string;
  metrics: {
    sharpe: number;
    sortino: number;
    maxDrawdown: number;
    hitRate: number;
    totalReturn: number;
    turnover: number;
  };
  equityCurve: { ts: string; value: number }[];
}

export interface Alert {
  id: string;
  condition: {
    type: string;
    assetA?: string;
    assetB?: string;
    threshold?: number;
  };
  channel: string;
  isActive: boolean;
  createdAt: string;
}

// Seeded random number generator
class SeededRandom {
  private seed: number;
  constructor(seed: number) { this.seed = seed; }
  next(): number {
    this.seed = (this.seed * 1664525 + 1013904223) & 0xffffffff;
    return (this.seed >>> 0) / 0xffffffff;
  }
  normal(mean = 0, std = 1): number {
    const u1 = this.next();
    const u2 = this.next();
    return mean + std * Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  }
}

const rng = new SeededRandom(42);

// ===== ASSETS =====
export const assets: Asset[] = [
  // Equities
  { id: 'spx', ticker: 'SPX', name: 'S&P 500', assetClass: 'equity', currency: 'USD', isActive: true },
  { id: 'ndx', ticker: 'NDX', name: 'NASDAQ 100', assetClass: 'equity', currency: 'USD', isActive: true },
  { id: 'eem', ticker: 'EEM', name: 'Emerging Markets', assetClass: 'equity', currency: 'USD', isActive: true },
  { id: 'dax', ticker: 'DAX', name: 'DAX 40', assetClass: 'equity', currency: 'EUR', isActive: true },
  { id: 'nkx', ticker: 'NKY', name: 'Nikkei 225', assetClass: 'equity', currency: 'JPY', isActive: true },
  { id: 'rtx', ticker: 'RTY', name: 'Russell 2000', assetClass: 'equity', currency: 'USD', isActive: true },
  // Bonds / Rates
  { id: 'us10y', ticker: 'US10Y', name: 'US 10Y Treasury', assetClass: 'bond', currency: 'USD', isActive: true },
  { id: 'us2y', ticker: 'US2Y', name: 'US 2Y Treasury', assetClass: 'bond', currency: 'USD', isActive: true },
  { id: 'tlt', ticker: 'TLT', name: '20+ Year Treasury ETF', assetClass: 'bond', currency: 'USD', isActive: true },
  { id: 'us30y', ticker: 'US30Y', name: 'US 30Y Treasury', assetClass: 'bond', currency: 'USD', isActive: true },
  { id: 'bund', ticker: 'BUND', name: 'German Bund 10Y', assetClass: 'bond', currency: 'EUR', isActive: true },
  // Credit
  { id: 'hy_oas', ticker: 'HY_OAS', name: 'High Yield OAS', assetClass: 'credit', currency: 'USD', isActive: true },
  { id: 'ig_oas', ticker: 'IG_OAS', name: 'Investment Grade OAS', assetClass: 'credit', currency: 'USD', isActive: true },
  { id: 'cdx_ig', ticker: 'CDX_IG', name: 'CDX IG Index', assetClass: 'credit', currency: 'USD', isActive: true },
  // Volatility
  { id: 'vix', ticker: 'VIX', name: 'CBOE Volatility Index', assetClass: 'volatility', currency: 'USD', isActive: true },
  { id: 'move', ticker: 'MOVE', name: 'Bond Volatility Index', assetClass: 'volatility', currency: 'USD', isActive: true },
  { id: 'vvix', ticker: 'VVIX', name: 'VIX of VIX', assetClass: 'volatility', currency: 'USD', isActive: true },
  // FX
  { id: 'dxy', ticker: 'DXY', name: 'US Dollar Index', assetClass: 'fx', currency: 'USD', isActive: true },
  { id: 'eurusd', ticker: 'EURUSD', name: 'EUR/USD', assetClass: 'fx', currency: 'USD', isActive: true },
  { id: 'usdjpy', ticker: 'USDJPY', name: 'USD/JPY', assetClass: 'fx', currency: 'JPY', isActive: true },
  { id: 'audjpy', ticker: 'AUDJPY', name: 'AUD/JPY (Carry)', assetClass: 'fx', currency: 'JPY', isActive: true },
  { id: 'gbpusd', ticker: 'GBPUSD', name: 'GBP/USD', assetClass: 'fx', currency: 'USD', isActive: true },
  // Commodities
  { id: 'brent', ticker: 'BRENT', name: 'Brent Crude', assetClass: 'commodity', currency: 'USD', isActive: true },
  { id: 'wti', ticker: 'WTI', name: 'WTI Crude', assetClass: 'commodity', currency: 'USD', isActive: true },
  { id: 'gold', ticker: 'GOLD', name: 'Gold', assetClass: 'commodity', currency: 'USD', isActive: true },
  { id: 'copper', ticker: 'COPPER', name: 'Copper', assetClass: 'commodity', currency: 'USD', isActive: true },
  { id: 'silver', ticker: 'SILVER', name: 'Silver', assetClass: 'commodity', currency: 'USD', isActive: true },
  { id: 'natgas', ticker: 'NATGAS', name: 'Natural Gas', assetClass: 'commodity', currency: 'USD', isActive: true },
  // Crypto
  { id: 'btc', ticker: 'BTC', name: 'Bitcoin', assetClass: 'crypto', currency: 'USD', isActive: true },
  { id: 'eth', ticker: 'ETH', name: 'Ethereum', assetClass: 'crypto', currency: 'USD', isActive: true },
  // Indices
  { id: 'bcom', ticker: 'BCOM', name: 'Bloomberg Commodity Index', assetClass: 'index', currency: 'USD', isActive: true },
  { id: 'vix3m', ticker: 'VIX3M', name: 'VIX 3-Month', assetClass: 'volatility', currency: 'USD', isActive: true },
];

// ===== PRICE GENERATION =====
// Geometric Brownian Motion with regime switching
function generatePrices(): PriceBar[] {
  const bars: PriceBar[] = [];
  const startDate = new Date('2020-01-02');
  const numDays = 1260; // ~5 years of trading days
  
  // Base parameters per asset class
  const baseParams: Record<AssetClass, { drift: number; vol: number; startPrice: number }> = {
    equity: { drift: 0.0004, vol: 0.012, startPrice: 100 },
    bond: { drift: 0.00005, vol: 0.004, startPrice: 100 },
    credit: { drift: -0.0001, vol: 0.008, startPrice: 100 },
    volatility: { drift: -0.001, vol: 0.04, startPrice: 20 },
    fx: { drift: 0.00001, vol: 0.005, startPrice: 100 },
    commodity: { drift: 0.0002, vol: 0.015, startPrice: 100 },
    crypto: { drift: 0.001, vol: 0.035, startPrice: 100 },
    index: { drift: 0.0002, vol: 0.012, startPrice: 100 },
  };

  // Specific start prices for realism
  const startPrices: Record<string, number> = {
    spx: 3250, ndx: 9000, eem: 42, dax: 13000, nkx: 23500, rtx: 165,
    us10y: 1.9, us2y: 1.6, tlt: 135, us30y: 2.4, bund: -0.1,
    hy_oas: 350, ig_oas: 100, cdx_ig: 75,
    vix: 17, move: 80, vvix: 90,
    dxy: 97, eurusd: 1.12, usdjpy: 109, audjpy: 75, gbpusd: 1.30,
    brent: 60, wti: 55, gold: 1520, copper: 2.8, silver: 17.5, natgas: 2.5,
    btc: 7200, eth: 180, bcom: 85, vix3m: 20,
  };

  // Regime: 0 = risk-on, 1 = risk-off
  // Generate regime sequence
  const regimes: number[] = [];
  let regime = 0;
  for (let i = 0; i < numDays; i++) {
    if (rng.next() < 0.02) regime = 1 - regime; // 2% chance of regime switch
    regimes.push(regime);
  }

  for (const asset of assets) {
    const params = baseParams[asset.assetClass];
    const startPrice = startPrices[asset.id] || params.startPrice;
    let price = startPrice;
    
    for (let i = 0; i < numDays; i++) {
      const date = new Date(startDate);
      date.setDate(date.getDate() + Math.floor(i * 365.25 / 252));
      
      // Regime adjustment
      const regimeAdj = regimes[i] === 1 ? -0.001 : 0.0002;
      const volAdj = regimes[i] === 1 ? 1.5 : 1.0;
      
      // Seasonality (weak)
      const month = date.getMonth();
      const seasonality = Math.sin(2 * Math.PI * month / 12) * 0.0001;
      
      const dailyReturn = params.drift + regimeAdj + seasonality + params.vol * volAdj * rng.normal();
      price = price * Math.exp(dailyReturn);
      
      const dayVol = params.vol * volAdj * Math.abs(rng.normal());
      const open = price * (1 + rng.normal(0, 0.002));
      const high = Math.max(open, price) * (1 + Math.abs(rng.normal(0, dayVol * 0.5)));
      const low = Math.min(open, price) * (1 - Math.abs(rng.normal(0, dayVol * 0.5)));
      
      bars.push({
        assetId: asset.id,
        ts: date.toISOString().split('T')[0],
        open: Math.round(open * 10000) / 10000,
        high: Math.round(high * 10000) / 10000,
        low: Math.round(low * 10000) / 10000,
        close: Math.round(price * 10000) / 10000,
        volume: Math.round(1000000 * (0.5 + rng.next())),
      });
    }
  }
  
  return bars;
}

// ===== CORRELATIONS =====
function generateCorrelations(bars: PriceBar[]): Correlation[] {
  const correlations: Correlation[] = [];
  const windows = [20, 60, 250];
  const assetIds = assets.map(a => a.id);
  
  // Group by asset
  const pricesByAsset: Record<string, number[]> = {};
  for (const asset of assets) {
    pricesByAsset[asset.id] = bars
      .filter(b => b.assetId === asset.id)
      .map(b => Math.log(b.close));
  }
  
  // Generate correlations for key pairs
  const keyPairs: [string, string][] = [
    ['spx', 'ndx'], ['spx', 'eem'], ['spx', 'dax'], ['spx', 'us10y'],
    ['spx', 'vix'], ['spx', 'dxy'], ['spx', 'gold'], ['spx', 'btc'],
    ['us10y', 'us2y'], ['us10y', 'tlt'], ['us10y', 'vix'],
    ['gold', 'us10y'], ['gold', 'dxy'], ['gold', 'vix'],
    ['btc', 'eth'], ['btc', 'ndx'], ['btc', 'vix'],
    ['brent', 'wti'], ['brent', 'dxy'], ['copper', 'gold'],
    ['dxy', 'eurusd'], ['dxy', 'usdjpy'], ['dxy', 'gold'],
    ['hy_oas', 'spx'], ['hy_oas', 'vix'], ['ig_oas', 'spx'],
    ['vix', 'move'], ['vix', 'vvix'],
    ['spx', 'rtx'], ['ndx', 'nkx'], ['eem', 'dax'],
  ];
  
  for (const [aId, bId] of keyPairs) {
    const pricesA = pricesByAsset[aId];
    const pricesB = pricesByAsset[bId];
    if (!pricesA || !pricesB) continue;
    
    const len = Math.min(pricesA.length, pricesB.length);
    
    for (const window of windows) {
      let prevCorr = 0;
      for (let i = window; i < len; i += 5) { // every 5 days
        const sliceA = pricesA.slice(i - window, i);
        const sliceB = pricesB.slice(i - window, i);
        
        // Calculate returns
        const retA = sliceA.map((v, j) => j > 0 ? v - sliceA[j-1] : 0).slice(1);
        const retB = sliceB.map((v, j) => j > 0 ? v - sliceB[j-1] : 0).slice(1);
        
        // Pearson correlation
        const n = retA.length;
        const meanA = retA.reduce((s, v) => s + v, 0) / n;
        const meanB = retB.reduce((s, v) => s + v, 0) / n;
        let cov = 0, varA = 0, varB = 0;
        for (let j = 0; j < n; j++) {
          cov += (retA[j] - meanA) * (retB[j] - meanB);
          varA += (retA[j] - meanA) ** 2;
          varB += (retB[j] - meanB) ** 2;
        }
        const corr = varA > 0 && varB > 0 ? cov / Math.sqrt(varA * varB) : 0;
        
        const date = new Date('2020-01-02');
        date.setDate(date.getDate() + Math.floor(i * 365.25 / 252));
        
        correlations.push({
          assetA: aId,
          assetB: bId,
          windowDays: window,
          ts: date.toISOString().split('T')[0],
          value: Math.round(corr * 1000) / 1000,
          deltaVsPrev: Math.round((corr - prevCorr) * 1000) / 1000,
          ciLow: Math.round((corr - 1.96 / Math.sqrt(window)) * 1000) / 1000,
          ciHigh: Math.round((corr + 1.96 / Math.sqrt(window)) * 1000) / 1000,
        });
        
        prevCorr = corr;
      }
    }
  }
  
  return correlations;
}

// ===== ANOMALIES =====
function generateAnomalies(): Anomaly[] {
  const anomalies: Anomaly[] = [];
  const types: Anomaly['type'][] = ['corr_break', 'coint_break', 'divergence'];
  const severities: Anomaly['severity'][] = ['low', 'medium', 'high', 'critical'];
  const statuses: Anomaly['status'][] = ['active', 'resolved', 'monitoring'];
  
  const pairs: [string, string][] = [
    ['spx', 'vix'], ['spx', 'us10y'], ['gold', 'dxy'], ['btc', 'ndx'],
    ['brent', 'wti'], ['copper', 'gold'], ['hy_oas', 'spx'], ['eurusd', 'dxy'],
    ['spx', 'eem'], ['vix', 'move'], ['btc', 'eth'], ['spx', 'ndx'],
    ['gold', 'us10y'], ['dxy', 'usdjpy'], ['brent', 'dxy'],
  ];
  
  for (let i = 0; i < 200; i++) {
    const pair = pairs[Math.floor(rng.next() * pairs.length)];
    const dayOffset = Math.floor(rng.next() * 1200) + 60;
    const date = new Date('2020-01-02');
    date.setDate(date.getDate() + Math.floor(dayOffset * 365.25 / 252));
    
    anomalies.push({
      id: `anom_${i}`,
      assetA: pair[0],
      assetB: pair[1],
      type: types[Math.floor(rng.next() * types.length)],
      zScore: Math.round((2 + rng.next() * 3) * 100) / 100,
      direction: rng.next() > 0.5 ? 'positive' : 'negative',
      detectedAt: date.toISOString().split('T')[0],
      severity: severities[Math.floor(rng.next() * severities.length)],
      status: statuses[Math.floor(rng.next() * statuses.length)],
    });
  }
  
  return anomalies.sort((a, b) => b.detectedAt.localeCompare(a.detectedAt));
}

// ===== MACRO SERIES =====
function generateMacroSeries(): MacroSeries[] {
  const startDate = new Date('2020-01-02');
  const numDays = 1260;
  
  function genSeries(baseValue: number, vol: number, trend: number): { ts: string; value: number }[] {
    const values: { ts: string; value: number }[] = [];
    let val = baseValue;
    for (let i = 0; i < numDays; i += 5) {
      const date = new Date(startDate);
      date.setDate(date.getDate() + Math.floor(i * 365.25 / 252));
      val += trend + vol * rng.normal();
      values.push({ ts: date.toISOString().split('T')[0], value: Math.round(val * 100) / 100 });
    }
    return values;
  }
  
  return [
    { code: 'yield_curve_2s10s', name: '2s10s Spread', unit: 'bps', values: genSeries(30, 15, -0.3) },
    { code: 'yield_curve_3m10y', name: '3m10y Spread', unit: 'bps', values: genSeries(80, 20, -0.5) },
    { code: 'hy_oas', name: 'HY OAS', unit: 'bps', values: genSeries(350, 30, 0.1) },
    { code: 'ig_oas', name: 'IG OAS', unit: 'bps', values: genSeries(100, 10, 0.05) },
    { code: 'vix_level', name: 'VIX Level', unit: '', values: genSeries(17, 3, -0.01) },
    { code: 'dxy_level', name: 'DXY Level', unit: '', values: genSeries(97, 1.5, 0.02) },
    { code: 'fed_funds', name: 'Fed Funds Rate', unit: '%', values: genSeries(1.5, 0, 0.015) },
    { code: 'real_yield', name: '10Y Real Yield', unit: '%', values: genSeries(-0.5, 0.2, 0.005) },
  ];
}

// ===== STRATEGIES =====
function generateStrategies(): Strategy[] {
  return [
    { id: 'strat_1', name: 'SPX-VIX Mean Reversion', assetA: 'spx', assetB: 'vix', signalType: 'mean_reversion', params: { entryZ: 2.0, exitZ: 0.5, window: 60 }, createdAt: '2023-01-15' },
    { id: 'strat_2', name: 'Gold-DXY Momentum', assetA: 'gold', assetB: 'dxy', signalType: 'momentum', params: { lookback: 20, threshold: 0.02 }, createdAt: '2023-03-20' },
    { id: 'strat_3', name: 'BTC-ETH Lead-Lag', assetA: 'btc', assetB: 'eth', signalType: 'lead_lag', params: { lagDays: 2, threshold: 0.03 }, createdAt: '2023-06-10' },
    { id: 'strat_4', name: 'Copper-Gold Ratio', assetA: 'copper', assetB: 'gold', signalType: 'mean_reversion', params: { entryZ: 1.5, exitZ: 0.3, window: 90 }, createdAt: '2023-08-05' },
    { id: 'strat_5', name: 'HY OAS Regime', assetA: 'hy_oas', assetB: 'spx', signalType: 'momentum', params: { lookback: 40, threshold: 0.05 }, createdAt: '2024-01-10' },
    { id: 'strat_6', name: 'Brent-WTI Spread', assetA: 'brent', assetB: 'wti', signalType: 'mean_reversion', params: { entryZ: 2.5, exitZ: 0.5, window: 30 }, createdAt: '2024-03-15' },
    { id: 'strat_7', name: 'EURUSD Carry', assetA: 'eurusd', assetB: 'us10y', signalType: 'lead_lag', params: { lagDays: 3, threshold: 0.02 }, createdAt: '2024-05-20' },
  ];
}

// ===== BACKTESTS =====
function generateBacktests(): Backtest[] {
  const backtests: Backtest[] = [];
  
  for (const strat of generateStrategies()) {
    const equityCurve: { ts: string; value: number }[] = [];
    let equity = 100;
    const startDate = new Date('2021-01-01');
    
    for (let i = 0; i < 500; i++) {
      const date = new Date(startDate);
      date.setDate(date.getDate() + Math.floor(i * 365.25 / 252));
      equity *= (1 + rng.normal(0.0003, 0.008));
      equityCurve.push({ ts: date.toISOString().split('T')[0], value: Math.round(equity * 100) / 100 });
    }
    
    backtests.push({
      strategyId: strat.id,
      metrics: {
        sharpe: Math.round((0.5 + rng.next() * 2) * 100) / 100,
        sortino: Math.round((0.8 + rng.next() * 2.5) * 100) / 100,
        maxDrawdown: Math.round((-5 - rng.next() * 20) * 100) / 100,
        hitRate: Math.round((45 + rng.next() * 20) * 100) / 100,
        totalReturn: Math.round((rng.next() * 50 - 5) * 100) / 100,
        turnover: Math.round((10 + rng.next() * 40) * 100) / 100,
      },
      equityCurve,
    });
  }
  
  return backtests;
}

// ===== ALERTS =====
function generateAlerts(): Alert[] {
  return [
    { id: 'alert_1', condition: { type: 'corr_break', assetA: 'spx', assetB: 'vix', threshold: -0.7 }, channel: 'email', isActive: true, createdAt: '2024-01-15' },
    { id: 'alert_2', condition: { type: 'divergence', assetA: 'gold', assetB: 'dxy', threshold: 2.0 }, channel: 'slack', isActive: true, createdAt: '2024-02-20' },
    { id: 'alert_3', condition: { type: 'corr_break', assetA: 'btc', assetB: 'ndx', threshold: 0.8 }, channel: 'email', isActive: true, createdAt: '2024-03-10' },
    { id: 'alert_4', condition: { type: 'coint_break', assetA: 'brent', assetB: 'wti', threshold: 3.0 }, channel: 'slack', isActive: false, createdAt: '2024-04-05' },
    { id: 'alert_5', condition: { type: 'divergence', assetA: 'copper', assetB: 'gold', threshold: 2.5 }, channel: 'email', isActive: true, createdAt: '2024-05-12' },
    { id: 'alert_6', condition: { type: 'corr_break', assetA: 'hy_oas', assetB: 'spx', threshold: -0.6 }, channel: 'slack', isActive: true, createdAt: '2024-06-01' },
    { id: 'alert_7', condition: { type: 'regime_change', threshold: 0.7 }, channel: 'email', isActive: true, createdAt: '2024-06-15' },
  ];
}

// ===== GENERATE ALL DATA =====
export const priceBars = generatePrices();
export const correlations = generateCorrelations(priceBars);
export const anomalies = generateAnomalies();
export const macroSeries = generateMacroSeries();
export const strategies = generateStrategies();
export const backtests = generateBacktests();
export const alerts = generateAlerts();

// ===== HELPER FUNCTIONS =====
export function getAssetByTicker(ticker: string): Asset | undefined {
  return assets.find(a => a.ticker === ticker || a.id === ticker.toLowerCase());
}

export function getAssetById(id: string): Asset | undefined {
  return assets.find(a => a.id === id);
}

export function getPricesForAsset(assetId: string, from?: string, to?: string): PriceBar[] {
  return priceBars.filter(b => {
    if (b.assetId !== assetId) return false;
    if (from && b.ts < from) return false;
    if (to && b.ts > to) return false;
    return true;
  });
}

export function getCorrelationsForPair(assetA: string, assetB: string, window?: number): Correlation[] {
  return correlations.filter(c => {
    const match = (c.assetA === assetA && c.assetB === assetB) || (c.assetA === assetB && c.assetB === assetA);
    if (!match) return false;
    if (window && c.windowDays !== window) return false;
    return true;
  });
}

export function getLatestPrices(): { assetId: string; price: number; change: number; changePct: number }[] {
  return assets.map(asset => {
    const assetBars = priceBars.filter(b => b.assetId === asset.id);
    const latest = assetBars[assetBars.length - 1];
    const prev = assetBars[assetBars.length - 2];
    if (!latest || !prev) return { assetId: asset.id, price: 0, change: 0, changePct: 0 };
    return {
      assetId: asset.id,
      price: latest.close,
      change: latest.close - prev.close,
      changePct: ((latest.close - prev.close) / prev.close) * 100,
    };
  });
}

export function getCorrelationMatrix(window: number): { assets: string[]; matrix: number[][] } {
  const assetIds = assets.map(a => a.id);
  const matrix: number[][] = assetIds.map(() => assetIds.map(() => 0));
  
  for (const corr of correlations) {
    if (corr.windowDays !== window) continue;
    // Use the latest correlation for each pair
    const iA = assetIds.indexOf(corr.assetA);
    const iB = assetIds.indexOf(corr.assetB);
    if (iA >= 0 && iB >= 0) {
      matrix[iA][iB] = corr.value;
      matrix[iB][iA] = corr.value;
    }
  }
  
  // Fill diagonal
  for (let i = 0; i < assetIds.length; i++) {
    matrix[i][i] = 1;
  }
  
  return { assets: assetIds, matrix };
}

export function getRegimeData(): { score: number; components: { name: string; value: number; signal: string }[] } {
  return {
    score: 62,
    components: [
      { name: 'Equity-Bond Corr', value: -0.35, signal: 'Risk-On' },
      { name: 'VIX Term Structure', value: 0.72, signal: 'Risk-On' },
      { name: 'Credit Spreads', value: 0.55, signal: 'Neutral' },
      { name: 'DXY Momentum', value: -0.28, signal: 'Risk-On' },
      { name: 'HY-IG Spread', value: 0.65, signal: 'Risk-On' },
      { name: 'Commodity Momentum', value: 0.42, signal: 'Neutral' },
    ],
  };
}
