# TgMonitorBot - Configuration Guide

## Overview

All configuration is managed through environment variables loaded from a `.env` file in the project root using `python-decouple`.

## Environment Variables

### Telegram API Credentials

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `API_ID` | integer | Yes | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | string | Yes | Telegram API hash from [my.telegram.org](https://my.telegram.org) |
| `PHONE` | string | Yes | Phone number for Telegram authentication (international format) |
| `LOGIN` | string | Yes | Session name — used as the filename for `.session` file |
| `SESSION_STRING` | string | No | Pyrogram session string for non-interactive auth (Docker). Overrides file-based session when set. Generate with `python export_session.py` |

### Monitoring Configuration

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `GROUP_IDS` | string | Yes | Comma-separated list of group identifiers to monitor |
| `KEYWORDS` | string | Yes | Comma-separated list of keywords to detect (case-insensitive) |
| `TARGET_USER` | string | Yes | Alert recipient — `@username` or numeric user ID |

## Example .env File

```env
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890
PHONE=+1234567890
LOGIN=MySession

GROUP_IDS=@public_group,-1001234567890
KEYWORDS=urgent,help,alert
TARGET_USER=@my_username

# Optional: session string for Docker deployment
# SESSION_STRING=BQC...
```

## Variable Details

### GROUP_IDS

Supports two identifier formats, mixed freely in one comma-separated list:

- **Username**: `@groupname` — for public groups with a username
- **Numeric ID**: `-1001234567890` — for private groups or groups without a username

To find a group's numeric ID, forward a message from the group to [@userinfobot](https://t.me/userinfobot) or use Pyrogram's `get_chat()` method.

```env
# Single group
GROUP_IDS=@my_group

# Multiple groups (mixed formats)
GROUP_IDS=@public_group,-1001234567890,@another_group
```

### KEYWORDS

Comma-separated list of keywords. Matching is:
- **Case-insensitive**: `"alert"` matches `"ALERT"`, `"Alert"`, etc.
- **Substring-based**: `"help"` matches `"helpful"`, `"please help me"`, etc.

```env
# Single keyword
KEYWORDS=urgent

# Multiple keywords
KEYWORDS=urgent,help,alert,important
```

### TARGET_USER

The user who receives alert messages. Accepts:
- **Username**: `@my_username`
- **Numeric ID**: `123456789`

The bot's authenticated account must be able to send messages to this user.

### LOGIN

Used as the session file name. Pyrogram creates `{LOGIN}.session` and `{LOGIN}.session-journal` files in the project root. These files persist Telegram authentication and should not be deleted during operation.

## Security Notes

- **Never commit `.env`** — it contains real credentials
- **Never commit `.session` files** — they contain authenticated Telegram sessions
- Both are excluded in `.gitignore`
- Rotate `API_HASH` if compromised via [my.telegram.org](https://my.telegram.org)

---

**Last Updated:** 2026-03-27
**Maintained By:** Development Team
