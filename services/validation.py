"""
validation.py - Checks user input BEFORE anything is saved.

Every function here is "pure": it only looks at the values you give it and
returns a result. No database, no Flask. That makes unit testing easy.

Most functions return a tuple:  (clean_value, error_message)
  - if the input is fine:   (value, None)
  - if the input is bad:    (None, "Meaningful error message")
"""
from datetime import datetime
from decimal import Decimal, InvalidOperation

from services.constants import (
    EXPENSE_CATEGORIES,
    INCOME_CATEGORY,
    MAX_AMOUNT,
    MAX_DESCRIPTION_LENGTH,
    MAX_TITLE_LENGTH,
    TYPE_EXPENSE,
    TYPE_INCOME,
)


def validate_amount(raw_amount):
    """Amount must be present, numeric, > 0, <= MAX_AMOUNT, max 2 decimal places."""
    if raw_amount is None or str(raw_amount).strip() == "":
        return None, "Amount is required."

    try:
        value = Decimal(str(raw_amount).strip())
    except InvalidOperation:
        return None, "Amount must be a valid number."

    if not value.is_finite():
        return None, "Amount must be a valid number."
    if value <= 0:
        return None, "Amount must be greater than zero."
    if value > MAX_AMOUNT:
        return None, f"Amount cannot be more than {MAX_AMOUNT:,}."
    if value.as_tuple().exponent < -2:
        return None, "Amount can have at most 2 decimal places."

    return float(value), None


def validate_date(raw_date):
    """Date must be present and in YYYY-MM-DD format (what the HTML date picker sends)."""
    if raw_date is None or str(raw_date).strip() == "":
        return None, "Date is required."

    try:
        parsed = datetime.strptime(str(raw_date).strip(), "%Y-%m-%d").date()
    except ValueError:
        return None, "Date must be a valid date in YYYY-MM-DD format."

    return parsed, None


def validate_required_text(raw_text, label, max_length=MAX_TITLE_LENGTH):
    """Required text field: cannot be blank, cannot be too long."""
    text = "" if raw_text is None else str(raw_text).strip()
    if text == "":
        return None, f"{label} is required."
    if len(text) > max_length:
        return None, f"{label} cannot be longer than {max_length} characters."
    return text, None


def validate_description(raw_description):
    """Description is optional but limited in length."""
    text = "" if raw_description is None else str(raw_description).strip()
    if len(text) > MAX_DESCRIPTION_LENGTH:
        return None, f"Description cannot be longer than {MAX_DESCRIPTION_LENGTH} characters."
    return text, None


def validate_category(raw_category):
    """Expense category must be one of the allowed categories."""
    category = "" if raw_category is None else str(raw_category).strip()
    if category == "":
        return None, "Category is required."
    if category not in EXPENSE_CATEGORIES:
        return None, "Please choose a valid category."
    return category, None


def validate_income_data(form):
    """
    Validate the Add Income form.
    `form` can be request.form or a plain dict.
    Returns (clean_data, errors). If `errors` is empty the data is safe to save.
    """
    errors = {}

    source, error = validate_required_text(form.get("source"), "Income source")
    if error:
        errors["source"] = error

    amount, error = validate_amount(form.get("amount"))
    if error:
        errors["amount"] = error

    parsed_date, error = validate_date(form.get("date"))
    if error:
        errors["date"] = error

    description, error = validate_description(form.get("description"))
    if error:
        errors["description"] = error

    clean_data = {}
    if not errors:
        clean_data = {
            "type": TYPE_INCOME,
            "title": source,
            "amount": amount,
            "category": INCOME_CATEGORY,
            "date": parsed_date,
            "description": description,
        }
    return clean_data, errors


def validate_expense_data(form):
    """Validate the Add Expense form. Same return shape as validate_income_data."""
    errors = {}

    title, error = validate_required_text(form.get("title"), "Expense title")
    if error:
        errors["title"] = error

    amount, error = validate_amount(form.get("amount"))
    if error:
        errors["amount"] = error

    category, error = validate_category(form.get("category"))
    if error:
        errors["category"] = error

    parsed_date, error = validate_date(form.get("date"))
    if error:
        errors["date"] = error

    description, error = validate_description(form.get("description"))
    if error:
        errors["description"] = error

    clean_data = {}
    if not errors:
        clean_data = {
            "type": TYPE_EXPENSE,
            "title": title,
            "amount": amount,
            "category": category,
            "date": parsed_date,
            "description": description,
        }
    return clean_data, errors
