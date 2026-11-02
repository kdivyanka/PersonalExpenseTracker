"""
calculations.py - All the maths for the dashboard and monthly summary.

These functions are "pure": they take a list of transactions (plain
dictionaries) and return numbers. They never touch the database or Flask,
so you can unit test them with made-up data.

A transaction dictionary looks like:
    {"type": "Income" or "Expense", "amount": 100.0,
     "category": "Food", "date": datetime.date(2026, 11, 1)}
"""
from datetime import date, datetime

from services.constants import TYPE_EXPENSE, TYPE_INCOME


def _as_date(value):
    """Accept a date object or a 'YYYY-MM-DD' string and return a date."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def _month_key(value):
    """Turn a date into 'YYYY-MM' (used for grouping)."""
    d = _as_date(value)
    return f"{d.year:04d}-{d.month:02d}"


def _month_label(month_key):
    """'2026-11' -> 'Nov 2026'."""
    year, month = month_key.split("-")
    return datetime(int(year), int(month), 1).strftime("%b %Y")


def calculate_total_income(transactions):
    total = sum(t["amount"] for t in transactions if t["type"] == TYPE_INCOME)
    return round(total, 2)


def calculate_total_expenses(transactions):
    total = sum(t["amount"] for t in transactions if t["type"] == TYPE_EXPENSE)
    return round(total, 2)


def calculate_available_balance(transactions):
    """Balance = total income - total expenses (can be negative)."""
    return round(calculate_total_income(transactions) - calculate_total_expenses(transactions), 2)


def count_transactions(transactions):
    return len(transactions)


def calculate_category_breakdown(transactions):
    """
    Expense totals per category, biggest first.
    Returns a list of (category, total) tuples, e.g. [("Food", 450.0), ("Bills", 300.0)].
    """
    totals = {}
    for t in transactions:
        if t["type"] == TYPE_EXPENSE:
            totals[t["category"]] = totals.get(t["category"], 0) + t["amount"]
    ordered = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    return [(category, round(total, 2)) for category, total in ordered]


def filter_transactions_by_month(transactions, year, month):
    """Keep only the transactions that fall in the given year and month."""
    result = []
    for t in transactions:
        d = _as_date(t["date"])
        if d.year == year and d.month == month:
            result.append(t)
    return result


def calculate_monthly_summary(transactions, year, month):
    """
    Summary for ONE month:
      income, expenses, savings (income - expenses) and expense category breakdown.
    """
    month_transactions = filter_transactions_by_month(transactions, year, month)
    income = calculate_total_income(month_transactions)
    expenses = calculate_total_expenses(month_transactions)
    return {
        "year": year,
        "month": month,
        "label": datetime(year, month, 1).strftime("%B %Y"),
        "income": income,
        "expenses": expenses,
        "savings": round(income - expenses, 2),
        "category_breakdown": calculate_category_breakdown(month_transactions),
        "transaction_count": len(month_transactions),
    }


def calculate_monthly_totals(transactions, limit=None):
    """
    Income / expenses / savings for every month that has data, oldest first.
    If `limit` is given, only the most recent `limit` months are returned.
    """
    months = {}
    for t in transactions:
        key = _month_key(t["date"])
        entry = months.setdefault(key, {"income": 0.0, "expenses": 0.0})
        if t["type"] == TYPE_INCOME:
            entry["income"] += t["amount"]
        elif t["type"] == TYPE_EXPENSE:
            entry["expenses"] += t["amount"]

    rows = []
    for key in sorted(months):
        income = round(months[key]["income"], 2)
        expenses = round(months[key]["expenses"], 2)
        rows.append({
            "month": key,
            "label": _month_label(key),
            "income": income,
            "expenses": expenses,
            "savings": round(income - expenses, 2),
        })

    if limit is not None:
        rows = rows[-limit:]
    return rows
