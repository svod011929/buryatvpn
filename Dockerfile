FROM python:3.11-slim

# Метаданные образа
LABEL maintainer="BuryatVPN Team <dev@buryatvpn.com>"
LABEL version="2.0.0"
LABEL description="BuryatVPN - Modern VPN service"

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя для приложения
RUN groupadd -r buryatvpn && useradd -r -g buryatvpn buryatvpn

# Установка рабочей директории
WORKDIR /app

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование приложения
COPY . .

# Создание необходимых директорий
RUN mkdir -p data logs && \
    chown -R buryatvpn:buryatvpn /app

# Переключение на пользователя приложения
USER buryatvpn

# Открытие портов
EXPOSE 8000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Команда по умолчанию
CMD ["python", "-m", "app.main"]
