# Используем стабильный Python
FROM python:3.11-slim

# Чтобы логи сразу выводились
ENV PYTHONUNBUFFERED=1

# Рабочая директория
WORKDIR /app

# Устанавливаем системные зависимости (нужны для aiohttp/ssl)
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости отдельно (для кеширования)
COPY requirements.txt .

# Обновляем pip и ставим зависимости
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Render ОБЯЗАТЕЛЬНО требует слушать порт из $PORT
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
