import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent / "journal.db"


def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                qty REAL DEFAULT 1,
                entry REAL,
                exit REAL,
                pnl REAL NOT NULL,
                note TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                content TEXT,
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trade_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id INTEGER,
                date TEXT,
                filename TEXT,
                data BLOB,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY(trade_id) REFERENCES trades(id)
            )
        """)
        conn.commit()


def insert_trade(date, symbol, side, qty, entry, exit_, pnl, note=""):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO trades (date, symbol, side, qty, entry, exit, pnl, note) VALUES (?,?,?,?,?,?,?,?)",
            (date, symbol, side, qty, entry, exit_, pnl, note)
        )
        conn.commit()
        return cur.lastrowid


def delete_trade(trade_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM trades WHERE id=?", (trade_id,))
        conn.execute("DELETE FROM trade_images WHERE trade_id=?", (trade_id,))
        conn.commit()


def get_trades_by_date(date_str):
    with get_conn() as conn:
        df = pd.read_sql("SELECT * FROM trades WHERE date=? ORDER BY created_at", conn, params=(date_str,))
    return df


def get_all_trades():
    with get_conn() as conn:
        df = pd.read_sql("SELECT * FROM trades ORDER BY date, created_at", conn)
    return df


def get_daily_pnl():
    with get_conn() as conn:
        df = pd.read_sql(
            "SELECT date, SUM(pnl) as daily_pnl, COUNT(*) as trade_count FROM trades GROUP BY date ORDER BY date",
            conn
        )
    return df


def save_note(date_str, content):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO notes (date, content) VALUES (?,?) ON CONFLICT(date) DO UPDATE SET content=?, updated_at=datetime('now')",
            (date_str, content, content)
        )
        conn.commit()


def get_note(date_str):
    with get_conn() as conn:
        row = conn.execute("SELECT content FROM notes WHERE date=?", (date_str,)).fetchone()
    return row[0] if row else ""


def get_notes():
    with get_conn() as conn:
        df = pd.read_sql("SELECT * FROM notes ORDER BY date DESC", conn)
    return df


def save_image(trade_id, date_str, filename, data):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO trade_images (trade_id, date, filename, data) VALUES (?,?,?,?)",
            (trade_id, date_str, filename, data)
        )
        conn.commit()


def get_images_by_date(date_str):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, trade_id, filename, data FROM trade_images WHERE date=? ORDER BY created_at",
            (date_str,)
        ).fetchall()
    return rows


def delete_image(image_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM trade_images WHERE id=?", (image_id,))
        conn.commit()
