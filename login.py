import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = "expense.db"


# ---------------- DATABASE CONNECTION ----------------

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- REGISTER ----------------

def register(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        hashed_password = generate_password_hash(password)

        cursor.execute(
            """
            INSERT INTO users (username, password)
            VALUES (?, ?)
            """,
            (username, hashed_password)
        )

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        print("Username already exists.")
        return False

    except Exception as e:
        print("REGISTER ERROR:", e)
        return False

    finally:
        conn.close()


# ---------------- LOGIN ----------------

def login(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, username, password
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    user = cursor.fetchone()

    conn.close()

    if user and check_password_hash(user["password"], password):
        return user

    return None


# ---------------- GET USER ----------------

def get_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    conn.close()

    return user


# ---------------- CHANGE PASSWORD ----------------

def change_password(user_id, new_password):
    conn = get_connection()
    cursor = conn.cursor()

    hashed_password = generate_password_hash(new_password)

    cursor.execute(
        """
        UPDATE users
        SET password = ?
        WHERE id = ?
        """,
        (hashed_password, user_id)
    )

    conn.commit()
    conn.close()

    return True