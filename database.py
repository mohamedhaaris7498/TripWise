import sqlite3
import json
import time
from typing import Generator, Any, Dict, List, Optional
from contextlib import contextmanager
from app.config import settings

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Provide a transactional database connection scope with row factory."""
    conn = sqlite3.connect(settings.DB_PATH, timeout=10.0, check_same_thread=False)
    conn.row_factory = dict_factory
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initialize SQLite database tables for users, itineraries, bookings, and persistent cache."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Users table (Age-aware)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            age INTEGER NOT NULL,
            location TEXT,
            age_bracket TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)

        # 2. Itineraries table (Saved destinations and day plans)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS itineraries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            destination_id TEXT,
            destination_name TEXT NOT NULL,
            category TEXT,
            day_number INTEGER DEFAULT 1,
            notes TEXT,
            cost_estimate REAL DEFAULT 0.0,
            details_json TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        # 3. Bookings table (Rooms, Packages & Payments)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_reference TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            item_type TEXT NOT NULL,
            item_name TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'INR',
            status TEXT NOT NULL,
            payment_order_id TEXT,
            payment_id TEXT,
            receipt_data_json TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        # 4. Cache table (Backup persistent caching for zero-lag API responses)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cache_entries (
            key TEXT PRIMARY KEY,
            data_json TEXT NOT NULL,
            expires_at REAL NOT NULL
        );
        """)

        conn.commit()
