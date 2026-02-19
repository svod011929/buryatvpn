# Configuration Reference

Справочник по основным переменным окружения.

## Обязательные переменные

- `BOT_TOKEN` — токен Telegram-бота.
- `SECRET_KEY` — секрет приложения.
- `ENCRYPTION_KEY` — Fernet ключ для шифрования.
- `JWT_SECRET_KEY` — секрет подписи JWT.
- `WEB_ADMIN_EMAIL` — логин администратора API.
- `WEB_ADMIN_PASSWORD_HASH` — bcrypt-хэш пароля администратора.

## База данных

- `DATABASE_URL`
  - Dev (SQLite): `sqlite:///data/database.db`
  - Prod (PostgreSQL async): `postgresql+asyncpg://user:pass@host:5432/dbname`
- `DATABASE_ECHO` — SQL debug logging (`true/false`)
- `DATABASE_POOL_SIZE` — размер пула подключений
- `DATABASE_MAX_OVERFLOW` — overflow пула

## Redis

- `REDIS_URL`
- `REDIS_TTL`
- `REDIS_MAX_CONNECTIONS`

## JWT

- `JWT_ALGORITHM` (default: `HS256`)
- `JWT_EXPIRE_HOURS` (default: `24`)

## Web/API

- `WEB_HOST` (default: `0.0.0.0`)
- `WEB_PORT` (default: `8000`)
- `WEB_DEBUG` (`true/false`)

## Monitoring

- `METRICS_ENABLED` (`true/false`)
- `PROMETHEUS_PORT`
- `HEALTH_CHECK_INTERVAL`

## Логирование

- `LOG_LEVEL`
- `LOG_FILE`
- `LOG_MAX_SIZE`
- `LOG_BACKUP_COUNT`

## Примечания

1. Для production не используйте SQLite.
2. Секреты храните в vault/secret manager, а не в git.
3. После смены JWT секрета все старые токены станут невалидны.
