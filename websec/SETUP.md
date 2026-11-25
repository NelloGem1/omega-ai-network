# Websec Lab — Setup & Run

One-command stack: Docker Compose in WSL Ubuntu.

## Start everything

    cd ~/websec_lab
    docker compose up -d

## Stop / restart

    docker compose stop        # stop, keep containers
    docker compose start       # start again
    docker compose down        # stop AND remove containers
    docker compose up -d --force-recreate   # pick up compose changes

Logs:

    docker compose logs -f juice-shop
    docker logs -f dvwa
    docker logs -f webgoat

## URLs

| Lab        | URL                              |
|------------|----------------------------------|
| Juice Shop | http://localhost:3000             |
| DVWA       | http://localhost:4280            |
| WebGoat    | http://localhost:18080/WebGoat    |
| WebWolf    | http://localhost:19090/WebWolf    |

Note: WebGoat uses host ports 18080/19090 (not 8080/9090) so it does NOT
collide with Burp Suite's default proxy listener on Windows 127.0.0.1:8080.
Access it from Windows via http://localhost:18080/WebGoat.

## First-run setup per lab

- Juice Shop: nothing — opens straight to the app. Scoreboard:
  http://localhost:3000/#/score-board
- DVWA: open http://localhost:4280/setup.php -> 'Create / Reset Database',
  then log in at http://localhost:4280/login.php (default admin/password).
- WebGoat: first boot is slow (Java, ~1-2 min). Register a user at
  http://localhost:18080/WebGoat/login — WebWolf on 19090 is its companion.

## Port conflicts

If a host port is busy, edit docker-compose.yml and remap the LEFT side:
  "4281:80" etc., then run: docker compose up -d --force-recreate

Known conflict handled: a native Juice Shop systemd user service
(juice-shop.service) was occupying :3000. It has been disabled via
  systemctl --user disable --now juice-shop.service
To re-enable the native copy instead of the container:
  systemctl --user enable --now juice-shop.service
and change the container's port mapping in docker-compose.yml.

## crAPI

Not included — crAPI is a heavy multi-service stack (identity/community/workshop
services + Postgres/Mongo/Kafka). If wanted later, see
https://github.com/OWASP/crAPI — add it as a separate compose project.

## Safety

These apps are intentionally vulnerable. Keep ports bound to localhost only,
never expose them, and only attack systems you are authorized to test.
