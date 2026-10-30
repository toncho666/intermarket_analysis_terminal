import httpx
from typing import Optional
import structlog
from app.config import settings

logger = structlog.get_logger()


class TelegramService:
    """Service for sending Telegram notifications."""
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None
    
    async def send_message(
        self,
        message: str,
        chat_id: Optional[str] = None,
        parse_mode: str = "HTML"
    ) -> bool:
        """
        Send a message to Telegram chat.
        
        Args:
            message: Message text (supports HTML formatting)
            chat_id: Target chat ID (defaults to configured chat_id)
            parse_mode: 'HTML' or 'Markdown'
        
        Returns:
            True if sent successfully
        """
        if not self.base_url:
            logger.warning("Telegram bot token not configured")
            return False
        
        target_chat_id = chat_id or self.chat_id
        if not target_chat_id:
            logger.warning("No chat_id configured or provided")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": target_chat_id,
                        "text": message,
                        "parse_mode": parse_mode,
                        "disable_web_page_preview": True
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                
            logger.info("Telegram message sent", chat_id=target_chat_id)
            return True
            
        except Exception as e:
            logger.error("Failed to send Telegram message", error=str(e))
            return False
    
    async def send_anomaly_alert(
        self,
        asset_a: str,
        asset_b: str,
        anomaly_type: str,
        z_score: float,
        severity: str,
        detected_at: str
    ) -> bool:
        """Send anomaly detection alert."""
        emoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }.get(severity, '⚪')
        
        message = f"""
{emoji} <b>Anomaly Detected</b>

<b>Pair:</b> {asset_a} × {asset_b}
<b>Type:</b> {anomaly_type.replace('_', ' ').title()}
<b>Z-Score:</b> {z_score:.2f}σ
<b>Severity:</b> {severity.upper()}
<b>Time:</b> {detected_at}

<i>Intermarket Analysis Terminal</i>
""".strip()
        
        return await self.send_message(message)
    
    async def send_regime_change_alert(
        self,
        from_regime: str,
        to_regime: str,
        score: float
    ) -> bool:
        """Send regime change alert."""
        emoji = '🟢' if to_regime == 'Risk-On' else ('🔴' if to_regime == 'Risk-Off' else '🟡')
        
        message = f"""
{emoji} <b>Regime Change Detected</b>

<b>From:</b> {from_regime}
<b>To:</b> {to_regime}
<b>Score:</b> {score:.1f}/100

<i>Intermarket Analysis Terminal</i>
""".strip()
        
        return await self.send_message(message)
    
    async def send_correlation_break_alert(
        self,
        asset_a: str,
        asset_b: str,
        current_corr: float,
        previous_corr: float,
        window: int
    ) -> bool:
        """Send correlation break alert."""
        delta = current_corr - previous_corr
        direction = "📈" if delta > 0 else "📉"
        
        message = f"""
{direction} <b>Correlation Break</b>

<b>Pair:</b> {asset_a} × {asset_b}
<b>Window:</b> {window}D
<b>Previous:</b> {previous_corr:.3f}
<b>Current:</b> {current_corr:.3f}
<b>Change:</b> {delta:+.3f}

<i>Intermarket Analysis Terminal</i>
""".strip()
        
        return await self.send_message(message)
    
    async def send_backtest_complete_alert(
        self,
        strategy_name: str,
        sharpe: float,
        total_return: float,
        max_drawdown: float
    ) -> bool:
        """Send backtest completion alert."""
        emoji = '✅' if sharpe > 1 else '⚠️'
        
        message = f"""
{emoji} <b>Backtest Complete</b>

<b>Strategy:</b> {strategy_name}
<b>Sharpe:</b> {sharpe:.2f}
<b>Return:</b> {total_return:+.1f}%
<b>Max DD:</b> {max_drawdown:.1f}%

<i>Intermarket Analysis Terminal</i>
""".strip()
        
        return await self.send_message(message)
    
    async def send_daily_summary(
        self,
        regime_score: float,
        regime_label: str,
        num_anomalies: int,
        top_movers: list
    ) -> bool:
        """Send daily market summary."""
        movers_text = "\n".join([
            f"  • {m['ticker']}: {m['change']:+.2f}%"
            for m in top_movers[:5]
        ])
        
        emoji = '🟢' if regime_score >= 70 else ('🔴' if regime_score < 40 else '🟡')
        
        message = f"""
{emoji} <b>Daily Market Summary</b>

<b>Regime:</b> {regime_label} ({regime_score:.0f}/100)
<b>Anomalies:</b> {num_anomalies}

<b>Top Movers:</b>
{movers_text}

<i>Intermarket Analysis Terminal</i>
""".strip()
        
        return await self.send_message(message)
    
    async def test_connection(self) -> bool:
        """Test Telegram bot connection."""
        if not self.base_url:
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/getMe",
                    timeout=10.0
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error("Telegram connection test failed", error=str(e))
            return False
