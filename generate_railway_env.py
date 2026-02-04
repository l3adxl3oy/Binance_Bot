"""
🚀 Railway Environment Setup Script
สคริปต์สำหรับตั้งค่า environment variables ใน Railway อัตโนมัติ
"""
import secrets
import string

print("=" * 70)
print("    Railway Environment Variables Generator")
print("=" * 70)

# Generate secure random strings
def generate_secret(length=32):
    """Generate a secure random string"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Generate JWT secret
jwt_secret = generate_secret(48)
print("\n[1/2] Generated JWT_SECRET_KEY:")
print(f"      {jwt_secret}")

# Generate encryption key
encryption_key = generate_secret(32)
print("\n[2/2] Generated ENCRYPTION_KEY:")
print(f"      {encryption_key}")

print("\n" + "=" * 70)
print("    Copy these to Railway Dashboard")
print("=" * 70)

railway_vars = f"""
# ==================== COPY TO RAILWAY ====================

JWT_SECRET_KEY={jwt_secret}
ENCRYPTION_KEY={encryption_key}

# Binance API (ใส่ API keys จริงของคุณ)
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here

# Binance Network
BINANCE_BASE_URL=https://testnet.binance.vision

# Telegram (optional)
TELEGRAM_ENABLED=false
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# ==================== END ====================
"""

print(railway_vars)

# Save to file
output_file = ".env.railway.generated"
with open(output_file, "w") as f:
    f.write(railway_vars)

print(f"\n[SUCCESS] Variables saved to: {output_file}")
print("\nNext steps:")
print("  1. Copy the variables above")
print("  2. Go to Railway Dashboard → Your Project → Variables")
print("  3. Click 'New Variable' and paste each one")
print("  4. Replace BINANCE_API_KEY and BINANCE_API_SECRET with your real keys")
print("  5. Save and redeploy")
print("\n" + "=" * 70)
