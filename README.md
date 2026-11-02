# Personal Expense Tracker

A Flask + SQLite web app (Software Testing Methodologies assignment).
Runs locally. No cloud, Docker or external hosting needed.

## 1. Run it (Windows, VS Code)

1. Install Python 3.10+ from python.org (tick "Add Python to PATH").
2. Unzip this folder, then in VS Code: **File > Open Folder** > `PersonalExpenseTracker`.
3. Open the terminal: **Terminal > New Terminal** (PowerShell).
4. Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

   If PowerShell blocks the script, run once:
   `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, or use Command Prompt: `venv\Scripts\activate.bat`

5. Install dependencies: `pip install -r requirements.txt`
6. (Optional) Create the database yourself: `python init_db.py`
   Add sample data too: `python init_db.py --sample`
   (The app also creates the database automatically on first start.)
7. Start the app: `python app.py`
8. Open **http://127.0.0.1:5000** in your browser. Stop with `Ctrl + C`.

In VS Code press `Ctrl+Shift+P` > "Python: Select Interpreter" > choose the one inside `venv`.

Note: the pages load Bootstrap, Chart.js and a Google font from the internet (CDN), so you need internet for styling and charts.

## 2. Files explained

| File | Purpose |
|---|---|
| `app.py` | Creates the Flask app and defines all pages (routes) |
| `config.py` | Settings: database path, secret key, currency symbol, test settings |
| `models.py` | Database table definition and connection helpers (SQLite) |
| `init_db.py` | Optional script to create the database / add sample data |
| `services/constants.py` | Shared values: categories, limits, type names |
| `services/validation.py` | Input checks (pure functions, easy to unit test) |
| `services/calculations.py` | Totals, balance, monthly summaries (pure functions) |
| `services/transaction_service.py` | Add, search, delete records in the database |
| `templates/` | HTML pages (Jinja2) |
| `static/css/style.css` | Styling |
| `static/js/script.js` | Charts and delete confirmation |
| `instance/expense_tracker.db` | The SQLite database (created automatically) |

## 3. Routes

| URL | Page |
|---|---|
| `/` | Dashboard |
| `/add-income` | Add Income (GET shows form, POST saves) |
| `/add-expense` | Add Expense |
| `/transactions` | History. Query: `search`, `type`, `category`, `sort` (`date_desc`/`date_asc`) |
| `/transactions/<id>/delete` | Delete (POST only) |
| `/monthly-summary?month=YYYY-MM` | Monthly Summary |

## 4. Verify every feature (manual checklist)

1. Open the app with an empty database: all pages load, totals show 0.00, charts show "no data" notes.
2. **Add Income**: submit with empty fields. Expect red messages ("Income source is required.", "Amount is required.", "Date is required."). Then add Salary, 50000, today. Expect a green success message and the record in Transactions.
3. **Add Expense**: try amount `0`, `-5`, `abc`, `10.555` (each shows an error). Leave category empty (error). Then add Groceries, 1200, Food.
4. **Dashboard**: totals, balance and transaction count match what you entered; both charts appear.
5. **Transactions**: search "gro", filter Type = Expense, filter Category = Food, sort Oldest first, press Reset.
6. **Delete**: click Delete, confirm the popup, the row disappears and the dashboard updates.
7. **Monthly Summary**: pick the month, check income/expenses/savings and the category table.

## 5. Testing hooks (for pytest and Selenium later)

- Unit tests: `services/validation.py` and `services/calculations.py` need no database or Flask.
- Integration tests: `from app import create_app` and `from config import TestConfig`, then
  `app = create_app(TestConfig)` and `client = app.test_client()`. This uses `instance/test_expense_tracker.db`, not your real data.
  Delete that file between tests for a clean start.
- System tests (Selenium): start the app, then use these IDs.

| Page | Element IDs |
|---|---|
| Sidebar | `nav-dashboard`, `nav-add-income`, `nav-add-expense`, `nav-transactions`, `nav-monthly-summary` |
| All pages | `page-heading` (h1), `flash-success`, `flash-danger`, `flash-warning` |
| Dashboard | `total-income`, `total-expenses`, `available-balance`, `transaction-count`, `recent-transactions-table`, `category-chart`, `income-expense-chart`, `month-income`, `month-expenses`, `month-savings` |
| Add Income | `income-form`, `income-source`, `income-amount`, `income-date`, `income-description`, `income-submit`, `form-error-summary`, `error-income-source`, `error-income-amount`, `error-income-date` |
| Add Expense | `expense-form`, `expense-title`, `expense-amount`, `expense-category`, `expense-date`, `expense-description`, `expense-submit`, `error-expense-title`, `error-expense-amount`, `error-expense-category`, `error-expense-date` |
| Transactions | `search-input`, `filter-type`, `filter-category`, `sort-date`, `apply-filters-btn`, `reset-filters-btn`, `result-count`, `transactions-table`, `transaction-row-<id>`, `delete-btn-<id>`, `no-transactions-message` |
| Monthly Summary | `month-select`, `view-month-btn`, `selected-month-label`, `summary-income`, `summary-expenses`, `summary-savings`, `category-breakdown-table`, `monthly-overview-table` |

Page titles: "Dashboard | Personal Expense Tracker", "Add Income | ...", "Add Expense | ...", "Transaction History | ...", "Monthly Summary | ...".

Selenium tips:
- Delete shows a browser confirm popup: use `driver.switch_to.alert.accept()`.
- Forms use `novalidate`, so validation messages come from the server and always appear.
- Date inputs: setting the value with JavaScript is more reliable than `send_keys`, e.g.
  `driver.execute_script("arguments[0].value='2026-11-01'", date_input)`.
- Install test tools later with `pip install -r requirements-dev.txt`.

## 6. Troubleshooting

| Problem | Fix |
|---|---|
| `python` is not recognized | Reinstall Python and tick "Add Python to PATH", or try `py` instead of `python` |
| `Activate.ps1 cannot be loaded` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, or use `venv\Scripts\activate.bat` |
| `ModuleNotFoundError: No module named 'flask'` | Activate the venv, then `pip install -r requirements.txt` |
| `Address already in use` / port 5000 busy | Close the other app, or change the last line of `app.py` to `.run(debug=True, port=5001)` |
| Charts or styling missing | You are offline: the CDN files could not load. Connect to the internet |
| `unable to open database file` | Make sure the `instance` folder exists and the folder is not read-only |
| Want a fresh start | Stop the app and delete `instance/expense_tracker.db` (a new one is created) |
| Want sample data | `python init_db.py --sample` (only inserts when the table is empty) |
| VS Code underlines imports | Select the venv interpreter (`Ctrl+Shift+P` > Python: Select Interpreter) |

## 7. Notes

- The currency symbol is `CURRENCY_SYMBOL` in `config.py`.
- Database access uses Python's built-in `sqlite3` module (no extra install, simple to read).
- Forms have no CSRF token, to keep Selenium tests simple. Add Flask-WTF if you ever deploy this publicly.
