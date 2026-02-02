"""
📢 Enhanced Alert System
Smart notifications with severity tiers and multi-channel delivery
"""

import logging
from datetime import datetime, UTC
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
import asyncio


logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "🔴 CRITICAL"
    HIGH = "🟠 HIGH"
    MEDIUM = "🟡 MEDIUM"
    LOW = "🟢 LOW"
    INFO = "ℹ️ INFO"


class AlertCategory(Enum):
    """Alert categories"""
    TRADE = "💰 TRADE"
    RISK = "⚠️ RISK"
    EVENT = "📅 EVENT"
    SYSTEM = "⚙️ SYSTEM"
    PERFORMANCE = "📊 PERFORMANCE"
    SENTIMENT = "💭 SENTIMENT"


@dataclass
class Alert:
    """Single alert message"""
    severity: AlertSeverity
    category: AlertCategory
    title: str
    message: str
    timestamp: datetime
    data: Optional[Dict] = None
    
    def format_telegram(self) -> str:
        """Format for Telegram"""
        lines = [
            f"{self.severity.value} {self.category.value}",
            "━━━━━━━━━━━━━━━━━",
            f"<b>{self.title}</b>",
            "",
            self.message
        ]
        
        if self.data:
            lines.append("")
            for key, value in self.data.items():
                lines.append(f"• {key}: {value}")
        
        lines.append("━━━━━━━━━━━━━━━━━")
        lines.append(f"🕐 {self.timestamp.strftime('%H:%M:%S UTC')}")
        
        return "\n".join(lines)


class AlertManager:
    """
    Enhanced Alert System
    
    Features:
    - Severity-based prioritization
    - Smart alert throttling (prevent spam)
    - Multi-channel delivery (Telegram, Email, SMS)
    - Alert history and analytics
    - Custom alert rules
    - Performance summaries
    """
    
    def __init__(self, telegram_bot=None, telegram_chat_id: Optional[str] = None):
        self.telegram_bot = telegram_bot
        self.telegram_chat_id = telegram_chat_id
        
        # Alert tracking
        self.alert_history: List[Alert] = []
        self.last_alert_time: Dict[str, datetime] = {}
        self.alert_counts: Dict[AlertCategory, int] = {cat: 0 for cat in AlertCategory}
        
        # Throttling config (seconds between same alert type)
        self.throttle_config = {
            AlertSeverity.CRITICAL: 0,      # No throttle
            AlertSeverity.HIGH: 30,         # Max every 30s
            AlertSeverity.MEDIUM: 60,       # Max every 60s
            AlertSeverity.LOW: 300,         # Max every 5 min
            AlertSeverity.INFO: 600         # Max every 10 min
        }
        
        # Statistics
        self.stats = {
            "total_alerts": 0,
            "alerts_by_severity": {sev: 0 for sev in AlertSeverity},
            "alerts_by_category": {cat: 0 for cat in AlertCategory}
        }
    
    # ==================== CORE ALERT FUNCTIONS ====================
    
    async def send_alert(self, severity: AlertSeverity, category: AlertCategory,
                        title: str, message: str, data: Optional[Dict] = None,
                        force: bool = False) -> bool:
        """
        Send alert with throttling
        
        Args:
            severity: Alert severity level
            category: Alert category
            title: Short title
            message: Detailed message
            data: Optional structured data
            force: Skip throttling
            
        Returns:
            True if sent, False if throttled
        """
        alert = Alert(
            severity=severity,
            category=category,
            title=title,
            message=message,
            timestamp=datetime.now(UTC),
            data=data
        )
        
        # Check throttling (unless force or critical)
        if not force and severity != AlertSeverity.CRITICAL:
            throttle_key = f"{category.name}_{title}"
            if self._should_throttle(throttle_key, severity):
                logger.debug(f"⏸️ Alert throttled: {title}")
                return False
        
        # Send via channels
        success = await self._deliver_alert(alert)
        
        if success:
            # Track
            self.alert_history.append(alert)
            self.alert_counts[category] += 1
            self.stats["total_alerts"] += 1
            self.stats["alerts_by_severity"][severity] += 1
            self.stats["alerts_by_category"][category] += 1
            
            # Update throttle tracking
            throttle_key = f"{category.name}_{title}"
            self.last_alert_time[throttle_key] = datetime.now(UTC)
        
        return success
    
    def _should_throttle(self, key: str, severity: AlertSeverity) -> bool:
        """Check if alert should be throttled"""
        if key not in self.last_alert_time:
            return False
        
        throttle_seconds = self.throttle_config[severity]
        if throttle_seconds == 0:
            return False
        
        elapsed = (datetime.now(UTC) - self.last_alert_time[key]).total_seconds()
        return elapsed < throttle_seconds
    
    async def _deliver_alert(self, alert: Alert) -> bool:
        """Deliver alert to all channels"""
        success = False
        
        # Telegram
        if self.telegram_bot and self.telegram_chat_id:
            try:
                message = alert.format_telegram()
                await self.telegram_bot.send_message(
                    chat_id=self.telegram_chat_id,
                    text=message,
                    parse_mode="HTML"
                )
                success = True
                logger.debug(f"✅ Alert sent via Telegram: {alert.title}")
            except Exception as e:
                logger.error(f"❌ Telegram alert failed: {e}")
        
        # Email (TODO: implement if needed)
        # SMS (TODO: implement for critical alerts)
        
        return success
    
    # ==================== SPECIALIZED ALERTS ====================
    
    async def alert_trade_entry(self, symbol: str, side: str, entry_price: float,
                               size: float, tp: float, sl: float, 
                               confidence: float, reason: str):
        """Alert when opening position"""
        tp_pct = ((tp - entry_price) / entry_price) * 100
        sl_pct = ((entry_price - sl) / entry_price) * 100
        
        await self.send_alert(
            severity=AlertSeverity.INFO,
            category=AlertCategory.TRADE,
            title=f"Opening {side.upper()} {symbol}",
            message=f"Entry: ${entry_price:.2f} | Size: {size:.6f}\n"
                   f"TP: ${tp:.2f} (+{tp_pct:.2f}%) | SL: ${sl:.2f} (-{sl_pct:.2f}%)\n"
                   f"Confidence: {confidence:.0%}\n"
                   f"Reason: {reason}",
            data={
                "Symbol": symbol,
                "Side": side.upper(),
                "Entry": f"${entry_price:.2f}",
                "Size": f"{size:.6f}",
                "Risk/Reward": f"1:{tp_pct/sl_pct:.1f}"
            }
        )
    
    async def alert_trade_exit(self, symbol: str, side: str, entry_price: float,
                              exit_price: float, pnl: float, pnl_pct: float,
                              reason: str, balance: float, win_rate: float):
        """Alert when closing position"""
        is_win = pnl > 0
        severity = AlertSeverity.INFO if is_win else AlertSeverity.LOW
        
        emoji = "✅" if is_win else "❌"
        
        await self.send_alert(
            severity=severity,
            category=AlertCategory.TRADE,
            title=f"{emoji} {side.upper()} {symbol} Closed",
            message=f"Entry: ${entry_price:.2f} → Exit: ${exit_price:.2f}\n"
                   f"P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)\n"
                   f"Reason: {reason}\n"
                   f"Balance: ${balance:.2f} | Win Rate: {win_rate:.1f}%",
            data={
                "Symbol": symbol,
                "P&L": f"${pnl:+.2f}",
                "P&L %": f"{pnl_pct:+.2f}%",
                "Balance": f"${balance:.2f}",
                "Win Rate": f"{win_rate:.1f}%"
            }
        )
    
    async def alert_risk_warning(self, warning_type: str, severity: AlertSeverity,
                                details: str, action: str):
        """Alert for risk warnings"""
        await self.send_alert(
            severity=severity,
            category=AlertCategory.RISK,
            title=warning_type,
            message=f"{details}\n\n"
                   f"Action Taken: {action}",
            force=True  # Risk alerts not throttled
        )
    
    async def alert_event(self, event_name: str, severity: AlertSeverity,
                         time_until: str, expected_impact: str, action: str):
        """Alert for upcoming events"""
        await self.send_alert(
            severity=severity,
            category=AlertCategory.EVENT,
            title=f"Upcoming: {event_name}",
            message=f"Time: {time_until}\n"
                   f"Expected Impact: {expected_impact}\n"
                   f"Action: {action}",
            force=True
        )
    
    async def alert_sentiment_shift(self, old_level: str, new_level: str,
                                   index_value: int, interpretation: str,
                                   action: str):
        """Alert for sentiment changes"""
        await self.send_alert(
            severity=AlertSeverity.MEDIUM,
            category=AlertCategory.SENTIMENT,
            title=f"Sentiment: {old_level} → {new_level}",
            message=f"Fear & Greed Index: {index_value}/100\n"
                   f"Interpretation: {interpretation}\n"
                   f"Action: {action}"
        )
    
    async def alert_cascade_detected(self, cascade_type: str, severity: str,
                                    change: float, action: str):
        """Alert for market cascades"""
        await self.send_alert(
            severity=AlertSeverity.CRITICAL,
            category=AlertCategory.RISK,
            title=f"🚨 {cascade_type.upper()} DETECTED",
            message=f"Price Change: {change:+.1f}%\n"
                   f"Severity: {severity}\n"
                   f"Emergency Action: {action}",
            force=True
        )
    
    async def alert_daily_summary(self, trades: int, wins: int, losses: int,
                                 win_rate: float, pnl: float, pnl_pct: float,
                                 balance: float, best_trade: float, 
                                 worst_trade: float):
        """Send daily performance summary"""
        emoji = "🚀" if pnl > 0 else "📉"
        
        await self.send_alert(
            severity=AlertSeverity.INFO,
            category=AlertCategory.PERFORMANCE,
            title=f"{emoji} Daily Summary",
            message=f"Trades: {trades} ({wins}W-{losses}L)\n"
                   f"Win Rate: {win_rate:.1f}%\n"
                   f"P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)\n"
                   f"Balance: ${balance:.2f}\n"
                   f"Best: ${best_trade:+.2f} | Worst: ${worst_trade:+.2f}",
            force=True
        )
    
    async def alert_hourly_status(self, balance: float, open_positions: int,
                                  daily_pnl: float, daily_pnl_pct: float,
                                  win_rate: float, next_event: Optional[str]):
        """Send hourly status update"""
        await self.send_alert(
            severity=AlertSeverity.INFO,
            category=AlertCategory.PERFORMANCE,
            title="📊 Hourly Status",
            message=f"Balance: ${balance:.2f} ({daily_pnl_pct:+.2f}% today)\n"
                   f"Open Positions: {open_positions}\n"
                   f"Win Rate: {win_rate:.1f}%\n"
                   f"Next Event: {next_event or 'None'}",
            data={
                "Balance": f"${balance:.2f}",
                "Daily P&L": f"${daily_pnl:+.2f}",
                "Positions": str(open_positions),
                "Win Rate": f"{win_rate:.1f}%"
            }
        )
    
    # ==================== POSITION UPDATES ====================
    
    async def alert_position_update(self, symbol: str, entry: float, current: float,
                                   pnl: float, pnl_pct: float, time_in_trade: int,
                                   tp_progress: float):
        """Update on active position (throttled to every 5 min)"""
        status = "✅" if pnl > 0 else "⏳"
        
        await self.send_alert(
            severity=AlertSeverity.INFO,
            category=AlertCategory.TRADE,
            title=f"{status} Position Update: {symbol}",
            message=f"Entry: ${entry:.2f} → Current: ${current:.2f}\n"
                   f"P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)\n"
                   f"Time: {time_in_trade}s | TP: {tp_progress:.0%}",
            data={
                "Symbol": symbol,
                "Current": f"${current:.2f}",
                "P&L": f"${pnl:+.2f}",
                "Progress": f"{tp_progress:.0%}"
            }
        )
    
    async def alert_trailing_stop_activated(self, symbol: str, current_price: float,
                                           trailing_stop: float, profit_pct: float):
        """Alert when trailing stop activates"""
        await self.send_alert(
            severity=AlertSeverity.LOW,
            category=AlertCategory.TRADE,
            title=f"🎯 Trailing Stop: {symbol}",
            message=f"Profit: +{profit_pct:.2f}%\n"
                   f"Trailing stop activated at ${trailing_stop:.2f}\n"
                   f"Protecting gains!",
            data={
                "Symbol": symbol,
                "Profit": f"+{profit_pct:.2f}%",
                "Trail Price": f"${trailing_stop:.2f}"
            }
        )
    
    # ==================== STATISTICS & REPORTING ====================
    
    def get_alert_stats(self) -> Dict:
        """Get alert statistics"""
        return {
            "total": self.stats["total_alerts"],
            "by_severity": {sev.name: count for sev, count in self.stats["alerts_by_severity"].items()},
            "by_category": {cat.name: count for cat, count in self.stats["alerts_by_category"].items()},
            "recent_count": len([a for a in self.alert_history if 
                               (datetime.now(UTC) - a.timestamp).seconds < 3600])
        }
    
    async def alert_system_status(self, uptime: str, trades_today: int,
                                  cpu_usage: float, memory_usage: float,
                                  api_calls: int):
        """System health status"""
        await self.send_alert(
            severity=AlertSeverity.INFO,
            category=AlertCategory.SYSTEM,
            title="⚙️ System Status",
            message=f"Uptime: {uptime}\n"
                   f"Trades Today: {trades_today}\n"
                   f"CPU: {cpu_usage:.1f}% | Memory: {memory_usage:.1f}%\n"
                   f"API Calls: {api_calls}",
            force=True
        )
    
    # ==================== SYNCHRONOUS WRAPPERS ====================
    
    def send_alert_sync(self, severity: AlertSeverity, category: AlertCategory,
                       title: str, message: str, data: Optional[Dict] = None,
                       force: bool = False):
        """Synchronous wrapper for send_alert"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Create task if loop running
                asyncio.create_task(
                    self.send_alert(severity, category, title, message, data, force)
                )
            else:
                # Run in new loop
                asyncio.run(
                    self.send_alert(severity, category, title, message, data, force)
                )
        except Exception as e:
            logger.error(f"❌ Failed to send alert sync: {e}")
    
    def alert_trade_entry_sync(self, symbol: str, side: str, entry_price: float,
                              size: float, tp: float, sl: float,
                              confidence: float, reason: str):
        """Sync wrapper for trade entry alert"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(
                    self.alert_trade_entry(symbol, side, entry_price, size, tp, sl, confidence, reason)
                )
            else:
                asyncio.run(
                    self.alert_trade_entry(symbol, side, entry_price, size, tp, sl, confidence, reason)
                )
        except Exception as e:
            logger.error(f"❌ Failed to send trade entry alert: {e}")
    
    def alert_trade_exit_sync(self, symbol: str, side: str, entry_price: float,
                             exit_price: float, pnl: float, pnl_pct: float,
                             reason: str, balance: float, win_rate: float):
        """Sync wrapper for trade exit alert"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(
                    self.alert_trade_exit(symbol, side, entry_price, exit_price, pnl, pnl_pct, reason, balance, win_rate)
                )
            else:
                asyncio.run(
                    self.alert_trade_exit(symbol, side, entry_price, exit_price, pnl, pnl_pct, reason, balance, win_rate)
                )
        except Exception as e:
            logger.error(f"❌ Failed to send trade exit alert: {e}")
