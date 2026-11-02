"""
models.py - The database layer: table structure + connection helpers.

We use Python's built-in `sqlite3` module (no extra install needed).
The database file is created automatically the first time the app starts.

Table: transactions
  id               - Transaction ID (primary key, auto-increment)
  transaction_type - 'Income' or 'Expense'
  title            - Expense title or income source
  amount           - Money amount (always > 0)
  category         - Expense category (income rows use 'Income')
  date             - Transaction date, stored as text 'YYYY-MM-DD'
  description      - Optional note
  created_at       - When the row was saved
"""
import os
import sqlite3
from datetime import date

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS transactions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_type TEXT    NOT NULL CHECK (transaction_type IN ('Income', 'Expense')),
    title            TEXT    NOT NULL,
    amount           REAL    NOT NULL CHECK (amount > 0),
    category         TEXT    NOT NULL,
    date             TEXT    NOT NULL,
    description      TEXT    NOT NULL DEFAULT '',
    created_at       TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def get_db():
    """Open (once per request) and return the SQLite connection."""
    if "db" not in g:
        db_path = current_app.config["DATABASE_PATH"]
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row   # lets us read columns by name
    return g.db


def close_db(error=None):
    """Close the connection at the end of every request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the transactions table if it does not exist yet."""
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()


def row_to_dict(row):
    """Convert a database row into a plain dictionary used by templates and calculations."""
    return {
        "id": row["id"],
        "type": row["transaction_type"],
        "title": row["title"],
        "amount": row["amount"],
        "category": row["category"],
        "date": date.fromisoformat(row["date"]),
        "description": row["description"],
        "created_at": row["created_at"],
    }
