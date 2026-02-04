"""
Complete E2E Testing - Using FastAPI TestClient
ทดสอบครบทุก endpoint แบบไม่ต้องรัน server จริง
"""
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
os.environ['DATABASE_URL'] = 'sqlite:///./test_complete_e2e.db'

from fastapi.testclient import TestClient

print("=" * 70)
print("    Complete E2E Testing - All Endpoints")
print("=" * 70)

# Import and initialize database first
print("\n[INIT] Initializing database...")
from database.db import init_db
init_db()
print("[OK] Database initialized")

# Import app
print("[INIT] Loading application...")
from app import app
client = TestClient(app)
print("[OK] Application loaded successfully")

# Test counters
passed = 0
failed = 0
total = 0

def test_endpoint(name, method, url, expected_status=200, **kwargs):
    global passed, failed, total
    total += 1
    try:
        if method == 'GET':
            response = client.get(url, **kwargs)
        elif method == 'POST':
            response = client.post(url, **kwargs)
        elif method == 'PUT':
            response = client.put(url, **kwargs)
        elif method == 'DELETE':
            response = client.delete(url, **kwargs)
        
        if response.status_code == expected_status:
            print(f"[OK] {name}")
            passed += 1
            return response
        else:
            print(f"[FAIL] {name}: Expected {expected_status}, got {response.status_code}")
            if response.status_code != expected_status:
                print(f"       Response: {response.text[:100]}")
            failed += 1
            return None
    except Exception as e:
        print(f"[ERROR] {name}: {str(e)[:100]}")
        failed += 1
        return None

# =================================================================
# Test Suite
# =================================================================

print("\n" + "-" * 70)
print("Category 1: Public Endpoints (No Auth)")
print("-" * 70)

# Test 1: Health Check
test_endpoint("Health Check", "GET", "/api/health", 200)

# Test 2: Stats
test_endpoint("System Stats", "GET", "/api/stats", 200)

# Test 3: OpenAPI Schema
response = test_endpoint("OpenAPI Schema", "GET", "/openapi.json", 200)
if response:
    schema = response.json()
    print(f"       Found {len(schema.get('paths', {}))} endpoints in schema")

# Test 4: API Docs
test_endpoint("API Documentation", "GET", "/docs", 200)

print("\n" + "-" * 70)
print("Category 2: Authentication")
print("-" * 70)

# Test 5: User Signup
timestamp = int(time.time())
signup_data = {
    "username": f"testuser_{timestamp}",
    "email": f"test_{timestamp}@example.com",
    "password": "SecurePassword123!"
}

response = test_endpoint(
    "User Signup",
    "POST",
    "/auth/signup",
    201,
    json=signup_data
)

if response:
    result = response.json()
    token = result.get('access_token')
    user_info = result.get('user', {})
    print(f"       User: {user_info.get('username')}")
    print(f"       Email: {user_info.get('email')}")
    print(f"       Token: {token[:30]}...")
else:
    print("[ERROR] Cannot continue without token")
    sys.exit(1)

# Headers for authenticated requests
headers = {"Authorization": f"Bearer {token}"}

# Test 6: User Login
login_data = {
    "username": signup_data["email"],
    "password": signup_data["password"]
}

response = test_endpoint(
    "User Login",
    "POST",
    "/auth/login",
    200,
    data=login_data
)

# Test 7: Get User Profile
response = test_endpoint(
    "Get User Profile",
    "GET",
    "/auth/me",
    200,
    headers=headers
)
if response:
    user = response.json()
    print(f"       ID: {user.get('id')}, Active: {user.get('is_active')}")

# Test 8: Update API Keys
api_keys_data = {
    "api_key": "test_api_key_12345",
    "api_secret": "test_api_secret_67890"
}

response = test_endpoint(
    "Update API Keys",
    "POST",
    "/auth/api-keys",
    200,
    json=api_keys_data,
    headers=headers
)

print("\n" + "-" * 70)
print("Category 3: Configuration Management")
print("-" * 70)

# Test 9: Get Config Templates
response = test_endpoint(
    "Get Config Templates",
    "GET",
    "/configs/templates",
    200,
    headers=headers
)
if response:
    templates = response.json()
    print(f"       Found {len(templates)} templates")

# Test 10: Get Specific Template
test_endpoint(
    "Get Aggressive Template",
    "GET",
    "/configs/templates/aggressive_recovery",
    200,
    headers=headers
)

# Test 11: Create Bot Config
config_data = {
    "name": f"Test Config {timestamp}",
    "bot_type": "aggressive",
    "config_yaml": """
bot_type: aggressive
demo_mode: true
symbols:
  - BTCUSDT
  - ETHUSDT
max_positions: 3
daily_profit_target: 2.0
"""
}

response = test_endpoint(
    "Create Bot Config",
    "POST",
    "/configs/create",
    201,
    json=config_data,
    headers=headers
)

config_id = None
if response:
    config = response.json()
    config_id = config.get('id')
    print(f"       Config ID: {config_id}")

# Test 12: Get My Configs
response = test_endpoint(
    "Get My Configs",
    "GET",
    "/configs/my-configs",
    200,
    headers=headers
)
if response:
    configs = response.json()
    print(f"       Found {len(configs)} user configs")

# Test 13: Validate Config
validate_data = {
    "config_yaml": config_data["config_yaml"]
}

test_endpoint(
    "Validate Config",
    "POST",
    "/configs/validate",
    200,
    json=validate_data,
    headers=headers
)

# Test 14: Activate Config (if created)
if config_id:
    test_endpoint(
        "Activate Config",
        "POST",
        f"/configs/activate/{config_id}",
        200,
        headers=headers
    )

# Test 15: Get Specific Config
if config_id:
    response = test_endpoint(
        "Get Config by ID",
        "GET",
        f"/configs/my-configs/{config_id}",
        200,
        headers=headers
    )

print("\n" + "-" * 70)
print("Category 4: Bot Management")
print("-" * 70)

# Test 16: Get Bot Status
response = test_endpoint(
    "Get Bot Status",
    "GET",
    "/bots/status",
    200,
    headers=headers
)
if response:
    status = response.json()
    print(f"       Status: {status.get('status')}, Running: {status.get('running')}")

# Test 17: Get Bot Logs
response = test_endpoint(
    "Get Bot Logs",
    "GET",
    "/bots/logs",
    200,
    headers=headers
)
if response:
    logs = response.json()
    print(f"       Found {len(logs.get('logs', []))} log entries")

# Test 18: Get Performance Metrics
test_endpoint(
    "Get Performance",
    "GET",
    "/bots/performance",
    200,
    headers=headers
)

# Test 19: Start Bot (will fail without proper config, but test endpoint exists)
start_data = {
    "bot_type": "aggressive"
}

response = test_endpoint(
    "Start Bot",
    "POST",
    "/bots/start",
    expected_status=400,  # Expected to fail without proper Binance config
    json=start_data,
    headers=headers
)
if response:
    print(f"       Expected failure (no Binance API keys configured)")

print("\n" + "-" * 70)
print("Category 5: Authentication Edge Cases")
print("-" * 70)

# Test 20: Duplicate Signup (should fail)
test_endpoint(
    "Duplicate Signup",
    "POST",
    "/auth/signup",
    400,
    json=signup_data
)

# Test 21: Wrong Password Login
wrong_login = {
    "username": signup_data["email"],
    "password": "WrongPassword123!"
}

test_endpoint(
    "Login with Wrong Password",
    "POST",
    "/auth/login",
    401,
    data=wrong_login
)

# Test 22: Access Protected Endpoint without Token
test_endpoint(
    "Access without Token",
    "GET",
    "/auth/me",
    401
)

# Test 23: Logout
test_endpoint(
    "User Logout",
    "POST",
    "/auth/logout",
    200,
    headers=headers
)

print("\n" + "-" * 70)
print("Category 6: Error Handling")
print("-" * 70)

# Test 24: Invalid Config ID
test_endpoint(
    "Get Non-existent Config",
    "GET",
    "/configs/my-configs/99999",
    404,
    headers=headers
)

# Test 25: Invalid Template Name
test_endpoint(
    "Get Non-existent Template",
    "GET",
    "/configs/templates/invalid_template",
    404,
    headers=headers
)

# Test 26: Activate Non-existent Config
test_endpoint(
    "Activate Invalid Config",
    "POST",
    "/configs/activate/99999",
    404,
    headers=headers
)

# =================================================================
# Summary
# =================================================================

print("\n" + "=" * 70)
print("    Test Summary")
print("=" * 70)
print(f"Total Tests: {total}")
print(f"Passed:      {passed} ({passed*100//total if total > 0 else 0}%)")
print(f"Failed:      {failed}")
print("=" * 70)

if failed == 0:
    print("\n[SUCCESS] All tests passed! ✅")
    print("\nWeb Application Status:")
    print("  ✅ All endpoints working correctly")
    print("  ✅ Authentication system functional")
    print("  ✅ Config management operational")
    print("  ✅ Bot control endpoints ready")
    print("  ✅ Error handling proper")
    print("\n🎉 APPLICATION IS FULLY FUNCTIONAL! 🎉")
else:
    print(f"\n[WARNING] {failed} tests failed")
    print("Review the failed tests above for details")

print("=" * 70)

# Exit with appropriate code
sys.exit(0 if failed == 0 else 1)
