# Базовый образ Python
FROM python:3.9-slim

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копирование всех файлов проекта в контейнер
COPY . .

# Установка зависимостей
RUN pip install python-telegram-bot

# Команда для запуска бота
CMD ["python", "bot.py"]

