"""
NelloGem WebSec Lab - vulnerable subscription app (practice target).
Run:  pip install -r requirements.txt && python app.py
Then: http://localhost:5000
"""
import sqlite3
import os
from flask import Flask, request, session, redirect, url_for, render_template_string

app = Flask(__name__)
# VULN: hardcoded, weak secret key -> session cookies can be forged/brute-forced
app.secret_key = "dev-secret-change-me"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "lab.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    with open(os.path.join(BASE_DIR, "schema.sql")) as f:
        conn.executescript(f.read())
    # seed a demo user if none exist
    if conn.execute("SELECT COUNT(*) c FROM users").fetchone()["c"] == 0:
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("demo", "demo123", "free"),
        )
        conn.execute(
            "INSERT INTO subscriptions (user_id, plan, status) VALUES (1, 'free', 'active')"
        )
        conn.commit()
    conn.close()


init_db()

PAGE = """<!doctype html>
<html><head><title>NelloGem SubLab</title></head>
<body>
<h1>NelloGem SubLab</h1>
{% if user %}<p>Logged in as <b>{{ user.username }}</b> (role: {{ user.role }})</p>{% endif %}
<nav>
<a href="/">home</a> |
<a href="/register">register</a> |
<a href="/login">login</a> |
<a href="/status">status</a> |
<a href="/upgrade">upgrade</a> |
<a href="/premium">premium</a> |
<a href="/logout">logout</a>
</nav>
<hr>
{{ body|safe }}
</body></html>"""


def page(body, user=None):
    return render_template_string(PAGE, body=body, user=user)


def current_user():
    username = session.get("username")
    if not username:
        return None
    conn = get_db()
    u = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return u


@app.route("/")
def home():
    u = current_user()
    return page("<h2>Welcome to the subscription lab.</h2><p>Sign up, log in, and try the premium tier.</p>", u)


@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        # VULN: plaintext password storage (no hashing) - see also login below
        try:
            conn = get_db()
            cur = conn.execute(
                # VULN: string-built SQL -> SQL injection via username/password fields
                "INSERT INTO users (username, password, role) VALUES ('%s', '%s', 'free')"
                % (username, password)
            )
            conn.execute(
                "INSERT INTO subscriptions (user_id, plan, status) VALUES (?, 'free', 'active')",
                (cur.lastrowid,),
            )
            conn.commit()
            conn.close()
            return page("<p>Registered! <a href='/login'>Log in</a></p>")
        except sqlite3.IntegrityError:
            msg = "<p style='color:red'>Username already taken.</p>"
        except Exception as e:
            # VULN: verbose error messages leak internals (SQL errors, paths)
            msg = f"<p style='color:red'>Error: {e}</p>"
    form = """<h2>Register</h2>
    <form method="post">
    Username: <input name="username"><br>
    Password: <input name="password" type="password"><br>
    <button type="submit">Sign up</button></form>""" + msg
    return page(form)


@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        conn = get_db()
        # VULN: SQL injection in login -> auth bypass e.g. ' OR '1'='1
        row = conn.execute(
            "SELECT * FROM users WHERE username = '%s' AND password = '%s'"
            % (username, password)
        ).fetchone()
        conn.close()
        if row:
            # VULN: privilege/role taken straight from DB but client can influence
            # session contents elsewhere; also no password hashing anywhere
            session["username"] = row["username"]
            # VULN: client-controllable session flag (also settable via cookie tampering)
            session["is_premium"] = (row["role"] == "premium")
            session["role"] = row["role"]
            return redirect(url_for("status"))
        msg = "<p style='color:red'>Invalid credentials.</p>"
    form = """<h2>Login</h2>
    <form method="post">
    Username: <input name="username"><br>
    Password: <input name="password" type="password"><br>
    <button type="submit">Log in</button></form>""" + msg
    return page(form)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/status")
def status():
    u = current_user()
    if not u:
        return page("<p>Please <a href='/login'>log in</a> first.</p>")
    conn = get_db()
    sub = conn.execute(
        "SELECT * FROM subscriptions WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (u["id"],),
    ).fetchone()
    conn.close()
    plan = sub["plan"] if sub else "free"
    body = f"""<h2>Subscription status</h2>
    <p>Plan: <b>{plan}</b></p>
    <p>Session premium flag: <b>{session.get('is_premium')}</b></p>
    <p>Session role: <b>{session.get('role')}</b></p>
    <p><a href="/upgrade">Upgrade to Premium ($9.99/mo)</a></p>"""
    return page(body, u)


@app.route("/upgrade", methods=["GET", "POST"])
def upgrade():
    u = current_user()
    if not u:
        return page("<p>Please <a href='/login'>log in</a> first.</p>")
    if request.method == "GET":
        return page("""<h2>Upgrade to Premium</h2>
        <p>Premium content: ad-free, early access, SECRET_RECIPE_42.</p>
        <form method="post">
        <!-- VULN: "payment" is entirely client-side; no gateway, no verification -->
        <input type="hidden" name="payment_success" value="1">
        <button type="submit">Pay $9.99 (mock)</button>
        </form>""", u)
    # VULN: trusts client-supplied flag - anyone can POST payment_success=1
    # (or just skip the form entirely) and get premium without paying.
    paid = request.form.get("payment_success") == "1"
    if paid:
        conn = get_db()
        conn.execute(
            "UPDATE users SET role = 'premium' WHERE id = ?", (u["id"],)
        )
        conn.execute(
            "UPDATE subscriptions SET plan = 'premium', status = 'active' WHERE user_id = ?",
            (u["id"],),
        )
        conn.execute(
            "INSERT INTO payments (user_id, amount_cents) VALUES (?, 999)",
            (u["id"],),
        )
        conn.commit()
        conn.close()
        session["is_premium"] = True
        session["role"] = "premium"
        return page("<p>Payment successful! You are now PREMIUM.</p><a href='/premium'>View premium content</a>", u)
    return page("<p>Payment failed/cancelled.</p><a href='/upgrade'>Try again</a>", u)


@app.route("/premium")
def premium():
    u = current_user()
    if not u:
        return page("<p>Please <a href='/login'>log in</a> first.</p>")
    # VULN: authorization decided ONLY by a session flag the client may influence
    # (cookie tampering / weak secret key). Never re-checks the DB role here.
    if not session.get("is_premium"):
        return page("<h2>Premium content</h2><p style='color:red'>403 - Premium members only. <a href='/upgrade'>Upgrade</a></p>", u)
    body = """<h2>Premium content</h2>
    <p>SECRET_RECIPE_42: the secret ingredient is <b>unlimited retries</b>.</p>
    <p>Premium roadmap: quantum billing, AI support, and more.</p>"""
    return page(body, u)


if __name__ == "__main__":
    # VULN: debug mode on + no CSRF protection anywhere
    app.run(host="127.0.0.1", port=5000, debug=True)
