# Telegram Setup Guide (v2.0)

## ขั้นตอนเปิดใช้งาน Telegram Control

### 1) สร้าง Telegram Bot
1. เปิด Telegram แล้วค้นหา **@BotFather**
2. พิมพ์คำสั่ง /newbot
3. ตั้งชื่อ bot ตามต้องการ (เช่น My Trading Bot)
4. ตั้ง username ของ bot (ต้องลงท้ายด้วย bot เช่น my_trading_bot)
5. **บันทึก TOKEN** ที่ @BotFather ให้มา

### 2) หา Chat ID ของคุณ
1. ส่งข้อความอะไรก็ได้ไปหา bot ของคุณ (เช่น /start)
2. รันสคริปต์หา Chat ID:
   ```powershell
   python get_chat_id.py
   ```
3. ใส่ TOKEN ของ bot เมื่อถูกถาม
4. **บันทึก Chat ID** ที่แสดงออกมา

### 3) อัปเดตค่าใน daily_scalping_bot.py
เปิดไฟล์และแก้ไขส่วน Config:
```python
# Telegram Bot (ใส่ค่าจาก @BotFather)
TELEGRAM_ENABLED = True
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"
```

### 4) รันบอท
```powershell
python daily_scalping_bot.py
```

เมื่อ bot เริ่มทำงาน คุณจะได้รับข้อความแจ้งเตือนใน Telegram

---

## คำสั่ง Telegram ทั้งหมด

### ✅ ควบคุมบอท
- /start - เริ่มบอทและแสดงคำสั่งพื้นฐาน
- /stop - หยุดบอทและปิดออเดอร์ทั้งหมดอย่างปลอดภัย
- /pause - หยุดเปิดออเดอร์ใหม่ชั่วคราว
- /resume - เทรดต่อหลังหยุดชั่วคราว
- /help - แสดงคำสั่งทั้งหมด

### 📊 ข้อมูลการเทรด
- /status - สถานะปัจจุบัน (balance, positions, daily P&L)
- /balance - ยอดเงินปัจจุบันและกำไร/ขาดทุน
- /positions หรือ /pos - รายการออเดอร์ที่เปิดอยู่
- /trades - เทรดล่าสุด 5 รายการ
- /stats - สถิติละเอียด (win rate, avg win/loss, per-symbol)

### 🔍 การวิเคราะห์
- /symbols - รายชื่อเหรียญที่ active + momentum score
- /price [SYMBOL] - ราคาปัจจุบัน (เช่น /price BTC)
- /logic [SYMBOL] - วิเคราะห์สัญญาณล่าสุดแบบละเอียด
- /settings - การตั้งค่าบอททั้งหมด

---

## ตัวอย่างข้อความแจ้งเตือน

### เมื่อบอทเริ่มทำงาน
```
🤖 Trading Bot เริ่มทำงานแล้ว!
Use /help for commands
```

### เมื่อเช็คสถานะด้วย /status
```
🤖 Daily Scalping Bot v2.0

⚡ Status: ✅ RUNNING
🎮 Trading: ▶️ ACTIVE
🎮 Mode: DEMO
💰 Balance: $100.53
📊 Daily P&L: +0.53%

📈 Positions: 1/10
🎯 Active Symbols: 10/20
📊 Win Rate: 66.7%
```

---

## Troubleshooting

### Bot ไม่ตอบใน Telegram
1. ตรวจสอบว่าใส่ TOKEN และ CHAT_ID ถูกต้อง
2. ตรวจสอบว่า TELEGRAM_ENABLED = True
3. ตรวจสอบว่าส่งข้อความไปหา bot แล้ว
4. ดู log ใน terminal มี error หรือไม่

### Bot ตอบว่า Unauthorized
- ตรวจสอบว่า CHAT_ID ที่ใส่ตรงกับ chat ที่ส่งคำสั่ง

### หา Chat ID ไม่เจอ
- รันสคริปต์ python get_chat_id.py อีกครั้ง
- ตรวจสอบว่าส่งข้อความไปหา bot แล้ว

---

## Security Tips
1. **ไม่ควรแชร์ TOKEN** ให้คนอื่น
2. **ไม่ควร push TOKEN ขึ้น GitHub**
3. ถ้า TOKEN หลุด ให้ไปที่ @BotFather แล้วพิมพ์ /revoke เพื่อสร้าง token ใหม่
4. ตรวจสอบว่า command มาจาก CHAT_ID ที่ถูกต้อง

---

## Ready!
ตอนนี้คุณสามารถควบคุม bot จากมือถือผ่าน Telegram ได้แล้ว
