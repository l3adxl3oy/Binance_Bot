# 🚀 Railway Deployment Guide - Multi-User Trading Bot

## Prerequisites
1. Railway Account: https://railway.app
2. GitHub Account (for connecting repo)
3. PostgreSQL Database on Railway

---

## 📋 Step-by-Step Deployment

### **Step 1: Prepare Your Repository**

Push your code to GitHub:
```bash
git init
git add .
git commit -m "Initial commit - Multi-user trading bot"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

---

### **Step 2: Create Railway Project**

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub
5. Select your trading bot repository

---

### **Step 3: Add PostgreSQL Database**

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway will automatically create and provision the database
4. Copy the `DATABASE_URL` from the PostgreSQL service (it's auto-generated)

---

### **Step 4: Configure Environment Variables**

In your Railway project settings → **Variables**, add:

#### **Required Variables:**
```env
# Database (automatically set by Railway, but verify)
DATABASE_URL=<railway-provides-this>

# Security (CHANGE THESE!)
SECRET_KEY=<generate-random-32-char-string>
ENCRYPTION_KEY=<generate-random-32-char-string>

# Binance API (optional - users will set their own)
# These are defaults if you want admin bot
API_KEY=your_binance_api_key
API_SECRET=your_binance_api_secret

# Application Settings
DEMO_MODE=True
ENVIRONMENT=production
PORT=8000

# Telegram (optional)
TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>
TELEGRAM_CHAT_ID=<your-telegram-chat-id>
```

#### **Generate SECRET_KEY and ENCRYPTION_KEY:**
```bash
# Run locally or use online generator
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

### **Step 5: Deploy Configuration**

Railway should auto-detect your `Procfile` and `railway.json`. Verify:

**Procfile:**
```
web: python app.py
```

**railway.json:**
```json
{
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "python app.py",
    "healthcheckPath": "/api/health",
    "restartPolicyType": "always"
  }
}
```

---

### **Step 6: Initialize Database Schema**

After first deployment:

1. Go to Railway project → Your web service
2. Click **"Deployments"** → Latest deployment → **"View Logs"**
3. Database tables should auto-create on first run
4. Verify logs show: `✅ Database tables created successfully`

**OR manually via Railway CLI:**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and link project
railway login
railway link

# Run migration
railway run alembic upgrade head
```

---

### **Step 7: Access Your Application**

1. Railway will provide a public URL like:
   ```
   https://your-app.up.railway.app
   ```

2. Visit the URL → You should see login page
3. Create first user account
4. Configure your bot with YAML configs
5. Start trading! 🚀

---

## 🔒 Security Checklist

- [ ] Changed `SECRET_KEY` to random value
- [ ] Changed `ENCRYPTION_KEY` to random value
- [ ] Set `DEMO_MODE=True` for testing (change to `False` for real trading)
- [ ] Configured Binance API keys per user (not in env vars)
- [ ] Enabled Railway's built-in HTTPS
- [ ] Review CORS settings in `app.py`

---

## 📊 Monitoring & Logs

**View Logs:**
- Railway Dashboard → Your Service → Deployments → View Logs

**Health Check:**
```
GET https://your-app.up.railway.app/api/health
```

**WebSocket Logs:**
```javascript
ws://your-app.up.railway.app/ws
```

---

## 🛠️ Troubleshooting

### Database Connection Issues
- Verify `DATABASE_URL` is set correctly
- Check PostgreSQL service is running
- Ensure `psycopg2-binary` is in requirements.txt

### Import Errors
- Check all dependencies are in `requirements.txt`
- Rebuild: Railway → Settings → Redeploy

### Port Issues
- Railway auto-assigns `PORT` env variable
- `app.py` uses `int(os.getenv("PORT", 8000))`

### Bot Not Starting
- Check logs for errors
- Verify API keys are encrypted correctly
- Ensure configs are activated per user

---

## 🔄 Updates & Redeployment

Railway auto-deploys on every push to `main` branch:

```bash
git add .
git commit -m "Update bot logic"
git push origin main
```

Railway will automatically:
1. Pull latest code
2. Rebuild container
3. Run migrations
4. Restart service

---

## 💰 Cost Optimization

**Railway Free Tier:**
- $5 free credit/month
- Web service: ~$5-10/month
- PostgreSQL: ~$5/month

**Recommendations:**
- Use Railway's sleep feature for dev environments
- Scale down database for small user base
- Monitor usage in Railway dashboard

---

## 🎯 Post-Deployment Steps

1. **Test Complete Flow:**
   - Signup → Login → Create Config → Activate → Start Bot

2. **Monitor First Trades:**
   - Watch logs for trading activity
   - Verify WebSocket updates work
   - Check database for trade records

3. **User Onboarding:**
   - Share application URL
   - Provide setup instructions
   - Guide API key configuration

---

## 📞 Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Bot Issues: Check logs and README.md

---

**Your multi-user trading bot is now LIVE on Railway! 🎉**
