from pyrogram import Client, filters, idle
from decouple import config
from pyrogram.types import Message
import logging
import asyncio


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


API_ID = config('API_ID', cast=int)
API_HASH = config('API_HASH')
PHONE = config('PHONE')
LOGIN = config('LOGIN')
proxy_settings = {
    "scheme": "socks5",
    "hostname": "68.71.245.206",   # из списка
    "port": 4145                    # из списка
}

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

# Инициализация клиента
bot = Client(
    name=LOGIN,
    api_id=API_ID,
    api_hash=API_HASH,
    phone_number=PHONE,
    proxy=proxy_settings
)

async def send_alert(client: Client, chat, from_user, text: str):


    # Информация о группе
    if chat.username:
        group_link = f"https://t.me/{chat.username}"
        group_info = f"Группа: {chat.title or chat.username} ({group_link})"
    else:
        group_info = f"Группа: {chat.title or 'Без названия'}"

    # Информация об отправителе
    if from_user:
        full_name = f"{from_user.first_name or ''} {from_user.last_name or ''}".strip()
        if from_user.username:
            sender_link = f"https://t.me/{from_user.username}"
            sender_info = f"Отправитель: {full_name} ({sender_link})"
        else:
            sender_info = f"Отправитель: {full_name}"
    else:
        sender_info = "Отправитель: Аноним"

    # Текст сообщения
    message_text = f"Сообщение:\n{text}"

    # Собираем всё вместе
    full_message = f"{group_info}\n{sender_info}\n{message_text}"

    try:
        # Отправляем без parse_mode – обычный текст
        await client.send_message(TARGET_USER, full_message)
        logger.info(f"Оповещение отправлено в {TARGET_USER} (из чата {chat.id})")
    except Exception as e:
        logger.error(f"Ошибка при отправке оповещения: {e}")

# Обработчик новых сообщений
@bot.on_message(filters.chat(GROUP_IDS) & filters.text)
async def monitor_new_messages(client: Client, message: Message):
    text_lower = message.text.lower()
    if any(keyword in text_lower for keyword in keywords_list):
        await send_alert(client, message.chat, message.from_user, message.text)

# Функция для обработки истории сообщений
async def process_history():
    """Проходит по каждому чату из GROUP_IDS, получает последние 500 сообщений и проверяет их."""
    for chat in GROUP_IDS:
        try:
            logger.info(f"Обработка истории чата: {chat}")
            async for message in bot.get_chat_history(chat, limit=500):
                if message.text and any(kw in message.text.lower() for kw in keywords_list):
                    await send_alert(bot, message.chat, message.from_user, message.text)
                await asyncio.sleep(0.05)  # небольшая задержка для избежания флуда API
        except Exception as e:
            logger.error(f"Не удалось получить историю для чата {chat}: {e}")

# Основная асинхронная функция
async def main():
    await bot.start()
   # logger.info("Клиент запущен. Начинаю обработку истории...")
   # await process_history()
    logger.info("Обработка истории завершена. Перехожу в режим мониторинга новых сообщений.")
    await idle()  # правильный вызов вместо bot.idle()
    await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
