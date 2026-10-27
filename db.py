
import sqlite3
import hashlib
import secrets
from pathlib import Path
from contextlib import contextmanager

DB_NAME = Path(__file__).resolve().parent / "pocketpad.db"


@contextmanager
def connect_db():
    conn = sqlite3.connect(DB_NAME)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                category TEXT,
                amount REAL,
                type TEXT
            )
        """)

        columns = {
            row[1] for row in
            conn.execute("PRAGMA table_info(transactions)").fetchall()
        }

        if "user_id" not in columns:
            conn.execute(
                "ALTER TABLE transactions ADD COLUMN user_id INTEGER"
            )

        conn.execute("""
            CREATE TABLE IF NOT EXISTS monthly_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                month TEXT NOT NULL,
                expected_income REAL NOT NULL,
                expense_budget REAL NOT NULL,
                UNIQUE(user_id, month)
            )
        """)


def hash_password(password):
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 200000
    ).hex()
    return f"pbkdf2_sha256${salt}${hashed}"


def verify_password(password, saved_password):
    if saved_password.startswith("pbkdf2_sha256$"):
        try:
            _, salt, old_hash = saved_password.split("$")
            new_hash = hashlib.pbkdf2_hmac(
                "sha256", password.encode(), salt.encode(), 200000
            ).hex()
            return secrets.compare_digest(new_hash, old_hash)
        except ValueError:
            return False

    # Support passwords created by the older version.
    old_hash = hashlib.sha256(password.encode()).hexdigest()
    return secrets.compare_digest(old_hash, saved_password)


def signup(name, email, password):
    try:
        with connect_db() as conn:
            conn.execute(
                """INSERT INTO users (name, email, password)
                   VALUES (?, ?, ?)""",
                (name.strip(), email.strip().lower(),
                 hash_password(password))
            )
        return True
    except sqlite3.IntegrityError:
        return False


def login(email, password):
    with connect_db() as conn:
        user = conn.execute(
            """SELECT id, name, password FROM users
               WHERE email = ?""",
            (email.strip().lower(),)
        ).fetchone()

        if not user or not verify_password(password, user[2]):
            return None

        if not user[2].startswith("pbkdf2_sha256$"):
            conn.execute(
                "UPDATE users SET password = ? WHERE id = ?",
                (hash_password(password), user[0])
            )

        return user[0], user[1]


def save_monthly_plan(user_id, month, expected_income, expense_budget):
    with connect_db() as conn:
        conn.execute(
            """INSERT INTO monthly_plans
               (user_id, month, expected_income, expense_budget)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(user_id, month) DO UPDATE SET
               expected_income = excluded.expected_income,
               expense_budget = excluded.expense_budget""",
            (user_id, month, expected_income, expense_budget)
        )


def get_monthly_plan(user_id, month):
    with connect_db() as conn:
        return conn.execute(
            """SELECT expected_income, expense_budget
               FROM monthly_plans
               WHERE user_id = ? AND month = ?""",
            (user_id, month)
        ).fetchone()


def get_transactions(user_id):
    with connect_db() as conn:
        return conn.execute(
            """SELECT id, date, category, amount, type
               FROM transactions
               WHERE user_id = ?
               ORDER BY date DESC, id DESC""",
            (user_id,)
        ).fetchall()


def add_transaction(user_id, date, category, amount, t_type):
    with connect_db() as conn:
        conn.execute(
            """INSERT INTO transactions
               (user_id, date, category, amount, type)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, str(date), category, amount, t_type)
        )


def delete_transaction(transaction_id, user_id):
    with connect_db() as conn:
        conn.execute(
            """DELETE FROM transactions
               WHERE id = ? AND user_id = ?""",
            (transaction_id, user_id)
        )
