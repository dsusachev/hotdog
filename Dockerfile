# ==================== STAGE 1: BUILDER ====================
FROM python:3.11-slim as builder

WORKDIR /app

# Устанавливаем системные зависимости для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости и устанавливаем их в отдельную директорию
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ==================== STAGE 2: RUNTIME ====================
FROM python:3.11-slim

WORKDIR /app

# Копируем установленные зависимости из builder
COPY --from=builder /root/.local /root/.local

# Устанавливаем runtime-зависимости (если нужны)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем исходный код
COPY . .

# Обновляем PATH для пользовательских пакетов
ENV PATH=/root/.local/bin:$PATH

# Переменные окружения (можно переопределить при запуске)
ENV PYTHONPATH=/app
ENV PORT=8000

# Открываем порт
EXPOSE $PORT

# Команда запуска (можно переопределить)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
