# NelloGem SubLab — vulnerable subscription app

A deliberately insecure Flask app for practicing web-security audits.
It is intentionally full of beginner-realistic bugs — each one is marked
with a `# VULN:` comment in `app.py` so you have targets to find.

## Run it

```bash
cd /home/neilh/websec_lab/app
python3 -m venv .venv          # or reuse ~/venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000

A demo account is seeded on first run: `demo` / `demo123` (free plan).

## What's inside

- `/register`, `/login` — account creation & login
- `/status` — shows your plan + session flags
- `/upgrade` — "mock payment" that should grant premium
- `/premium` — premium-only page with secret content

## Suggested audit exercises

1. Register two accounts and try the upgrade flow.
2. Look at how `/premium` decides access — can you get in without paying?
3. Try the login form with unusual input.
4. Check what the browser actually sends to `/upgrade`.
5. Read `app.py` and map each `# VULN:` comment to a real attack.
