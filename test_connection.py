"""Test Binance API Connection"""
from config.config import Config
from binance.spot import Spot

try:
    print("🔄 กำลังเชื่อมต่อ Binance Testnet...")
    print(f"📡 Base URL: {Config.BASE_URL}")
    print(f"🔑 API Key: {Config.API_KEY[:10]}...{Config.API_KEY[-10:]}")
    print()
    
    client = Spot(
        api_key=Config.API_KEY,
        api_secret=Config.API_SECRET,
        base_url=Config.BASE_URL
    )
    
    account = client.account()
    
    print("✅ เชื่อมต่อสำเร็จ!")
    print("="*50)
    print("💰 ยอดเงินใน Spot Wallet:")
    print("="*50)
    
    total_usdt = 0
    has_balance = False
    
    for asset in account['balances']:
        free = float(asset['free'])
        locked = float(asset['locked'])
        total = free + locked
        
        if total > 0:
            has_balance = True
            print(f"  {asset['asset']:10s}: {free:15,.2f} (locked: {locked:,.2f})")
            
            if asset['asset'] == 'USDT':
                total_usdt = total
    
    if not has_balance:
        print("  ⚠️ ไม่มียอดเงินในบัญชี")
        print("  💡 ไปที่ https://testnet.binance.vision/ เพื่อเติมเงินทดสอบ")
    else:
        print("="*50)
        print(f"💵 USDT ที่พร้อมใช้: {total_usdt:,.2f}")
        print()
        print("🎉 บอทพร้อมเทรดแล้ว! รัน RUN_IN_TERMINAL.bat ได้เลย")
    
except Exception as e:
    print("❌ เชื่อมต่อไม่สำเร็จ!")
    print(f"Error: {e}")
    print()
    print("💡 แก้ไข:")
    print("  1. ตรวจสอบ API Key และ Secret ใน .env")
    print("  2. ตรวจสอบว่า API Key ยังใช้ได้อยู่ที่ https://testnet.binance.vision/")
    print("  3. ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต")
