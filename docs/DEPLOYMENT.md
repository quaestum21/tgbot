# TgMonitorBot - Deployment Guide

## Deployment Overview

TgMonitorBot runs as a long-lived Python process that maintains a persistent connection to Telegram. It requires initial interactive authentication, then runs unattended.

## Prerequisites

- **Python**: 3.10+
- **pip**: For dependency installation
- **Server**: Any Linux server or machine with stable internet
- **Telegram account**: With API credentials configured

## Production Setup

### 1. Prepare Environment

```bash
git clone <repository-url>
cd BotTelegram
pip install -r requirements.txt
```

### 2. Configure

Create `.env` file with production values. See [CONFIGURATION](CONFIGURATION.md) for details.

### 3. Initial Authentication

The first run requires interactive input (Telegram auth code):

```bash
python start_work.py
```

Enter the verification code sent to your Telegram account. If 2FA is enabled, enter the password when prompted. This creates the `.session` file — subsequent runs authenticate automatically.

### 4. Run as Service

#### Option A: systemd (recommended for Linux)

Create `/etc/systemd/system/tgmonitorbot.service`:

```ini
[Unit]
Description=TgMonitorBot - Telegram Monitoring Bot
After=network.target

[Service]
Type=simple
User=<your-user>
WorkingDirectory=/path/to/BotTelegram
ExecStart=/usr/bin/python3 start_work.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable tgmonitorbot
sudo systemctl start tgmonitorbot
```

#### Option B: Screen/tmux

```bash
# Using screen
screen -S tgmonitorbot
python start_work.py
# Detach: Ctrl+A, D

# Using tmux
tmux new -s tgmonitorbot
python start_work.py
# Detach: Ctrl+B, D
```

#### Option C: Docker (recommended)

The project includes a `Dockerfile` and `docker-compose.deploy.yml` for containerized deployment.

1. Copy `.env.example` to `.env` and fill in credentials:
   ```bash
   cp .env.example .env
   # Edit .env with real values
   ```

2. Authenticate locally first to generate the `.session` file:
   ```bash
   pip install -r requirements.txt
   python start_work.py
   # Enter Telegram auth code, then stop with Ctrl+C
   ```

3. Export the session string for Docker:
   ```bash
   python export_session.py
   # Copy the output SESSION_STRING=... into your .env file
   ```

4. Start the bot:
   ```bash
   docker compose -f docker-compose.deploy.yml up -d
   ```

The `SESSION_STRING` env var provides non-interactive authentication inside the container. The `.env` file is passed to the container at runtime — it is never baked into the image.

#### CI/CD Deployment

The GitLab CI/CD pipeline (`.gitlab-ci.yml`) automates build and deploy:

- **Build stage**: Builds the Docker image and pushes to GitLab Container Registry (`gitlab.kidsgames.top:5050`)
- **Deploy stage**: SSHes to the target server, pulls the latest image, and restarts the container

Pipeline triggers automatically on push to `develop`, or manually on other branches.

Required CI/CD variables in GitLab (Settings > CI/CD > Variables):
- `SSH_PRIVATE_KEY` — private key for server access
- `SSH_KNOWN_HOSTS` — server's SSH host key
- `SSH_HOST` — target server address

## Monitoring

### Check Status

```bash
# systemd
sudo systemctl status tgmonitorbot
journalctl -u tgmonitorbot -f

# Docker
docker compose -f docker-compose.deploy.yml logs -f
```

### Log Output

The bot logs to stdout with the format:
```
2026-03-27 12:00:00 - __main__ - INFO - Monitored chats: [...]
2026-03-27 12:00:00 - __main__ - INFO - Keywords: [...]
2026-03-27 12:00:01 - __main__ - INFO - Client started. Entering new message monitoring mode.
2026-03-27 12:00:15 - __main__ - INFO - Alert sent to @user (from chat -100123456)
```

## Session Management

- `.session` files persist Telegram authentication
- If the session expires or becomes invalid, stop the service, delete the `.session` file, and re-authenticate interactively
- Session files are SQLite databases — do not edit manually
- Back up `.session` files when migrating to a new server

## Known Limitations

- **No duplicate detection**: The same keyword match in the same message can trigger alerts if the bot restarts and `process_history()` is enabled
- **Single instance only**: Running multiple instances with the same session will cause conflicts
- **No health check endpoint**: Monitor via process status and log output

## Updating

```bash
# Pull latest changes
git pull origin develop

# Install any new dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart tgmonitorbot
```

---

**Last Updated:** 2026-03-27
**Maintained By:** Development Team
