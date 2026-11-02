"""constants.py - Values shared by validation, calculations and the database code."""

TYPE_INCOME = "Income"
TYPE_EXPENSE = "Expense"

INCOME_CATEGORY = "Income"   # income records are stored with this category

EXPENSE_CATEGORIES = [
    "Food",
    "Shopping",
    "Travel",
    "Education",
    "Entertainment",
    "Healthcare",
    "Bills",
    "Others",
]

MAX_AMOUNT = 10_000_000
MAX_TITLE_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 255
