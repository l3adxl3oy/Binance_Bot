import threading
import time
import requests
from datetime import datetime, UTC
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class TelegramCommandHandler:
    def __init__(self, bot_instance, bot_token: str, chat_id: str):
        self.bot = bot_instance
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.last_update_id = 0
        self.running = True
        
        self.commands = {
            '/start': self.cmd_start,
            '/stop': self.cmd_stop,
            '/status': self.cmd_status,
            '/help': self.cmd_help,
            '/balance': self.cmd_balance,
            '/positions': self.cmd_positions,
            '/pos': self.cmd_positions,
            '/trades': self.cmd_trades,
            '/stats': self.cmd_stats,
            '/symbols': self.cmd_symbols,
            '/price': self.cmd_price,
            '/logic': self.cmd_logic,
            '/pause': self.cmd_pause,
            '/resume': self.cmd_resume,
            '/settings': self.cmd_settings,
        }
    
    def start_polling(self):
        logger.info(" Telegram command listener started")
        while self.running:
            try:
                updates = self.get_updates()
                for update in updates:
                    self.process_update(update)
                time.sleep(1)
            except Exception as e:
                logger.error(f"Telegram polling error: {e}")
                time.sleep(5)
    
    def get_updates(self) -> List[Dict]:
        try:
            url = f"{self.base_url}/getUpdates"
            params = {"offset": self.last_update_id + 1, "timeout": 30}
            response = requests.get(url, params=params, timeout=35)
            
            if response.status_code == 200:
                data = response.json()
                if data['ok']:
                    updates = data['result']
                    if updates:
                        self.last_update_id = updates[-1]['update_id']
                    return updates
            return []
        except:
            return []
    
    def process_update(self, update: Dict):
        if 'message' not in update or 'text' not in update['message']:
            return
        
        message = update['message']
        chat_id = str(message['chat']['id'])
        text = message['text'].strip()
        
        if chat_id != self.chat_id:
            self.send_message(chat_id, " Unauthorized")
            return
        
        parts = text.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if command in self.commands:
            try:
                self.commands[command](chat_id, args)
            except Exception as e:
                self.send_message(chat_id, f" Error: {str(e)}")
        else:
            self.send_message(chat_id, " Unknown command. Use /help")
    
    def send_message(self, chat_id: str, text: str):
        try:
            url = f"{self.base_url}/sendMessage"
            data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
            requests.post(url, data=data, timeout=10)
        except Exception as e:
            logger.error(f"Send message error: {e}")
    
    def cmd_start(self, chat_id: str, args: List[str]):
        """เริ่มต้นบอทและแสดงคำสั่งพื้นฐาน"""
        self.bot.trading_paused = False
        msg = """
🤖 <b>Trading Bot เริ่มทำงานแล้ว!</b>

<b>📱 คำสั่งพื้นฐาน:</b>

/status - ดูสถานะบอท
/stop - หยุดเทรด
/balance - ดูยอดเงิน
/positions - ดูออเดอร์
/help - ดูคำสั่งทั้งหมด

✅ บอทพร้อมทำงาน!
"""
        self.send_message(chat_id, msg.strip())
    
    def cmd_help(self, chat_id: str, args: List[str]):
        """แสดงคำสั่งทั้งหมด"""
        msg = """
📖 <b>Daily Scalping Bot v2.0 Commands</b>

<b>🎮 Control:</b>
/start - Start bot
/stop - Stop bot
/status - Current status
/pause - Pause trading
/resume - Resume trading

<b>💰 Trading Info:</b>
/balance - Account balance
/positions or /pos - Open positions
/trades - Recent trades
/stats - Detailed statistics
/symbols - Active symbols & momentum

<b>📊 Analysis:</b>
/price [SYMBOL] - Current price
/logic - Signal analysis
/settings - Bot configuration

<b>🆕 v2.0 Features:</b>
✅ Weighted signal scoring
✅ Trend filter (EMA 20/50)
✅ Multi-symbol trading
✅ Enhanced risk management
"""
        self.send_message(chat_id, msg.strip())
    
    def cmd_status(self, chat_id: str, args: List[str]):
        from daily_scalping_bot import Config

        status = "✅ RUNNING" if self.bot.running else "🛑 STOPPED"
        trading = "⏸️ PAUSED" if getattr(self.bot, "trading_paused", False) else "▶️ ACTIVE"
        mode = "DEMO" if Config.DEMO_MODE else "LIVE"
        
        # Get positions from position manager
        all_positions = self.bot.position_manager.get_all_positions()
        positions_text = ""
        
        if all_positions:
            for i, pos in enumerate(all_positions[:5], 1):
                # Simple display without fetching current price
                positions_text += f"\n  {i}. {pos.symbol} {pos.side} @${pos.entry_price:.2f}"
        else:
            positions_text = "\n  None"
        
        balance = self.bot.trade_history.current_balance
        daily_pnl = self.bot.trade_history.get_daily_pnl_percent()
        
        # Active symbols
        active_symbols = self.bot.symbol_manager.get_active_symbols()
        
        # Recovery mode status
        recovery = "🔴 RECOVERY" if self.bot.recovery_mode else "✅ Normal"
        profit_lock = "🔒 LOCKED" if self.bot.profit_locked else "🔓 Active"
        
        msg = f"""
🤖 <b>Daily Scalping Bot v2.0</b>

⚡ Status: {status}
🎮 Trading: {trading}
🎮 Mode: <b>{mode}</b>
💰 Balance: <b>${balance:.2f}</b>
📊 Daily P&L: <b>{daily_pnl:+.2f}%</b>

📈 Positions: {len(all_positions)}/{self.bot.position_manager.max_total_positions}{positions_text}

🎯 <b>Trading Info:</b>
• Active Symbols: {len(active_symbols)}/20
• Risk Mode: {recovery}
• Profit Lock: {profit_lock}

📊 <b>Today's Stats:</b>
• Trades: {len(self.bot.trade_history.trades)}
• Win Rate: {self.bot.trade_history.get_win_rate():.1f}%
• Target: {Config.DAILY_PROFIT_TARGET}%

🕐 {datetime.now(UTC).strftime('%H:%M:%S UTC')}
"""
        self.send_message(chat_id, msg.strip())
    
    def cmd_stop(self, chat_id: str, args: List[str]):
        """หยุดบอทและปิดทุกออเดอร์"""
        self.bot.running = False
        
        # Count positions to close
        positions = self.bot.position_manager.get_all_positions()
        
        msg = f"""
⛔ <b>Stopping Bot...</b>

• Bot will stop after closing positions
• Open positions: {len(positions)}
• Will execute shutdown safely

⚠️ Bot is shutting down...
"""
        self.send_message(chat_id, msg.strip())
    
    def cmd_pause(self, chat_id: str, args: List[str]):
        """หยุดเทรดชั่วคราว (ไม่เปิดออเดอร์ใหม่)"""
        # Set a pause flag (you might want to add this to the bot class)
        if not hasattr(self.bot, 'trading_paused'):
            self.bot.trading_paused = False
        
        self.bot.trading_paused = True
        
        positions = self.bot.position_manager.get_all_positions()
        
        msg = f"""
⏸️ <b>Trading Paused</b>

• No new positions will be opened
• Existing positions continue: {len(positions)}
• Send /resume to continue
"""
        self.send_message(chat_id, msg.strip())
    
    def cmd_resume(self, chat_id: str, args: List[str]):
        """เทรดต่อหลังหยุดชั่วคราว"""
        if hasattr(self.bot, 'trading_paused'):
            self.bot.trading_paused = False
        
        msg = """
▶️ <b>Trading Resumed</b>

✅ Bot will start looking for entries
✅ All systems active
"""
        self.send_message(chat_id, msg.strip())
    
    def cmd_balance(self, chat_id: str, args: List[str]):
        """แสดงยอดเงิน"""
        balance = self.bot.trade_history.current_balance
        initial = self.bot.trade_history.daily_start_balance
        pnl = balance - initial
        pnl_pct = (pnl / initial * 100) if initial > 0 else 0
        
        msg = f"""
💰 <b>ยอดเงิน</b>

• ปัจจุบัน: <b>${balance:,.2f}</b>
• เริ่มต้น: ${initial:,.2f}
• กำไร/ขาดทุน: {pnl:+.2f} USD ({pnl_pct:+.2f}%)
"""
        self.send_message(chat_id, msg.strip())
    
    def cmd_positions(self, chat_id: str, args: List[str]):
        all_positions = self.bot.position_manager.get_all_positions()
        
        if not all_positions:
            self.send_message(chat_id, "📭 No open positions")
            return
        
        msg = f"📊 <b>Open Positions ({len(all_positions)}/{self.bot.position_manager.max_total_positions})</b>\n\n"
        
        for i, pos in enumerate(all_positions, 1):
            # Get current data for this symbol
            data = self.bot.get_market_data(pos.symbol)
            if data:
                current_price = data['current_price']
                if pos.side == "BUY":
                    pnl = ((current_price - pos.entry_price) / pos.entry_price * 100)
                else:
                    pnl = ((pos.entry_price - current_price) / pos.entry_price * 100)
            else:
                current_price = pos.entry_price
                pnl = 0.0
            
            # Time in position
            time_elapsed = (datetime.now(UTC) - pos.entry_time).total_seconds()
            time_str = f"{int(time_elapsed//60)}m{int(time_elapsed%60)}s"
            
            # Trailing stop indicator
            trailing = "🔄" if pos.trailing_stop_active else ""
            
            emoji = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
            
            msg += f"""
{i}. {emoji} <b>{pos.symbol} {pos.side}</b> {trailing}
   Entry: ${pos.entry_price:.2f}
   Current: ${current_price:.2f} ({pnl:+.2f}%)
   SL: ${pos.stop_loss:.2f} | TP: ${pos.take_profit:.2f}
   Score: {pos.confluence_score} | Time: {time_str}

"""
        
        self.send_message(chat_id, msg.strip())
    
    def cmd_trades(self, chat_id: str, args: List[str]):
        """แสดงประวัติเทรดล่าสุด"""
        trades = self.bot.trade_history.trades[-5:]
        
        if not trades:
            self.send_message(chat_id, "📝 ยังไม่มีเทรด")
            return
        
        msg = "📝 <b>เทรดล่าสุด (5 รายการ)</b>\n\n"
        
        for i, trade in enumerate(reversed(trades), 1):
            emoji = "✅" if trade.profit_percent and trade.profit_percent > 0 else "❌"
            msg += (
                f"{i}. {emoji} {trade.symbol} {trade.side} @ ${trade.entry_price:.2f} "
                f"({trade.profit_percent:+.2f}%)\n"
            )
        
        self.send_message(chat_id, msg.strip())
    
    def cmd_stats(self, chat_id: str, args: List[str]):
        """แสดงสถิติการเทรดที่ละเอียด"""
        trades = self.bot.trade_history.trades
        total = len(trades)
        
        if total == 0:
            self.send_message(chat_id, "📊 No trades yet")
            return
        
        wins = sum(1 for t in trades if t.profit_percent > 0)
        losses = total - wins
        wr = self.bot.trade_history.get_win_rate()
        pnl = self.bot.trade_history.get_daily_pnl_percent()
        
        # Calculate average profit/loss
        winning_trades = [t.profit_percent for t in trades if t.profit_percent > 0]
        losing_trades = [t.profit_percent for t in trades if t.profit_percent <= 0]
        
        avg_win = sum(winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(losing_trades) / len(losing_trades) if losing_trades else 0
        
        # Best and worst trades
        best_trade = max(trades, key=lambda t: t.profit_percent)
        worst_trade = min(trades, key=lambda t: t.profit_percent)
        
        # Per-symbol stats (top 3)
        symbol_stats = self.bot.trade_history.symbol_stats
        top_symbols = ""
        if symbol_stats:
            sorted_symbols = sorted(symbol_stats.items(), key=lambda x: x[1]['pnl'], reverse=True)[:3]
            for symbol, stats in sorted_symbols:
                top_symbols += f"\n  • {symbol}: {stats['pnl']:+.2f}% ({stats['wins']}W/{stats['losses']}L)"
        else:
            top_symbols = "\n  • No data yet"
        
        msg = f"""
📈 <b>Trading Statistics</b>

📊 <b>Overall:</b>
• Total Trades: {total}
• Wins: {wins} | Losses: {losses}
• Win Rate: <b>{wr:.1f}%</b>
• Daily P&L: <b>{pnl:+.2f}%</b>

💰 <b>Performance:</b>
• Avg Win: +{avg_win:.2f}%
• Avg Loss: {avg_loss:.2f}%
• Best Trade: {best_trade.symbol} {best_trade.profit_percent:+.2f}%
• Worst Trade: {worst_trade.symbol} {worst_trade.profit_percent:+.2f}%

🎯 <b>Top Symbols:</b>{top_symbols}

💵 <b>Balance:</b>
• Current: ${self.bot.trade_history.current_balance:.2f}
• Start: ${self.bot.trade_history.daily_start_balance:.2f}
• Profit: ${self.bot.trade_history.current_balance - self.bot.trade_history.daily_start_balance:+.2f}
"""
        self.send_message(chat_id, msg.strip())
    
    def cmd_settings(self, chat_id: str, args: List[str]):
        """แสดงการตั้งค่า"""
        # Import Config from main bot file
        from daily_scalping_bot import Config
        
        msg = f"""
⚙️ <b>Bot Configuration v2.0</b>

<b>📊 Strategy:</b>
• Timeframe: {Config.TIMEFRAME}
• Min Signal Strength: {Config.MIN_SIGNAL_STRENGTH}
• Weighted Signals: {'✅ ON' if Config.USE_WEIGHTED_SIGNALS else '❌ OFF'}
• Trend Filter: {'✅ ON' if Config.TRADE_WITH_TREND_ONLY else '❌ OFF'}

<b>📈 Indicators:</b>
• RSI Period: {Config.RSI_PERIOD}
• Volume Multiplier: {Config.VOLUME_MULTIPLIER}x
• EMA Fast/Slow: {Config.EMA_FAST}/{Config.EMA_SLOW}

<b>💰 Risk Management:</b>
• Max Loss/Trade: {Config.MAX_LOSS_PER_TRADE}%
• Stop Loss: {Config.STOP_LOSS_PERCENT}%
• Take Profit (3sig): {Config.TAKE_PROFIT_3_SIGNALS}%
• Take Profit (4sig): {Config.TAKE_PROFIT_4_SIGNALS}%
• Time Stop: {Config.TIME_STOP_SECONDS}s

<b>🔄 Trailing Stop:</b>
• Enabled: {'✅ YES' if Config.TRAILING_STOP_ENABLED else '❌ NO'}
• Activation: {Config.TRAILING_ACTIVATION_PROFIT}%
• Trail Distance: {Config.TRAILING_STOP_PERCENT}%

<b>🎯 Daily Limits:</b>
• Loss Limit: -{Config.DAILY_LOSS_LIMIT}%
• Profit Target: +{Config.DAILY_PROFIT_TARGET}%
• Max Target: +{Config.DAILY_MAX_TARGET}%

<b>📊 Multi-Symbol:</b>
• Symbol Pool: {len(Config.SYMBOL_POOL)} symbols
• Max Active: {Config.MAX_ACTIVE_SYMBOLS}
• Max Positions: {Config.MAX_TOTAL_POSITIONS}
"""
        self.send_message(chat_id, msg.strip())
    
    def cmd_price(self, chat_id: str, args: List[str]):
        """แสดงราคาปัจจุบัน"""
        # If symbol provided, get that symbol's price
        if args:
            symbol = args[0].upper()
            if not symbol.endswith('USDT'):
                symbol += 'USDT'
        else:
            # Get first active symbol
            active_symbols = self.bot.symbol_manager.get_active_symbols()
            symbol = active_symbols[0] if active_symbols else 'BTCUSDT'
        
        # Get market data
        data = self.bot.get_market_data(symbol)
        if data:
            price = data['current_price']
            self.send_message(chat_id, f"💹 {symbol}: <b>${price:.2f}</b>")
        else:
            self.send_message(chat_id, f"❌ Cannot fetch price for {symbol}")
    
    def cmd_symbols(self, chat_id: str, args: List[str]):
        """แสดง active symbols และ momentum"""
        active_symbols = self.bot.symbol_manager.get_active_symbols()
        
        if not active_symbols:
            self.send_message(chat_id, "📊 No active symbols")
            return
        
        msg = f"📊 <b>Active Symbols ({len(active_symbols)}/{self.bot.symbol_manager.max_active})</b>\n\n"
        
        # Get momentum scores
        for i, symbol in enumerate(active_symbols[:10], 1):
            momentum = self.bot.symbol_manager.momentum_scores.get(symbol, {})
            score = momentum.get('score', 0)
            
            # Get current price
            data = self.bot.get_market_data(symbol)
            if data:
                price = data['current_price']
                msg += f"{i}. {symbol}: ${price:.2f} (score: {score:.1f})\n"
            else:
                msg += f"{i}. {symbol}: N/A\n"
        
        # Rotation info
        next_rotation = self.bot.symbol_manager.next_rotation_time - datetime.now(UTC).timestamp()
        next_rotation_min = int(next_rotation / 60)
        
        msg += f"\n🔄 Next rotation: {next_rotation_min}m"
        
        self.send_message(chat_id, msg.strip())
    
    def cmd_logic(self, chat_id: str, args: List[str]):
        """แสดง logic การวิเคราะห์สัญญาณล่าสุด"""
        from daily_scalping_bot import Config
        
        # Get symbol argument or use first active symbol
        if args:
            symbol = args[0].upper()
            if not symbol.endswith('USDT'):
                symbol += 'USDT'
        else:
            active_symbols = self.bot.symbol_manager.get_active_symbols()
            symbol = active_symbols[0] if active_symbols else 'BTCUSDT'
        
        # Get current market data and calculate signals
        data = self.bot.get_market_data(symbol)
        if not data:
            self.send_message(chat_id, f"❌ Cannot fetch data for {symbol}")
            return
        
        signals = self.bot.calculate_signals(symbol, data)
        
        # Extract signal details
        current_price = signals['current_price']
        rsi = signals['rsi']
        bb_width = signals['bb_width']
        macd_hist = signals['macd_hist']
        volume_ratio = signals['volume_ratio']
        
        buy_strength = signals.get('buy_strength', 0)
        sell_strength = signals.get('sell_strength', 0)
        is_uptrend = signals.get('is_uptrend', False)
        is_downtrend = signals.get('is_downtrend', False)
        
        # Trend status
        trend_emoji = "📈" if is_uptrend else "📉" if is_downtrend else "➡️"
        trend_text = "UPTREND" if is_uptrend else "DOWNTREND" if is_downtrend else "SIDEWAYS"
        
        # Signal details with emojis
        signal_details = signals.get('signal_details', [])
        signals_text = ", ".join(signal_details) if signal_details else "No signals"
        
        # Entry decision
        if Config.USE_WEIGHTED_SIGNALS:
            if buy_strength >= Config.MIN_SIGNAL_STRENGTH:
                entry_decision = f"🟢 <b>BUY Signal</b> (Strength: {buy_strength:.1f})"
            elif sell_strength >= Config.MIN_SIGNAL_STRENGTH:
                entry_decision = f"🔴 <b>SELL Signal</b> (Strength: {sell_strength:.1f})"
            else:
                entry_decision = f"⚪ <b>NO ENTRY</b> (Buy: {buy_strength:.1f}, Sell: {sell_strength:.1f})"
        else:
            buy_signals = signals.get('buy_signals', 0)
            sell_signals = signals.get('sell_signals', 0)
            if buy_signals >= Config.MIN_CONFLUENCE_SIGNALS:
                entry_decision = f"🟢 <b>BUY Signal</b> ({buy_signals}/4)"
            elif sell_signals >= Config.MIN_CONFLUENCE_SIGNALS:
                entry_decision = f"🔴 <b>SELL Signal</b> ({sell_signals}/4)"
            else:
                entry_decision = f"⚪ <b>NO ENTRY</b> (Buy: {buy_signals}/4, Sell: {sell_signals}/4)"
        
        # Check filters
        passed, reason = self.bot.check_filters(symbol, signals)
        filter_status = "✅ All filters passed" if passed else f"❌ Blocked: {reason}"
        
        msg = f"""
🔍 <b>Signal Analysis - {symbol}</b>

💰 <b>Current Price:</b> ${current_price:.2f}
{trend_emoji} <b>Trend:</b> {trend_text}

📊 <b>Indicators:</b>

1️⃣ RSI({Config.RSI_PERIOD}): {rsi:.1f}
   {'🔴 Overbought' if rsi > 70 else '🟢 Oversold' if rsi < 30 else '⚪ Neutral'}

2️⃣ Bollinger Bands: {bb_width:.2f}% width
   {'⚠️ Sideways' if bb_width < Config.SIDEWAYS_THRESHOLD else '✅ Trending'}

3️⃣ MACD Histogram: {macd_hist:.4f}
   {'📈 Bullish' if macd_hist > 0 else '📉 Bearish'}

4️⃣ Volume: {volume_ratio:.1f}x average
   {'🔥 High volume' if volume_ratio > Config.VOLUME_MULTIPLIER else '⚪ Normal'}

━━━━━━━━━━━━━━━━━━━━

<b>🎯 Signal Strength:</b>
• Buy: {buy_strength:.1f}
• Sell: {sell_strength:.1f}
• Min Required: {Config.MIN_SIGNAL_STRENGTH}

<b>📋 Active Signals:</b>
{signals_text}

━━━━━━━━━━━━━━━━━━━━

<b>🎲 Entry Decision:</b>
{entry_decision}

<b>🚦 Filters:</b>
{filter_status}

━━━━━━━━━━━━━━━━━━━━

<b>💡 Strategy (v2.0):</b>

<b>Entry Rules:</b>
✓ Weighted signal strength ≥ {Config.MIN_SIGNAL_STRENGTH}
✓ Trend aligned ({Config.TRADE_WITH_TREND_ONLY and 'REQUIRED' or 'OPTIONAL'})
✓ Volume confirmation ({Config.VOLUME_MULTIPLIER}x)
✓ Not in sideways market
✓ Within position limits

<b>Exit Rules:</b>
✓ TP: {Config.TAKE_PROFIT_3_SIGNALS}% / {Config.TAKE_PROFIT_4_SIGNALS}%
✓ SL: {Config.STOP_LOSS_PERCENT}%
✓ Trailing: {Config.TRAILING_ACTIVATION_PROFIT}% activation
✓ Time Stop: {Config.TIME_STOP_SECONDS}s

🕐 {datetime.now(UTC).strftime('%H:%M:%S UTC')}
"""
        self.send_message(chat_id, msg.strip())