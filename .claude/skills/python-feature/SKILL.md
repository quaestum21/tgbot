---
name: python-feature
description: Guides Python/Pyrogram implementation in the TgMonitorBot project. Enforces architecture rules: async/await patterns, Pyrogram decorators and filters, python-decouple config, logging in English. Use when implementing new handlers, fixing bugs, or refactoring the bot. Typically invoked after feature-spec confirms a spec, or directly via /python-feature.
---

# Python Feature Implementation

## Hard Rules (non-negotiable)

Before any implementation, internalize these. See [architecture-rules.md](references/architecture-rules.md) for full patterns and examples.

- **All functions must be `async`** — use `await` for all Pyrogram and I/O calls
- **Pyrogram decorators** for handler registration — `@bot.on_message(filters.chat(...) & filters.text)`
- **Handler signature** — `async def handler_name(client: Client, message: Message)`
- **`python-decouple`** for all config — `config('VAR_NAME')` with appropriate `cast=`
- **`logging` module only** — never `print()`. Use `logger.info/error/warning`
- **All comments and log messages in English**
- **Never hardcode credentials** — always via `.env`
- **Single-file architecture** — keep everything in `start_work.py` unless project grows beyond ~300 lines

## Step 0: Read Before Touching

1. CLAUDE.md is already loaded — do NOT re-read it
2. Read `start_work.py` — the entire application
3. If no spec yet: run `feature-spec` skill first
4. Identify which branch applies → go to that section

---

## Branch A: New Feature

1. **Identify feature type** — new message handler, new alert type, new filter, new monitoring source, or utility function
2. **Check existing code** — can an existing handler be extended, or is a new one needed?
3. **Add handler function** with `async def` and Pyrogram decorator:
   ```python
   @bot.on_message(filters.chat(GROUP_IDS) & filters.text)
   async def new_handler(client: Client, message: Message):
       # handler logic
   ```
   See [Message Handler Pattern](references/architecture-rules.md#message-handler-pattern) for the full template.
4. **Add config variables** (if needed) — add to `.env` loading section (lines 12-30 of `start_work.py`) using `config('VAR_NAME')`
5. **Add dependencies** (if needed) — add to `requirements.txt`
6. **Update CLAUDE.md** — Architecture section (new handler), Configuration table (new .env vars)
7. **Use `send_alert()` pattern** for any notification output — see [Alert Sending Pattern](references/architecture-rules.md#alert-sending-pattern)
8. **Ask the user:** "Do you need tests for this feature?"

---

## Branch B: Bugfix

1. **Read `start_work.py`** before touching anything
2. **Invoke `superpowers:systematic-debugging`** to diagnose root cause
3. **Verify fix** doesn't violate architecture rules (see [architecture-rules.md](references/architecture-rules.md))
4. **Update CLAUDE.md** if behavior changed

---

## Branch C: Refactor

1. **Read all affected code** before touching anything
2. **Preserve invariants:**
   - Async handlers with decorator-based registration
   - Config via `python-decouple`
   - Logging in English via `logging` module
   - `send_alert()` as the single alert output path
3. **If splitting into multiple files:** create a package structure, update imports, update CLAUDE.md architecture section
4. **Update CLAUDE.md** if file structure or architecture changes

---

## Completion Checklist (all branches)

Before considering the task done, verify:

- [ ] No `print()` calls — only `logger.info/error/warning`
- [ ] No hardcoded credentials or IDs — all via `.env`
- [ ] All new config variables added to `.env` loading section and documented in CLAUDE.md
- [ ] Handler follows `async def handler_name(client: Client, message: Message)` pattern
- [ ] Comments and log messages in English
- [ ] `requirements.txt` updated if new dependency added
- [ ] `CLAUDE.md` updated if architecture or config changed
- [ ] Test prompt shown to user (for new features)
