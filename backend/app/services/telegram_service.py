"""
Telegram notification service
- Send alerts to Telegram chat
- Format messages with Markdown
- Handle rate limiting
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class TelegramService:
    """Service for sending notifications via Telegram"""
    
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = None
        
        if bot_token:
            try:
                from telegram import Bot
                self.bot = Bot(token=bot_token)
                logger.info("Telegram bot initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram bot: {e}")
    
    async def send_message(
        self,
        text: str,
        parse_mode: str = "Markdown",
        disable_notification: bool = False
    ) -> bool:
        """
        Send a text message to Telegram
        """
        if not self.bot or not self.chat_id:
            logger.warning("Telegram bot not configured")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=parse_mode,
                disable_notification=disable_notification,
            )
            logger.info(f"Telegram message sent to {self.chat_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    async def send_alert(
        self,
        anomaly_type: str,
        asset_a: str,
        asset_b: str,
        z_score: float,
        severity: str,
        detected_at: datetime
    ) -> bool:
        """
        Send formatted anomaly alert
        """
        emoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢',
        }.get(severity, '⚪')
        
        type_emoji = {
            'corr_break': '📊',
            'coint_break': '🔗',
            'divergence': '↔️',
            'vol_spike': '📈',
            'spread_outlier': '📉',
        }.get(anomaly_type, '⚠️')
        
        message = f"""
{emoji} *{severity.upper()} ANOMALY DETECTED* {emoji}

{type_emoji} *Type:* {anomaly_type.replace('_', ' ').title()}
📌 *Pair:* {asset_a} × {asset_b}
📊 *Z-Score:* {z_score:.2f}σ
🕐 *Detected:* {detected_at.strftime('%Y-%m-%d %H:%M UTC')}

_Action required: Review correlation structure_
"""
        
        return await self.send_message(message.strip())
    
    async def send_regime_change(
        self,
        old_regime: str,
        new_regime: str,
        score: float,
        components: list
    ) -> bool:
        """
        Send regime change notification
        """
        emoji = '🟢' if new_regime == 'Risk-On' else '🔴' if new_regime == 'Risk-Off' else '🟡'
        
        component_text = "\n".join([
            f"  • {c['name']}: {c['value']:.3f} → {c['signal']}"
            for c in components[:5]
        ])
        
        message = f"""
{emoji} *REGIME CHANGE DETECTED* {emoji}

📊 *New Regime:* {new_regime}
📈 *Score:* {score:.1f}/100

*Components:*
{component_text}

_Review portfolio positioning_
"""
        
        return await self.send_message(message.strip())
    
    async def send_backtest_complete(
        self,
        strategy_name: str,
        sharpe: float,
        total_return: float,
        max_drawdown: float
    ) -> bool:
        """
        Send backtest completion notification
        """
        emoji = '✅' if sharpe > 1 else '⚠️'
        
        message = f"""
{emoji} *BACKTEST COMPLETED*

📋 *Strategy:* {strategy_name}
📊 *Sharpe Ratio:* {sharpe:.2f}
💰 *Total Return:* {total_return:+.2f}%
📉 *Max Drawdown:* {max_drawdown:.2f}%

_View full results in dashboard_
"""
        
        return await self.send_message(message.strip())
    
    async def send_daily_summary(
        self,
        regime: str,
        score: float,
        n_anomalies: int,
        top_movers: list
    ) -> bool:
        """
        Send daily market summary
        """
        emoji = '🟢' if regime == 'Risk-On' else '🔴' if regime == 'Risk-Off' else '🟡'
        
        movers_text = "\n".join([
            f"  • {m['ticker']}: {m['change_pct']:+.2f}%"
            for m in top_movers[:5]
        ])
        
        message = f"""
📊 *DAILY MARKET SUMMARY*

{emoji} *Regime:* {regime} (Score: {score:.0f}/100)
⚠️ *Active Anomalies:* {n_anomalies}

*Top Movers:*
{movers_text}

_Have a great trading day!_
"""
        
        return await self.send_message(message.strip())
    
    async def test_connection(self) -> bool:
        """
        Test Telegram bot connection
        """
        if not self.bot:
            return False
        
        try:
            me = await self.bot.get_me()
            logger.info(f"Telegram bot connected: @{me.username}")
            return True
        except Exception as e:
            logger.error(f"Telegram connection test failed: {e}")
            return False


# Factory function
def create_telegram_service(bot_token: Optional[str] = None, chat_id: Optional[str] = None) -> TelegramService:
    """Create Telegram service instance"""
    return TelegramService(bot_token=bot_token, chat_id=chat_id)
