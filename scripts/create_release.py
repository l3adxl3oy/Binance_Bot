import requests
import json
import os

# GitHub Repository Information
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')  # ถ้ามี token ใน environment
REPO_OWNER = "l3adxl3oy"
REPO_NAME = "Binance_Bot"
TAG_NAME = "v3.0.0"

# Release Information
RELEASE_TITLE = "BinanceBot v3.0.0 - Initial Release"
RELEASE_NOTES = """# 🚀 BinanceBot v3.0.0 - Initial Release

## ✨ Features

### 🤖 Trading Bots
- **Daily Scalping Bot** - เหมาะสำหรับมือใหม่ (Target: 2-5% daily)
- **Aggressive Recovery Bot** - เหมาะสำหรับมือโปร (Target: 5-8% daily)

### 🧠 AI Features
- ✅ **Event Manager** - ติดตามข่าวเศรษฐกิจและความเชื่อมั่นตลาด
- ✅ **Risk Manager** - คำนวณความเสี่ยงและจัดการ Position Size
- ✅ **Adaptive Strategy** - ปรับกลยุทธ์ตามสภาพตลาดอัตโนมัติ
- ✅ **Enhanced Alerts** - แจ้งเตือนผ่าน Telegram แบบอัจฉริยะ

### 📊 Trading Features
- Multi-symbol trading (20+ pairs)
- 1-minute scalping strategy
- Multi-indicator confluence
- Smart Martingale recovery (Aggressive Bot)
- Trailing stop management
- Telegram bot control

### 🔧 Technical Features
- Auto-update system
- Backtesting support
- Walk-forward testing
- Performance analytics
- State persistence

## 📥 Installation

1. Download and extract the release
2. Run `INSTALL.bat` to install dependencies
3. Configure `config/config.py` with your Binance API keys
4. Run `RUN_IN_TERMINAL.bat` to start

## 📚 Documentation

Complete documentation is included in the `docs/` folder:
- Quick Start Guide
- Setup Guide
- Bot Specifications
- Telegram Setup
- Backtest Guide

## ⚠️ Important Notes

- Test in DEMO mode first before using real money
- Understand the risks of cryptocurrency trading
- Read the Terms of Use before using
- Backup your bot_state.json regularly

## 🔄 Auto-Update

This release includes auto-update functionality. The bot will check for updates automatically when you start it.

---

**Release Date:** February 3, 2026  
**Version:** 3.0.0  
**License:** See LICENSE.txt
"""

def create_github_release():
    """Create GitHub Release using API"""
    
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    
    # Add token if available
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    data = {
        "tag_name": TAG_NAME,
        "target_commitish": "master",
        "name": RELEASE_TITLE,
        "body": RELEASE_NOTES,
        "draft": False,
        "prerelease": False
    }
    
    print(f"🚀 Creating GitHub Release: {RELEASE_TITLE}")
    print(f"📦 Tag: {TAG_NAME}")
    print(f"🔗 Repository: {REPO_OWNER}/{REPO_NAME}")
    print()
    
    try:
        response = requests.post(api_url, headers=headers, json=data)
        
        if response.status_code == 201:
            release_data = response.json()
            print("✅ Release created successfully!")
            print(f"🔗 URL: {release_data['html_url']}")
            print(f"📝 Release ID: {release_data['id']}")
            return True
        elif response.status_code == 401:
            print("❌ Authentication failed!")
            print("⚠️ You need to create a GitHub Personal Access Token")
            print()
            print("📋 Manual Steps:")
            print("1. Go to: https://github.com/l3adxl3oy/Binance_Bot/releases/new")
            print(f"2. Tag version: {TAG_NAME}")
            print(f"3. Release title: {RELEASE_TITLE}")
            print("4. Copy the release notes above")
            print("5. Click 'Publish release'")
            return False
        elif response.status_code == 422:
            error_msg = response.json().get('message', 'Unknown error')
            if 'already_exists' in error_msg.lower():
                print(f"⚠️ Release {TAG_NAME} already exists!")
                print(f"🔗 View: https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/tag/{TAG_NAME}")
                return True
            else:
                print(f"❌ Validation error: {error_msg}")
                print(f"Response: {response.json()}")
                return False
        else:
            print(f"❌ Failed to create release: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("="*70)
    print("  GitHub Release Creator - BinanceBot v3.0.0")
    print("="*70)
    print()
    
    success = create_github_release()
    
    print()
    print("="*70)
    
    if not success:
        print()
        print("💡 Alternative: Create release manually on GitHub")
        print(f"   https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/new")
        print()
        print("   Release notes saved to: release_notes.txt")
        
        # Save release notes to file
        with open("release_notes.txt", "w", encoding="utf-8") as f:
            f.write(RELEASE_NOTES)
