import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "fraud.db"

@contextmanager
def get_connection():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    try:
        yield c
    finally:
        c.close()

def init_db():
    with get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'analyst' CHECK (role IN ('analyst', 'admin')),
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )""")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            amount REAL, hour INTEGER, distance_from_home REAL,
            merchant_risk REAL, device_trust REAL, international INTEGER,
            velocity_24h INTEGER, account_age_days INTEGER,
            fraud_probability REAL, prediction TEXT, created_at TEXT
        )""")
        transaction_columns = {
            row[1] for row in conn.execute("PRAGMA table_info(transactions)")
        }
        if "user_id" not in transaction_columns:
            conn.execute(
                "ALTER TABLE transactions ADD COLUMN user_id INTEGER REFERENCES users(id)"
            )
        conn.commit()


def create_user(username, email, password_hash, role="analyst"):
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (username, email, password_hash, role),
        )
        conn.commit()
        return cur.lastrowid


def get_user_by_login(login):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE lower(username) = lower(?) OR lower(email) = lower(?)",
            (login, login),
        ).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None

def insert_transaction(d, user_id=None):
    with get_connection() as conn:
        cur = conn.execute("""
        INSERT INTO transactions
        (user_id,amount,hour,distance_from_home,merchant_risk,device_trust,
         international,velocity_24h,account_age_days,fraud_probability,
         prediction,created_at)
          VALUES (?,?,?,?,?,?,?,?,?,?,?,datetime('now'))
          """, (user_id, d["amount"], d["hour"], d["distance_from_home"],
              d["merchant_risk"], d["device_trust"], d["international"],
              d["velocity_24h"], d["account_age_days"],
              d["fraud_probability"], d["prediction"]))
        conn.commit()
        return cur.lastrowid

def list_transactions(limit=50):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM transactions ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

def count_transactions():
    with get_connection() as conn:
        return conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]

def count_fraud():
    with get_connection() as conn:
        return conn.execute(
            "SELECT COUNT(*) FROM transactions WHERE prediction='FRAUD'"
        ).fetchone()[0]

def average_probability():
    with get_connection() as conn:
        value = conn.execute(
            "SELECT AVG(fraud_probability) FROM transactions"
        ).fetchone()[0]
        return float(value or 0)
