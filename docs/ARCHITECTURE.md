# Architecture Overview

## Компоненты

- **Bot Layer (`app/bot`)**: Telegram-интерфейс для пользователей.
- **API Layer (`app/api`)**: Flask API для админских операций.
- **Service Layer (`app/services`)**: бизнес-операции и orchestration.
- **Data Layer (`app/database`)**: SQLAlchemy модели и репозитории.
- **Core (`app/core`)**: кэш, безопасность, исключения, мониторинг.
- **Config (`config`)**: настройки и логирование.

## Поток запроса (API)

1. Запрос приходит в Flask route.
2. Middleware проверяет формат/заголовки.
3. Route валидирует JWT и входные данные.
4. Service выполняет бизнес-логику.
5. Repository работает с БД через async session.
6. Ответ сериализуется в JSON.

## Данные и хранение

- Основная БД: SQLite (dev) / PostgreSQL (prod).
- Кэш/временные структуры: Redis.
- Логи: файл + stdout/stderr (в зависимости от конфигурации).

## Безопасность

- JWT для API-доступа администратора.
- Rate limiter для login endpoint.
- Security headers на API-ответах.
- Шифрование чувствительных данных через Fernet.

## Наблюдаемость

- Health endpoint `/health`.
- Prometheus endpoint `/metrics`.
- Логирование через централизованный конфиг.
