import os
import sys
import tempfile

# Point the app at a throwaway DB BEFORE importing it (init_db runs at import).
os.environ["LAB_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "test_lab.db")
os.environ["APP_SECRET_KEY"] = "pytest-secret-key"
os.environ["PAYMENT_SECRET"] = "pytest-payment-secret"
os.environ["PAYMENT_WEBHOOK_SECRET"] = "pytest-webhook-secret"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402

import app as lab_app  # noqa: E402


@pytest.fixture()
def client():
    lab_app.app.config["TESTING"] = True
    return lab_app.app.test_client()


def get_csrf(client, path):
    import re

    html = client.get(path).get_data(as_text=True)
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert m, f"no csrf token found on {path}"
    return m.group(1)


def register(client, username, password="pw12345"):
    return client.post(
        "/register",
        data={
            "username": username,
            "password": password,
            "csrf_token": get_csrf(client, "/register"),
        },
    )


def login(client, username, password="pw12345"):
    return client.post(
        "/login",
        data={
            "username": username,
            "password": password,
            "csrf_token": get_csrf(client, "/login"),
        },
        follow_redirects=False,
    )


def register_and_login(client, username, password="pw12345"):
    register(client, username, password)
    r = login(client, username, password)
    assert r.status_code == 302, f"login failed for {username}: {r.status_code}"
