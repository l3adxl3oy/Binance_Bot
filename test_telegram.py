"""
🧪 Telegram Setup & Test Script
ทดสอบการส่งข้อความผ่าน Telegram Bot
"""

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import Config
import requests

def test_telegram():
    """ทดสอบการส่งข้อความ Telegram"""
    
    print("="*60)
    print("📱 TELEGRAM BOT TEST".center(60))
    print("="*60)
    
    # Check configuration
    print("\n1️⃣ ตรวจสอบการตั้งค่า:")
    print(f"   TELEGRAM_ENABLED: {Config.TELEGRAM_ENABLED}")
    print(f"   BOT_TOKEN: {'✅ Set' if Config.TELEGRAM_BOT_TOKEN and Config.TELEGRAM_BOT_TOKEN != 'YOUR_TELEGRAM_BOT_TOKEN' else '❌ Not Set'}")
    print(f"   CHAT_ID: {'✅ Set' if Config.TELEGRAM_CHAT_ID and Config.TELEGRAM_CHAT_ID != 'YOUR_TELEGRAM_CHAT_ID' else '❌ Not Set'}")
    
    if not Config.TELEGRAM_ENABLED:
        print("\n⚠️  Telegram ยังไม่ได้เปิดใช้งาน!")
        print("   แก้ไขในไฟล์ .env: TELEGRAM_ENABLED=true")
        return
    
    if Config.TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("\n❌ ยังไม่ได้ตั้งค่า BOT_TOKEN!")
        print("\n📖 วิธีตั้งค่า:")
        print("   1. เปิด Telegram → ค้นหา @BotFather")
        print("   2. ส่งคำสั่ง /newbot")
        print("   3. ตั้งชื่อ bot และ username")
        print("   4. คัดลอก TOKEN ที่ได้มา")
        print("   5. แก้ไขใน .env: TELEGRAM_BOT_TOKEN=<your_token>")
        return
    
    if Config.TELEGRAM_CHAT_ID == "YOUR_TELEGRAM_CHAT_ID":
        print("\n❌ ยังไม่ได้ตั้งค่า CHAT_ID!")
        print("\n📖 วิธีหา CHAT_ID:")
        print("   1. ค้นหา bot ของคุณใน Telegram")
        print("   2. ส่งข้อความ /start")
        print("   3. รันคำสั่ง: python utils/get_chat_id.py")
        print("   4. คัดลอก CHAT_ID ที่ได้มา")
        print("   5. แก้ไขใน .env: TELEGRAM_CHAT_ID=<your_chat_id>")
        return
    
    # Test sending message
    print("\n2️⃣ ทดสอบส่งข้อความ...")
    
    try:
        url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
        
        test_message = """
🧪 <b>Telegram Bot Test</b>

✅ การตั้งค่าถูกต้อง!
🤖 Bot พร้อมใช้งาน

<b>ฟีเจอร์ที่มี:</b>
• ✅ การแจ้งเตือนเมื่อเปิด/ปิดออเดอร์
• ✅ คำสั่งควบคุม Bot (/status, /balance, etc.)
• ✅ สรุปผลการเทรดรายวัน

<i>ทดสอบสำเร็จ! 🎉</i>
"""
        
        data = {
            "chat_id": Config.TELEGRAM_CHAT_ID,
            "text": test_message.strip(),
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("   ✅ ส่งข้อความสำเร็จ!")
                print("\n3️⃣ ตรวจสอบใน Telegram:")
                print("   📱 เปิด Telegram และดูข้อความทดสอบ")
                print("\n✅ Telegram Bot พร้อมใช้งาน!")
                print("\n💡 คำสั่งที่ใช้ได้:")
                print("   /start  - เริ่มบอท")
                print("   /status - ดูสถานะ")
                print("   /balance - ดูยอดเงิน")
                print("   /positions - ดูออเดอร์")
                print("   /help - ดูคำสั่งทั้งหมด")
                return True
            else:
                print(f"   ❌ API Error: {result}")
                return False
        else:
            print(f"   ❌ HTTP Error {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 401:
                print("\n   💡 BOT_TOKEN ไม่ถูกต้อง - ตรวจสอบใหม่")
            elif response.status_code == 400:
                print("\n   💡 CHAT_ID อาจไม่ถูกต้อง - ตรวจสอบใหม่")
            
            return False
            
    except requests.exceptions.Timeout:
        print("   ❌ Timeout - ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("\n")
    success = test_telegram()
    print("\n" + "="*60)
    
    if success:
        print("\n🎉 Setup สำเร็จ! พร้อมใช้งาน Bot")
    else:
        print("\n⚠️  กรุณาแก้ไขปัญหาตามคำแนะนำด้านบน")
    
    print("\n")
