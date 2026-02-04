# 🗄️ Railway Database Setup Guide

## วิธีการเชื่อมต่อและใช้งาน PostgreSQL จาก Railway

---

## 📋 Overview

Railway จะสร้าง PostgreSQL database ให้อัตโนมัติ และใส่ `DATABASE_URL` environment variable ให้โดยอัตโนมัติ

Code ของคุณรองรับแล้ว! ดูที่ [database/db.py](database/db.py#L10-L20):

```python
# Auto-detect Railway PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trading_bot.db")

# Auto-fix Railway URL format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
```

---

## 🚀 Quick Start

### Option 1: ใช้ Railway Database (Production) ✅ แนะนำ

**ไม่ต้องทำอะไรเลย!** Railway จะ:
1. สร้าง PostgreSQL database อัตโนมัติ
2. ใส่ `DATABASE_URL` environment variable
3. App จะเชื่อมต่ออัตโนมัติ

### Option 2: เชื่อมต่อ Railway Database จาก Local

#### Step 1: ดึง DATABASE_URL จาก Railway

```bash
# ติดตั้ง Railway CLI (ถ้ายังไม่มี)
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# ดู environment variables
railway variables

# หรือคัดลอกจาก Railway Dashboard
```

#### Step 2: สร้างไฟล์ .env

```bash
# .env
DATABASE_URL=postgresql://postgres:PASSWORD@HOST:PORT/DATABASE_NAME

# ตัวอย่าง (จาก Railway)
DATABASE_URL=postgresql://postgres:abc123...@containers-us-west-123.railway.app:5432/railway
```

#### Step 3: ทดสอบการเชื่อมต่อ

```bash
# Windows PowerShell
$env:DATABASE_URL="postgresql://..."
python test_railway_connection.py
```

---

## 🔧 สร้าง Test Script

สร้างไฟล์ `test_railway_connection.py`:

```python
"""
Test Railway PostgreSQL Connection
"""
import os
from database.db import engine, init_db
from sqlalchemy import text

print("=" * 60)
print("Testing Railway PostgreSQL Connection")
print("=" * 60)

# Check DATABASE_URL
db_url = os.getenv("DATABASE_URL", "Not set")
if "sqlite" in db_url:
    print("\n⚠️  Using SQLite (Local)")
    print(f"   {db_url}")
else:
    # Mask password in output
    masked_url = db_url.split('@')[1] if '@' in db_url else db_url
    print(f"\n✅ Using PostgreSQL (Railway)")
    print(f"   Host: {masked_url}")

# Test connection
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"\n✅ Connection successful!")
        print(f"   PostgreSQL Version: {version[:50]}...")
        
        # Check tables
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public'
        """))
        tables = [row[0] for row in result]
        
        if tables:
            print(f"\n✅ Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table}")
        else:
            print("\n⚠️  No tables found. Run init_db() to create tables.")
            
except Exception as e:
    print(f"\n❌ Connection failed: {e}")
    print("\n💡 Solutions:")
    print("   1. Check DATABASE_URL is correct")
    print("   2. Verify Railway database is running")
    print("   3. Check firewall/network settings")

# Initialize database if needed
try:
    print("\n" + "=" * 60)
    print("Initializing Database Tables...")
    print("=" * 60)
    init_db()
    print("✅ Database tables created/updated successfully!")
except Exception as e:
    print(f"⚠️  Init DB error (may already exist): {e}")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
```

รันทดสอบ:
```bash
python test_railway_connection.py
```

---

## 📊 Railway Dashboard - จัดการ Database

### 1. ดู Database Info
```
Railway Dashboard → Your Project → PostgreSQL
- Host
- Port
- Database Name
- Username
- Password
```

### 2. Connect ผ่าน Railway CLI
```bash
# Open psql shell
railway psql

# หรือ connect ด้วย connection string
railway connect
```

### 3. Query ข้อมูล
```sql
-- ดู tables ทั้งหมด
\dt

-- ดู users
SELECT * FROM users;

-- ดู configs
SELECT * FROM bot_configs;

-- ดู trades
SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10;
```

---

## 🔐 Environment Variables ใน Railway

Railway จะใส่ให้อัตโนมัติ:
```
DATABASE_URL          (Auto-generated)
PGHOST               (Auto-generated)
PGPORT               (Auto-generated)
PGUSER               (Auto-generated)
PGPASSWORD           (Auto-generated)
PGDATABASE           (Auto-generated)
```

คุณต้องเพิ่มเอง:
```
BINANCE_API_KEY       (Required)
BINANCE_API_SECRET    (Required)
TELEGRAM_BOT_TOKEN    (Optional)
TELEGRAM_CHAT_ID      (Optional)
```

---

## 🛠️ Database Migration (Advanced)

### ใช้ Alembic สำหรับ Schema Changes

#### 1. ติดตั้ง Alembic
```bash
pip install alembic
```

#### 2. Initialize
```bash
alembic init alembic
```

#### 3. แก้ไข `alembic.ini`
```ini
# เปลี่ยนจาก
sqlalchemy.url = driver://user:pass@localhost/dbname

# เป็น (ใช้ environment variable)
# sqlalchemy.url = (comment out)
```

#### 4. แก้ไข `alembic/env.py`
```python
from database.db import DATABASE_URL
from database.models import Base

config.set_main_option('sqlalchemy.url', DATABASE_URL)
target_metadata = Base.metadata
```

#### 5. สร้าง Migration
```bash
# สร้าง migration แรก
alembic revision --autogenerate -m "Initial schema"

# ดู migration file
cat alembic/versions/*.py

# Apply to database
alembic upgrade head
```

#### 6. ใช้งานจริง
```bash
# เมื่อมีการเปลี่ยน models
alembic revision --autogenerate -m "Add new fields"

# Apply changes
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 💾 Backup & Restore

### Backup จาก Railway
```bash
# ผ่าน Railway CLI
railway psql -c "pg_dump railway" > backup.sql

# หรือใช้ pg_dump โดยตรง
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

### Restore
```bash
# Restore จาก backup
railway psql < backup.sql
```

---

## 🔍 Debug Connection Issues

### 1. ตรวจสอบ DATABASE_URL
```python
import os
print(os.getenv("DATABASE_URL"))
```

### 2. Test Direct Connection
```python
from sqlalchemy import create_engine, text

engine = create_engine("postgresql://user:pass@host:port/db")
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print(result.fetchone())
```

### 3. Check Railway Logs
```bash
railway logs
```

### 4. Common Errors

**Error: `no such table: users`**
```bash
# Solution: Initialize database
python -c "from database.db import init_db; init_db()"
```

**Error: `connection refused`**
```bash
# Solution: Check Railway database is running
railway status
```

**Error: `password authentication failed`**
```bash
# Solution: Re-fetch DATABASE_URL from Railway
railway variables
```

---

## 📈 Performance Tips

### 1. Connection Pooling
```python
# database/db.py (already configured)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Verify connections
    pool_size=10,            # Max connections
    max_overflow=20,         # Extra connections
)
```

### 2. Query Optimization
```python
# Use indexes
from sqlalchemy import Index
Index('idx_user_email', User.email)

# Lazy loading vs Eager loading
users = db.query(User).options(joinedload(User.configs)).all()
```

### 3. Monitor Queries
```python
# Enable SQL logging
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

---

## 🎯 Production Checklist

- [ ] DATABASE_URL set ใน Railway
- [ ] Database tables initialized (`init_db()`)
- [ ] Connection pooling configured
- [ ] Migrations ready (if using Alembic)
- [ ] Backup strategy in place
- [ ] Monitoring/alerting setup
- [ ] Test connection from Railway app

---

## 🚨 Security Best Practices

1. **ไม่เปิดเผย DATABASE_URL**
   - ใช้ environment variables เสมอ
   - ไม่ commit .env เข้า git

2. **ใช้ SSL Connection**
   ```python
   # Railway จัดการให้อัตโนมัติ
   engine = create_engine(DATABASE_URL + "?sslmode=require")
   ```

3. **Rotate Passwords**
   - เปลี่ยน password เป็นระยะ
   - ทำผ่าน Railway Dashboard

---

## 📞 Need Help?

**Railway Docs:** https://docs.railway.app/databases/postgresql  
**SQLAlchemy Docs:** https://docs.sqlalchemy.org/  
**Alembic Docs:** https://alembic.sqlalchemy.org/

---

**✅ สรุป:** Code ของคุณพร้อมใช้กับ Railway PostgreSQL แล้ว! แค่ deploy ไป Railway ก็จะทำงานอัตโนมัติ 🚀
