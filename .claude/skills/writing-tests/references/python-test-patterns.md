# Python Test Patterns Reference

## File Location

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_keyword_matching.py
├── test_alert_formatting.py
└── test_config_parsing.py
```

---

## Shared Fixtures (conftest.py)

```python
import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_client():
    """Mock Pyrogram Client with async send_message."""
    client = AsyncMock()
    client.send_message = AsyncMock()
    return client


@pytest.fixture
def mock_chat():
    """Mock Pyrogram Chat object."""
    chat = MagicMock()
    chat.title = "Test Group"
    chat.username = "testgroup"
    chat.id = -100123456
    return chat


@pytest.fixture
def mock_chat_no_username():
    """Mock Chat without username (private/restricted group)."""
    chat = MagicMock()
    chat.title = "Private Group"
    chat.username = None
    chat.id = -100654321
    return chat


@pytest.fixture
def mock_user():
    """Mock Pyrogram User object."""
    user = MagicMock()
    user.first_name = "Иван"
    user.last_name = "Петров"
    user.username = "ivanpetrov"
    return user


@pytest.fixture
def mock_user_no_username():
    """Mock User without username."""
    user = MagicMock()
    user.first_name = "Анна"
    user.last_name = None
    user.username = None
    return user


@pytest.fixture
def mock_message(mock_chat, mock_user):
    """Mock Pyrogram Message with text."""
    message = MagicMock()
    message.text = "Ищу паблишера для игры"
    message.chat = mock_chat
    message.from_user = mock_user
    return message
```

---

## Testing Keyword Matching

```python
import pytest


def test_keyword_found_in_text():
    """Keyword substring match should be case-insensitive."""
    keywords_list = ["паблишер", "издатель"]
    text_lower = "Ищу паблишера для игры".lower()
    assert any(kw in text_lower for kw in keywords_list)


def test_keyword_not_found():
    """No match when message doesn't contain any keyword."""
    keywords_list = ["паблишер", "издатель"]
    text_lower = "Обычное сообщение о погоде".lower()
    assert not any(kw in text_lower for kw in keywords_list)


def test_keyword_case_insensitive():
    """Match should work regardless of case."""
    keywords_list = ["паблишер"]
    text_lower = "ИЩЕМ ПАБЛИШЕРА".lower()
    assert any(kw in text_lower for kw in keywords_list)


def test_keyword_partial_match():
    """Substring matching: 'издатель' matches 'издателя'."""
    keywords_list = ["издатель"]
    text_lower = "нужен издателя".lower()
    assert any(kw in text_lower for kw in keywords_list)
```

---

## Testing Alert Formatting

```python
import pytest


@pytest.mark.asyncio
async def test_alert_with_group_username(mock_client, mock_chat, mock_user):
    """Alert should include group link when username is available."""
    from start_work import send_alert

    await send_alert(mock_client, mock_chat, mock_user, "Test message")

    mock_client.send_message.assert_called_once()
    call_args = mock_client.send_message.call_args
    message_text = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get("text", "")

    assert "https://t.me/testgroup" in message_text
    assert "Test Group" in message_text


@pytest.mark.asyncio
async def test_alert_without_group_username(mock_client, mock_chat_no_username, mock_user):
    """Alert should show title without link when no username."""
    from start_work import send_alert

    await send_alert(mock_client, mock_chat_no_username, mock_user, "Test message")

    mock_client.send_message.assert_called_once()
    call_args = mock_client.send_message.call_args
    message_text = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get("text", "")

    assert "Private Group" in message_text
    assert "https://t.me/" not in message_text


@pytest.mark.asyncio
async def test_alert_anonymous_sender(mock_client, mock_chat):
    """Alert should handle None from_user gracefully."""
    from start_work import send_alert

    await send_alert(mock_client, mock_chat, None, "Test message")

    mock_client.send_message.assert_called_once()
    call_args = mock_client.send_message.call_args
    message_text = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get("text", "")

    assert "Аноним" in message_text
```

---

## Testing Config Parsing

```python
def test_group_ids_mixed_types():
    """Group IDs should support both @username and numeric formats."""
    raw = "@hyper_casual, -100123456, @gamedev_chat"
    raw_ids = [x.strip() for x in raw.split(",") if x.strip()]
    result = []
    for item in raw_ids:
        try:
            result.append(int(item))
        except ValueError:
            result.append(item)

    assert result == ["@hyper_casual", -100123456, "@gamedev_chat"]


def test_keywords_lowercased():
    """Keywords should be normalized to lowercase."""
    raw = "Паблишер, ИЗДАТЕЛЬ, Ищу Паблишера"
    keywords = [kw.strip().lower() for kw in raw.split(",")]
    assert keywords == ["паблишер", "издатель", "ищу паблишера"]


def test_empty_group_ids_filtered():
    """Empty entries from trailing commas should be filtered out."""
    raw = "@chat1, , @chat2, "
    raw_ids = [x.strip() for x in raw.split(",") if x.strip()]
    assert raw_ids == ["@chat1", "@chat2"]
```

---

## Mocking python-decouple

```python
def test_config_loading(monkeypatch):
    """Test that config values are loaded correctly from environment."""
    monkeypatch.setenv("API_ID", "12345")
    monkeypatch.setenv("API_HASH", "testhash")
    monkeypatch.setenv("PHONE", "+79991234567")
    monkeypatch.setenv("LOGIN", "TestUser")
    monkeypatch.setenv("GROUP_IDS", "@test_chat")
    monkeypatch.setenv("KEYWORDS", "test,keyword")
    monkeypatch.setenv("TARGET_USER", "@target")

    from decouple import config
    assert config("API_ID", cast=int) == 12345
    assert config("API_HASH") == "testhash"
```

---

## Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Specific test file
python -m pytest tests/test_keyword_matching.py -v

# Specific test function
python -m pytest tests/test_keyword_matching.py::test_keyword_found_in_text -v

# With output (print statements visible)
python -m pytest tests/ -v -s
```
