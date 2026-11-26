"""Double-entry ledger — every coin accounted for."""
import sqlite3, time, json, os

DB = os.path.join(os.path.dirname(__file__), '..', 'data', 'purchases.db')

SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  balance REAL NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS transactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts REAL NOT NULL,
  vendor TEXT NOT NULL,
  amount REAL NOT NULL,
  purpose TEXT NOT NULL,
  capability_tag TEXT,
  status TEXT NOT NULL DEFAULT 'pending',  -- pending|approved|settled|refunded|rejected
  meta TEXT DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  txn_id INTEGER NOT NULL REFERENCES transactions(id),
  account TEXT NOT NULL,
  debit REAL NOT NULL DEFAULT 0,
  credit REAL NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS budgets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  category TEXT UNIQUE NOT NULL,
  cap REAL NOT NULL,
  spent REAL NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS approvals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  txn_id INTEGER NOT NULL REFERENCES transactions(id),
  requested_ts REAL NOT NULL,
  decided_ts REAL,
  decision TEXT  -- approved|rejected
);
"""

def db():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    return c

def init_cash(amount=10000.0):
    c = db()
    if not c.execute("SELECT 1 FROM accounts WHERE name='cash'").fetchone():
        c.execute("INSERT INTO accounts(name,balance) VALUES('cash',?)", (amount,))
        c.commit()
    return c

def account_balance(c, name):
    r = c.execute("SELECT balance FROM accounts WHERE name=?", (name,)).fetchone()
    return r['balance'] if r else 0.0

def post_transaction(c, vendor, amount, purpose, capability_tag=None, meta=None):
    """Create pending txn + double entries. Returns txn_id."""
    cur = c.execute(
        "INSERT INTO transactions(ts,vendor,amount,purpose,capability_tag,meta) VALUES(?,?,?,?,?,?)",
        (time.time(), vendor, amount, purpose, capability_tag, json.dumps(meta or {})))
    txn_id = cur.lastrowid
    # cash credited (money leaves), vendor payable debited (obligation)
    c.execute("INSERT INTO entries(txn_id,account,debit,credit) VALUES(?,?,?,?)",
              (txn_id, 'cash', 0, amount))
    c.execute("INSERT INTO entries(txn_id,account,debit,credit) VALUES(?,?,?,?)",
              (txn_id, f'vendor:{vendor}', amount, 0))
    c.commit()
    return txn_id

def settle(c, txn_id):
    """Move vendor payable to expense; update cash + vendor accounts."""
    t = c.execute("SELECT * FROM transactions WHERE id=?", (txn_id,)).fetchone()
    if not t or t['status'] != 'pending':
        return False
    # cash balance decreases
    c.execute("UPDATE accounts SET balance=balance-? WHERE name='cash'", (t['amount'],))
    # vendor payable account closes to expense account
    c.execute("INSERT INTO accounts(name,balance) VALUES('expense:general',0) ON CONFLICT(name) DO NOTHING")
    c.execute("UPDATE accounts SET balance=balance+? WHERE name='expense:general'", (t['amount'],))
    c.execute("DELETE FROM accounts WHERE name=?", (f"vendor:{t['vendor']}",))
    c.execute("UPDATE transactions SET status='settled' WHERE id=?", (txn_id,))
    c.commit()
    return True

def reject(c, txn_id):
    c.execute("UPDATE transactions SET status='rejected' WHERE id=? AND status='pending'", (txn_id,))
    c.execute("DELETE FROM entries WHERE txn_id=?", (txn_id,))
    c.execute("DELETE FROM transactions WHERE id=?", (txn_id,))
    c.commit()

def check_balance(c):
    """Verify books balance: sum(debits)==sum(credits) across entries."""
    r = c.execute("SELECT COALESCE(SUM(debit),0) d, COALESCE(SUM(credit),0) cr FROM entries").fetchone()
    return abs(r['d'] - r['cr']) < 0.001

def spent_in_category(c, category):
    b = c.execute("SELECT spent FROM budgets WHERE category=?", (category,)).fetchone()
    return b['spent'] if b else 0.0

def set_budget(c, category, cap):
    c.execute("INSERT INTO budgets(category,cap,spent) VALUES(?,?,0) ON CONFLICT(category) DO UPDATE SET cap=?",
              (category, cap, cap))
    c.commit()

def charge_budget(c, category, amount):
    c.execute("UPDATE budgets SET spent=spent+? WHERE category=?", (amount, category))
    c.commit()

def request_approval(c, txn_id):
    c.execute("INSERT INTO approvals(txn_id,requested_ts) VALUES(?,?)", (txn_id, time.time()))
    c.commit()

def decide_approval(c, txn_id, approve):
    c.execute("UPDATE approvals SET decided_ts=?, decision=? WHERE txn_id=?",
              (time.time(), 'approved' if approve else 'rejected', txn_id))
    c.commit()

def pending_approvals(c):
    return c.execute("""SELECT a.id aid, a.txn_id, t.vendor, t.amount, t.purpose
                        FROM approvals a JOIN transactions t ON t.id=a.txn_id
                        WHERE a.decision IS NULL""").fetchall()

def status(c):
    cash = account_balance(c, 'cash')
    pending = c.execute("SELECT COUNT(*) n FROM transactions WHERE status='pending'").fetchone()['n']
    settled = c.execute("SELECT COALESCE(SUM(amount),0) s FROM transactions WHERE status='settled'").fetchone()['s']
    return {'cash': round(cash,2), 'pending_txns': pending,
            'total_spent': round(settled,2), 'books_balanced': check_balance(c)}
