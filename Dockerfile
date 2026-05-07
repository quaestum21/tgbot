# Используем официальный образ Python 3.9 (легковесный)
FROM python:3.9-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта в контейнер
COPY . .

# Создаём пользователя без прав root (для безопасности)
RUN useradd -m botuser && chown -R botuser:botuser /app
USER botuser

# Команда по умолчанию для запуска бота
CMD ["python", "start_work.py"]