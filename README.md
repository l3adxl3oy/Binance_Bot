# BinanceBot Professional - Automated Scalping Trading Bot

🚀 **Professional-grade automated trading bot** สำหรับ Binance Spot Market  
✨ รองรับ Multi-symbol trading พร้อม Telegram real-time notifications

---

## 🎯 Features

### 🤖 Core Trading Features
✅ **Ultra-Fast Scalping** - 1-minute timeframe trading  
✅ **Multi-Symbol Trading** - จัดการได้ถึง 15 symbols พร้อมกัน  
✅ **Advanced Risk Management** - Stop Loss, Take Profit, Trailing Stop  
✅ **Multi-Indicator Confluence** - RSI, Bollinger Bands, MACD, Volume  
✅ **Adaptive Position Sizing** - ปรับขนาด position ตามสถานการณ์  
✅ **Multi-Timeframe Analysis** - ยืนยันสัญญาณจาก 1m, 3m, 5m timeframes  
✅ **Telegram Integration** - ควบคุมและรับ notifications แบบ real-time  
✅ **Daily Profit Target** - หยุดเทรดอัตโนมัติเมื่อถึงเป้าหมาย

### 🧠 Intelligent Systems (v3.0)
✅ **Event Manager** - ตรวจจับเหตุการณ์เศรษฐกิจ NFP, FOMC, CPI และปรับกลยุทธ์  
✅ **Sentiment Tracking** - ติดตาม Fear & Greed Index และปรับความเสี่ยง  
✅ **Cascade Detection** - ตรวจจับ liquidation cascades และปิด positions ฉุกเฉิน  
✅ **Risk Manager** - Kelly Criterion, Correlation Filter, Drawdown Protection  
✅ **Adaptive Strategy** - ตรวจจับ market regime และปรับ parameters อัตโนมัติ  
✅ **Enhanced Alerts** - การแจ้งเตือนแบบมีระดับความสำคัญ (CRITICAL/HIGH/MEDIUM/LOW)  
✅ **Portfolio Correlation** - ป้องกันการเปิด positions ที่ correlation สูงเกินไป  
✅ **Consecutive Loss Protection** - ลดความเสี่ยงหลังแพ้ติดต่อกัน  

---

## 📊 Performance Expectations

**Target Performance (v3.0 with Intelligent Systems):**
- Daily Profit Target: **+5% to +10%**
- Win Rate: **60-70%** (improved by Multi-TF + Adaptive Strategy)
- Risk per Trade: **0.6% of capital** (dynamic with Kelly Criterion)
- Max Drawdown: **-2.5%** (auto-stop + Drawdown Protection)
- Max Portfolio Correlation: **0.65** (prevents over-exposure)

**Trading Style:**
- **Ultra-short term** (1-5 minutes per trade)
- **Smart frequency** (6-15 trades/day, adaptive to market conditions)
- **Dynamic risk** (Kelly + Volatility + Correlation adjustments)
- **Event-aware** (pauses/adjusts during NFP, FOMC, high volatility)

---

## 🛠️ System Requirements

- **Python**: 3.8 or higher
- **Capital**: Recommended starting at $100+
- **Binance Account**: Spot trading enabled
- **API Keys**: With spot trading permissions
- **Internet**: Stable connection required
- **OS**: Windows, Linux, or macOS

---

## 📦 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd BinanceBot

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy config template
cp config/config_example.py config/config.py

# Edit config.py and add your credentials:
# - Binance API Key & Secret
# - Telegram Bot Token & Chat ID (optional)
```

**Important Settings:**
```python
API_KEY = "your_binance_api_key"
API_SECRET = "your_binance_secret"
BASE_URL = "https://testnet.binance.vision"  # Start with testnet!
DEMO_MODE = True  # Keep True for testing
```

### 3. Run the Bot

```bash
# Make sure you're in the project root directory
python bots/daily_scalping_bot.py
```

---

## 🧠 Intelligent Features (v3.0)

บอท v3.0 มาพร้อมระบบอัจฉริยะ 4 ระบบหลัก:

### 1. Event Manager
- 📅 **Economic Calendar**: ตรวจจับ NFP, FOMC, CPI ล่วงหน้า 30-120 นาที
- 😱 **Fear & Greed Index**: ปรับ position size ตาม sentiment (×1.5 ตอน extreme fear, ×0.5 ตอน extreme greed)
- 🌊 **Cascade Detection**: ตรวจจับ flash crash (>10% ใน 1 นาที) และปิด positions ฉุกเฉิน
- 🛡️ **Auto Protection**: ปิด positions อัตโนมัติก่อนเหตุการณ์สำคัญ

### 2. Risk Manager
- 🎯 **Kelly Criterion**: คำนวณ position size ที่เหมาะสมจาก win rate และ win/loss ratio
- 🔗 **Correlation Filter**: ป้องกันการเปิด positions ที่ correlation >0.65
- 📉 **Volatility Adjustment**: ลด position size 60% เมื่อ volatility สูงเกินไป
- 🎢 **Drawdown Protection**: ลด size 50% เมื่อ drawdown ถึง 15%
- 🔴 **Consecutive Loss**: ลด size 60% หลังแพ้ติดต่อกัน 5 ครั้ง
- 🚨 **Daily/Monthly Limits**: หยุดเทรดอัตโนมัติถ้าขาดทุน >2.5%/วัน หรือ >10%/เดือน

### 3. Adaptive Strategy Engine
- 📊 **Market Regime Detection**: ตรวจจับ BULL/BEAR/RANGING/VOLATILE/BREAKOUT
- ⚙️ **Dynamic Parameters**: ปรับ TP/SL/Position Size ตาม regime
- 📈 **Performance Learning**: ปรับ parameters จาก win rate (>65% = aggressive, <50% = defensive)
- ⏰ **Time-of-Day**: ลด size 50% ช่วงกลางคืน (2-6 AM UTC), เพิ่ม 20% ช่วง peak (1-5 PM UTC)

### 4. Enhanced Alert System
- 🔴 **CRITICAL Alerts**: ส่งทันที (NFP, liquidation cascade)
- 🟠 **HIGH Alerts**: สูงสุดทุก 30 วินาที
- 🟡 **MEDIUM Alerts**: สูงสุดทุก 60 วินาที
- 📊 **Daily Summary**: รายงานสรุปท้ายวันพร้อมสถิติ

---

## 📚 Documentation

- [Setup Guide](docs/SETUP_GUIDE.md) - การติดตั้งและตั้งค่าละเอียด
- [Quick Start Guide](docs/QUICK_START_V2.md) - เริ่มต้นใช้งานอย่างรวดเร็ว
- [Intelligent Features](docs/INTELLIGENT_FEATURES.md) - 🆕 ระบบอัจฉริยะ v3.0 ทั้งหมด
- [Strategy Analysis](docs/STRATEGY_ANALYSIS_V3.md) - วิเคราะห์กลยุทธ์การเทรด
- [Telegram Commands](docs/TELEGRAM_COMMANDS_V2.md) - คำสั่ง Telegram ทั้งหมด
- [Telegram Setup](docs/TELEGRAM_GUIDE.md) - การติดตั้ง Telegram bot

---

## ⚙️ Configuration Overview

### Trading Parameters
```python
STARTING_BALANCE = 100.0        # เงินทุนเริ่มต้น
MAX_ACTIVE_SYMBOLS = 15         # จำนวน symbols สูงสุด
TIMEFRAME = "1m"                # 1-minute candles
DEMO_MODE = True                # ทดสอบก่อน (ไม่ส่ง order จริง)
```

### Risk Management
```python
MAX_LOSS_PER_TRADE = 0.6        # ความเสี่ยงต่อเทรด (%)
STOP_LOSS_PERCENT = 0.35        # Stop Loss (%)
TAKE_PROFIT_4_SIGNALS = 1.15    # Take Profit สูงสุด (%)
DAILY_LOSS_LIMIT = 2.5          # หยุดเทรดถ้าขาดทุน (%)
DAILY_PROFIT_TARGET = 5.0       # เป้าหมายกำไรรายวัน (%)
```

### Strategy Settings
```python
MIN_CONFLUENCE_SIGNALS = 3      # ต้องการสัญญาณขั้นต่ำ 3/4
RSI_OVERSOLD = 30               # RSI oversold threshold
RSI_OVERBOUGHT = 70             # RSI overbought threshold
VOLUME_MULTIPLIER = 1.5         # ต้องการ volume สูง 1.5x
```

### Intelligent Features (v3.0)
```python
# Event Management
ENABLE_EVENT_MANAGER = True           # Economic calendar + sentiment
ENABLE_SENTIMENT_TRACKING = True      # Fear & Greed Index
ENABLE_CASCADE_DETECTION = True       # Flash crash detection

# Risk Management
ENABLE_ADVANCED_RISK = True           # Kelly + Correlation + Drawdown
ENABLE_CORRELATION_FILTER = True      # Block correlated positions
MAX_CORRELATION_ALLOWED = 0.65        # Max portfolio correlation

# Adaptive Strategy
ENABLE_ADAPTIVE_STRATEGY = True       # Regime detection + learning
ENABLE_REGIME_DETECTION = True        # BULL/BEAR/RANGING detection

# Enhanced Alerts
ENABLE_ENHANCED_ALERTS = True         # Severity-based alerts
ALERT_DAILY_SUMMARY = True            # End-of-day report
```

---

## 📱 Telegram Integration

**Available Commands:**
- `/start` - เริ่ม bot
- `/stop` - หยุด bot
- `/status` - ดูสถานะปัจจุบัน
- `/positions` - ดู positions ที่เปิดอยู่
- `/balance` - ดู balance และ P&L
- `/trades` - ดูประวัติเทรด
- `/stats` - ดูสถิติโดยรวม
- `/symbols` - ดู symbols ที่กำลังเทรด

**Setup:**
1. สร้าง bot ใหม่กับ @BotFather
2. รับ Bot Token
3. หา Chat ID จาก @userinfobot
4. ใส่ใน config.py

---

## ⚠️ Important Warnings

**🔴 ALWAYS test on Testnet first!**
```python
BASE_URL = "https://testnet.binance.vision"  # Testnet
DEMO_MODE = True  # No real orders
```

**💰 Risk Management:**
- Never risk more than you can afford to lose
- Start with small capital ($100-$500)
- Monitor the bot regularly
- Use stop loss limits
- Don't over-leverage

**🔐 Security:**
- Never share your API keys
- Use API restrictions (Spot trading only)
- Don't enable withdrawals on API
- Keep your config.py private

---

## 🏗️ Project Structure

```
BinanceBot/
├── bots/
│   └── daily_scalping_bot.py     # Main trading bot
├── core/
│   ├── indicators.py              # Technical indicators
│   └── models.py                  # Data models
├── managers/
│   ├── position_manager.py        # Position management
│   └── symbol_manager.py          # Symbol selection
├── modules/
│   └── trailing_stop.py           # Trailing stop implementation
├── config/
│   ├── config.py                  # Your configuration (create this)
│   └── config_example.py          # Configuration template
├── utils/
│   ├── telegram_commands.py       # Telegram bot handler
│   └── get_chat_id.py             # Telegram setup utility
├── docs/                          # Documentation
└── requirements.txt               # Python dependencies
```

---

## 🔧 Troubleshooting

### Bot won't start
- Check API credentials are correct
- Verify API permissions (Spot trading enabled)
- Check internet connection

### No trades happening
- Verify market conditions (need volatility)
- Check if symbols have enough volume
- Review confluence requirements (MIN_CONFLUENCE_SIGNALS)

### Telegram not working
- Verify Bot Token and Chat ID
- Check TELEGRAM_ENABLED = True
- Test connection with /start command

---

## 📈 Optimization Tips

1. **Start Conservative**: Use high MIN_CONFLUENCE_SIGNALS (3-4)
2. **Test Thoroughly**: Run on testnet for at least 1 week
3. **Monitor Performance**: Check win rate and adjust parameters
4. **Adjust Risk**: Start with 0.5% risk per trade
5. **Review Symbols**: Focus on high-volume pairs only

---

## 📞 Support & Updates

For support, please refer to the documentation in the `docs/` folder.

**Recommended reading order:**
1. SETUP_GUIDE.md - ติดตั้งระบบ
2. QUICK_START_V2.md - เริ่มต้นใช้งาน
3. TELEGRAM_GUIDE.md - ตั้งค่า Telegram
4. STRATEGY_ANALYSIS_V3.md - ทำความเข้าใจกลยุทธ์

---

## 📄 License

This software is provided for educational and trading purposes.  
**Use at your own risk. Trading involves substantial risk of loss.**

---

## ✨ Built With

- **Python 3.8+**
- **python-binance** - Binance API wrapper
- **pandas** - Data analysis
- **numpy** - Numerical computing
- **requests** - HTTP library (for Telegram)

---

**⚡ Happy Trading! ⚡**

*Remember: Past performance does not guarantee future results. Always trade responsibly.*
