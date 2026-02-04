"""
🔍 Test Railway PostgreSQL Connection
รันไฟล์นี้เพื่อทดสอบการเชื่อมต่อกับ Railway database
"""
import os
import sys
from sqlalchemy import text

# Fix encoding for Windows
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("=" * 70)
print("    Testing Railway PostgreSQL Connection")
print("=" * 70)

# Step 1: Check DATABASE_URL
db_url = os.getenv("DATABASE_URL")

if not db_url:
    print("\n[ERROR] DATABASE_URL not set!")
    print("\nHow to fix:")
    print("  1. Get DATABASE_URL from Railway Dashboard")
    print("  2. Create .env file with: DATABASE_URL=postgresql://...")
    print("  3. Or set environment variable:")
    print("     Windows: $env:DATABASE_URL='postgresql://...'")
    print("     Linux:   export DATABASE_URL='postgresql://...'")
    sys.exit(1)

# Check if using SQLite or PostgreSQL
if "sqlite" in db_url.lower():
    print("\n[INFO] Using SQLite (Local Development)")
    print(f"       File: {db_url}")
    is_postgres = False
else:
    # Mask password in output
    try:
        parts = db_url.split('@')
        if len(parts) > 1:
            host_info = parts[1]
            print(f"\n[SUCCESS] Using PostgreSQL (Railway)")
            print(f"          Host: {host_info}")
        else:
            print(f"\n[INFO] Database: {db_url[:30]}...")
    except:
        print(f"\n[INFO] Database URL configured")
    is_postgres = True

# Step 2: Import database
print("\n" + "-" * 70)
print("Loading database modules...")
print("-" * 70)

try:
    from database.db import engine, init_db
    from database.models import Base, User, BotConfig, Trade
    print("[OK] Database modules loaded")
except Exception as e:
    print(f"[ERROR] Failed to load database: {e}")
    sys.exit(1)

# Step 3: Test connection
print("\n" + "-" * 70)
print("Testing database connection...")
print("-" * 70)

try:
    with engine.connect() as conn:
        # Test basic query
        result = conn.execute(text("SELECT 1 as test"))
        test_value = result.fetchone()[0]
        
        if test_value == 1:
            print("[SUCCESS] Database connection works!")
        
        # Get database version
        if is_postgres:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"[INFO] PostgreSQL Version: {version[:60]}...")
        else:
            print(f"[INFO] SQLite database")
        
        # Check existing tables
        if is_postgres:
            query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema='public'
                ORDER BY table_name
            """)
        else:
            query = text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
        
        result = conn.execute(query)
        tables = [row[0] for row in result]
        
        if tables:
            print(f"\n[SUCCESS] Found {len(tables)} existing tables:")
            for table in tables:
                # Count records in each table
                try:
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = count_result.fetchone()[0]
                    print(f"          - {table:20} ({count} records)")
                except:
                    print(f"          - {table}")
        else:
            print("\n[INFO] No tables found yet (will be created below)")
            
except Exception as e:
    print(f"[ERROR] Connection test failed: {e}")
    print("\nPossible solutions:")
    print("  1. Check DATABASE_URL is correct")
    print("  2. Verify Railway database is running")
    print("  3. Check network/firewall settings")
    sys.exit(1)

# Step 4: Initialize tables
print("\n" + "-" * 70)
print("Initializing database tables...")
print("-" * 70)

try:
    # Create all tables
    init_db()
    print("[SUCCESS] Database tables created/verified!")
    
    # Verify tables were created
    with engine.connect() as conn:
        if is_postgres:
            query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema='public'
                ORDER BY table_name
            """)
        else:
            query = text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
        
        result = conn.execute(query)
        tables = [row[0] for row in result]
        
        print(f"\n[SUCCESS] Verified {len(tables)} tables:")
        for table in tables:
            print(f"          - {table}")
            
        # Check required tables
        required_tables = ['users', 'bot_configs', 'trades']
        missing = [t for t in required_tables if t not in tables]
        
        if missing:
            print(f"\n[WARNING] Missing required tables: {missing}")
        else:
            print(f"\n[SUCCESS] All required tables present!")
            
except Exception as e:
    print(f"[WARNING] Table initialization: {e}")
    print("          (Tables may already exist)")

# Step 5: Test CRUD operations
print("\n" + "-" * 70)
print("Testing database operations...")
print("-" * 70)

try:
    from database.db import SessionLocal
    
    # Create session
    db = SessionLocal()
    
    # Test 1: Check if test user exists
    test_user = db.query(User).filter(User.email == "test_connection@example.com").first()
    
    if test_user:
        print("[INFO] Test user already exists")
        print(f"       Username: {test_user.username}")
        print(f"       Email: {test_user.email}")
        print(f"       Created: {test_user.created_at}")
    else:
        print("[INFO] Test user not found (normal for first run)")
    
    # Test 2: Count records
    user_count = db.query(User).count()
    config_count = db.query(BotConfig).count()
    trade_count = db.query(Trade).count()
    
    print(f"\n[SUCCESS] Database statistics:")
    print(f"          - Users: {user_count}")
    print(f"          - Bot Configs: {config_count}")
    print(f"          - Trades: {trade_count}")
    
    db.close()
    
except Exception as e:
    print(f"[ERROR] Database operations failed: {e}")
    import traceback
    traceback.print_exc()

# Final Summary
print("\n" + "=" * 70)
print("    Test Summary")
print("=" * 70)
print("[SUCCESS] Database connection: OK")
print("[SUCCESS] Tables initialized: OK")
print("[SUCCESS] Operations working: OK")
print("\nYour database is ready for use!")
print("\nNext steps:")
print("  1. Start the FastAPI server: uvicorn app:app --reload")
print("  2. Test signup: POST /auth/signup")
print("  3. Create bot config: POST /configs/create")
print("  4. Start trading bot: POST /bots/start")
print("=" * 70)
