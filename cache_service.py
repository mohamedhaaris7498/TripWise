import time
import json
import threading
from typing import Any, Optional
from app.config import settings
from app.database import get_db

class InMemoryTTLCache:
    """Thread-safe zero-lag in-memory cache with TTL expiration and SQLite backup persistence."""
    
    def __init__(self, default_ttl: int = 1800):
        self._cache = {}
        self._lock = threading.Lock()
        self._default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        now = time.time()
        with self._lock:
            if key in self._cache:
                value, expires_at = self._cache[key]
                if expires_at > now:
                    return value
                else:
                    del self._cache[key]
        
        # Check SQLite persistent cache fallback
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT data_json, expires_at FROM cache_entries WHERE key = ?", (key,))
                row = cursor.fetchone()
                if row and row["expires_at"] > now:
                    data = json.loads(row["data_json"])
                    # Re-populate in-memory cache
                    with self._lock:
                        self._cache[key] = (data, row["expires_at"])
                    return data
                elif row:
                    cursor.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
        except Exception:
            pass
        
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = ttl if ttl is not None else self._default_ttl
        expires_at = time.time() + ttl
        with self._lock:
            self._cache[key] = (value, expires_at)
        
        # Asynchronously or safely persist to SQLite cache table
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                data_json = json.dumps(value)
                cursor.execute("""
                INSERT INTO cache_entries (key, data_json, expires_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET data_json = excluded.data_json, expires_at = excluded.expires_at
                """, (key, data_json, expires_at))
        except Exception:
            pass

    def delete(self, key: str) -> None:
        with self._lock:
            self._cache.pop(key, None)
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
        except Exception:
            pass

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cache_entries")
        except Exception:
            pass

cache = InMemoryTTLCache(default_ttl=settings.CACHE_TTL_SECONDS)
