# Используем Python 3.11
FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости и устанавливаем
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# Открываем порт для Render
ENV PORT 10000
EXPOSE $PORT

# Запуск FastAPI (app.py)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"
