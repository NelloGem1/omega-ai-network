# WebSec Lab — Setup Guide (NelloGem)

Practice environment for learning web security / ethical hacking on
Windows 11 + WSL Ubuntu. All apps run **inside WSL Ubuntu**.

Last verified: 2026-11-25

---

## 1. What's installed

Docker Engine is running **natively inside WSL** (`dockerd` + `containerd`,
socket `/var/run/docker.sock`). The `docker` CLI is at `/usr/bin/docker`
and user `neilh` is in the `docker` group.

| App | URL | Port | Status |
|-----|-----|------|--------|
| OWASP Juice Shop (`bkimminich/juice-shop`) | http://localhost:3000 | 3000 | ✅ HTTP 200 |
| OWASP WebGoat (`webgoat/webgoat`) | http://localhost:18080/WebGoat | 18080 | ✅ HTTP 302→login |
| WebWolf (WebGoat companion, `webgoat/webgoat`) | http://localhost:19090 | 19090 | ✅ running |
| DVWA (`vulnerables/web-dvwa`) | http://localhost:4280 | 4280 | ✅ HTTP 302→login |
| NelloGem SubLab (Flask app, manual) | http://localhost:5000 | 5000 | ✅ verified HTTP 200 |

Container names: `juice-shop`, `webgoat`, `dvwa` (all `docker ps` visible,
restart policy enabled — they come back with Docker/WSL).

> Note: the `webgoat` container shows Docker status "unhealthy" — that's
> only because the image's healthcheck calls `curl`, which isn't installed
> in the container. The app itself works fine (verified HTTP 302).

---

## 2. Docker commands

```bash
docker ps                 # list running apps
docker ps -a              # include stopped
docker logs -f juice-shop # follow logs
docker restart dvwa       # restart one
docker stop webgoat       # stop one
docker start juice-shop   # start one
```

If `docker` ever says "permission denied", run `newgrp docker` or open a
new WSL shell (group membership was just added).

---

## 3. App details & credentials

### Juice Shop — http://localhost:3000
- No signup needed; open and start the tutorial or score board
  (`/#/score-board`)
- Admin login: `admin@juice-sh.op` / `admin123`
- ~100 challenges across all major vuln classes

### WebGoat — http://localhost:18080/WebGoat
- Self-register any username/password on first visit
- WebWolf (the "attacker" mailbox app): http://localhost:19090
  (login with the same credentials you register in WebGoat)

### DVWA — http://localhost:4280
- Login: `admin` / `password`
- Security level is set on the "DVWA Security" page after login
  (start at *low* / *medium* for learning)
- Database setup: click "Create / Reset Database" on the home page
  if you see DB errors

---

## 4. NelloGem SubLab — your audit target

- **Location:** `/home/neilh/websec_lab/app/`
- **Files:** `app.py` (secured version), `app_vulnerable.py`
  (original, every bug marked `# VULN:`), `schema.sql`,
  `requirements.txt`, `README.md`, `tests/`
- **Python:** `/home/neilh/venv` (Flask 3.1.3)

### Run it

```bash
cd /home/neilh/websec_lab/app
/home/neilh/venv/bin/python app.py        # secured version → :5000
/home/neilh/venv/bin/python app_vulnerable.py   # vulnerable version
```

> `app.py` and `app_vulnerable.py` both try to bind :5000 — run ONE at a
> time, or edit the `port=` in `app.run(...)` to use e.g. 5001 for the
> vulnerable copy so you can compare them side by side.

Demo account (auto-seeded): `demo` / `demo123`

### Intentional weaknesses (in `app_vulnerable.py`)

- SQL injection in `/register` and `/login`
- Plaintext password storage
- Weak hardcoded Flask `secret_key`
- Client-side "payment" — POST `payment_success=1` to `/upgrade`
- `/premium` trusts a session flag, not the DB
- Debug mode + verbose errors, no CSRF protection

`app.py` is the "fixed" version — diff the two files to see what each
`# VULN:` maps to.

---

## 5. Cheat sheet

```bash
# Health check everything
for p in 3000 18080 19090 4280; do
  curl -s -o /dev/null -w "port $p -> %{http_code}\n" http://localhost:$p
done

# Python deps live in ~/venv:
/home/neilh/venv/bin/python ...
/home/neilh/venv/bin/pip ...
```

## 6. Layout on disk

```
/home/neilh/websec_lab/
├── SETUP.md            ← this file
├── app/                ← your Flask subscription app (+ tests/)
└── tools/
    ├── juice-shop.tgz            (installer archive, can be deleted)
    ├── juice-shop_20.4.0-SNAPSHOT/ (manual install — unused, docker is canonical)
    ├── jre/                      (Temurin JRE 21 — unused, docker is canonical)
    └── webgoat/webgoat-2023.8.jar (manual install — unused, docker is canonical)
```

The `tools/` manual installs (~1 GB total) are kept as offline backups;
the Docker containers are what you should actually use. Safe to delete
`tools/` if you need disk space.
