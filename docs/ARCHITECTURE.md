# TgMonitorBot - Architecture

## Overview

TgMonitorBot is a single-file Telegram monitoring bot built with Python and Pyrogram. It operates as a **user account** (not a bot token), watching configured groups for keyword mentions and forwarding alerts to a target user.

## Application Architecture

```
┌─────────────────────────────────────────────────────┐
│                   start_work.py                      │
│                                                      │
│  ┌──────────────┐   ┌──────────────────────────┐    │
│  │ Configuration │   │    Pyrogram Client        │    │
│  │ Loading       │──▶│    (User Account Auth)    │    │
│  │ (.env)        │   └──────────┬───────────────┘    │
│  └──────────────┘              │                     │
│                                │                     │
│                    ┌───────────▼────────────┐        │
│                    │   Event Handler         │        │
│                    │   monitor_new_messages() │        │
│                    │   (decorator-based)      │        │
│                    └───────────┬────────────┘        │
│                                │                     │
│                    ┌───────────▼────────────┐        │
│                    │   Keyword Matching      │        │
│                    │   (case-insensitive     │        │
│                    │    substring search)    │        │
│                    └───────────┬────────────┘        │
│                                │ match found         │
│                    ┌───────────▼────────────┐        │
│                    │   send_alert()          │        │
│                    │   → TARGET_USER         │        │
│                    └───────────────────────── ┘        │
│                                                      │
│  ┌──────────────────────────────────────────┐        │
│  │   process_history() [optional]            │        │
│  │   Scans last 500 messages per group       │        │
│  │   (currently disabled in main)            │        │
│  └──────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────┘
```

## Module Breakdown

### Configuration Loading (lines 12-31)

Reads all settings from `.env` via `python-decouple`:
- Telegram API credentials (`API_ID`, `API_HASH`, `PHONE`, `LOGIN`)
- Monitoring targets (`GROUP_IDS` — supports both `@username` and numeric IDs)
- Alert keywords (`KEYWORDS` — lowercased for case-insensitive matching)
- Alert recipient (`TARGET_USER`)

### Pyrogram Client (lines 35-46)

Initializes a Pyrogram `Client` configured as a **user account** (not a bot):
- If `SESSION_STRING` is set: uses in-memory session (for Docker deployment)
- Otherwise: authenticates using phone number + file-based `.session` (for local dev)
- Connects to Telegram via MTProto protocol

### send_alert() (lines 42-72)

Formats and sends alert messages to `TARGET_USER`. Alert format:
```
Group: <title> (<link if public>)
Sender: <full name> (<profile link if available>)
Message:
<original message text>
```

### monitor_new_messages() (lines 75-79)

Decorator-based event handler triggered on:
- Text messages only (`filters.text`)
- Messages in monitored groups only (`filters.chat(GROUP_IDS)`)

Performs case-insensitive substring matching against keyword list.

### process_history() (lines 82-92)

Optional batch processing function (currently commented out in `main()`):
- Iterates over each monitored group
- Fetches the last 500 messages per group
- Applies same keyword matching logic
- Includes 50ms delay between messages to avoid API rate limiting

### main() (lines 95-103)

Entry point using async context manager pattern:
- `async with bot:` ensures proper client startup and cleanup
- Enters `idle()` loop for real-time message monitoring

## Data Flow

```
Telegram Group Message
        │
        ▼
Pyrogram Event System
        │
        ▼
filters.chat(GROUP_IDS) ──── no match ──▶ ignored
        │
        yes
        ▼
filters.text ──── no text ──▶ ignored
        │
        yes
        ▼
monitor_new_messages()
        │
        ▼
keyword in text.lower() ──── no match ──▶ ignored
        │
        yes
        ▼
send_alert() ──▶ TARGET_USER receives alert
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Single-file architecture | Simple monitoring bot, low complexity threshold |
| User account (not bot) | Access to private groups where bots cannot be added |
| Pyrogram (MTProto) | Direct Telegram API access, better than Bot API for user accounts |
| Substring matching | Simple and sufficient for keyword detection |
| No duplicate detection | Trade-off for simplicity; same match can trigger repeated alerts |
| python-decouple | Clean separation of config from code |

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pyrogram | 2.0.106 | Telegram MTProto client library |
| tgcrypto | 1.2.5 | Pyrogram crypto accelerator |
| python-decouple | 3.8 | Environment variable management |

---

**Last Updated:** 2026-03-27
**Maintained By:** Development Team
