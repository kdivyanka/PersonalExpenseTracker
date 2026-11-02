"""
config.py - Application settings in one place.

Keeping settings here (instead of scattered through the code) makes it easy
to switch to a separate test database later.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Normal settings used when you run the app."""
    SECRET_KEY = "change-this-secret-key-for-real-use"   # needed for flash messages
    DATABASE_PATH = str(BASE_DIR / "instance" / "expense_tracker.db")
    CURRENCY_SYMBOL = "₹"          # change to "$" if you prefer
    LOAD_SAMPLE_DATA = False        # True = insert sample rows when DB is empty


class TestConfig(Config):
    """Settings for automated tests: a separate database file, so your real data is safe."""
    TESTING = True
    DATABASE_PATH = str(BASE_DIR / "instance" / "test_expense_tracker.db")
