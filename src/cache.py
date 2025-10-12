"""Caching system for resume content and other parsed data."""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Optional, Any

from platformdirs import user_cache_dir
from rich.console import Console

console = Console()


class ResumeCache:
    """Simple file-based cache for resume content using platformdirs."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir is None:
            # Use platformdirs to get system-appropriate cache directory
            self.cache_dir = Path(user_cache_dir("job-application-agent", "job-application-agent"))
        else:
            self.cache_dir = Path(cache_dir)
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "resume_cache.json"
        self.cache_data = self._load_cache()
    
    def _load_cache(self) -> dict:
        """Load cache data from file."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                console.print("[yellow]Warning: Cache file corrupted, starting fresh[/yellow]", file=sys.stderr)
        return {}
    
    def _save_cache(self):
        """Save cache data to file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            console.print(f"[yellow]Warning: Could not save cache: {e}[/yellow]", file=sys.stderr)
    
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
                console.print(f"[blue]Using cached resume content[/blue]", file=sys.stderr)
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
            'file_path': str(Path(file_path).absolute())
        }
        
        self._save_cache()
        console.print(f"[green]Cached resume content[/green]", file=sys.stderr)
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self.cache_data = {}
        if self.cache_file.exists():
            self.cache_file.unlink()
        console.print("[blue]Cache cleared[/blue]", file=sys.stderr)
    
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
            console.print(f"[blue]Cleaned up {removed_count} old cache entries[/blue]", file=sys.stderr)
        
        return removed_count


# Global cache instance
resume_cache = ResumeCache()
