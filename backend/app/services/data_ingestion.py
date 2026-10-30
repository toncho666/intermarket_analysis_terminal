"""
Data ingestion service
- yfinance for stocks, ETFs, FX, commodities
- FRED for macro data
- Binance API for crypto
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import asyncio

logger = logging.getLogger(__name__)


class DataIngestionService:
    """Service for ingesting market data from various sources"""
    
    @staticmethod
    async def fetch_yfinance_data(
        ticker: str,
        start_date: str,
        end_date: str,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch data from Yahoo Finance
        """
        try:
            import yfinance as yf
            
            # Run in thread pool (yfinance is synchronous)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None,
                lambda: yf.download(ticker, start=start_date, end=end_date, interval=interval, progress=False)
            )
            
            if data.empty:
                logger.warning(f"No data from yfinance for {ticker}")
                return pd.DataFrame()
            
            # Flatten multi-level columns if present
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            # Standardize column names
            data = data.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume',
                'Adj Close': 'adj_close',
            })
            
            data['ts'] = data.index
            data = data.reset_index(drop=True)
            
            return data
        except Exception as e:
            logger.error(f"yfinance fetch failed for {ticker}: {e}")
            return pd.DataFrame()
    
    @staticmethod
    async def fetch_fred_series(
        series_id: str,
        start_date: str,
        end_date: str,
        api_key: str
    ) -> pd.DataFrame:
        """
        Fetch macro data from FRED (Federal Reserve Economic Data)
        """
        try:
            from fredapi import Fred
            
            loop = asyncio.get_event_loop()
            fred = await loop.run_in_executor(None, lambda: Fred(api_key=api_key))
            
            data = await loop.run_in_executor(
                None,
                lambda: fred.get_series(series_id, observation_start=start_date, observation_end=end_date)
            )
            
            if data.empty:
                logger.warning(f"No data from FRED for {series_id}")
                return pd.DataFrame()
            
            df = pd.DataFrame({'ts': data.index, 'value': data.values})
            df = df.dropna()
            
            return df
        except Exception as e:
            logger.error(f"FRED fetch failed for {series_id}: {e}")
            return pd.DataFrame()
    
    @staticmethod
    async def fetch_binance_klines(
        symbol: str,
        interval: str = "1d",
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Fetch crypto data from Binance
        """
        try:
            import aiohttp
            
            url = "https://api.binance.com/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit,
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    data = await response.json()
            
            if not data:
                return pd.DataFrame()
            
            df = pd.DataFrame(data, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert types
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            df['ts'] = pd.to_datetime(df['open_time'], unit='ms')
            
            return df[['ts', 'open', 'high', 'low', 'close', 'volume']]
        except Exception as e:
            logger.error(f"Binance fetch failed for {symbol}: {e}")
            return pd.DataFrame()
    
    @staticmethod
    async def fetch_all_assets(
        assets: List[Dict[str, str]],
        start_date: str,
        end_date: str,
        fred_api_key: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for all assets in parallel
        """
        tasks = []
        
        for asset in assets:
            ticker = asset['ticker']
            source = asset.get('source', 'yfinance')
            
            if source == 'yfinance':
                tasks.append(DataIngestionService.fetch_yfinance_data(ticker, start_date, end_date))
            elif source == 'fred' and fred_api_key:
                tasks.append(DataIngestionService.fetch_fred_series(ticker, start_date, end_date, fred_api_key))
            elif source == 'binance':
                tasks.append(DataIngestionService.fetch_binance_klines(ticker))
            else:
                tasks.append(DataIngestionService.fetch_yfinance_data(ticker, start_date, end_date))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        data_dict = {}
        for asset, result in zip(assets, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to fetch {asset['ticker']}: {result}")
                data_dict[asset['ticker']] = pd.DataFrame()
            else:
                data_dict[asset['ticker']] = result
        
        return data_dict
    
    @staticmethod
    def calculate_log_returns(prices: pd.Series) -> pd.Series:
        """Calculate log returns"""
        return np.log(prices / prices.shift(1))
    
    @staticmethod
    def calculate_realized_volatility(returns: pd.Series, window: int = 20) -> pd.Series:
        """Calculate annualized realized volatility"""
        return returns.rolling(window=window).std() * np.sqrt(252)
    
    @staticmethod
    def resample_ohlcv(
        df: pd.DataFrame,
        frequency: str = "1D"
    ) -> pd.DataFrame:
        """
        Resample OHLCV data to different frequency
        """
        if df.empty:
            return df
        
        df = df.set_index('ts')
        
        resampled = df.resample(frequency).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
        })
        
        resampled = resampled.dropna()
        resampled['ts'] = resampled.index
        resampled = resampled.reset_index(drop=True)
        
        return resampled


# Singleton instance
data_ingestion_service = DataIngestionService()
