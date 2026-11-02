"""
transaction_service.py - Functions that talk to the database.

Routes (app.py) call these functions. These functions call validation.py
first, so invalid data never reaches the database.

Adding returns:   (transaction_id, errors)
   success -> (5, {})          failure -> (None, {"amount": "Amount is required."})
"""
import sqlite3
from datetime import date, timedelta

from models import get_db, row_to_dict
from services.constants import TYPE_EXPENSE, TYPE_INCOME
from services.validation import validate_expense_data, validate_income_data

DATABASE_ERROR_MESSAGE = "A database error occurred. The transaction was not saved. Please try again."

SORT_OPTIONS = {
    "date_desc": "date DESC, id DESC",
    "date_asc": "date ASC, id ASC",
}


def _insert_transaction(clean_data):
    """Insert one already-validated transaction. Returns (new_id, errors)."""
    try:
        db = get_db()
        cursor = db.execute(
            "INSERT INTO transactions (transaction_type, title, amount, category, date, description) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                clean_data["type"],
                clean_data["title"],
                clean_data["amount"],
                clean_data["category"],
                clean_data["date"].isoformat(),
                clean_data["description"],
            ),
        )
        db.commit()
        return cursor.lastrowid, {}
    except sqlite3.Error:
        get_db().rollback()
        return None, {"database": DATABASE_ERROR_MESSAGE}


def add_income(form):
    """Validate and save an income record."""
    clean_data, errors = validate_income_data(form)
    if errors:
        return None, errors
    return _insert_transaction(clean_data)


def add_expense(form):
    """Validate and save an expense record."""
    clean_data, errors = validate_expense_data(form)
    if errors:
        return None, errors
    return _insert_transaction(clean_data)


def get_all_transactions():
    """Every transaction (newest first) as a list of dictionaries."""
    rows = get_db().execute("SELECT * FROM transactions ORDER BY date DESC, id DESC").fetchall()
    return [row_to_dict(row) for row in rows]


def get_recent_transactions(limit=5):
    rows = get_db().execute(
        "SELECT * FROM transactions ORDER BY date DESC, id DESC LIMIT ?", (limit,)
    ).fetchall()
    return [row_to_dict(row) for row in rows]


def get_transaction_by_id(transaction_id):
    row = get_db().execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,)).fetchone()
    return row_to_dict(row) if row else None


def search_transactions(search_text="", transaction_type="all", category="all", sort="date_desc"):
    """
    Transaction History query: text search + type filter + category filter + date sort.
    Unknown filter/sort values fall back to safe defaults.
    """
    conditions = []
    params = []

    search_text = (search_text or "").strip()
    if search_text:
        escaped = search_text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        pattern = f"%{escaped}%"
        conditions.append(
            "(title LIKE ? ESCAPE '\\' OR description LIKE ? ESCAPE '\\' OR category LIKE ? ESCAPE '\\')"
        )
        params.extend([pattern, pattern, pattern])

    if transaction_type in (TYPE_INCOME, TYPE_EXPENSE):
        conditions.append("transaction_type = ?")
        params.append(transaction_type)

    if category and category != "all":
        conditions.append("category = ?")
        params.append(category)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    order_clause = SORT_OPTIONS.get(sort, SORT_OPTIONS["date_desc"])

    sql = f"SELECT * FROM transactions {where_clause} ORDER BY {order_clause}"
    rows = get_db().execute(sql, params).fetchall()
    return [row_to_dict(row) for row in rows]


def delete_transaction(transaction_id):
    """Delete one transaction. Returns (success, message)."""
    try:
        db = get_db()
        cursor = db.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        db.commit()
    except sqlite3.Error:
        get_db().rollback()
        return False, "A database error occurred. The transaction was not deleted."

    if cursor.rowcount == 0:
        return False, "Transaction not found. It may have already been deleted."
    return True, "Transaction deleted successfully."


# ----- Optional sample data -------------------------------------------------

# (type, title, amount, category, days_ago, description)
SAMPLE_TRANSACTIONS = [
    (TYPE_INCOME, "Monthly Salary", 50000.00, "Income", 62, "Salary"),
    (TYPE_INCOME, "Monthly Salary", 50000.00, "Income", 32, "Salary"),
    (TYPE_INCOME, "Monthly Salary", 50000.00, "Income", 3, "Salary"),
    (TYPE_INCOME, "Freelance Project", 8000.00, "Income", 18, "Website design work"),
    (TYPE_EXPENSE, "Groceries", 3200.50, "Food", 58, "Weekly groceries"),
    (TYPE_EXPENSE, "Electricity Bill", 1800.00, "Bills", 52, "Monthly bill"),
    (TYPE_EXPENSE, "Bus Pass", 900.00, "Travel", 45, "Monthly pass"),
    (TYPE_EXPENSE, "Online Course", 2500.00, "Education", 40, "Python course"),
    (TYPE_EXPENSE, "Movie Night", 650.00, "Entertainment", 28, "Cinema tickets"),
    (TYPE_EXPENSE, "New Shoes", 3400.00, "Shopping", 22, ""),
    (TYPE_EXPENSE, "Pharmacy", 480.75, "Healthcare", 14, "Medicines"),
    (TYPE_EXPENSE, "Restaurant Dinner", 1250.00, "Food", 9, "Dinner with friends"),
    (TYPE_EXPENSE, "Internet Bill", 999.00, "Bills", 5, "Monthly bill"),
    (TYPE_EXPENSE, "Stationery", 320.00, "Others", 1, "Notebooks and pens"),
]


def seed_sample_data():
    """
    Insert sample rows ONLY when the table is empty.
    Returns how many rows were inserted (0 if the table already had data).
    The app works perfectly fine without this.
    """
    db = get_db()
    existing = db.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    if existing > 0:
        return 0

    today = date.today()
    for t_type, title, amount, category, days_ago, description in SAMPLE_TRANSACTIONS:
        db.execute(
            "INSERT INTO transactions (transaction_type, title, amount, category, date, description) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (t_type, title, amount, category, (today - timedelta(days=days_ago)).isoformat(), description),
        )
    db.commit()
    return len(SAMPLE_TRANSACTIONS)
