# 🔧 Setup Guide - การติดตั้งและรัน Bot

## ⚠️ สถานะปัจจุบัน

ตรวจพบว่าระบบยังไม่มี **Python** ติดตั้ง ต้องติดตั้งก่อนจึงจะรัน bot ได้

---

## 📥 Step 1: ติดตั้ง Python

### วิธีที่ 1: ดาวน์โหลดจาก Official Website (แนะนำ)

1. ไปที่ https://www.python.org/downloads/
2. ดาวน์โหลด **Python 3.11** หรือ **3.12** (เวอร์ชันล่าสุด)
3. รันไฟล์ installer
4. **✅ สำคัญ**: ติ๊กถูก "Add Python to PATH" ก่อนกด Install
5. กด "Install Now"
6. รอจนเสร็จ

### วิธีที่ 2: ใช้ Chocolatey (สำหรับผู้ใช้ Chocolatey)

```powershell
choco install python -y
```

### วิธีที่ 3: ใช้ Microsoft Store

```powershell
# เปิด Microsoft Store แล้วค้นหา "Python 3.11" หรือ "Python 3.12"
# หรือรันคำสั่งนี้
winget install Python.Python.3.11
```

---

## ✅ Step 2: ตรวจสอบการติดตั้ง

เปิด **PowerShell ใหม่** (ปิดแล้วเปิดใหม่) แล้วรัน:

```powershell
python --version
```

ควรได้ผลลัพธ์: `Python 3.11.x` หรือ `Python 3.12.x`

ถ้ายังไม่ได้ ลอง:
```powershell
py --version
```

---

## 📦 Step 3: ติดตั้ง Dependencies

```powershell
# ไปที่โฟลเดอร์ BinanceBot
cd D:\Work\BinanceBot

# ติดตั้ง packages
pip install binance-connector pandas numpy

# หรือใช้ requirements.txt
pip install -r requirements.txt
```

---

## 🚀 Step 4: รัน Bot (DEMO Mode)

```powershell
python advanced_scalping_bot.py
```

---

## 🔑 Step 5: ตั้งค่า API Keys (ถ้ายังไม่ได้ทำ)

### สมัคร Binance Testnet (ฟรี, ไม่มีความเสี่ยง)

1. ไปที่: https://testnet.binance.vision/
2. กด "Login with GitHub" หรือ "Login with Binance"
3. หลังจาก Login แล้วจะได้:
   - **API Key**
   - **API Secret**
4. คัดลอก API Key และ Secret

### แก้ไข Config

เปิดไฟล์ `advanced_scalping_bot.py` แก้ไขในส่วน `Config`:

```python
class Config:
    API_KEY = "your_api_key_here"       # วาง API Key ของคุณ
    API_SECRET = "your_api_secret_here" # วาง API Secret ของคุณ
    BASE_URL = "https://testnet.binance.vision"  # Testnet
    DEMO_MODE = True  # True = ไม่ส่ง order จริง
```

---

## 🎮 การใช้งาน

### รัน Bot
```powershell
python advanced_scalping_bot.py
```

### หยุด Bot
กด **Ctrl+C** เพื่อหยุดและดู Summary

### Output ที่คาดหวัง
```
============================================================
🚀 Advanced Scalping Bot Starting...
Mode: DEMO (No Real Orders)
Symbol: ETHUSDT | Timeframe: 5m
Strategy: Multi-Indicator Confluence Scalping
============================================================
✅ Bot is running... Press Ctrl+C to stop

[10:15:32] 📊 Signal: BUY | Confluence: 4/4 ✅ | RSI:28 | BB:Lower | MACD:Cross | Vol:High
[10:15:32] 🎯 Entry: 2345.50 | Stop: 2342.45 (-0.3%) | TP: 2358.67 (+0.8%)
[10:15:32] 💡 DEMO: Would place BUY order for 0.142 ETHUSDT
```

---

## 🐛 Troubleshooting

### ❌ Error: "ModuleNotFoundError: No module named 'binance'"
```powershell
pip install binance-connector
```

### ❌ Error: "ModuleNotFoundError: No module named 'pandas'"
```powershell
pip install pandas numpy
```

### ❌ Error: "APIError: Invalid API-key, IP, or permissions"
- ตรวจสอบว่า API Key และ Secret ถูกต้อง
- ตรวจสอบว่าใช้ Testnet URL: `https://testnet.binance.vision`
- Testnet keys ไม่ work กับ Mainnet (และตรงกันข้าม)

### ❌ Error: "Connection refused" หรือ "Network error"
- ตรวจสอบ Internet connection
- ลองรันใหม่อีกครั้ง
- Binance API อาจ busy ชั่วคราว

---

## ⚙️ การปรับแต่ง

### เปลี่ยน Symbol
```python
SYMBOL = "BTCUSDT"   # Bitcoin
SYMBOL = "SOLUSDT"   # Solana
```

### เปลี่ยน Timeframe
```python
TIMEFRAME = "1m"   # 1 นาที (เร็วมาก, trades เยอะ)
TIMEFRAME = "15m"  # 15 นาที (ช้ากว่า, trades น้อยลง)
```

### ปรับความเข้มงวดของสัญญาณ
```python
MIN_CONFLUENCE_SIGNALS = 4  # ต้องมีครบ 4/4 สัญญาณ (เข้มงวด)
MIN_CONFLUENCE_SIGNALS = 2  # แค่ 2/4 สัญญาณ (หลวมกว่า)
```

---

## 📞 Quick Commands

```powershell
# ตรวจสอบ Python
python --version

# ติดตั้ง dependencies
pip install -r requirements.txt

# รัน bot
python advanced_scalping_bot.py

# Update packages
pip install --upgrade binance-connector pandas numpy

# ดู installed packages
pip list
```

---

## ✅ Checklist ก่อนรัน

- [ ] ติดตั้ง Python แล้ว (3.8+)
- [ ] ติดตั้ง dependencies แล้ว (binance-connector, pandas, numpy)
- [ ] มี API Key และ Secret จาก Testnet
- [ ] ใส่ API Keys ใน config แล้ว
- [ ] ตั้ง DEMO_MODE = True (สำหรับการทดสอบ)
- [ ] เชื่อมต่อ Internet ได้

---

## 🎯 Expected First Run

เมื่อรันครั้งแรก bot จะ:
1. เชื่อมต่อกับ Binance Testnet
2. ดึงข้อมูล candles 100 ราคา
3. คำนวณ indicators (RSI, BB, MACD, Volume, ATR)
4. รอสัญญาณ confluence ≥ 3/4
5. แสดง log เมื่อมีสัญญาณ
6. DEMO: แสดง "Would place order" (ไม่ส่งจริง)

**ใช้เวลารอ**: อาจต้องรอ 5-15 นาทีจึงจะเห็นสัญญาณครั้งแรก (ขึ้นกับสภาวะตลาด)

---

## 🎓 Tips สำหรับมือใหม่

1. **เริ่มจาก DEMO Mode**: อย่ารีบใช้เงินจริง
2. **ดู Logs อย่างละเอียด**: เรียนรู้ว่า bot ตัดสินใจยังไง
3. **ทดสอบหลาย Timeframe**: ลอง 1m, 5m, 15m ดูว่าอันไหนเหมาะกับคุณ
4. **ปรับ Parameters**: ทดลองปรับค่าต่างๆ ดูผล
5. **Backtest**: ถ้าเป็นไปได้ ควร backtest ข้อมูลย้อนหลัง
6. **Start Small**: เมื่อจะใช้จริง เริ่มจาก position size เล็กๆ

---

**Happy Trading! 🚀**
