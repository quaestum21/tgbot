# CLAUDE.md

Telegram monitoring bot (Python/Pyrogram). Watches groups for keyword mentions, alerts a target user. Single-file async app.

**Full docs:** [docs/INDEX.md](docs/INDEX.md)

## Commands

```bash
pip install -r requirements.txt
python start_work.py  # first run requires interactive Telegram auth
python export_session.py  # export session string for Docker deployment

# Docker deployment (requires SESSION_STRING in .env)
docker compose -f docker-compose.deploy.yml up -d
```

No build step, test suite, or linter configured. CI/CD pipeline in `.gitlab-ci.yml` (builds image, deploys via SSH on push to `develop`).

## Architecture

`start_work.py` — entire app (~110 lines). User account auth (not bot token). Session via `SESSION_STRING` env var (Docker) or `{LOGIN}.session` file (local dev).

`export_session.py` — one-time helper to export `.session` file to a string for Docker deployment.

Key functions: `send_alert()`, `monitor_new_messages()` (decorator handler), `process_history()` (disabled), `main()` (async context manager + `idle()`).

## Key Rules

- Language: all comments and logs in English
- Dependencies: `pyrogram`, `tgcrypto`, `python-decouple` only
- Never commit `.env` (credentials) or `*.session` files
