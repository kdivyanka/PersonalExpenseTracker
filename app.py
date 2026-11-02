"""
app.py - The Flask application: creates the app and defines every page (route).

Run it with:   python app.py      then open   http://127.0.0.1:5000

Each route follows the same simple pattern:
    1. read what the user sent (form / URL)
    2. call a function from services/ to do the real work
    3. show a template (HTML page) with the result
"""
import sqlite3
from datetime import date, datetime

from flask import Flask, flash, redirect, render_template, request, url_for

from config import Config
from models import close_db, init_db
from services import calculations as calc
from services import transaction_service as ts
from services.constants import EXPENSE_CATEGORIES, INCOME_CATEGORY


def create_app(config_object=Config):
    """Application factory: builds and returns a configured Flask app."""
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Close the DB connection after every request; create the table on startup.
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
        if app.config.get("LOAD_SAMPLE_DATA"):
            ts.seed_sample_data()

    register_template_helpers(app)
    register_routes(app)
    register_error_handlers(app)
    return app


def register_template_helpers(app):
    @app.template_filter("money")
    def money(value):
        """1234.5 -> '1,234.50'"""
        return f"{value:,.2f}"

    @app.context_processor
    def inject_globals():
        return {
            "currency": app.config["CURRENCY_SYMBOL"],
            "expense_categories": EXPENSE_CATEGORIES,
            "today_iso": date.today().isoformat(),
        }


def register_routes(app):
    # ------------------------------------------------------------ Dashboard
    @app.route("/")
    def dashboard():
        transactions = ts.get_all_transactions()
        today = date.today()

        category_breakdown = calc.calculate_category_breakdown(transactions)
        monthly_totals = calc.calculate_monthly_totals(transactions, limit=6)

        return render_template(
            "dashboard.html",
            total_income=calc.calculate_total_income(transactions),
            total_expenses=calc.calculate_total_expenses(transactions),
            available_balance=calc.calculate_available_balance(transactions),
            transaction_count=calc.count_transactions(transactions),
            recent_transactions=ts.get_recent_transactions(5),
            current_month=calc.calculate_monthly_summary(transactions, today.year, today.month),
            monthly_totals=monthly_totals,
            category_labels=[name for name, _ in category_breakdown],
            category_values=[total for _, total in category_breakdown],
            chart_months=[row["label"] for row in monthly_totals],
            chart_income=[row["income"] for row in monthly_totals],
            chart_expenses=[row["expenses"] for row in monthly_totals],
        )

    # ----------------------------------------------------------- Add Income
    @app.route("/add-income", methods=["GET", "POST"])
    def add_income():
        form_data, errors = {}, {}
        if request.method == "POST":
            form_data = request.form.to_dict()
            transaction_id, errors = ts.add_income(request.form)
            if transaction_id:
                flash(f"Income '{form_data['source'].strip()}' added successfully.", "success")
                return redirect(url_for("transactions"))
            if "database" in errors:
                flash(errors["database"], "danger")
        return render_template("add_income.html", form_data=form_data, errors=errors)

    # ---------------------------------------------------------- Add Expense
    @app.route("/add-expense", methods=["GET", "POST"])
    def add_expense():
        form_data, errors = {}, {}
        if request.method == "POST":
            form_data = request.form.to_dict()
            transaction_id, errors = ts.add_expense(request.form)
            if transaction_id:
                flash(f"Expense '{form_data['title'].strip()}' added successfully.", "success")
                return redirect(url_for("transactions"))
            if "database" in errors:
                flash(errors["database"], "danger")
        return render_template("add_expense.html", form_data=form_data, errors=errors)

    # ---------------------------------------------------- Transaction History
    @app.route("/transactions")
    def transactions():
        search_text = request.args.get("search", "").strip()
        type_filter = request.args.get("type", "all")
        category_filter = request.args.get("category", "all")
        sort = request.args.get("sort", "date_desc")

        results = ts.search_transactions(search_text, type_filter, category_filter, sort)
        return render_template(
            "transactions.html",
            transactions=results,
            filter_categories=EXPENSE_CATEGORIES + [INCOME_CATEGORY],
            search_text=search_text,
            type_filter=type_filter,
            category_filter=category_filter,
            sort=sort,
            filters_active=bool(search_text) or type_filter != "all" or category_filter != "all",
        )

    # ----------------------------------------------------- Delete Transaction
    @app.route("/transactions/<int:transaction_id>/delete", methods=["POST"])
    def delete_transaction(transaction_id):
        success, message = ts.delete_transaction(transaction_id)
        flash(message, "success" if success else "danger")
        return redirect(url_for("transactions"))

    # -------------------------------------------------------- Monthly Summary
    @app.route("/monthly-summary")
    def monthly_summary():
        today = date.today()
        selected = request.args.get("month", "").strip()
        year, month = today.year, today.month

        if selected:
            try:
                parsed = datetime.strptime(selected, "%Y-%m")
                year, month = parsed.year, parsed.month
            except ValueError:
                flash("Invalid month selected. Showing the current month instead.", "warning")

        transactions = ts.get_all_transactions()
        summary = calc.calculate_monthly_summary(transactions, year, month)
        monthly_totals = calc.calculate_monthly_totals(transactions)

        return render_template(
            "monthly_summary.html",
            summary=summary,
            selected_month=f"{year:04d}-{month:02d}",
            monthly_totals=monthly_totals,
            category_labels=[name for name, _ in summary["category_breakdown"]],
            category_values=[total for _, total in summary["category_breakdown"]],
            chart_months=[row["label"] for row in monthly_totals],
            chart_income=[row["income"] for row in monthly_totals],
            chart_expenses=[row["expenses"] for row in monthly_totals],
        )


def register_error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("error.html", code=404, message="That page does not exist."), 404

    @app.errorhandler(sqlite3.Error)
    def database_error(error):
        return render_template(
            "error.html", code=500, message="A database error occurred. Please try again."
        ), 500


if __name__ == "__main__":
    create_app().run(debug=True)
