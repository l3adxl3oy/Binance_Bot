"""
🗓️ Event Management System
Tracks economic calendar, crypto events, and makes smart trading decisions
"""

import logging
import requests
from datetime import datetime, timedelta, UTC
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import json


logger = logging.getLogger(__name__)


class EventSeverity(Enum):
    """Event impact levels"""
    CRITICAL = "🔴"  # Close 100%, pause 2+ hours
    HIGH = "🟠"      # Close 50%, reduce size 75%
    MEDIUM = "🟡"    # Close 25%, reduce size 50%
    LOW = "🟢"       # No action needed
    CLEAR = "✅"     # All clear


class EventType(Enum):
    """Types of market events"""
    ECONOMIC = "economic"
    CRYPTO = "crypto"
    TECHNICAL = "technical"
    SENTIMENT = "sentiment"
    BLOCKCHAIN = "blockchain"


@dataclass
class MarketEvent:
    """Single market event"""
    event_type: EventType
    name: str
    severity: EventSeverity
    scheduled_time: datetime
    description: str
    expected_impact: str  # e.g., "BTC -2% to -5%"
    confidence: float  # 0.0 to 1.0
    
    def time_until(self) -> timedelta:
        """Time until event"""
        return self.scheduled_time - datetime.now(UTC)
    
    def minutes_until(self) -> float:
        """Minutes until event"""
        return self.time_until().total_seconds() / 60
    
    def is_upcoming(self, minutes: int = 120) -> bool:
        """Check if event is upcoming within N minutes"""
        mins = self.minutes_until()
        return 0 <= mins <= minutes


class EventManager:
    """
    Intelligent Event Manager
    
    Features:
    - Economic calendar tracking (NFP, FOMC, CPI, etc.)
    - Crypto event monitoring (halvings, upgrades, listings)
    - Sentiment tracking (Fear & Greed Index)
    - Cascade detection (liquidations, flash crashes)
    - Smart trading decisions based on events
    """
    
    def __init__(self):

        self.events: List[MarketEvent] = []
        self.last_update = None
        self.fear_greed_index = 50  # Neutral
        self.last_sentiment_update = None
        
        # Cached decisions
        self.current_trading_action = None
        self.last_decision_time = None
        
    # ==================== ECONOMIC CALENDAR ====================
    
    def fetch_economic_calendar(self) -> List[MarketEvent]:
        """
        Fetch upcoming economic events
        
        Returns major events that affect crypto:
        - NFP (Non-Farm Payroll)
        - FOMC (Fed Rate Decision)
        - CPI (Inflation Data)
        - ECB/BOJ meetings
        - GDP reports
        """
        events = []
        
        try:
            # Use investing.com economic calendar API
            # Note: This is a simplified version - in production use proper API
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "NEWS_SENTIMENT",
                "topics": "economy_fiscal,economy_monetary",
                "apikey": "demo"  # Replace with real API key
            }
            
            # For now, we'll use a static list of known events
            # In production, parse from actual calendar API
            known_events = self._get_known_economic_events()
            events.extend(known_events)
            
        except Exception as e:
            logger.error(f"❌ ดึง Economic Calendar ล้มเหลว: {e}")
            
        return events
    
    def _get_known_economic_events(self) -> List[MarketEvent]:
        """
        Get list of known recurring economic events
        This should be updated regularly in production
        """
        now = datetime.now(UTC)
        events = []
        
        # NFP - First Friday of month at 12:30 UTC
        next_nfp = self._get_next_first_friday(now, hour=12, minute=30)
        events.append(MarketEvent(
            event_type=EventType.ECONOMIC,
            name="NFP (Non-Farm Payroll)",
            severity=EventSeverity.CRITICAL,
            scheduled_time=next_nfp,
            description="US Employment data - Major market mover",
            expected_impact="BTC ±2% to ±5%",
            confidence=0.85
        ))
        
        # FOMC - Every 6 weeks at 18:00 UTC
        # (Simplified - actual dates should come from Fed calendar)
        fomc_dates = [
            datetime(2026, 2, 10, 18, 0, tzinfo=UTC),
            datetime(2026, 3, 18, 18, 0, tzinfo=UTC),
            datetime(2026, 5, 6, 18, 0, tzinfo=UTC),
        ]
        for fomc_date in fomc_dates:
            if fomc_date > now:
                events.append(MarketEvent(
                    event_type=EventType.ECONOMIC,
                    name="FOMC Rate Decision",
                    severity=EventSeverity.CRITICAL,
                    scheduled_time=fomc_date,
                    description="Federal Reserve interest rate decision",
                    expected_impact="BTC ±3% to ±8%",
                    confidence=0.90
                ))
                break
        
        # CPI - Around 13th of month at 12:30 UTC
        next_cpi = datetime(now.year, now.month, 13, 12, 30, tzinfo=UTC)
        if next_cpi < now:
            # Next month
            if now.month == 12:
                next_cpi = datetime(now.year + 1, 1, 13, 12, 30, tzinfo=UTC)
            else:
                next_cpi = datetime(now.year, now.month + 1, 13, 12, 30, tzinfo=UTC)
        
        events.append(MarketEvent(
            event_type=EventType.ECONOMIC,
            name="CPI (Inflation Data)",
            severity=EventSeverity.CRITICAL,
            scheduled_time=next_cpi,
            description="US Consumer Price Index - Inflation indicator",
            expected_impact="BTC ±2% to ±6%",
            confidence=0.80
        ))
        
        return events
    
    def _get_next_first_friday(self, from_date: datetime, hour: int, minute: int) -> datetime:
        """Get next first Friday of month"""
        # Start from next month
        if from_date.month == 12:
            check_date = datetime(from_date.year + 1, 1, 1, hour, minute, tzinfo=UTC)
        else:
            check_date = datetime(from_date.year, from_date.month + 1, 1, hour, minute, tzinfo=UTC)
        
        # Find first Friday
        while check_date.weekday() != 4:  # 4 = Friday
            check_date += timedelta(days=1)
        
        return check_date
    
    # ==================== CRYPTO EVENTS ====================
    
    def fetch_crypto_events(self) -> List[MarketEvent]:
        """
        Monitor crypto-specific events:
        - Bitcoin Halving
        - Ethereum Upgrades
        - Token Unlocks
        - Major Exchange Listings
        - Regulatory News
        """
        events = []
        now = datetime.now(UTC)
        
        # Bitcoin Halving (next one approximately April 2028)
        halving_date = datetime(2028, 4, 15, 0, 0, tzinfo=UTC)
        if (halving_date - now).days < 90:  # Within 90 days
            events.append(MarketEvent(
                event_type=EventType.CRYPTO,
                name="Bitcoin Halving",
                severity=EventSeverity.HIGH,
                scheduled_time=halving_date,
                description="Bitcoin mining reward halves - Major bull signal",
                expected_impact="BTC +100% to +300% over 6-12 months",
                confidence=0.40  # Long-term uncertain
            ))
        
        # Ethereum Upgrades (check actual dates from ethereum.org)
        # This is placeholder - should fetch from real source
        
        return events
    
    # ==================== SENTIMENT TRACKING ====================
    
    def fetch_fear_greed_index(self) -> int:
        """
        Fetch Fear & Greed Index (0-100)
        
        Scale:
        - 0-20: Extreme Fear (buy opportunity)
        - 20-40: Fear
        - 40-60: Neutral
        - 60-80: Greed
        - 80-100: Extreme Greed (sell warning)
        """
        try:
            # Alternative.me Fear & Greed Index API
            url = "https://api.alternative.me/fng/"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data and len(data["data"]) > 0:
                    value = int(data["data"][0]["value"])
                    self.fear_greed_index = value
                    self.last_sentiment_update = datetime.now(UTC)
                    return value
            
        except Exception as e:
            pass  # Silent fail on sentiment fetch
        
        # Return cached value if fetch fails
        return self.fear_greed_index
    
    def get_sentiment_signal(self) -> Dict:
        """
        Interpret sentiment and return trading signal
        
        Returns:
        {
            "level": "extreme_fear" | "fear" | "neutral" | "greed" | "extreme_greed",
            "action": "buy_opportunity" | "normal" | "reduce_risk",
            "position_multiplier": 0.5 to 1.5,
            "message": "Human readable explanation"
        }
        """
        index = self.fear_greed_index
        
        if index < 20:
            return {
                "level": "extreme_fear",
                "action": "buy_opportunity",
                "position_multiplier": 1.5,
                "message": f"😱 EXTREME FEAR ({index}/100) - Great buying opportunity!"
            }
        elif index < 40:
            return {
                "level": "fear",
                "action": "cautious_buy",
                "position_multiplier": 1.2,
                "message": f"😟 FEAR ({index}/100) - Market pessimistic, good entry"
            }
        elif index < 60:
            return {
                "level": "neutral",
                "action": "normal",
                "position_multiplier": 1.0,
                "message": f"😐 NEUTRAL ({index}/100) - Normal conditions"
            }
        elif index < 80:
            return {
                "level": "greed",
                "action": "reduce_risk",
                "position_multiplier": 0.8,
                "message": f"😊 GREED ({index}/100) - Market optimistic, be cautious"
            }
        else:
            return {
                "level": "extreme_greed",
                "action": "high_risk",
                "position_multiplier": 0.5,
                "message": f"🤑 EXTREME GREED ({index}/100) - Bubble warning! Reduce exposure"
            }
    
    # ==================== CASCADE DETECTION ====================
    
    def detect_cascade(self, current_price: float, previous_price: float, 
                      time_window: float = 60.0) -> Optional[Dict]:
        """
        Detect dangerous market cascades:
        - Flash Crash (>10% in 1 minute)
        - Liquidation Cascade (rapid price drop with high volume)
        
        Args:
            current_price: Current asset price
            previous_price: Price 1 minute ago
            time_window: Seconds between prices
            
        Returns:
            Cascade info dict if detected, None otherwise
        """
        price_change_pct = ((current_price - previous_price) / previous_price) * 100
        
        # Flash Crash Detection (>10% move in 1 minute)
        if abs(price_change_pct) > 10.0 and time_window <= 60:
            return {
                "type": "flash_crash",
                "severity": "CRITICAL",
                "change": price_change_pct,
                "action": "CLOSE_ALL_POSITIONS",
                "message": f"🚨 FLASH CRASH: {price_change_pct:+.1f}% in {time_window:.0f}s"
            }
        
        # Large Move Detection (>5% in 1 minute)
        if abs(price_change_pct) > 5.0 and time_window <= 60:
            return {
                "type": "large_move",
                "severity": "HIGH",
                "change": price_change_pct,
                "action": "CLOSE_50_PERCENT",
                "message": f"⚠️ LARGE MOVE: {price_change_pct:+.1f}% in {time_window:.0f}s"
            }
        
        # Rapid Drop (>3% in 1 minute)
        if price_change_pct < -3.0 and time_window <= 60:
            return {
                "type": "rapid_drop",
                "severity": "MEDIUM",
                "change": price_change_pct,
                "action": "REDUCE_POSITIONS",
                "message": f"⚠️ RAPID DROP: {price_change_pct:.1f}% in {time_window:.0f}s"
            }
        
        return None
    
    # ==================== TRADING DECISION ENGINE ====================
    
    def get_trading_decision(self) -> Dict:
        """
        Make intelligent trading decision based on all events
        
        Returns:
        {
            "status": "CLEAR" | "CAUTION" | "PAUSE" | "EMERGENCY",
            "action": "normal" | "reduce_50" | "close_all" | "pause",
            "position_size_multiplier": 0.0 to 1.0,
            "leverage_multiplier": 0.33 to 1.0 (1x to 3x),
            "reason": "Why this decision",
            "next_check": minutes until next check
        }
        """
        # Update events if needed (every 5 minutes)
        self._update_events_if_needed()
        
        # Check for upcoming critical events
        critical_events = [e for e in self.events if e.severity == EventSeverity.CRITICAL]
        
        for event in critical_events:
            minutes_until = event.minutes_until()
            
            # CRITICAL event in next 30 minutes
            if 0 <= minutes_until <= 30:
                return {
                    "status": "EMERGENCY",
                    "action": "close_all",
                    "position_size_multiplier": 0.0,
                    "leverage_multiplier": 0.33,  # 1x
                    "reason": f"🔴 {event.name} in {minutes_until:.0f} min - CLOSING ALL",
                    "next_check": 5,
                    "event": event
                }
            
            # CRITICAL event in next 60 minutes
            if 30 < minutes_until <= 60:
                return {
                    "status": "PAUSE",
                    "action": "reduce_50",
                    "position_size_multiplier": 0.25,
                    "leverage_multiplier": 0.5,  # 1.5x
                    "reason": f"🟠 {event.name} in {minutes_until:.0f} min - REDUCING",
                    "next_check": 10,
                    "event": event
                }
            
            # CRITICAL event in next 2 hours
            if 60 < minutes_until <= 120:
                return {
                    "status": "CAUTION",
                    "action": "reduce_25",
                    "position_size_multiplier": 0.5,
                    "leverage_multiplier": 1.0,  # 3x normal
                    "reason": f"🟡 {event.name} in {minutes_until:.0f} min - CAUTIOUS",
                    "next_check": 15,
                    "event": event
                }
        
        # Check HIGH severity events
        high_events = [e for e in self.events if e.severity == EventSeverity.HIGH]
        for event in high_events:
            minutes_until = event.minutes_until()
            
            if 0 <= minutes_until <= 60:
                return {
                    "status": "CAUTION",
                    "action": "reduce_25",
                    "position_size_multiplier": 0.5,
                    "leverage_multiplier": 0.67,  # 2x
                    "reason": f"🟠 {event.name} in {minutes_until:.0f} min",
                    "next_check": 15,
                    "event": event
                }
        
        # Check sentiment
        sentiment = self.get_sentiment_signal()
        if sentiment["level"] == "extreme_greed":
            return {
                "status": "CAUTION",
                "action": "reduce_risk",
                "position_size_multiplier": 0.5,
                "leverage_multiplier": 0.67,
                "reason": sentiment["message"],
                "next_check": 30
            }
        
        # All clear - apply sentiment multiplier
        return {
            "status": "CLEAR",
            "action": "normal",
            "position_size_multiplier": sentiment["position_multiplier"],
            "leverage_multiplier": 1.0,
            "reason": f"✅ No events - {sentiment['message']}",
            "next_check": 60
        }
    
    def _update_events_if_needed(self):
        """Update events if cache is stale (>5 minutes)"""
        now = datetime.now(UTC)
        
        if self.last_update is None or (now - self.last_update).seconds > 300:
            # Fetch all event types (silent)
            economic = self.fetch_economic_calendar()
            crypto = self.fetch_crypto_events()
            
            # Update sentiment
            self.fetch_fear_greed_index()
            
            # Combine and sort by time
            self.events = economic + crypto
            self.events.sort(key=lambda e: e.scheduled_time)
            
            # Remove past events
            self.events = [e for e in self.events if e.scheduled_time > now]
            
            self.last_update = now
            
            logger.info(f"📅 อัปเดตปฏิทิน: {len(self.events)} events | Fear&Greed: {self.fear_greed_index}")
    
    # ==================== RECOVERY MODE ====================
    
    def get_recovery_plan(self, minutes_after_event: float) -> Dict:
        """
        Gradual recovery after major event
        
        Stages:
        - 0-5 min: 10% of normal (testing waters)
        - 5-15 min: 30% of normal
        - 15-30 min: 50% of normal
        - 30-60 min: 75% of normal
        - 60+ min: 100% normal
        """
        if minutes_after_event < 5:
            return {
                "stage": "RECOVERY_1",
                "position_multiplier": 0.1,
                "leverage_multiplier": 0.33,
                "message": "🔄 Testing waters - 10% position size"
            }
        elif minutes_after_event < 15:
            return {
                "stage": "RECOVERY_2",
                "position_multiplier": 0.3,
                "leverage_multiplier": 0.5,
                "message": "🔄 Gradual recovery - 30% position size"
            }
        elif minutes_after_event < 30:
            return {
                "stage": "RECOVERY_3",
                "position_multiplier": 0.5,
                "leverage_multiplier": 0.67,
                "message": "🔄 Stabilizing - 50% position size"
            }
        elif minutes_after_event < 60:
            return {
                "stage": "RECOVERY_4",
                "position_multiplier": 0.75,
                "leverage_multiplier": 0.83,
                "message": "🔄 Almost normal - 75% position size"
            }
        else:
            return {
                "stage": "NORMAL",
                "position_multiplier": 1.0,
                "leverage_multiplier": 1.0,
                "message": "✅ Full recovery - Normal trading"
            }
    
    # ==================== STATUS & REPORTING ====================
    
    def get_status_report(self) -> str:
        """Generate human-readable status report"""
        self._update_events_if_needed()
        
        report = ["=" * 50]
        report.append("📅 EVENT MANAGER STATUS")
        report.append("=" * 50)
        
        # Trading decision
        decision = self.get_trading_decision()
        report.append(f"\n🎯 Current Status: {decision['status']}")
        report.append(f"📊 Action: {decision['action']}")
        report.append(f"💰 Position Size: {decision['position_size_multiplier']:.0%}")
        report.append(f"⚡ Leverage: {decision['leverage_multiplier']:.0%}")
        report.append(f"📝 Reason: {decision['reason']}")
        
        # Sentiment
        sentiment = self.get_sentiment_signal()
        report.append(f"\n💭 Sentiment: {sentiment['message']}")
        
        # Upcoming events
        report.append(f"\n📅 Upcoming Events:")
        if self.events:
            for event in self.events[:5]:  # Show next 5
                mins = event.minutes_until()
                if mins > 0:
                    hours = mins / 60
                    if hours < 24:
                        time_str = f"in {hours:.1f}h"
                    else:
                        time_str = f"in {hours/24:.1f}d"
                    report.append(f"  {event.severity.value} {event.name} - {time_str}")
        else:
            report.append("  ✅ No major events upcoming")
        
        report.append("=" * 50)
        
        return "\n".join(report)
