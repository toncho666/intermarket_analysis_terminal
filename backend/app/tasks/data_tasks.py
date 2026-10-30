import asyncio
from datetime import datetime, timedelta
from typing import List
import structlog
import pandas as pd

from app.tasks.celery_app import celery_app
from app.services.data_ingestion import DataIngestionService, DEFAULT_ASSETS
from app.database import async_session
from app.models import Asset, PriceBar

logger = structlog.get_logger()


@celery_app.task(name="app.tasks.data_tasks.fetch_all_prices")
def fetch_all_prices():
    """Fetch latest prices for all assets."""
    asyncio.run(_fetch_all_prices_async())


async def _fetch_all_prices_async():
    """Async implementation of price fetching."""
    service = DataIngestionService()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5)  # Last 5 days
    
    async with async_session() as session:
        for asset_config in DEFAULT_ASSETS:
            try:
                # Fetch data based on asset class
                if asset_config['asset_class'] == 'crypto':
                    # Use Binance for crypto
                    symbol = asset_config['ticker'].replace('-USD', 'USDT')
                    df = await service.fetch_binance_data(
                        symbol=symbol,
                        start_date=start_date,
                        end_date=end_date
                    )
                else:
                    # Use yfinance for everything else
                    df = await service.fetch_yfinance_data(
                        ticker=asset_config['ticker'],
                        start_date=start_date,
                        end_date=end_date
                    )
                
                if df.empty:
                    continue
                
                # Ensure asset exists
                asset = await session.get(Asset, asset_config['id'])
                if not asset:
                    asset = Asset(
                        id=asset_config['id'],
                        ticker=asset_config['ticker'],
                        name=asset_config['name'],
                        asset_class=asset_config['asset_class'],
                        currency=asset_config['currency']
                    )
                    session.add(asset)
                    await session.flush()
                
                # Insert price bars
                for _, row in df.iterrows():
                    price_bar = PriceBar(
                        asset_id=asset_config['id'],
                        ts=row['ts'],
                        open=float(row['open']),
                        high=float(row['high']),
                        low=float(row['low']),
                        close=float(row['close']),
                        volume=float(row.get('volume', 0)),
                        frequency='1d'
                    )
                    session.add(price_bar)
                
                await session.commit()
                logger.info("Fetched prices", asset=asset_config['id'], rows=len(df))
                
            except Exception as e:
                logger.error("Failed to fetch prices", asset=asset_config['id'], error=str(e))
                await session.rollback()


@celery_app.task(name="app.tasks.data_tasks.fetch_macro_data")
def fetch_macro_data():
    """Fetch macro data from FRED."""
    asyncio.run(_fetch_macro_data_async())


async def _fetch_macro_data_async():
    """Async implementation of macro data fetching."""
    service = DataIngestionService()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * 5)  # 5 years
    
    from app.services.data_ingestion import FRED_SERIES
    
    async with async_session() as session:
        for series_config in FRED_SERIES:
            try:
                df = await service.fetch_fred_series(
                    series_id=series_config['code'],
                    start_date=start_date,
                    end_date=end_date
                )
                
                if df.empty:
                    continue
                
                # Store in macro_values table (to be created)
                logger.info("Fetched macro data", series=series_config['code'], rows=len(df))
                
            except Exception as e:
                logger.error("Failed to fetch macro data", series=series_config['code'], error=str(e))


@celery_app.task(name="app.tasks.data_tasks.initialize_assets")
def initialize_assets():
    """Initialize default assets in database."""
    asyncio.run(_initialize_assets_async())


async def _initialize_assets_async():
    """Async implementation of asset initialization."""
    async with async_session() as session:
        for asset_config in DEFAULT_ASSETS:
            existing = await session.get(Asset, asset_config['id'])
            if not existing:
                asset = Asset(
                    id=asset_config['id'],
                    ticker=asset_config['ticker'],
                    name=asset_config['name'],
                    asset_class=asset_config['asset_class'],
                    currency=asset_config['currency']
                )
                session.add(asset)
        
        await session.commit()
        logger.info("Initialized assets", count=len(DEFAULT_ASSETS))
