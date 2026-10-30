import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import structlog
from fredapi import Fred
import httpx

from app.config import settings

logger = structlog.get_logger()


class DataIngestionService:
    """Service for ingesting market data from various sources."""
    
    def __init__(self):
        self.fred = Fred(api_key=settings.FRED_API_KEY) if settings.FRED_API_KEY else None
    
    async def fetch_yfinance_data(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """Fetch price data from Yahoo Finance."""
        try:
            logger.info("Fetching yfinance data", ticker=ticker, start=start_date, end=end_date)
            data = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                interval=interval,
                progress=False
            )
            
            if data.empty:
                logger.warning("No data returned", ticker=ticker)
                return pd.DataFrame()
            
            # Flatten multi-level columns if present
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            data = data.reset_index()
            data.columns = [col.lower() for col in data.columns]
            
            # Rename date column
            if 'date' in data.columns:
                data = data.rename(columns={'date': 'ts'})
            elif 'datetime' in data.columns:
                data = data.rename(columns={'datetime': 'ts'})
            
            return data
            
        except Exception as e:
            logger.error("Error fetching yfinance data", ticker=ticker, error=str(e))
            return pd.DataFrame()
    
    async def fetch_fred_series(
        self,
        series_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """Fetch macro data from FRED."""
        if not self.fred:
            logger.warning("FRED API key not configured")
            return pd.DataFrame()
        
        try:
            logger.info("Fetching FRED data", series_id=series_id)
            data = self.fred.get_series(
                series_id,
                observation_start=start_date,
                observation_end=end_date
            )
            
            df = data.reset_index()
            df.columns = ['ts', 'value']
            df['ts'] = pd.to_datetime(df['ts'])
            
            return df
            
        except Exception as e:
            logger.error("Error fetching FRED data", series_id=series_id, error=str(e))
            return pd.DataFrame()
    
    async def fetch_binance_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """Fetch crypto data from Binance API."""
        try:
            logger.info("Fetching Binance data", symbol=symbol)
            
            url = "https://api.binance.com/api/v3/klines"
            start_ms = int(start_date.timestamp() * 1000)
            end_ms = int(end_date.timestamp() * 1000)
            
            params = {
                "symbol": symbol,
                "interval": interval,
                "startTime": start_ms,
                "endTime": end_ms,
                "limit": 1000
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
            
            if not data:
                return pd.DataFrame()
            
            df = pd.DataFrame(data, columns=[
                'ts', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            df['ts'] = pd.to_datetime(df['ts'], unit='ms')
            df = df[['ts', 'open', 'high', 'low', 'close', 'volume']].copy()
            df = df.astype({'open': float, 'high': float, 'low': float, 'close': float, 'volume': float})
            
            return df
            
        except Exception as e:
            logger.error("Error fetching Binance data", symbol=symbol, error=str(e))
            return pd.DataFrame()
    
    def calculate_log_returns(self, prices: pd.Series) -> pd.Series:
        """Calculate log returns from price series."""
        return np.log(prices / prices.shift(1))
    
    def calculate_realized_volatility(
        self,
        returns: pd.Series,
        window: int = 20,
        annualize: bool = True
    ) -> pd.Series:
        """Calculate realized volatility."""
        vol = returns.rolling(window=window).std()
        if annualize:
            vol = vol * np.sqrt(252)
        return vol
    
    def calculate_parkinson_volatility(
        self,
        high: pd.Series,
        low: pd.Series,
        window: int = 20
    ) -> pd.Series:
        """Calculate Parkinson volatility estimator."""
        hl_ratio = np.log(high / low) ** 2
        factor = 1 / (4 * np.log(2))
        vol = np.sqrt(factor * hl_ratio.rolling(window=window).mean() * 252)
        return vol


# Default assets to track
DEFAULT_ASSETS = [
    # Equities
    {"id": "spx", "ticker": "^GSPC", "name": "S&P 500", "asset_class": "equity", "currency": "USD"},
    {"id": "ndx", "ticker": "^NDX", "name": "NASDAQ 100", "asset_class": "equity", "currency": "USD"},
    {"id": "eem", "ticker": "EEM", "name": "Emerging Markets ETF", "asset_class": "equity", "currency": "USD"},
    {"id": "dax", "ticker": "^GDAXI", "name": "DAX 40", "asset_class": "equity", "currency": "EUR"},
    {"id": "nky", "ticker": "^N225", "name": "Nikkei 225", "asset_class": "equity", "currency": "JPY"},
    {"id": "rty", "ticker": "^RUT", "name": "Russell 2000", "asset_class": "equity", "currency": "USD"},
    
    # Bonds
    {"id": "us10y", "ticker": "^TNX", "name": "US 10Y Treasury Yield", "asset_class": "bond", "currency": "USD"},
    {"id": "us2y", "ticker": "^IRX", "name": "US 2Y Treasury Yield", "asset_class": "bond", "currency": "USD"},
    {"id": "tlt", "ticker": "TLT", "name": "20+ Year Treasury ETF", "asset_class": "bond", "currency": "USD"},
    {"id": "us30y", "ticker": "^TYX", "name": "US 30Y Treasury Yield", "asset_class": "bond", "currency": "USD"},
    
    # Credit (proxies)
    {"id": "hyg", "ticker": "HYG", "name": "High Yield Bond ETF", "asset_class": "credit", "currency": "USD"},
    {"id": "lqd", "ticker": "LQD", "name": "Investment Grade Bond ETF", "asset_class": "credit", "currency": "USD"},
    
    # Volatility
    {"id": "vix", "ticker": "^VIX", "name": "CBOE Volatility Index", "asset_class": "volatility", "currency": "USD"},
    {"id": "vix3m", "ticker": "^VIX3M", "name": "VIX 3-Month", "asset_class": "volatility", "currency": "USD"},
    
    # FX
    {"id": "dxy", "ticker": "UUP", "name": "US Dollar Index (ETF proxy)", "asset_class": "fx", "currency": "USD"},
    {"id": "eurusd", "ticker": "EURUSD=X", "name": "EUR/USD", "asset_class": "fx", "currency": "USD"},
    {"id": "usdjpy", "ticker": "JPY=X", "name": "USD/JPY", "asset_class": "fx", "currency": "JPY"},
    
    # Commodities
    {"id": "brent", "ticker": "BZ=F", "name": "Brent Crude", "asset_class": "commodity", "currency": "USD"},
    {"id": "wti", "ticker": "CL=F", "name": "WTI Crude", "asset_class": "commodity", "currency": "USD"},
    {"id": "gold", "ticker": "GC=F", "name": "Gold", "asset_class": "commodity", "currency": "USD"},
    {"id": "copper", "ticker": "HG=F", "name": "Copper", "asset_class": "commodity", "currency": "USD"},
    {"id": "silver", "ticker": "SI=F", "name": "Silver", "asset_class": "commodity", "currency": "USD"},
    
    # Crypto
    {"id": "btc", "ticker": "BTC-USD", "name": "Bitcoin", "asset_class": "crypto", "currency": "USD"},
    {"id": "eth", "ticker": "ETH-USD", "name": "Ethereum", "asset_class": "crypto", "currency": "USD"},
]

# FRED series to track
FRED_SERIES = [
    {"code": "DFF", "name": "Federal Funds Rate", "unit": "%"},
    {"code": "DGS2", "name": "2-Year Treasury Yield", "unit": "%"},
    {"code": "DGS10", "name": "10-Year Treasury Yield", "unit": "%"},
    {"code": "T10Y2Y", "name": "10Y-2Y Spread", "unit": "%"},
    {"code": "BAMLH0A0HYM2", "name": "High Yield OAS", "unit": "bps"},
    {"code": "BAMLC0A0CM", "name": "Investment Grade OAS", "unit": "bps"},
    {"code": "CPIAUCSL", "name": "CPI", "unit": "Index"},
    {"code": "UNRATE", "name": "Unemployment Rate", "unit": "%"},
]
