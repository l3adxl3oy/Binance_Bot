# 🎯 คัดลอกค่าเหล่านี้ไปใส่ใน Railway Environment Variables

## Required Variables (บังคับต้องมี):

```env
SECRET_KEY=pnQwDb76Dkjs8w3Z0Qw47BCR6fIpbkcIpK00pjBxvD8
ENCRYPTION_KEY=A2NOIsMYMXnppQIK2Fcao4Lc8ViGq09zixKAd02XXdg
DEMO_MODE=True
ENVIRONMENT=production
PORT=8000
```

## Database (Railway สร้างให้อัตโนมัติ):
```env
DATABASE_URL=<Railway-จะ-generate-ให้-เอง>
```

## Optional - Binance API (ถ้าต้องการทดสอบ bot):
```env
API_KEY=your_binance_api_key
API_SECRET=your_binance_api_secret
USE_TESTNET=True
```

## Optional - Telegram Alerts:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

---

## 📝 ขั้นตอนการใส่ค่าใน Railway:

1. ไปที่ Railway Dashboard → เลือก Project ของคุณ
2. คลิกที่ Web Service → **Variables** tab
3. คลิก **"+ New Variable"**
4. Copy-Paste ค่าแต่ละตัวจากด้านบน
5. คลิก **"Add"** → **"Deploy"**

---

## ⚠️ หมายเหตุสำคัญ:

- **SECRET_KEY** และ **ENCRYPTION_KEY** ถูกสร้างแบบสุ่มสำหรับคุณแล้ว
- **ห้ามแชร์** keys เหล่านี้กับใครก็ตาม
- เก็บไฟล์นี้ไว้ที่ปลอดภัย (ไม่ push ขึ้น GitHub)
- ถ้าต้องการสร้าง keys ใหม่ รันคำสั่ง:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

---

## ✅ Checklist ก่อน Deploy:

- [ ] Copy SECRET_KEY ไปใส่ใน Railway
- [ ] Copy ENCRYPTION_KEY ไปใส่ใน Railway
- [ ] ตั้ง DEMO_MODE=True (สำหรับทดสอบ)
- [ ] เพิ่ม PostgreSQL Database ใน Railway
- [ ] ตรวจสอบ DATABASE_URL ถูกสร้างแล้ว
- [ ] (Optional) ใส่ Binance API keys ถ้าต้องการทดสอบ bot

---

**หลังจากตั้งค่าเสร็จ → Railway จะ Deploy อัตโนมัติ → รอ 2-3 นาที → เข้า URL ที่ได้! 🚀**
