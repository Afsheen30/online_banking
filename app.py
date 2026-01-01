from flask import Flask, render_template, request, redirect, session
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- MYSQL CONNECTION ----------
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sharifunnisa123",   # change if different
        database="banking"
    )

# ---------- ROUTES ----------

@app.route("/")
def home():
    return redirect("/register")

# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        db = get_db()
        cur = db.cursor()

        cur.execute("""
            INSERT INTO users
            (fullname, email, phone, account_number, password, account_type, balance)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            request.form["fullname"],
            request.form["email"],
            request.form["phone"],
            request.form["account_number"],
            request.form["password"],
            request.form["account_type"],
            25000
        ))

        db.commit()
        cur.close()
        db.close()
        return redirect("/login")

    return render_template("register.html")

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        db = get_db()
        cur = db.cursor(dictionary=True)

        cur.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (request.form["email"], request.form["password"])
        )
        user = cur.fetchone()

        cur.close()
        db.close()

        if user:
            session["user_id"] = user["id"]
            return redirect("/dashboard")

    return render_template("login.html")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute(
        "SELECT * FROM users WHERE id=%s",
        (session["user_id"],)
    )
    user = cur.fetchone()

    cur.close()
    db.close()

    return render_template("dashboard.html", user=user)

# ---------- TRANSFER ----------
@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        amount = int(request.form["amount"])

        db = get_db()
        cur = db.cursor(dictionary=True)

        cur.execute(
            "SELECT balance FROM users WHERE id=%s",
            (session["user_id"],)
        )
        user = cur.fetchone()

        new_balance = user["balance"] - amount

        cur.execute(
            "UPDATE users SET balance=%s WHERE id=%s",
            (new_balance, session["user_id"])
        )

        cur.execute("""
            INSERT INTO transactions
            (user_id, amount, transaction_type, created_at)
            VALUES (%s,%s,%s,%s)
        """, (
            session["user_id"],
            amount,
            "DEBIT",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        db.commit()
        cur.close()
        db.close()

        return redirect("/transactions")

    return render_template("transfer.html")

# ---------- TRANSACTIONS ----------
@app.route("/transactions")
def transactions():
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute(
        "SELECT * FROM transactions WHERE user_id=%s ORDER BY id DESC",
        (session["user_id"],)
    )
    data = cur.fetchall()

    cur.close()
    db.close()

    return render_template("transactions.html", transactions=data)

# ---------- BENEFICIARY ----------
@app.route("/beneficiary", methods=["GET", "POST"])
def beneficiary():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        # values received but not stored yet
        beneficiary_name = request.form["beneficiary_name"]
        beneficiary_account = request.form["beneficiary_account"]
        return redirect("/dashboard")

    return render_template("beneficiary.html")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)