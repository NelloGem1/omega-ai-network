# Docker Setup in WSL Ubuntu

Docker Engine is installed inside WSL Ubuntu and verified working.

## Installed versions

- Docker Engine: `29.1.3` (`docker.io` Ubuntu package)
- Docker Compose: `2.40.3` (`docker compose` plugin via `docker-compose-v2` Ubuntu package)
- User `neilh` has been added to the `docker` group.

## Verify Docker

Run these inside WSL Ubuntu as `neilh`:

```bash
docker --version
docker compose version
docker ps
docker run --rm hello-world
```

Expected result: `hello-world` prints `Hello from Docker!`.

## Start/stop Docker in WSL

WSL has systemd enabled (`/etc/wsl.conf` contains `systemd=true`), so Docker can be managed with systemd:

```bash
# start
sudo systemctl start docker

# stop
sudo systemctl stop docker

# status
sudo systemctl status docker --no-pager

# follow logs
sudo journalctl -u docker -f
```

Ubuntu's service wrapper also works:

```bash
sudo service docker start
sudo service docker status
```

Docker is enabled to start automatically with systemd, but WSL only runs services while the distro is running.

## Run OWASP Juice Shop

```bash
docker run -d --name juice-shop -p 3000:3000 bkimminich/juice-shop
```

Open: `http://localhost:3000`

Useful commands:

```bash
docker logs -f juice-shop
docker stop juice-shop
docker start juice-shop
docker rm juice-shop
```

## Run DVWA

```bash
docker run -d --name dvwa -p 80:80 vulnerables/web-dvwa
```

Open: `http://localhost/setup.php`

DVWA requires one-time database setup through the browser. After setup, log in with the default credentials shown by DVWA.

Useful commands:

```bash
docker logs -f dvwa
docker stop dvwa
docker start dvwa
docker rm dvwa
```

If port 80 is already used on Windows/WSL, choose another host port:

```bash
docker run -d --name dvwa -p 8081:80 vulnerables/web-dvwa
```

Then open `http://localhost:8081/setup.php`.

## Run WebGoat

WebGoat is pulled as well. Start it with:

```bash
docker run -d --name webgoat \
  -p 127.0.0.1:8080:8080 \
  -p 127.0.0.1:9090:9090 \
  webgoat/webgoat
```

Open: `http://127.0.0.1:8080/WebGoat`

WebWolf is available on port `9090`. Create a user from the WebGoat login page.

## Docker Compose examples

Create `~/websec_research/juice-shop.compose.yml`:

```yaml
services:
  juice-shop:
    image: bkimminich/juice-shop:latest
    container_name: juice-shop
    ports:
      - "3000:3000"
    restart: unless-stopped
```

Run it:

```bash
cd ~/websec_research
docker compose -f juice-shop.compose.yml up -d
docker compose -f juice-shop.compose.yml logs -f
```

Create `~/websec_research/dvwa.compose.yml`:

```yaml
services:
  dvwa:
    image: vulnerables/web-dvwa:latest
    container_name: dvwa
    ports:
      - "80:80"
    restart: unless-stopped
```

Run it:

```bash
cd ~/websec_research
docker compose -f dvwa.compose.yml up -d
docker compose -f dvwa.compose.yml logs -f
```

Create `~/websec_research/webgoat.compose.yml`:

```yaml
services:
  webgoat:
    image: webgoat/webgoat:latest
    container_name: webgoat
    ports:
      - "127.0.0.1:8080:8080"
      - "127.0.0.1:9090:9090"
    environment:
      TZ: Europe/Amsterdam
    restart: unless-stopped
```

Run it:

```bash
cd ~/websec_research
docker compose -f webgoat.compose.yml up -d
docker compose -f webgoat.compose.yml logs -f
```

## Images currently pulled

```bash
docker images
```

Current images include:

- `bkimminich/juice-shop:latest` — about 527 MB
- `vulnerables/web-dvwa:latest` — about 935 MB
- `webgoat/webgoat:latest`
- `hello-world:latest`

## Troubleshooting

### `permission denied while trying to connect to the Docker daemon socket`

Make sure your current shell picked up the new `docker` group. Open a new WSL shell/window, or run:

```bash
newgrp docker
docker ps
```

If needed, you can temporarily use:

```bash
docker ps
# or, if permission still fails:
sudo docker ps
```

### Docker daemon is not running

```bash
sudo systemctl start docker
sudo systemctl status docker
sudo journalctl -u docker -n 100 --no-pager
```

### Port already in use

Check which host port is occupied and remap the container port, for example:

```bash
docker run -d --name juice-shop -p 3001:3000 bkimminich/juice-shop
docker run -d --name dvwa -p 8081:80 vulnerables/web-dvwa
docker run -d --name webgoat -p 127.0.0.1:8081:8080 -p 127.0.0.1:9091:9090 webgoat/webgoat
```

### Lab container exits immediately

Inspect logs:

```bash
docker ps -a
docker logs <container-name>
docker inspect <container-name>
```

Common causes are missing setup steps, port conflicts, or insufficient resources.

## Safety note

Only run these intentionally vulnerable apps locally for learning. Do not expose their ports publicly or point them at systems you are not authorized to test.
