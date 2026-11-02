import pytest
from services.calculations import (
    calculate_total_income,
    calculate_total_expenses,
    calculate_available_balance,
    count_transactions,
    calculate_category_breakdown,
    filter_transactions_by_month,
    calculate_monthly_summary,
    calculate_monthly_totals
)

from services.constants import TYPE_INCOME, TYPE_EXPENSE


# Sample transaction data
@pytest.fixture
def sample_transactions():
    return [
        {
            "type": TYPE_INCOME,
            "amount": 5000,
            "category": "Income",
            "date": "2026-11-01"
        },
        {
            "type": TYPE_EXPENSE,
            "amount": 1000,
            "category": "Food",
            "date": "2026-11-02"
        },
        {
            "type": TYPE_EXPENSE,
            "amount": 500,
            "category": "Travel",
            "date": "2026-11-03"
        },
        {
            "type": TYPE_INCOME,
            "amount": 3000,
            "category": "Income",
            "date": "2026-10-15"
        }
    ]


# UT-01: Test total income calculation
def test_total_income(sample_transactions):
    assert calculate_total_income(sample_transactions) == 8000


# UT-02: Test total expense calculation
def test_total_expenses(sample_transactions):
    assert calculate_total_expenses(sample_transactions) == 1500


# UT-03: Test available balance calculation
def test_available_balance(sample_transactions):
    assert calculate_available_balance(sample_transactions) == 6500


# UT-04: Test transaction count
def test_transaction_count(sample_transactions):
    assert count_transactions(sample_transactions) == 4


# UT-05: Test category-wise expense breakdown
def test_category_breakdown(sample_transactions):
    result = calculate_category_breakdown(sample_transactions)

    assert result == [
        ("Food", 1000),
        ("Travel", 500)
    ]


# UT-06: Test monthly transaction filtering
def test_month_filter(sample_transactions):
    result = filter_transactions_by_month(
        sample_transactions, 2026, 11
    )

    assert len(result) == 3


# UT-07: Test monthly summary
def test_monthly_summary(sample_transactions):
    result = calculate_monthly_summary(
        sample_transactions, 2026, 11
    )

    assert result["income"] == 5000
    assert result["expenses"] == 1500
    assert result["savings"] == 3500
    assert result["transaction_count"] == 3


# UT-08: Test monthly totals
def test_monthly_totals(sample_transactions):
    result = calculate_monthly_totals(sample_transactions)

    assert len(result) == 2
    assert result[0]["month"] == "2026-10"
    assert result[1]["month"] == "2026-11"