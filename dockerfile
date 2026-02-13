FROM python:3.11-slim

# Чтобы логи сразу выводились
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Системные зависимости (если нужны для aiogram / ssl)
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Сначала requirements (для кэширования)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Затем весь проект
COPY . .

# ВАЖНО: Render требует использовать переменную $PORT
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port $PORT"]
