# 🔄 Auto-Update Guide - BinanceBot

## 📋 Overview

BinanceBot now includes an automatic update system that checks GitHub for new releases and can update the bot automatically with user approval.

## ✨ Features

- ✅ Automatic version checking from GitHub releases
- ✅ Semantic version comparison (e.g., 3.0.1 > 3.0.0)
- ✅ User approval required before updates
- ✅ Automatic backup creation before updating
- ✅ Dependency installation after update
- ✅ Safe rollback if update fails
- ✅ Thai/English bilingual interface

## 🚀 Quick Start

### 1. Configure GitHub Repository

Edit `version.py` and update your repository information:

```python
GITHUB_REPO_OWNER = "YourGitHubUsername"  # Your GitHub username
GITHUB_REPO_NAME = "BinanceBot"           # Your repository name
```

**Example:**
```python
GITHUB_REPO_OWNER = "devleader"
GITHUB_REPO_NAME = "BinanceBot"
```

### 2. Run the Bot

When you run `RUN_IN_TERMINAL.bat`, the bot will:
1. Check for updates automatically
2. Display update information if available
3. Ask for your approval before updating
4. Create a backup before applying updates
5. Install updated dependencies
6. Launch the bot

## 📖 How It Works

### Automatic Update Check

When you start the bot via `RUN_IN_TERMINAL.bat`:

```
========================================
  🔍 ตรวจสอบอัปเดต / Checking for updates...
========================================

🔍 Checking for updates... (Current version: 3.0.0)
✅ You're running the latest version (3.0.0)
```

### Update Available

If a new version is found:

```
============================================================
🆕 NEW VERSION AVAILABLE: v3.0.1
📋 Release: BinanceBot v3.0.1 - Bug Fixes
📅 Published: 2026-02-03T10:30:00Z
============================================================

📝 Release Notes:
- Fixed trailing stop issue
- Improved correlation detection
- Updated risk management

============================================================

❓ Do you want to update now? (yes/no): 
```

### Update Process

If you choose to update:

1. **Backup Creation**
   ```
   💾 Creating backup: backup_v3.0.0_20260203_120000
   ✅ Backup created successfully
   ```

2. **Download Update**
   ```
   ⬇️ Downloading update...
   ⬇️ Downloading: 45.2%
   ✅ Download complete
   ```

3. **Apply Update**
   ```
   📦 Applying update to version 3.0.1...
   ✅ Update applied successfully!
   📝 Updated to version 3.0.1
   ```

4. **Install Dependencies**
   ```
   📦 Installing dependencies...
   ✅ Dependencies installed successfully
   ```

5. **Success**
   ```
   ============================================================
   🎉 UPDATE COMPLETE!
   ✨ BinanceBot updated to v3.0.1
   💾 Backup saved at: backups/backup_v3.0.0_20260203_120000
   ============================================================
   ```

## ⚙️ Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Auto-Update Settings
AUTO_UPDATE_CHECK_ENABLED=True      # Enable/disable update checking
AUTO_UPDATE_ON_STARTUP=False        # Require approval (recommended)
AUTO_UPDATE_CHECK_FREQUENCY=86400   # Check once per day (seconds)
AUTO_UPDATE_BACKUP_RETENTION=5      # Keep last 5 backups
```

### Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `AUTO_UPDATE_CHECK_ENABLED` | `True` | Enable automatic update checking |
| `AUTO_UPDATE_ON_STARTUP` | `False` | Require user approval for updates |
| `AUTO_UPDATE_CHECK_FREQUENCY` | `86400` | How often to check (seconds) |
| `AUTO_UPDATE_BACKUP_RETENTION` | `5` | Number of backups to keep |

## 🛠️ Manual Update Commands

### Check for Updates Only

```bash
python -m utils.updater
```

### Full Update Process

```bash
python -m utils.updater --update
```

## 📦 Backup Management

### Backup Location

Backups are stored in: `backups/backup_v{version}_{timestamp}/`

Example: `backups/backup_v3.0.0_20260203_120000/`

### What's Backed Up

- `bots/` - All bot code
- `core/` - Core systems
- `config/` - Configuration files
- `managers/` - Position and symbol managers
- `modules/` - Trading modules
- `utils/` - Utility functions
- `version.py` - Version information
- `requirements.txt` - Dependencies
- `bot_state.json` - Bot state

### Restore from Backup

If an update fails or you want to rollback:

1. Stop the bot
2. Navigate to the backup folder
3. Copy all files back to the project root
4. Restart the bot

```bash
# Example restoration
cd backups/backup_v3.0.0_20260203_120000
xcopy /E /Y * ..\..\
```

## 🔐 Security Considerations

### What's Safe

✅ Updates from official GitHub repository only
✅ User approval required by default
✅ Automatic backup before update
✅ No modification of sensitive files (.env, bot_state.json)
✅ Version verification before applying

### What to Check

⚠️ Always verify the GitHub repository URL in `version.py`
⚠️ Review release notes before updating
⚠️ Test updates on testnet first
⚠️ Keep your API keys in `.env` (never committed)

## 📝 Publishing Updates (For Developers)

### 1. Update Version

Edit `version.py`:
```python
__version__ = "3.0.1"  # Increment version
```

### 2. Commit Changes

```bash
git add .
git commit -m "Release v3.0.1: Bug fixes and improvements"
git push origin main
```

### 3. Create GitHub Release

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Tag version: `v3.0.1`
4. Release title: "BinanceBot v3.0.1 - Bug Fixes"
5. Description: List changes and improvements
6. Click "Publish release"

### 4. Users Get Update

Users will see the update notification on next bot start!

## 🐛 Troubleshooting

### "Repository not configured"

**Problem:** `version.py` still has placeholder values

**Solution:** Update `GITHUB_REPO_OWNER` and `GITHUB_REPO_NAME` in `version.py`

### "No releases published yet"

**Problem:** No GitHub releases created

**Solution:** Create your first release on GitHub (see Publishing Updates)

### "Update check timed out"

**Problem:** Network issues or GitHub API rate limit

**Solution:** 
- Check internet connection
- Wait a few minutes and try again
- GitHub API has rate limits (60 requests/hour for unauthenticated)

### "Failed to create backup"

**Problem:** Insufficient disk space or permission issues

**Solution:**
- Free up disk space
- Ensure write permissions on `backups/` folder
- Run as administrator if needed

### "Dependencies installation failed"

**Problem:** pip or package installation error

**Solution:**
```bash
# Manual dependency installation
.venv\Scripts\activate
pip install -r requirements.txt
```

## ❓ FAQ

### Q: Is auto-update safe?

A: Yes, when configured properly:
- Only updates from your official repository
- Creates backup before updating
- Requires user approval by default
- Does not modify sensitive files

### Q: Can I disable auto-update?

A: Yes, set in `.env`:
```bash
AUTO_UPDATE_CHECK_ENABLED=False
```

### Q: What happens if update fails?

A: The updater will:
1. Display error message
2. Keep backup intact
3. Not modify current installation
4. Allow manual restoration from backup

### Q: Can I skip a version?

A: Yes, simply click "no" when prompted. The update will be offered again next time.

### Q: How do I check current version?

A: Run the bot - version is displayed in startup banner:
```
🚀 BOT SCALPING อัจฉริยะ v3.0.0
```

### Q: Does it work offline?

A: No, requires internet to check GitHub. If offline:
- Update check will timeout gracefully
- Bot will continue to run normally
- Manual updates via `git pull` still work

## 📞 Support

If you encounter issues:

1. Check this guide first
2. Review error messages carefully
3. Check GitHub repository settings
4. Verify internet connection
5. Try manual update via `git pull`

## 🔗 Related Documentation

- [Setup Guide](SETUP_GUIDE.md)
- [Quick Start](QUICK_START_V2.md)
- [Telegram Guide](TELEGRAM_GUIDE.md)
- [Backtest Guide](BACKTEST_GUIDE.md)
