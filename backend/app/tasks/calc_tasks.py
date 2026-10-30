import asyncio
from datetime import datetime
import structlog
import pandas as pd
import numpy as np

from app.tasks.celery_app import celery_app
from app.database import async_session
from app.models import PriceBar, Correlation, Anomaly
from app.services.correlation_service import CorrelationService
from app.services.anomaly_service import AnomalyService
from app.services.regime_service import RegimeService
from app.services.telegram_service import TelegramService
from app.config import settings

logger = structlog.get_logger()


@celery_app.task(name="app.tasks.calc_tasks.calculate_correlations")
def calculate_correlations():
    """Calculate rolling correlations for all asset pairs."""
    asyncio.run(_calculate_correlations_async())


async def _calculate_correlations_async():
    """Async implementation of correlation calculation."""
    service = CorrelationService()
    
    async with async_session() as session:
        # Fetch all prices
        result = await session.execute(
            PriceBar.__table__.select().order_by(PriceBar.ts)
        )
        prices = result.fetchall()
        
        if not prices:
            logger.warning("No price data available")
            return
        
        # Group by asset
        prices_by_asset = {}
        for row in prices:
            asset_id = row.asset_id
            if asset_id not in prices_by_asset:
                prices_by_asset[asset_id] = []
            prices_by_asset[asset_id].append({
                'ts': row.ts,
                'close': row.close
            })
        
        # Calculate correlations for key pairs
        key_pairs = [
            ('spx', 'vix'), ('spx', 'us10y'), ('spx', 'gold'),
            ('gold', 'dxy'), ('gold', 'us10y'), ('btc', 'ndx'),
            ('brent', 'wti'), ('copper', 'gold'), ('hyg', 'spx'),
        ]
        
        for asset_a_id, asset_b_id in key_pairs:
            if asset_a_id not in prices_by_asset or asset_b_id not in prices_by_asset:
                continue
            
            # Create price series
            series_a = pd.Series(
                [p['close'] for p in prices_by_asset[asset_a_id]],
                index=[p['ts'] for p in prices_by_asset[asset_a_id]]
            )
            series_b = pd.Series(
                [p['close'] for p in prices_by_asset[asset_b_id]],
                index=[p['ts'] for p in prices_by_asset[asset_b_id]]
            )
            
            # Calculate rolling correlations for each window
            for window in settings.DEFAULT_CORR_WINDOWS:
                corr_df = service.calculate_rolling_correlation(
                    series_a, series_b, window=window
                )
                
                if corr_df.empty:
                    continue
                
                # Store latest correlation
                latest = corr_df.iloc[-1]
                
                # Get previous correlation for delta
                prev_corr = None
                if len(corr_df) > 1:
                    prev_corr = corr_df.iloc[-2]['correlation']
                
                delta = service.calculate_correlation_delta(
                    latest['correlation'],
                    prev_corr if prev_corr else latest['correlation']
                )
                
                correlation = Correlation(
                    asset_a_id=asset_a_id,
                    asset_b_id=asset_b_id,
                    window_days=window,
                    method='pearson',
                    ts=latest['ts'],
                    value=latest['correlation'],
                    delta_vs_prev=delta,
                    ci_low=latest['ci_low'],
                    ci_high=latest['ci_high'],
                    model_version=service.model_version
                )
                session.add(correlation)
        
        await session.commit()
        logger.info("Calculated correlations")


@celery_app.task(name="app.tasks.calc_tasks.detect_anomalies")
def detect_anomalies():
    """Detect anomalies in correlations and prices."""
    asyncio.run(_detect_anomalies_async())


async def _detect_anomalies_async():
    """Async implementation of anomaly detection."""
    anomaly_service = AnomalyService()
    telegram_service = TelegramService()
    
    async with async_session() as session:
        # Fetch recent correlations
        result = await session.execute(
            Correlation.__table__.select()
            .where(Correlation.window_days == 60)
            .order_by(Correlation.ts.desc())
            .limit(1000)
        )
        correlations = result.fetchall()
        
        if not correlations:
            return
        
        # Group by pair
        pairs = {}
        for corr in correlations:
            pair_key = f"{corr.asset_a_id}_{corr.asset_b_id}"
            if pair_key not in pairs:
                pairs[pair_key] = []
            pairs[pair_key].append({
                'ts': corr.ts,
                'value': corr.value,
                'asset_a': corr.asset_a_id,
                'asset_b': corr.asset_b_id
            })
        
        # Detect anomalies for each pair
        for pair_key, pair_data in pairs.items():
            corr_series = pd.Series(
                [p['value'] for p in reversed(pair_data)],
                index=[p['ts'] for p in reversed(pair_data)]
            )
            
            anomalies = anomaly_service.detect_correlation_anomaly(corr_series)
            
            for anomaly_data in anomalies[-5:]:  # Last 5 anomalies
                anomaly = Anomaly(
                    id=f"{pair_key}_{anomaly_data['ts'].timestamp()}",
                    asset_a_id=pair_data[0]['asset_a'],
                    asset_b_id=pair_data[0]['asset_b'],
                    type=anomaly_data['type'],
                    z_score=anomaly_data['z_score'],
                    direction=anomaly_data['direction'],
                    detected_at=anomaly_data['ts'],
                    severity=anomaly_data['severity'],
                    status='active',
                    model_version=anomaly_service.model_version
                )
                session.add(anomaly)
                
                # Send Telegram alert for high severity
                if anomaly_data['severity'] in ['high', 'critical']:
                    await telegram_service.send_anomaly_alert(
                        asset_a=pair_data[0]['asset_a'].upper(),
                        asset_b=pair_data[0]['asset_b'].upper(),
                        anomaly_type=anomaly_data['type'],
                        z_score=anomaly_data['z_score'],
                        severity=anomaly_data['severity'],
                        detected_at=anomaly_data['ts'].isoformat()
                    )
        
        await session.commit()
        logger.info("Detected anomalies")


@celery_app.task(name="app.tasks.calc_tasks.calculate_regime")
def calculate_regime():
    """Calculate market regime score."""
    asyncio.run(_calculate_regime_async())


async def _calculate_regime_async():
    """Async implementation of regime calculation."""
    regime_service = RegimeService()
    telegram_service = TelegramService()
    
    async with async_session() as session:
        # Fetch prices for regime calculation
        result = await session.execute(
            PriceBar.__table__.select()
            .where(PriceBar.asset_id.in_(['spx', 'us10y', 'vix', 'vix3m', 'dxy', 'eem', 'tlt', 'gold']))
            .order_by(PriceBar.ts)
        )
        prices = result.fetchall()
        
        if not prices:
            return
        
        # Group by asset
        prices_by_asset = {}
        for row in prices:
            if row.asset_id not in prices_by_asset:
                prices_by_asset[row.asset_id] = []
            prices_by_asset[row.asset_id].append({
                'ts': row.ts,
                'close': row.close
            })
        
        # Create series
        data = {}
        for asset_id, price_list in prices_by_asset.items():
            data[asset_id] = pd.Series(
                [p['close'] for p in price_list],
                index=[p['ts'] for p in price_list]
            )
        
        # Calculate regime
        regime_result = regime_service.calculate_regime_score(data)
        
        logger.info("Calculated regime", score=regime_result['score'], regime=regime_result['regime'])
        
        # TODO: Store regime score in database
        
        # Check for regime change (compare with previous)
        # If changed, send Telegram alert


@celery_app.task(name="app.tasks.calc_tasks.send_daily_summary")
def send_daily_summary():
    """Send daily market summary to Telegram."""
    asyncio.run(_send_daily_summary_async())


async def _send_daily_summary_async():
    """Async implementation of daily summary."""
    telegram_service = TelegramService()
    regime_service = RegimeService()
    
    # Calculate regime
    # (simplified - in production would fetch from DB)
    regime_score = 62
    regime_label = "Neutral"
    
    # Get top movers
    top_movers = [
        {'ticker': 'SPX', 'change': 0.45},
        {'ticker': 'NDX', 'change': 0.62},
        {'ticker': 'VIX', 'change': -2.3},
        {'ticker': 'GOLD', 'change': 0.18},
        {'ticker': 'BTC', 'change': 1.2},
    ]
    
    # Count active anomalies
    num_anomalies = 5
    
    await telegram_service.send_daily_summary(
        regime_score=regime_score,
        regime_label=regime_label,
        num_anomalies=num_anomalies,
        top_movers=top_movers
    )
    
    logger.info("Sent daily summary")
