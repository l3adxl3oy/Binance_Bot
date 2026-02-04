# 🚀 Railway.app Deployment Guide

## การ Deploy Trading Bot ไปยัง Railway.app

### 📋 สิ่งที่จะได้

- ✅ Web Dashboard ที่รันบน Cloud 24/7
- ✅ PostgreSQL Database (ฟรี 512MB)
- ✅ Auto-deploy จาก GitHub
- ✅ HTTPS SSL certificate อัตโนมัติ
- ✅ Environment variables ปลอดภัย
- ✅ $5 free credit/month

---

## 🔧 ขั้นตอนการ Deploy

### **Step 1: สร้างบัญชี Railway**

1. ไปที่ https://railway.app
2. Sign up ด้วย GitHub account
3. Verify email

### **Step 2: Push โค้ดไปยัง GitHub**

```bash
# Initialize git (ถ้ายังไม่ได้ทำ)
cd C:\Users\Admin\Documents\Binance_Bot
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Railway deployment ready"

# Create GitHub repository แล้ว push
git remote add origin https://github.com/YOUR_USERNAME/binance-bot.git
git branch -M main
git push -u origin main
```

### **Step 3: สร้าง Project บน Railway**

1. Login เข้า Railway Dashboard
2. คลิก **"New Project"**
3. เลือก **"Deploy from GitHub repo"**
4. เลือก repository **binance-bot**
5. Railway จะ auto-detect และเริ่ม deploy

### **Step 4: เพิ่ม PostgreSQL Database**

1. ใน Project dashboard คลิก **"+ New"**
2. เลือก **"Database"** → **"Add PostgreSQL"**
3. Railway จะสร้าง database และ set `DATABASE_URL` อัตโนมัติ

### **Step 5: ตั้งค่า Environment Variables**

ใน Railway Dashboard → Settings → Variables เพิ่ม:

```env
# Binance API (ใช้ Testnet ก่อน!)
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_secret_here
BINANCE_BASE_URL=https://testnet.binance.vision

# Telegram (optional)
TELEGRAM_ENABLED=false
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# App settings
DEMO_MODE=true
PORT=8000
```

**⚠️ สำคัญ:** เริ่มด้วย Testnet เสมอ! อย่าใช้ API จริงทันที

### **Step 6: Deploy และทดสอบ**

1. Railway จะ deploy อัตโนมัติ
2. รอ 2-3 นาที
3. คลิก **"Open App"** เพื่อดู Dashboard
4. URL จะเป็น: `https://your-app.railway.app`

---

## 🎛️ การใช้งาน Dashboard

### **เข้าถึง Dashboard:**
```
https://your-app.railway.app
```

### **Features:**
- 🟢 **Start Bot** - เริ่ม Trading Bot
- 🔴 **Stop Bot** - หยุด Bot
- 📊 **Real-time Stats** - ดูสถิติแบบ Real-time
- 📜 **Live Logs** - ดู logs สด
- 🔌 **WebSocket** - อัพเดทข้อมูลทุก 5 วินาที

---

## 🔐 Security Best Practices

### **1. ปกป้อง API Keys:**
```env
# ✅ ใช้ Environment Variables (ไม่ hard-code ในโค้ด)
# ✅ ใช้ IP Whitelist บน Binance
# ✅ จำกัด permissions (Spot Trading only, NO Withdraw)
```

### **2. ใช้ Testnet ก่อน:**
```env
BINANCE_BASE_URL=https://testnet.binance.vision
DEMO_MODE=true
```

### **3. Monitor Logs:**
```bash
# ดู logs แบบ real-time
railway logs
```

---

## 📊 Database Schema (PostgreSQL)

Railway สร้าง tables อัตโนมัติ:

```
✅ users - User accounts
✅ bot_configs - Bot settings per user
✅ trades - Trading history
✅ daily_performance - Daily stats
✅ alerts - System notifications
✅ market_data_cache - Cached market data
```

### **เข้าถึง Database:**
```bash
# Connect ด้วย Railway CLI
railway connect postgres

# หรือใช้ connection string จาก Dashboard
postgresql://user:pass@host:port/dbname
```

---

## 🔄 Auto-Deploy Process

### **Workflow:**
```
1. คุณ push code ไปยัง GitHub (main branch)
   ↓
2. Railway detect changes อัตโนมัติ
   ↓
3. Build ด้วย requirements.txt
   ↓
4. Run: python app.py
   ↓
5. Health check: /api/health
   ↓
6. ✅ Deployed!
```

### **ตัวอย่างการอัพเดท:**
```bash
# แก้ไขโค้ด
vim app.py

# Commit
git add .
git commit -m "Update dashboard UI"

# Push → Auto-deploy!
git push origin main
```

---

## 🐛 Troubleshooting

### **ปัญหา: Bot ไม่ start**
```bash
# ดู logs
railway logs

# ตรวจสอบ environment variables
railway variables
```

### **ปัญหา: Database connection failed**
```bash
# ตรวจสอบว่า PostgreSQL running
railway status

# Restart database
railway restart
```

### **ปัญหา: Out of memory**
```
# Upgrade plan (ถ้าจำเป็น)
Railway dashboard → Settings → Upgrade
```

---

## 💰 ค่าใช้จ่าย

### **Free Tier:**
- $5 credit/month
- 512MB RAM
- 1GB Disk
- 100GB Network
- **เพียงพอสำหรับ 1-2 bots**

### **ใช้เกิน Free Tier:**
- $0.000231/GB-minute (RAM)
- $0.01/GB (Network egress)
- ประมาณ **$10-20/month** สำหรับ production

---

## 🚀 Next Steps

### **1. เพิ่ม Authentication:**
```python
# Add JWT authentication
from fastapi.security import OAuth2PasswordBearer
```

### **2. เพิ่ม Frontend Framework:**
```bash
# React dashboard
npx create-react-app dashboard
```

### **3. Set up Custom Domain:**
```
# Railway Settings → Domains
your-domain.com → CNAME → your-app.railway.app
```

### **4. Monitoring & Alerts:**
```bash
# Add Sentry.io for error tracking
pip install sentry-sdk
```

---

## 📞 Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: https://github.com/YOUR_REPO/issues

---

## ✅ Checklist สำหรับ Production

- [ ] เปลี่ยนจาก Testnet → Live API
- [ ] Set `DEMO_MODE=false`
- [ ] เพิ่ม Authentication (Login system)
- [ ] Set up custom domain + SSL
- [ ] Enable database backups
- [ ] Set up monitoring (Sentry)
- [ ] Configure auto-restart on errors
- [ ] Add rate limiting
- [ ] Test thoroughly on testnet first!
- [ ] Start with small capital ($100-500)

---

**🎉 ยินดีด้วย! คุณพร้อม deploy แล้ว**

```bash
# คำสั่งสุดท้าย
git push origin main
# แล้วเปิด Railway dashboard ดู magic! ✨
```
