from pyrogram import Client, filters, idle
from pyrogram.types import Message
from decouple import config
import logging
import asyncio
import socket
import socks  # PySocks

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_ID = config('API_ID', cast=int)
API_HASH = config('API_HASH')
PHONE = config('PHONE')
LOGIN = config('LOGIN')

PROXY_FILE = config('PROXY_FILE', default='proxies.txt')

group_ids_str = config('GROUP_IDS')
raw_ids = [x.strip() for x in group_ids_str.split(',') if x.strip()]
GROUP_IDS = []
for item in raw_ids:
    try:
        GROUP_IDS.append(int(item))
    except ValueError:
        GROUP_IDS.append(item)

KEYWORDS = config('KEYWORDS')
TARGET_USER = config('TARGET_USER')
keywords_list = [kw.strip().lower() for kw in KEYWORDS.split(',')]

logger.info(f"Отслеживаемые чаты: {GROUP_IDS}")
logger.info(f"Ключевые слова: {keywords_list}")

# --- Загрузка списка прокси ---
def load_proxies(path):
    proxies = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(':')
            if len(parts) == 4:
                host, port, user, pwd = parts
                proxies.append({
                    "scheme": "socks5",
                    "hostname": host,
                    "port": int(port),
                    "username": user,
                    "password": pwd,
                })
            elif len(parts) == 2:
                host, port = parts
                proxies.append({
                    "scheme": "socks5",
                    "hostname": host,
                    "port": int(port),
                })
            else:
                logger.warning(f"Пропускаю строку (неизвестный формат): {line}")
    return proxies


# --- Быстрая TCP-проверка прокси через PySocks ---
def check_proxy(proxy, target_host="149.154.167.51", target_port=443, timeout=5):
    """Пробуем установить TCP-соединение через прокси до сервера Telegram (DC2)."""
    s = socks.socksocket()
    s.set_proxy(
        socks.SOCKS5,
        proxy["hostname"],
        proxy["port"],
        username=proxy.get("username"),
        password=proxy.get("password"),
    )
    s.settimeout(timeout)
    try:
        s.connect((target_host, target_port))
        s.close()
        return True
    except Exception as e:
        return False


# --- Логика отправки оповещения ---
async def send_alert(client: Client, chat, from_user, text: str):
    if chat.username:
        group_link = f"https://t.me/{chat.username}"
        group_info = f"Группа: {chat.title or chat.username} ({group_link})"
    else:
        group_info = f"Группа: {chat.title or 'Без названия'}"

    if from_user:
        full_name = f"{from_user.first_name or ''} {from_user.last_name or ''}".strip()
        if from_user.username:
            sender_link = f"https://t.me/{from_user.username}"
            sender_info = f"Отправитель: {full_name} ({sender_link})"
        else:
            sender_info = f"Отправитель: {full_name}"
    else:
        sender_info = "Отправитель: Аноним"

    full_message = f"{group_info}\n{sender_info}\nСообщение:\n{text}"

    try:
        await client.send_message(TARGET_USER, full_message)
        logger.info(f"Оповещение отправлено в {TARGET_USER} (из чата {chat.id})")
    except Exception as e:
        logger.error(f"Ошибка при отправке оповещения: {e}")


# --- Запуск Pyrogram с конкретным прокси ---
async def try_start_with_proxy(proxy):
    bot = Client(
        name=LOGIN,
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=PHONE,
        proxy=proxy,
    )

    @bot.on_message(filters.chat(GROUP_IDS) & filters.text)
    async def monitor_new_messages(client: Client, message: Message):
        text_lower = message.text.lower()
        if any(keyword in text_lower for keyword in keywords_list):
            await send_alert(client, message.chat, message.from_user, message.text)

    try:
        await asyncio.wait_for(bot.start(), timeout=30)
        return bot
    except Exception as e:
        logger.warning(f"Pyrogram не смог стартовать через {proxy['hostname']}:{proxy['port']} — {e}")
        try:
            await bot.stop()
        except Exception:
            pass
        return None


async def main():
    proxies = load_proxies(PROXY_FILE)
    if not proxies:
        logger.error("Список прокси пуст. Проверь proxies.txt.")
        return

    logger.info(f"Загружено прокси: {len(proxies)}")

    # 1) Быстрая TCP-проверка
    alive = []
    for i, p in enumerate(proxies, 1):
        ok = check_proxy(p)
        status = "OK" if ok else "DEAD"
        logger.info(f"[{i}/{len(proxies)}] {p['hostname']}:{p['port']} -> {status}")
        if ok:
            alive.append(p)

    if not alive:
        logger.error("Ни один прокси не прошёл TCP-проверку. Возьми другой список.")
        return

    logger.info(f"Живых прокси: {len(alive)}. Пробую запустить Pyrogram...")

    # 2) Пробуем стартануть Pyrogram по очереди
    bot = None
    for p in alive:
        logger.info(f"Пробую запуск через {p['hostname']}:{p['port']}...")
        bot = await try_start_with_proxy(p)
        if bot:
            logger.info(f"Запущен через {p['hostname']}:{p['port']}")
            break

    if not bot:
        logger.error("Ни один прокси не позволил Pyrogram авторизоваться.")
        return

    logger.info("Перехожу в режим мониторинга новых сообщений.")
    await idle()
    await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())