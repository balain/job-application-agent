"""Caching system for resume content and other parsed data with encryption support."""

import sys
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Optional, Any, Dict, List
from datetime import datetime, timedelta

from platformdirs import user_cache_dir
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console(file=sys.stderr)


class ResumeCache:
    """Enhanced file-based cache with encryption and automatic expiry."""
    
    def __init__(self, cache_dir: Optional[str] = None, encryption_manager=None):
        if cache_dir is None:
            # Use platformdirs to get system-appropriate cache directory
            self.cache_dir = Path(user_cache_dir("job-application-agent", "job-application-agent"))
        else:
            self.cache_dir = Path(cache_dir)
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "resume_cache.json"
        self.encryption_manager = encryption_manager
        self.cache_data = self._load_cache()
    
    def _load_cache(self) -> dict:
        """Load cache data from file with encryption support."""
        if self.cache_file.exists():
            try:
                # Check if file is encrypted
                if self._is_encrypted_file():
                    return self._load_encrypted_cache()
                else:
                    return self._load_plain_cache()
            except (json.JSONDecodeError, IOError, ValueError) as e:
                console.print(f"[yellow]Warning: Cache file corrupted, starting fresh: {e}[/yellow]")
        return {}
    
    def _is_encrypted_file(self) -> bool:
        """Check if cache file is encrypted."""
        try:
            with open(self.cache_file, 'rb') as f:
                # Read first few bytes to check for encryption signature
                header = f.read(16)
                # Simple heuristic: encrypted files don't start with '{'
                return not header.startswith(b'{')
        except:
            return False
    
    def _load_encrypted_cache(self) -> dict:
        """Load encrypted cache data."""
        if not self.encryption_manager or not self.encryption_manager.is_encryption_enabled():
            console.print("[red]Error: Encrypted cache found but encryption is disabled[/red]")
            return {}
        
        encryption = self.encryption_manager.get_encryption()
        if not encryption:
            console.print("[red]Error: Cannot initialize encryption for cache[/red]")
            return {}
        
        try:
            with open(self.cache_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = encryption.decrypt_data(encrypted_data)
            return json.loads(decrypted_data) if isinstance(decrypted_data, str) else decrypted_data
        except Exception as e:
            console.print(f"[red]Error decrypting cache: {e}[/red]")
            return {}
    
    def _load_plain_cache(self) -> dict:
        """Load plain text cache data."""
        with open(self.cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_cache(self):
        """Save cache data to file with encryption support."""
        try:
            # Check for expired entries before saving
            self._cleanup_expired_entries()
            
            if self.encryption_manager and self.encryption_manager.is_encryption_enabled():
                self._save_encrypted_cache()
            else:
                self._save_plain_cache()
        except IOError as e:
            console.print(f"[yellow]Warning: Could not save cache: {e}[/yellow]")
    
    def _save_encrypted_cache(self):
        """Save cache data with encryption."""
        encryption = self.encryption_manager.get_encryption()
        if not encryption:
            console.print("[red]Error: Cannot initialize encryption for cache[/red]")
            return
        
        try:
            encrypted_data = encryption.encrypt_data(self.cache_data)
            with open(self.cache_file, 'wb') as f:
                f.write(encrypted_data)
        except Exception as e:
            console.print(f"[red]Error encrypting cache: {e}[/red]")
    
    def _save_plain_cache(self):
        """Save cache data as plain text."""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache_data, f, indent=2, ensure_ascii=False)
    
    def _get_file_hash(self, file_path: str) -> str:
        """Generate hash for file content and modification time."""
        path = Path(file_path)
        if not path.exists():
            return ""
        
        # Get file stats
        stat = path.stat()
        file_info = f"{path.absolute()}:{stat.st_mtime}:{stat.st_size}"
        
        # Generate hash
        return hashlib.md5(file_info.encode()).hexdigest()
    
    def get_resume(self, file_path: str) -> Optional[str]:
        """
        Get cached resume content if available and up-to-date.
        
        Args:
            file_path: Path to resume file
            
        Returns:
            Cached resume content or None if not cached/outdated
        """
        file_hash = self._get_file_hash(file_path)
        if not file_hash:
            return None
        
        cache_key = f"resume_{file_hash}"
        
        if cache_key in self.cache_data:
            cached_entry = self.cache_data[cache_key]
            
            # Check if cache is still valid (file hasn't changed)
            if cached_entry.get('file_hash') == file_hash:
                console.print(f"[blue]Using cached resume content[/blue]")
                return cached_entry.get('content')
            else:
                # File has changed, remove old cache entry
                del self.cache_data[cache_key]
                self._save_cache()
        
        return None
    
    def set_resume(self, file_path: str, content: str) -> None:
        """
        Cache resume content.
        
        Args:
            file_path: Path to resume file
            content: Parsed resume content
        """
        file_hash = self._get_file_hash(file_path)
        if not file_hash:
            return
        
        cache_key = f"resume_{file_hash}"
        
        self.cache_data[cache_key] = {
            'content': content,
            'file_hash': file_hash,
            'cached_at': time.time(),
            'created_at': time.time(),
            'file_path': str(Path(file_path).absolute())
        }
        
        self._save_cache()
        console.print(f"[green]Cached resume content[/green]")
    
    def clear_cache(self) -> None:
        """Clear all cached data with secure deletion."""
        self.cache_data = {}
        if self.cache_file.exists():
            # Use secure deletion if encryption is enabled
            if self.encryption_manager and self.encryption_manager.is_encryption_enabled():
                encryption = self.encryption_manager.get_encryption()
                if encryption:
                    encryption.secure_delete(self.cache_file)
                else:
                    self.cache_file.unlink()
            else:
                self.cache_file.unlink()
        console.print("[blue]Cache cleared[/blue]")
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        total_entries = len(self.cache_data)
        resume_entries = sum(1 for key in self.cache_data.keys() if key.startswith('resume_'))
        
        return {
            'total_entries': total_entries,
            'resume_entries': resume_entries,
            'cache_file_size': self.cache_file.stat().st_size if self.cache_file.exists() else 0,
            'cache_directory': str(self.cache_dir.absolute())
        }
    
    def cleanup_old_entries(self, max_age_days: int = 30) -> int:
        """
        Remove cache entries older than specified days.
        
        Args:
            max_age_days: Maximum age in days
            
        Returns:
            Number of entries removed
        """
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        removed_count = 0
        keys_to_remove = []
        
        for key, entry in self.cache_data.items():
            if current_time - entry.get('cached_at', 0) > max_age_seconds:
                keys_to_remove.append(key)
                removed_count += 1
        
        for key in keys_to_remove:
            del self.cache_data[key]
        
        if removed_count > 0:
            self._save_cache()
            console.print(f"[blue]Cleaned up {removed_count} old cache entries[/blue]")
        
        return removed_count
    
    def _is_expired(self, entry: dict, max_age_days: int) -> bool:
        """Check if cache entry is expired."""
        current_time = time.time()
        created_at = entry.get('created_at', entry.get('cached_at', 0))
        max_age_seconds = max_age_days * 24 * 60 * 60
        return current_time - created_at > max_age_seconds
    
    def _cleanup_expired_entries(self) -> int:
        """Remove expired entries based on configured expiry."""
        if not self.encryption_manager:
            return 0
        
        # Get expiry days from config (default 90)
        max_age_days = getattr(self.encryption_manager, 'config', {}).get('CACHE_EXPIRY_DAYS', 90)
        return self.cleanup_old_entries(max_age_days)
    
    def export_cache(self, output_path: str) -> None:
        """Export all cached data to JSON file."""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create export data with metadata
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'total_entries': len(self.cache_data),
                'cache_directory': str(self.cache_dir.absolute()),
                'encryption_enabled': self.encryption_manager.is_encryption_enabled() if self.encryption_manager else False,
                'entries': self.cache_data
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            console.print(f"[green]Cache exported to: {output_path}[/green]")
        except Exception as e:
            console.print(f"[red]Error exporting cache: {e}[/red]")
    
    def get_cache_info(self) -> dict:
        """Get detailed cache information."""
        total_entries = len(self.cache_data)
        resume_entries = sum(1 for key in self.cache_data.keys() if key.startswith('resume_'))
        
        # Calculate expiry info
        current_time = time.time()
        expired_count = 0
        expiring_soon = 0
        
        for entry in self.cache_data.values():
            created_at = entry.get('created_at', entry.get('cached_at', 0))
            age_days = (current_time - created_at) / (24 * 60 * 60)
            
            if age_days > 90:  # Default expiry
                expired_count += 1
            elif age_days > 75:  # Expiring soon
                expiring_soon += 1
        
        return {
            'total_entries': total_entries,
            'resume_entries': resume_entries,
            'expired_entries': expired_count,
            'expiring_soon': expiring_soon,
            'cache_file_size': self.cache_file.stat().st_size if self.cache_file.exists() else 0,
            'cache_directory': str(self.cache_dir.absolute()),
            'encryption_enabled': self.encryption_manager.is_encryption_enabled() if self.encryption_manager else False,
            'expiry_days': getattr(self.encryption_manager, 'config', {}).get('CACHE_EXPIRY_DAYS', 90) if self.encryption_manager else 90
        }
    
    def display_cache_info(self) -> None:
        """Display formatted cache information."""
        info = self.get_cache_info()
        
        # Create info table
        table = Table(title="Cache Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Entries", str(info['total_entries']))
        table.add_row("Resume Entries", str(info['resume_entries']))
        table.add_row("Expired Entries", str(info['expired_entries']))
        table.add_row("Expiring Soon", str(info['expiring_soon']))
        table.add_row("File Size", f"{info['cache_file_size']:,} bytes")
        table.add_row("Directory", info['cache_directory'])
        table.add_row("Encryption", "Enabled" if info['encryption_enabled'] else "Disabled")
        table.add_row("Expiry Days", str(info['expiry_days']))
        
        console.print(table)
        
        # Show warnings if needed
        if info['expired_entries'] > 0:
            console.print(f"[yellow]Warning: {info['expired_entries']} entries have expired[/yellow]")
        if info['expiring_soon'] > 0:
            console.print(f"[yellow]Notice: {info['expiring_soon']} entries will expire soon[/yellow]")


# Global cache instance (will be updated with encryption manager)
resume_cache = ResumeCache()
