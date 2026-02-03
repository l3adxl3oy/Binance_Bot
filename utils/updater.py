"""
Auto-update module for BinanceBot
Checks GitHub releases for new versions and manages updates
"""

import os
import sys
import json
import shutil
import zipfile
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import version
except ImportError:
    print("⚠️ Cannot import version.py - using default version")
    class version:
        __version__ = "3.0.0"
        GITHUB_API_URL = ""
        GITHUB_REPO_URL = ""


class BotUpdater:
    """Manages bot version checking and updates"""
    
    def __init__(self, check_enabled: bool = True):
        self.current_version = version.__version__
        self.github_api_url = version.GITHUB_API_URL
        self.github_repo_url = version.GITHUB_REPO_URL
        self.check_enabled = check_enabled
        self.project_root = Path(__file__).parent.parent
        self.backup_dir = self.project_root / "backups"
        
    def compare_versions(self, version1: str, version2: str) -> int:
        """
        Compare two semantic versions
        Returns: 1 if version1 > version2, -1 if version1 < version2, 0 if equal
        """
        try:
            v1_parts = [int(x) for x in version1.lstrip('v').split('.')]
            v2_parts = [int(x) for x in version2.lstrip('v').split('.')]
            
            # Pad with zeros if lengths differ
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts += [0] * (max_len - len(v1_parts))
            v2_parts += [0] * (max_len - len(v2_parts))
            
            for i in range(max_len):
                if v1_parts[i] > v2_parts[i]:
                    return 1
                elif v1_parts[i] < v2_parts[i]:
                    return -1
            return 0
        except Exception as e:
            print(f"❌ Error comparing versions: {e}")
            return 0
    
    def check_for_updates(self, timeout: int = 10) -> Optional[Dict]:
        """
        Check GitHub for new releases
        Returns: dict with update info or None if no update available
        """
        if not self.check_enabled:
            return None
            
        if not self.github_api_url or "YourGitHubUsername" in self.github_api_url:
            print("⚠️ GitHub repository not configured. Update version.py with your repository URL.")
            return None
        
        try:
            print(f"🔍 Checking for updates... (Current version: {self.current_version})")
            
            response = requests.get(
                self.github_api_url,
                timeout=timeout,
                headers={"Accept": "application/vnd.github.v3+json"}
            )
            
            if response.status_code == 404:
                print("⚠️ Repository not found or no releases published yet")
                return None
            
            response.raise_for_status()
            release_data = response.json()
            
            latest_version = release_data.get('tag_name', '').lstrip('v')
            release_name = release_data.get('name', 'Unknown')
            release_notes = release_data.get('body', 'No release notes available')
            download_url = release_data.get('zipball_url', '')
            published_at = release_data.get('published_at', '')
            
            # Compare versions
            comparison = self.compare_versions(latest_version, self.current_version)
            
            if comparison > 0:
                return {
                    'available': True,
                    'version': latest_version,
                    'name': release_name,
                    'notes': release_notes,
                    'download_url': download_url,
                    'published_at': published_at,
                    'url': release_data.get('html_url', self.github_repo_url)
                }
            else:
                print(f"✅ You're running the latest version ({self.current_version})")
                return None
                
        except requests.exceptions.Timeout:
            print("⚠️ Update check timed out")
            return None
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Could not check for updates: {e}")
            return None
        except Exception as e:
            print(f"❌ Error checking for updates: {e}")
            return None
    
    def create_backup(self) -> Optional[Path]:
        """
        Create backup of current version
        Returns: Path to backup or None if failed
        """
        try:
            # Create backups directory if it doesn't exist
            self.backup_dir.mkdir(exist_ok=True)
            
            # Create timestamped backup folder name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_v{self.current_version}_{timestamp}"
            backup_path = self.backup_dir / backup_name
            
            print(f"💾 Creating backup: {backup_name}")
            
            # Files and directories to backup
            items_to_backup = [
                'bots', 'core', 'config', 'managers', 'modules', 'utils',
                'version.py', 'requirements.txt', 'bot_state.json'
            ]
            
            backup_path.mkdir(exist_ok=True)
            
            for item in items_to_backup:
                src = self.project_root / item
                if src.exists():
                    dst = backup_path / item
                    if src.is_dir():
                        shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
                    else:
                        shutil.copy2(src, dst)
            
            print(f"✅ Backup created successfully: {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return None
    
    def download_update(self, download_url: str, timeout: int = 60) -> Optional[Path]:
        """
        Download update from GitHub
        Returns: Path to downloaded file or None if failed
        """
        try:
            print(f"⬇️ Downloading update...")
            
            response = requests.get(download_url, timeout=timeout, stream=True)
            response.raise_for_status()
            
            # Save to temporary file
            download_path = self.project_root / "temp_update.zip"
            
            # Download with progress indication
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r⬇️ Downloading: {progress:.1f}%", end='', flush=True)
            
            print()  # New line after progress
            print(f"✅ Download complete: {download_path}")
            return download_path
            
        except Exception as e:
            print(f"❌ Failed to download update: {e}")
            return None
    
    def apply_update(self, update_file: Path, new_version: str) -> bool:
        """
        Apply downloaded update
        Returns: True if successful, False otherwise
        """
        try:
            print(f"📦 Applying update to version {new_version}...")
            
            # Extract zip file
            extract_dir = self.project_root / "temp_extract"
            extract_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(update_file, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find the extracted folder (GitHub creates a folder inside)
            extracted_folders = list(extract_dir.iterdir())
            if not extracted_folders:
                print("❌ No files found in update package")
                return False
            
            source_dir = extracted_folders[0]
            
            # Files and directories to update
            items_to_update = [
                'bots', 'core', 'config', 'managers', 'modules', 'utils',
                'version.py', 'requirements.txt'
            ]
            
            for item in items_to_update:
                src = source_dir / item
                dst = self.project_root / item
                
                if src.exists():
                    if dst.exists():
                        if dst.is_dir():
                            shutil.rmtree(dst)
                        else:
                            dst.unlink()
                    
                    if src.is_dir():
                        shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
                    else:
                        shutil.copy2(src, dst)
            
            # Clean up
            shutil.rmtree(extract_dir)
            update_file.unlink()
            
            print(f"✅ Update applied successfully!")
            print(f"📝 Updated to version {new_version}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to apply update: {e}")
            return False
    
    def install_dependencies(self) -> bool:
        """
        Install/update Python dependencies from requirements.txt
        Returns: True if successful, False otherwise
        """
        try:
            import subprocess
            
            print("📦 Installing dependencies...")
            requirements_file = self.project_root / "requirements.txt"
            
            if not requirements_file.exists():
                print("⚠️ requirements.txt not found")
                return False
            
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Dependencies installed successfully")
                return True
            else:
                print(f"❌ Failed to install dependencies:\n{result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error installing dependencies: {e}")
            return False
    
    def full_update_process(self) -> bool:
        """
        Complete update process: check, backup, download, apply
        Returns: True if update was successful, False otherwise
        """
        try:
            # Check for updates
            update_info = self.check_for_updates()
            
            if not update_info:
                return False
            
            # Display update information
            print("\n" + "="*60)
            print(f"🆕 NEW VERSION AVAILABLE: v{update_info['version']}")
            print(f"📋 Release: {update_info['name']}")
            print(f"📅 Published: {update_info['published_at']}")
            print("="*60)
            print(f"\n📝 Release Notes:\n{update_info['notes'][:500]}")
            if len(update_info['notes']) > 500:
                print("... (truncated)")
            print("\n" + "="*60)
            
            # Ask for confirmation
            response = input("\n❓ Do you want to update now? (yes/no): ").strip().lower()
            
            if response not in ['yes', 'y', 'ใช่']:
                print("⏭️ Update cancelled. You can update later.")
                print(f"🔗 Manual update: {update_info['url']}")
                return False
            
            # Create backup
            backup_path = self.create_backup()
            if not backup_path:
                print("❌ Cannot proceed without backup")
                return False
            
            # Download update
            download_path = self.download_update(update_info['download_url'])
            if not download_path:
                print("❌ Download failed")
                return False
            
            # Apply update
            if not self.apply_update(download_path, update_info['version']):
                print("❌ Update failed")
                print(f"💾 Backup available at: {backup_path}")
                return False
            
            # Install dependencies
            print("\n📦 Checking dependencies...")
            self.install_dependencies()
            
            print("\n" + "="*60)
            print(f"🎉 UPDATE COMPLETE!")
            print(f"✨ BinanceBot updated to v{update_info['version']}")
            print(f"💾 Backup saved at: {backup_path}")
            print("="*60)
            
            return True
            
        except Exception as e:
            print(f"❌ Update process failed: {e}")
            return False


def check_update_cli():
    """Command-line interface for update checking"""
    updater = BotUpdater()
    update_info = updater.check_for_updates()
    
    if update_info:
        print("\n🆕 Update available!")
        print(f"Current version: {updater.current_version}")
        print(f"Latest version: {update_info['version']}")
        print(f"Release: {update_info['name']}")
        print(f"URL: {update_info['url']}")
        return True
    else:
        print(f"\n✅ You're up to date! (v{updater.current_version})")
        return False


def auto_update_cli():
    """Command-line interface for full auto-update"""
    updater = BotUpdater()
    success = updater.full_update_process()
    return 0 if success else 1


if __name__ == "__main__":
    # Can be used standalone for testing
    if len(sys.argv) > 1 and sys.argv[1] == "--update":
        sys.exit(auto_update_cli())
    else:
        check_update_cli()
