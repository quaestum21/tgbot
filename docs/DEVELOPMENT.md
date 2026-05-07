# TgMonitorBot - Development Guide

## Development Setup

### Prerequisites
- Python 3.10+
- pip
- Telegram account with API credentials (obtain from [my.telegram.org](https://my.telegram.org))
- Git

### 1. Clone Repository

```bash
git clone <repository-url>
cd BotTelegram
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Dependencies:
- **pyrogram** (2.0.106) - Telegram MTProto API client
- **python-decouple** (3.8) - Environment variable management

### 3. Configure Environment

Create a `.env` file in the project root. See [CONFIGURATION](CONFIGURATION.md) for all available variables.

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 4. First Run

```bash
python start_work.py
```

On first run, Pyrogram will prompt for interactive Telegram authentication (phone code / 2FA password). This creates a `.session` file that persists authentication for subsequent runs.

## Project Structure

```
BotTelegram/
├── start_work.py          # Entire application (~104 lines)
├── requirements.txt       # Python dependencies
├── .env                   # Configuration (not committed)
├── *.session              # Telegram session files (not committed)
├── *.session-journal      # Session journal files (not committed)
├── CLAUDE.md              # AI development guidelines
└── docs/                  # Documentation
    ├── INDEX.md
    ├── ARCHITECTURE.md
    ├── CONFIGURATION.md
    ├── DEPLOYMENT.md
    └── DEVELOPMENT.md     # This file
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/<issue-number>-description
```

### 2. Make Changes

All application code lives in `start_work.py`. See [ARCHITECTURE](ARCHITECTURE.md) for module details.

### 3. Test Locally

```bash
python start_work.py
```

Send a test message containing a monitored keyword in one of the configured groups. Verify the alert is received by `TARGET_USER`.

### 4. Commit and Push

```bash
git add start_work.py
git commit -m "feat: Description of change"
git push origin feature/<issue-number>-description
```

### 5. Create Merge Request

Create a merge request to `develop` branch in GitLab.

## Code Style & Conventions

### Python
- **Async/await** for all I/O operations
- **Pyrogram decorators** (`@bot.on_message`) for event handlers
- **python-decouple** for all configuration
- **Logging** via Python `logging` module (English messages only)
- **snake_case** for functions and variables
- **PascalCase** for classes

### Logging
```python
logger.info("Descriptive message in English")
logger.error(f"Error context: {e}")
```

## Troubleshooting

### Authentication fails
- Ensure `API_ID`, `API_HASH`, and `PHONE` are correct in `.env`
- Delete the `.session` file and re-authenticate
- Check that 2FA password is entered correctly if enabled

### No alerts received
- Verify `GROUP_IDS` contains correct chat identifiers
- Check that the bot account is a member of the monitored groups
- Verify `KEYWORDS` are spelled correctly (case-insensitive matching)
- Check `TARGET_USER` is correct and reachable

### Session errors
- Delete `*.session` and `*.session-journal` files
- Re-run `python start_work.py` to re-authenticate

---

**Last Updated:** 2026-03-27
**Maintained By:** Development Team
