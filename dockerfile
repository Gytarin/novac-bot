# Используем официальный Python 3.11
FROM python:3.11-slim

# Устанавливаем зависимости ОС для aiohttp и uvloop
RUN apt-get update && apt-get install -y gcc libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# Пробрасываем порт Render
ENV PORT=10000

# Команда запуска uvicorn
CMD ["sh", "-c", "uvicorn bot:app --host 0.0.0.0 --port $PORT"]
