---
name: writing-tests
description: Use when writing tests for the TgMonitorBot project (Python/pytest), or when asked to add test coverage for new or existing features.
---

# Writing Tests for TgMonitorBot

Step-by-step guidance for writing Python tests for the Telegram monitoring bot. Follow this skill to produce correct, consistent tests on the first attempt.

## Decision Guide

| Signal | Test Type |
|--------|-----------|
| Testing keyword matching logic | **Unit test** |
| Testing alert message formatting | **Unit test** |
| Testing .env config parsing (group IDs, keywords) | **Unit test** |
| Testing handler filter behavior | **Unit test** (mock Pyrogram) |
| Testing actual Telegram API interaction | **Integration test** (requires auth — rarely needed) |

## Test Workflow

### Step 1: Choose test location

Place tests under `tests/` directory (create if it doesn't exist):
- `tests/test_keyword_matching.py` — keyword detection logic
- `tests/test_alert_formatting.py` — alert message construction
- `tests/test_config_parsing.py` — .env variable parsing
- `tests/test_handlers.py` — handler behavior with mocked Pyrogram

### Step 2: Set up test infrastructure (first time only)

If `tests/` doesn't exist yet:

1. Add test dependencies:
   ```bash
   pip install pytest pytest-asyncio
   ```

2. Create directory structure:
   ```
   tests/
   ├── __init__.py
   ├── conftest.py          # Shared fixtures
   ├── test_keyword_matching.py
   ├── test_alert_formatting.py
   └── test_config_parsing.py
   ```

3. Create `tests/conftest.py` with shared fixtures — see [references/python-test-patterns.md](references/python-test-patterns.md)

### Step 3: Plan test cases

For each function, cover:
- [ ] **Happy path** — keyword found, alert sent correctly
- [ ] **Edge cases** — no keywords match, empty message text, message without `from_user`
- [ ] **Config parsing** — mixed group ID types (@username + numeric), empty keywords list
- [ ] **Error handling** — `send_message` failure, network errors
- [ ] **Case insensitivity** — keywords with mixed case

### Step 4: Write tests using patterns

Use `unittest.mock.AsyncMock` for Pyrogram objects, `@pytest.mark.asyncio` for async tests, `monkeypatch` for config.

See **[references/python-test-patterns.md](references/python-test-patterns.md)** for:
- Mock Pyrogram objects (Client, Message, Chat, User)
- Async test patterns with pytest-asyncio
- Keyword matching test examples
- Alert formatting test examples
- Config parsing test examples
- Mocking python-decouple

### Step 5: Run and verify

```bash
python -m pytest tests/ -v
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Importing real Pyrogram Client in tests | Mock it with `unittest.mock.AsyncMock` |
| Not marking async tests | Use `@pytest.mark.asyncio` decorator |
| Testing against real Telegram API | Mock `client.send_message` — never call real API in unit tests |
| Hardcoding .env values in tests | Use `monkeypatch.setenv()` or mock `decouple.config` |
| Not testing case-insensitive matching | Test with mixed-case keywords and message text |
| Forgetting to test anonymous sender | Test `from_user=None` case in alert formatting |
