# 🚀 Quick Start - Railway Deployment

## เริ่มต้นใน 5 นาที!

### 📦 **ไฟล์ที่สร้างให้แล้ว:**

```
✅ app.py                  - FastAPI Web Server + Dashboard
✅ railway.toml           - Railway config
✅ Procfile               - Process definition
✅ railway.json           - Deployment settings
✅ requirements.txt       - Dependencies (updated)
✅ database/              - PostgreSQL models
✅ .env.example           - Environment template
✅ .dockerignore          - Ignore files for deployment
✅ docs/RAILWAY_DEPLOY.md - Full guide
```

---

## 🎯 **วิธี Deploy (3 Steps)**

### **Step 1: ทดสอบ Local**

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# แก้ไข .env ใส่ Binance API keys (ใช้ Testnet!)

# Run locally
python app.py

# เปิดเบราว์เซอร์ไปที่:
http://localhost:8000
```

### **Step 2: Push to GitHub**

```bash
# Initialize git (if not done)
git init
git add .
git commit -m "Railway deployment ready"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/binance-bot.git
git branch -M main
git push -u origin main
```

### **Step 3: Deploy to Railway**

1. ไปที่ https://railway.app
2. Login with GitHub
3. New Project → Deploy from GitHub repo
4. เลือก repo ของคุณ
5. Add PostgreSQL database
6. Set Environment Variables (ใน Settings):
   ```
   BINANCE_API_KEY=xxx
   BINANCE_API_SECRET=xxx
   BINANCE_BASE_URL=https://testnet.binance.vision
   DEMO_MODE=true
   ```
7. รอ deploy เสร็จ (2-3 นาที)
8. เปิด URL ที่ได้!

---

## 🎨 **Dashboard Features**

เมื่อเปิด Dashboard คุณจะเห็น:

- 🟢 **Start/Stop Bot** - ควบคุม Trading Bot
- 📊 **Real-time Stats** - กำไร/ขาดทุน, จำนวนเทรด
- 📈 **Active Positions** - ดู positions ที่เปิดอยู่
- 📜 **Live Logs** - ดู logs แบบทันที
- 🔌 **WebSocket** - อัพเดททุก 5 วินาที

---

## 🔑 **API Endpoints**

```
GET  /                   - Dashboard (HTML)
GET  /api/health         - Health check
GET  /api/stats          - Current statistics
GET  /api/config         - Bot configuration
POST /api/bot/start      - Start trading bot
POST /api/bot/stop       - Stop trading bot
WS   /ws                 - WebSocket (real-time)
```

### **ตัวอย่างการใช้:**

```bash
# Start bot
curl -X POST https://your-app.railway.app/api/bot/start \
  -H "Content-Type: application/json" \
  -d '{"bot_type": "aggressive"}'

# Check stats
curl https://your-app.railway.app/api/stats

# Stop bot
curl -X POST https://your-app.railway.app/api/bot/stop
```

---

## 📊 **Database Schema (PostgreSQL)**

Railway สร้างอัตโนมัติ:

| Table | Purpose |
|-------|---------|
| `users` | User accounts (สำหรับ multi-user) |
| `bot_configs` | Bot settings per user |
| `trades` | Trading history |
| `daily_performance` | Daily stats summary |
| `alerts` | System notifications |
| `market_data_cache` | Cached market data |

---

## 🔐 **Security Checklist**

- [ ] ใช้ .env สำหรับ API keys (ห้าม hard-code)
- [ ] เริ่มด้วย Testnet เสมอ
- [ ] ตั้ง IP Whitelist บน Binance
- [ ] จำกัด API permissions (Spot only, NO Withdraw)
- [ ] Set `DEMO_MODE=true` ตอนทดสอบ
- [ ] ใส่ `.env` ใน `.gitignore`

---

## 💰 **ค่าใช้จ่าย Railway**

| Resource | Free Tier | Cost (if exceeded) |
|----------|-----------|-------------------|
| Credit | $5/month | - |
| RAM | 512MB | $0.000231/GB-min |
| Disk | 1GB | Included |
| Network | 100GB | $0.01/GB |

**คาดการณ์:** ~$0-10/month สำหรับ bot 1 ตัว

---

## 🐛 **Troubleshooting**

### Bot ไม่ start:
```bash
# ดู logs
railway logs

# หรือใน Dashboard → Deployments → Logs
```

### Database error:
```bash
# Restart service
railway restart

# หรือ re-deploy
git commit --allow-empty -m "Trigger deploy"
git push
```

### Port error:
```bash
# Railway ใช้ PORT environment variable
# app.py รับค่าจาก os.getenv("PORT", 8000) อัตโนมัติ
```

---

## 🚀 **Next Steps**

### 1. เพิ่ม Authentication:
```python
# ใน app.py เพิ่ม JWT
from fastapi.security import OAuth2PasswordBearer
```

### 2. Custom Domain:
```
# Railway Settings → Domains
Add: your-domain.com
```

### 3. Monitoring:
```bash
# Add Sentry
pip install sentry-sdk
```

### 4. Production Ready:
```env
DEMO_MODE=false
BINANCE_BASE_URL=https://api.binance.com
```

---

## 📞 **Support**

- 📚 Full Guide: [docs/RAILWAY_DEPLOY.md](docs/RAILWAY_DEPLOY.md)
- 🌐 Railway Docs: https://docs.railway.app
- 💬 Railway Discord: https://discord.gg/railway

---

## ✅ **ทดสอบก่อน Deploy**

```bash
# Test locally
python app.py

# Test API
curl http://localhost:8000/api/health

# Test WebSocket (ใน browser console)
ws = new WebSocket("ws://localhost:8000/ws")
ws.onmessage = (e) => console.log(e.data)
```

---

**🎉 Happy Trading!**

```
คำเตือน: Trading มีความเสี่ยง ทดสอบใน Testnet ก่อนเสมอ!
ไม่รับประกันผลกำไร ใช้งานด้วยความระมัดระวัง
```
