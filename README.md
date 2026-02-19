
```bash
# Полное приложение (бот + API)
python -m app.main

# Или отдельно API
python -m app.api.main
```

## API для администратора

Базовый префикс: `/api/v1`

- `POST /auth/login` — вход администратора.
- `POST /auth/verify` — проверка JWT.
- `GET /users` — список пользователей.
- `POST /users/<telegram_id>/ban` — бан/разбан пользователя.
- `GET /admin/dashboard` — агрегированная статистика.
- `POST /admin/backup` — создать backup SQLite БД.

Примеры запросов и ответов: [docs/API.md](docs/API.md).

## Документация
