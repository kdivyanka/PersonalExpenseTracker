import pytest

from app import create_app
from config import TestConfig
from services.transaction_service import (
    add_income,
    add_expense,
    get_all_transactions,
    get_recent_transactions,
    get_transaction_by_id,
    search_transactions,
    delete_transaction,
)


@pytest.fixture
def app(tmp_path):
    class IsolatedTestConfig(TestConfig):
        DATABASE_PATH = str(tmp_path / "test_expense_tracker.db")

    app = create_app(IsolatedTestConfig)
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_transactions(app):
    with app.app_context():
        add_income({
            "source": "Salary",
            "amount": "50000",
            "date": "2026-11-01",
            "description": "Monthly salary",
        })

        add_expense({
            "title": "Groceries",
            "amount": "2000",
            "category": "Food",
            "date": "2026-11-02",
            "description": "Monthly groceries",
        })


def test_add_income_and_retrieve(app):
    with app.app_context():
        transaction_id, errors = add_income({
            "source": "Salary",
            "amount": "50000",
            "date": "2026-11-01",
            "description": "Monthly salary",
        })

        assert errors == {}
        assert transaction_id is not None

        transaction = get_transaction_by_id(transaction_id)
        assert transaction["title"] == "Salary"
        assert transaction["amount"] == 50000.0
        assert transaction["type"] == "Income"


def test_add_expense_and_retrieve(app):
    with app.app_context():
        transaction_id, errors = add_expense({
            "title": "Groceries",
            "amount": "2000",
            "category": "Food",
            "date": "2026-11-02",
            "description": "Monthly groceries",
        })

        assert errors == {}
        assert transaction_id is not None

        transaction = get_transaction_by_id(transaction_id)
        assert transaction["title"] == "Groceries"
        assert transaction["amount"] == 2000.0
        assert transaction["type"] == "Expense"


def test_retrieve_all_transactions(app, sample_transactions):
    with app.app_context():
        transactions = get_all_transactions()
        assert len(transactions) == 2


def test_retrieve_recent_transactions(app, sample_transactions):
    with app.app_context():
        transactions = get_recent_transactions(1)
        assert len(transactions) == 1


def test_search_transactions(app, sample_transactions):
    with app.app_context():
        results = search_transactions(
            search_text="Groceries",
            transaction_type="all",
            category="all",
            sort="date_desc",
        )

        assert len(results) == 1
        assert results[0]["title"] == "Groceries"


def test_delete_transaction(app):
    with app.app_context():
        transaction_id, errors = add_expense({
            "title": "Shopping",
            "amount": "1500",
            "category": "Shopping",
            "date": "2026-11-02",
            "description": "Test transaction",
        })

        assert errors == {}

        success, message = delete_transaction(transaction_id)

        assert success is True
        assert get_transaction_by_id(transaction_id) is None


def test_invalid_income_is_not_saved(app):
    with app.app_context():
        transaction_id, errors = add_income({
            "source": "",
            "amount": "-100",
            "date": "2026-11-01",
            "description": "",
        })

        assert transaction_id is None
        assert errors
        assert get_all_transactions() == []