"""
init_db.py - Creates the database file and table.

  python init_db.py             -> creates an empty database
  python init_db.py --sample    -> also adds sample transactions (only if empty)

You do NOT have to run this: the app creates the database by itself on first start.
It is provided so you can set up the database on purpose (e.g. before running tests).
"""
import sys

from app import create_app
from models import init_db
from services.transaction_service import seed_sample_data


def main():
    app = create_app()
    with app.app_context():
        init_db()
        print(f"Database ready: {app.config['DATABASE_PATH']}")
        if "--sample" in sys.argv:
            inserted = seed_sample_data()
            print(f"Sample transactions added: {inserted}")


if __name__ == "__main__":
    main()
