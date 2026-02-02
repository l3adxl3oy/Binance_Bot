# 📱 Telegram Bot Commands - v2.0 (Updated)

## 🎯 Overview
Daily Scalping Bot v2.0 รองรับการควบคุมผ่าน Telegram แบบเรียลไทม์ พร้อมคำสั่งเพิ่มเติมสำหรับ multi-symbol trading และ weighted signals

---

## 🚀 Quick Start Commands

### Basic Controls
```
/start - เริ่มบอท และแสดงคำสั่งพื้นฐาน
/stop - หยุดบอทและปิดออเดอร์ทั้งหมด
/status - ดูสถานะปัจจุบัน (balance, positions, daily P&L)
/help - แสดงคำสั่งทั้งหมด
```

---

## 📋 All Commands

### 🎮 Control Commands

#### `/start`
เริ่มต้นบอทและแสดงคำสั่งพื้นฐาน

#### `/stop`
หยุดบอทและปิดออเดอร์ทั้งหมดอย่างปลอดภัย

#### `/pause`
หยุดการเปิดออเดอร์ใหม่ชั่วคราว (ออเดอร์เดิมยังทำงาน)

#### `/resume`
เริ่มเทรดต่อหลังจาก pause

---

### 💰 Trading Information

#### `/status`
แสดงสถานะบอทแบบละเอียด
```
Example output:
🤖 Daily Scalping Bot v2.0

⚡ Status: ✅ RUNNING
🎮 Mode: TESTNET
💰 Balance: $100.53
📊 Daily P&L: +0.53%

📈 Positions: 2/10
🎯 Active Symbols: 10/20
📊 Win Rate: 73.3%
```

#### `/balance`
แสดงยอดเงินและกำไร/ขาดทุน

#### `/positions` หรือ `/pos`
แสดงออเดอร์ที่เปิดอยู่ทั้งหมด พร้อม trailing stop status

#### `/trades`
แสดงประวัติเทรดล่าสุด 5 รายการ

#### `/stats`
แสดงสถิติการเทรดแบบละเอียด
- Win rate, avg win/loss
- Best/worst trades
- Per-symbol performance

---

### 📊 Analysis Commands

#### `/symbols`
แสดง active symbols และ momentum scores
```
📊 Active Symbols (10/10)

1. BTCUSDT: $79,520.00 (score: 8.5)
2. ETHUSDT: $2,455.00 (score: 7.2)
...
```

#### `/price [SYMBOL]`
แสดงราคาปัจจุบัน
```
/price - ราคา symbol แรก
/price BTC - ราคา BTCUSDT
```

#### `/logic [SYMBOL]` 🆕
แสดงการวิเคราะห์สัญญาณแบบละเอียด (v2.0 feature!)
```
🔍 Signal Analysis - BTCUSDT

📊 Indicators:
1️⃣ RSI(14): 28.5 🟢 Oversold
2️⃣ BB: 0.85% width ✅ Trending
3️⃣ MACD: 0.0125 📈 Bullish
4️⃣ Volume: 2.3x 🔥 High

🎯 Signal Strength:
• Buy: 5.2
• Sell: 0.0
• Min Required: 4.0

🎲 Entry Decision:
🟢 BUY Signal (Strength: 5.2)
```

#### `/settings`
แสดงการตั้งค่าบอททั้งหมด
- Strategy parameters
- Risk management
- Trailing stop config
- Daily limits

---

## 🆕 What's New in v2.0

1. **Weighted Signal Scoring** - แสดง signal strength (0-10 scale)
2. **Multi-Symbol Support** - `/symbols` command ใหม่
3. **Trend Filter** - แสดง trend direction (↗ ↘)
4. **Enhanced Statistics** - Per-symbol performance
5. **Detailed Position Info** - Trailing stop status, time in position

---

## 💡 Usage Tips

### Monitor Trading
```
/status ทุก 5-10 นาที
/positions เมื่อมีออเดอร์
/stats ทุกชั่วโมง
```

### Analyze Signals
```
/logic - เข้าใจว่าทำไมเข้า/ไม่เข้า
/symbols - ดู momentum
/price - เช็คราคาเร็วๆ
```

### Control Bot
```
/pause - หยุดชั่วคราว
/resume - เทรดต่อ
/stop - ปิดบอท
```

---

## 📱 Example Workflow

### Morning Routine
```
/start → /status → /settings → /symbols
```

### During Trading
```
รอแจ้งเตือนเข้าออเดอร์ 🟢
→ /positions เช็คออเดอร์
→ /logic ดูสัญญาณ
→ รอแจ้งเตือนออกออเดอร์ 💰
```

### End of Day
```
/stats → /trades → /stop (ถ้าต้องการ)
```

---

## 📊 Automatic Notifications

บอทจะส่งแจ้งเตือนอัตโนมัติ:

### Entry Notification
```
🟢 ENTRY BTCUSDT
Side: BUY
Price: $79,350.00
Strength: 5.2
Signals: RSI<30⭐, MACD⬆⭐, Vol2.3x, ↗Trend
```

### Exit Notification
```
💰 EXIT BTCUSDT BUY
P&L: +0.72% ($+0.57)
Reason: TP
Balance: $100.57
```

### Daily Summary
```
📊 DAILY SUMMARY
Trades: 25
Win Rate: 72.0%
Daily P&L: +3.45%
Target: ✅ REACHED
```

---

**🚀 Happy Trading with Telegram Control!**

Version: 2.0  
Last Updated: Feb 2, 2026
