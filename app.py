from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

import os
import sqlite3
from functools import wraps

from werkzeug.security import generate_password_hash, check_password_hash

from login import register, login
from database import create_database

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "expense_tracker_secret_key_2026"
)

DATABASE = "expense.db"

# ---------------- DATABASE CONNECTION ----------------

def get_connection():

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    return conn


# ---------------- LOGIN REQUIRED ----------------

def login_required(f):

    @wraps(f)

    def decorated_function(*args, **kwargs):

        if "user_id" not in session:

            flash("Please login first.", "warning")

            return redirect(url_for("home"))

        return f(*args, **kwargs)

    return decorated_function


# ---------------- HOME ----------------

@app.route("/")
def home():

    if "user_id" in session:

        return redirect(url_for("dashboard"))

    return render_template("index.html")


# ---------------- REGISTER PAGE ----------------

@app.route("/register")
def register_page():

    return render_template("register.html")


# ---------------- REGISTER USER ----------------

@app.route("/register_user", methods=["POST"])
def register_user():

    username = request.form["username"].strip()
    password = request.form["password"]

    success = register(username, password)

    if success:
        flash("Account created successfully! Please login.", "success")
        return redirect(url_for("home"))

    flash("Username already exists. Please choose another username.", "danger")
    return redirect(url_for("register_page"))


# ---------------- LOGIN ----------------

@app.route("/login_user", methods=["POST"])
def login_user():

    username = request.form["username"].strip()

    password = request.form["password"]

    user = login(username, password)

    if user:

        session["user_id"] = user["id"]

        session["username"] = user["username"]

        flash("Welcome back!", "success")

        return redirect(url_for("dashboard"))

    flash("Invalid Username or Password.", "danger")

    return redirect(url_for("home"))


# ---------------- LOGOUT ----------------

@app.route("/logout")
@login_required
def logout():

    session.clear()

    return redirect(url_for("home"))
# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
@login_required
def dashboard():

    conn = get_connection()
    cursor = conn.cursor()

    user_id = session["user_id"]


    # ---------------- TOTAL EXPENSE ----------------

    cursor.execute(
        """
        SELECT IFNULL(SUM(amount), 0)
        FROM expenses
        WHERE user_id=?
        """,
        (user_id,)
    )

    total_expense = cursor.fetchone()[0]


    # ---------------- TOTAL INCOME ----------------

    cursor.execute(
        """
        SELECT IFNULL(SUM(amount), 0)
        FROM income
        WHERE user_id=?
        """,
        (user_id,)
    )

    total_income = cursor.fetchone()[0]


    # ---------------- RECENT TRANSACTIONS ----------------

    cursor.execute(
        """
        SELECT title,
               category,
               amount,
               date
        FROM expenses
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 5
        """,
        (user_id,)
    )

    transactions = cursor.fetchall()


    # ---------------- EXPENSE BY CATEGORY ----------------

    cursor.execute(
        """
        SELECT category,
               IFNULL(SUM(amount), 0)
        FROM expenses
        WHERE user_id=?
        GROUP BY category
        ORDER BY SUM(amount) DESC
        """,
        (user_id,)
    )

    category_data = cursor.fetchall()


    # ---------------- CLOSE DATABASE ----------------

    conn.close()


    # ---------------- CALCULATIONS ----------------

    balance = total_income - total_expense

    savings = balance


    # ---------------- SEND DATA TO DASHBOARD ----------------

    return render_template(
        "dashboard.html",

        username=session["username"],

        income=total_income,

        expense=total_expense,

        balance=balance,

        savings=savings,

        transactions=transactions,

        category_data=category_data
    )

# ---------------- ADD INCOME ----------------

@app.route("/add_income")
@login_required
def add_income():

    return render_template("add_income.html")

# ---------------- SAVE INCOME ----------------

@app.route("/save_income", methods=["POST"])
@login_required
def save_income():

    title = request.form["title"].strip()
    category = request.form["category"]
    amount = request.form["amount"]
    date = request.form["date"]
    description = request.form["description"].strip()

    if title == "":
        flash("Income title cannot be empty.", "danger")
        return redirect(url_for("add_income"))

    try:
        amount = float(amount)

        if amount <= 0:
            flash("Amount must be greater than zero.", "danger")
            return redirect(url_for("add_income"))

    except ValueError:
        flash("Invalid amount.", "danger")
        return redirect(url_for("add_income"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO income
        (user_id, title, category, amount, date, description)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            title,
            category,
            amount,
            date,
            description
        )
    )

    conn.commit()
    conn.close()

    flash("Income added successfully.", "success")

    return redirect(url_for("dashboard"))

# ---------------- INCOME HISTORY ----------------

@app.route("/income_history")
@login_required
def income_history():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            title,
            category,
            amount,
            date,
            description
        FROM income
        WHERE user_id=?
        ORDER BY date DESC, id DESC
        """,
        (session["user_id"],)
    )

    incomes = cursor.fetchall()

    conn.close()

    return render_template(
        "income_history.html",
        incomes=incomes
    )
# ---------------- REPORTS ----------------

@app.route("/reports")
@login_required
def reports():

    conn = get_connection()
    cursor = conn.cursor()

    user_id = session["user_id"]

    selected_filter = request.args.get("filter", "all")

    # ---------------- FILTER CONDITION ----------------

    expense_condition = "WHERE user_id=?"
    income_condition = "WHERE user_id=?"

    params = [user_id]

    if selected_filter == "today":
        expense_condition += " AND date = DATE('now','localtime')"
        income_condition += " AND date = DATE('now','localtime')"

    elif selected_filter == "month":
        expense_condition += " AND strftime('%Y-%m', date)=strftime('%Y-%m','now','localtime')"
        income_condition += " AND strftime('%Y-%m', date)=strftime('%Y-%m','now','localtime')"

    elif selected_filter == "year":
        expense_condition += " AND strftime('%Y', date)=strftime('%Y','now','localtime')"
        income_condition += " AND strftime('%Y', date)=strftime('%Y','now','localtime')"

    # ---------------- TOTAL EXPENSE ----------------

    cursor.execute(
        f"""
        SELECT IFNULL(SUM(amount),0)
        FROM expenses
        {expense_condition}
        """,
        params
    )

    total_expense = cursor.fetchone()[0]

    # ---------------- TOTAL INCOME ----------------

    cursor.execute(
        f"""
        SELECT IFNULL(SUM(amount),0)
        FROM income
        {income_condition}
        """,
        params
    )

    total_income = cursor.fetchone()[0]

    # Expense Category Data
    cursor.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        WHERE user_id=?
        GROUP BY category
    """, (user_id,))

    category_data = cursor.fetchall()

    # ---------------- MONTHLY EXPENSE DATA ----------------

    cursor.execute("""
    SELECT
        strftime('%m', date) AS month,
        SUM(amount)
    FROM expenses
    WHERE user_id=?
    GROUP BY strftime('%m', date)
    ORDER BY strftime('%m', date)
""", (user_id,))

    monthly_data = cursor.fetchall()

    conn.close()

    labels = []
    values = []

    for row in category_data:
        labels.append(row[0])
        values.append(row[1])

    month_labels = []
    month_values = []

    month_names = {
        "01": "Jan",
        "02": "Feb",
        "03": "Mar",
        "04": "Apr",
        "05": "May",
        "06": "Jun",
        "07": "Jul",
        "08": "Aug",
        "09": "Sep",
        "10": "Oct",
        "11": "Nov",
        "12": "Dec"
    }

    for row in monthly_data:
        month_labels.append(month_names.get(row[0], row[0]))
        month_values.append(row[1])

    balance = total_income - total_expense
    savings = balance

    return render_template(
        "reports.html",
        income=total_income,
        expense=total_expense,
        balance=balance,
        savings=savings,
        labels=labels,
        values=values,
        month_labels=month_labels,
        month_values=month_values,
        selected_filter=selected_filter
    )
# ---------------- PROFILE ----------------

@app.route("/profile")
@login_required
def profile():

    conn = get_connection()
    cursor = conn.cursor()

    user_id = session["user_id"]

    # Total Income
    cursor.execute("""
        SELECT IFNULL(SUM(amount),0)
        FROM income
        WHERE user_id=?
    """, (user_id,))
    total_income = cursor.fetchone()[0]

    # Total Expense
    cursor.execute("""
        SELECT IFNULL(SUM(amount),0)
        FROM expenses
        WHERE user_id=?
    """, (user_id,))
    total_expense = cursor.fetchone()[0]

    conn.close()

    balance = total_income - total_expense

    return render_template(
        "profile.html",
        username=session["username"],
        income=total_income,
        expense=total_expense,
        balance=balance
    )
# ---------------- SETTINGS ----------------

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():

    if request.method == "POST":

        old_password = request.form["old_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        conn = get_connection()
        cursor = conn.cursor()

        # Get current password from database
        cursor.execute(
            """
            SELECT password
            FROM users
            WHERE id=?
            """,
            (session["user_id"],)
        )

        user = cursor.fetchone()

        # Check current password
        if user and check_password_hash(user[0], old_password):

            # Check whether new passwords match
            if new_password != confirm_password:

                conn.close()

                flash(
                    "New Password and Confirm Password do not match.",
                    "danger"
                )

                return redirect(url_for("settings"))

            # Minimum password length
            if len(new_password) < 8:

                conn.close()

                flash(
                    "Password must be at least 8 characters long.",
                    "danger"
                )

                return redirect(url_for("settings"))

            # Hash new password
            new_hash = generate_password_hash(new_password)

            # Update password
            cursor.execute(
                """
                UPDATE users
                SET password=?
                WHERE id=?
                """,
                (new_hash, session["user_id"])
            )

            conn.commit()
            conn.close()

            flash(
                "Password updated successfully!",
                "success"
            )

            return redirect(url_for("settings"))

        else:

            conn.close()

            flash(
                "Current password is incorrect.",
                "danger"
            )

            return redirect(url_for("settings"))

    return render_template("settings.html")

# ---------------- EDIT INCOME ----------------

@app.route("/edit_income/<int:income_id>", methods=["GET", "POST"])
@login_required
def edit_income(income_id):

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        title = request.form["title"].strip()
        category = request.form["category"]
        amount = request.form["amount"]
        date = request.form["date"]
        description = request.form["description"].strip()

        if title == "":
            flash("Title cannot be empty.", "danger")
            conn.close()
            return redirect(url_for("edit_income", income_id=income_id))

        try:
            amount = float(amount)

            if amount <= 0:
                flash("Amount must be greater than zero.", "danger")
                conn.close()
                return redirect(url_for("edit_income", income_id=income_id))

        except ValueError:
            flash("Invalid amount.", "danger")
            conn.close()
            return redirect(url_for("edit_income", income_id=income_id))

        cursor.execute(
            """
            UPDATE income
            SET title=?,
                category=?,
                amount=?,
                date=?,
                description=?
            WHERE id=? AND user_id=?
            """,
            (
                title,
                category,
                amount,
                date,
                description,
                income_id,
                session["user_id"]
            )
        )

        conn.commit()
        conn.close()

        flash("Income updated successfully.", "success")

        return redirect(url_for("income_history"))

    cursor.execute(
        """
        SELECT *
        FROM income
        WHERE id=? AND user_id=?
        """,
        (
            income_id,
            session["user_id"]
        )
    )

    income = cursor.fetchone()

    conn.close()

    if income is None:
        flash("Income not found.", "danger")
        return redirect(url_for("income_history"))
                
    return render_template(
        "edit_income.html",
        income=income
    )


# ---------------- DELETE INCOME ----------------

@app.route("/delete_income/<int:income_id>")
@login_required
def delete_income(income_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM income
        WHERE id=? AND user_id=?
        """,
        (
            income_id,
            session["user_id"]
        )
    )

    conn.commit()
    conn.close()

    flash("Income deleted successfully.", "success")

    return redirect(url_for("income_history"))
# ---------------- ADD EXPENSE ----------------

@app.route("/add_expense")
@login_required
def add_expense():

    return render_template("add_expense.html")


# ---------------- SAVE EXPENSE ----------------

@app.route("/save_expense", methods=["POST"])
@login_required
def save_expense():

    title = request.form["title"].strip()
    category = request.form["category"]
    amount = request.form["amount"]
    date = request.form["date"]
    description = request.form["description"].strip()

    # Validation

    if title == "":
        flash("Expense title cannot be empty.", "danger")
        return redirect(url_for("add_expense"))

    try:
        amount = float(amount)

        if amount <= 0:
            flash("Amount must be greater than zero.", "danger")
            return redirect(url_for("add_expense"))

    except ValueError:

        flash("Invalid amount.", "danger")
        return redirect(url_for("add_expense"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO expenses
        (user_id,title,category,amount,date,description)
        VALUES (?,?,?,?,?,?)
        """,
        (
            session["user_id"],
            title,
            category,
            amount,
            date,
            description
        )
    )

    conn.commit()
    conn.close()

    flash("Expense added successfully.", "success")

    return redirect(url_for("expense_history"))


# ---------------- EXPENSE HISTORY ----------------

@app.route("/expense_history")
@login_required
def expense_history():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            title,
            category,
            amount,
            date,
            description
        FROM expenses
        WHERE user_id=?
        ORDER BY date DESC,id DESC
        """,
        (
            session["user_id"],
        )
    )

    expenses = cursor.fetchall()

    conn.close()

    return render_template(
        "expense_history.html",
        expenses=expenses
    )
# ---------------- EDIT EXPENSE ----------------

@app.route("/edit_expense/<int:expense_id>", methods=["GET", "POST"])
@login_required
def edit_expense(expense_id):

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        title = request.form["title"].strip()
        category = request.form["category"]
        amount = request.form["amount"]
        date = request.form["date"]
        description = request.form["description"].strip()

        if title == "":
            flash("Title cannot be empty.", "danger")
            conn.close()
            return redirect(url_for("edit_expense", expense_id=expense_id))

        try:
            amount = float(amount)

            if amount <= 0:
                flash("Amount must be greater than zero.", "danger")
                conn.close()
                return redirect(url_for("edit_expense", expense_id=expense_id))

        except ValueError:
            flash("Invalid amount.", "danger")
            conn.close()
            return redirect(url_for("edit_expense", expense_id=expense_id))

        cursor.execute(
            """
            UPDATE expenses
            SET title=?,
                category=?,
                amount=?,
                date=?,
                description=?
            WHERE id=? AND user_id=?
            """,
            (
                title,
                category,
                amount,
                date,
                description,
                expense_id,
                session["user_id"]
            )
        )

        conn.commit()
        conn.close()

        flash("Expense updated successfully.", "success")

        return redirect(url_for("expense_history"))

    cursor.execute(
        """
        SELECT *
        FROM expenses
        WHERE id=? AND user_id=?
        """,
        (
            expense_id,
            session["user_id"]
        )
    )

    expense = cursor.fetchone()

    conn.close()

    if expense is None:
        flash("Expense not found.", "danger")
        return redirect(url_for("expense_history"))

    return render_template(
        "edit_expense.html",
        expense=expense
    )


# ---------------- DELETE EXPENSE ----------------

@app.route("/delete_expense/<int:expense_id>")
@login_required
def delete_expense(expense_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM expenses
        WHERE id=? AND user_id=?
        """,
        (
            expense_id,
            session["user_id"]
        )
    )

    conn.commit()
    conn.close()

    flash("Expense deleted successfully.", "success")

    return redirect(url_for("expense_history"))


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    create_database()

    app.run(
        debug=True
    )