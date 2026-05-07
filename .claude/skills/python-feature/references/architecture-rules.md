# Architecture Reference

## Contents

- [Pyrogram Client Initialization](#pyrogram-client-initialization)
- [Configuration Loading Pattern](#configuration-loading-pattern)
- [Message Handler Pattern](#message-handler-pattern)
- [Alert Sending Pattern](#alert-sending-pattern)
- [Main Entry Point Pattern](#main-entry-point-pattern)
- [Pyrogram Filters Reference](#pyrogram-filters-reference)
- [Logging Pattern](#logging-pattern)

---

## Pyrogram Client Initialization

The bot authenticates as a **user account** (not a bot token). Session is persisted in `{LOGIN}.session` files.

```python
from pyrogram import Client

bot = Client(
    name=LOGIN,
    api_id=API_ID,
    api_hash=API_HASH,
    phone_number=PHONE
)
```

- First run requires interactive Telegram auth (phone code)
- Session files (`*.session`, `*.session-journal`) persist auth — never delete or commit them
- `LOGIN` determines the session filename

---

## Configuration Loading Pattern

All config is loaded via `python-decouple` from `.env`:

```python
from decouple import config

# Simple values
API_ID = config('API_ID', cast=int)
API_HASH = config('API_HASH')
PHONE = config('PHONE')
LOGIN = config('LOGIN')
TARGET_USER = config('TARGET_USER')

# Comma-separated list with mixed types (strings and ints)
group_ids_str = config('GROUP_IDS')
raw_ids = [x.strip() for x in group_ids_str.split(',') if x.strip()]
GROUP_IDS = []
for item in raw_ids:
    try:
        GROUP_IDS.append(int(item))
    except ValueError:
        GROUP_IDS.append(item)  # @username strings stay as-is

# Comma-separated list, normalized to lowercase
KEYWORDS = config('KEYWORDS')
keywords_list = [kw.strip().lower() for kw in KEYWORDS.split(',')]
```

### Adding a new config variable

1. Add to `.env` file
2. Add `config('VAR_NAME')` call in the loading section (lines 12-30)
3. Use appropriate `cast=` for non-string types: `cast=int`, `cast=float`, `cast=bool`
4. Update CLAUDE.md Configuration table

---

## Message Handler Pattern

Handlers use Pyrogram decorators for event-driven registration:

```python
@bot.on_message(filters.chat(GROUP_IDS) & filters.text)
async def monitor_new_messages(client: Client, message: Message):
    text_lower = message.text.lower()
    if any(keyword in text_lower for keyword in keywords_list):
        await send_alert(client, message.chat, message.from_user, message.text)
```

### Key rules:
- Always `async def`
- Signature: `(client: Client, message: Message)`
- Use `filters` to narrow which messages trigger the handler
- Call `send_alert()` for notifications — never send messages directly from handlers

---

## Alert Sending Pattern

All alerts go through `send_alert()` which formats and sends to `TARGET_USER`:

```python
async def send_alert(client: Client, chat, from_user, text: str):
    # Group info
    if chat.username:
        group_link = f"https://t.me/{chat.username}"
        group_info = f"Group: {chat.title or chat.username} ({group_link})"
    else:
        group_info = f"Group: {chat.title or 'Untitled'}"

    # Sender info
    if from_user:
        full_name = f"{from_user.first_name or ''} {from_user.last_name or ''}".strip()
        if from_user.username:
            sender_link = f"https://t.me/{from_user.username}"
            sender_info = f"Sender: {full_name} ({sender_link})"
        else:
            sender_info = f"Sender: {full_name}"
    else:
        sender_info = "Sender: Anonymous"

    # Message text
    message_text = f"Message:\n{text}"

    full_message = f"{group_info}\n{sender_info}\n{message_text}"

    try:
        await client.send_message(TARGET_USER, full_message)
        logger.info(f"Alert sent to {TARGET_USER} (from chat {chat.id})")
    except Exception as e:
        logger.error(f"Error sending alert: {e}")
```

### Key rules:
- Always wrap `send_message` in try/except
- Log success and failure in English
- Handle missing `username` and `from_user` gracefully

---

## Main Entry Point Pattern

```python
async def main():
    async with bot:
        logger.info("Client started. Entering new message monitoring mode.")
        await idle()  # Keep bot alive for real-time monitoring

if __name__ == "__main__":
    asyncio.run(main())
```

- `async with bot:` authenticates, connects, and guarantees cleanup on exceptions
- `idle()` blocks until Ctrl+C — handlers process messages during this time

---

## Pyrogram Filters Reference

Filters control which messages trigger a handler. Combine with `&` (AND), `|` (OR), `~` (NOT).

| Filter | Description |
|--------|-------------|
| `filters.chat(list_of_ids)` | Messages from specific chats (IDs or @usernames) |
| `filters.text` | Text messages only |
| `filters.regex(pattern)` | Messages matching a regex pattern |
| `filters.photo` | Photo messages |
| `filters.document` | Document messages |
| `filters.private` | Private (DM) messages |
| `filters.group` | Group messages |
| `filters.channel` | Channel messages |
| `filters.user(user_ids)` | Messages from specific users |

### Combining filters:

```python
# Text messages in monitored groups
filters.chat(GROUP_IDS) & filters.text

# Text OR photo messages
filters.text | filters.photo

# All messages except from a specific user
~filters.user(EXCLUDED_USER)

# Complex: text messages in groups, not from bots
filters.chat(GROUP_IDS) & filters.text & ~filters.bot
```

---

## Logging Pattern

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Usage — always in English
logger.info(f"Monitored chats: {GROUP_IDS}")
logger.info(f"Keywords: {keywords_list}")
logger.error(f"Error sending alert: {e}")
logger.warning(f"Failed to get history for chat {chat}: {e}")
```
