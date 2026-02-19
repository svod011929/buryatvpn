# BuryatVPN API

Актуальная документация по REST API для админского контура.

## Базовая информация

- Base URL: `http://<host>:<port>`
- API prefix: `/api/v1`
- Формат данных: `application/json`
- Аутентификация: `Authorization: Bearer <JWT>`

## Аутентификация

### `POST /api/v1/auth/login`

Вход администратора и получение access token.

**Request**

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "your_password"
}
```

**Response 200**

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Response 401**

```json
{
  "error": "Invalid credentials"
}
```

**Response 429** (слишком много попыток)

```json
{
  "error": "Too many attempts. Try later"
}
```

---

### `POST /api/v1/auth/verify`

Проверка валидности JWT.

**Request**

```http
POST /api/v1/auth/verify
Authorization: Bearer <jwt>
Content-Type: application/json
```

**Response 200**

```json
{
  "valid": true,
  "payload": {
    "email": "admin@example.com",
    "role": "admin",
    "exp": 9999999999
  }
}
```

## Пользователи

### `GET /api/v1/users`

Получение списка пользователей для админ-панели.

**Query params**

- `limit` (int, default `50`, max `200`)
- `offset` (int, default `0`)
- `search` (string, optional)
- `active_only` (`true`/`false`, default `true`)

**Request**

```http
GET /api/v1/users?limit=50&offset=0&active_only=true
Authorization: Bearer <jwt>
```

**Response 200**

```json
{
  "items": [
    {
      "id": 1,
      "telegram_id": 123456789,
      "username": "testuser",
      "first_name": "Test",
      "last_name": "User",
      "email": null,
      "is_active": true,
      "is_banned": false,
      "trial_used": false,
      "referral_code": "ABCD1234",
      "referred_by": null,
      "referral_count": 0,
      "created_at": "2026-01-01T10:00:00",
      "last_activity": "2026-01-05T13:00:00"
    }
  ],
  "limit": 50,
  "offset": 0
}
```

---

### `POST /api/v1/users/<telegram_id>/ban`

Блокировка или разблокировка пользователя.

**Request**

```http
POST /api/v1/users/123456789/ban
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "banned": true
}
```

**Response 200**

```json
{
  "telegram_id": 123456789,
  "banned": true,
  "updated": true
}
```

## Админский контур

### `GET /api/v1/admin/dashboard`

Сводная статистика по пользователям и БД.

**Response 200**

```json
{
  "users": {
    "total": 150,
    "active": 120,
    "banned": 4,
    "new_last_30_days": 20
  },
  "database": {
    "type": "SQLite",
    "version": "3.44.0",
    "url": "data/database.db",
    "tables": {
      "users": 150,
      "subscriptions": 80,
      "payments": 40
    }
  }
}
```

---

### `POST /api/v1/admin/backup`

Создание резервной копии SQLite БД.

**Request**

```http
POST /api/v1/admin/backup
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "path": "backups/manual_backup.db"
}
```

`path` можно не передавать — будет создан файл с timestamp.

**Response 200**

```json
{
  "status": "ok",
  "backup_path": "backups/database_backup_20260219_120000.db"
}
```

## Системные endpoints

- `GET /health` — проверка состояния сервиса.
- `GET /metrics` — Prometheus-метрики.

## Формат ошибок

Общий формат ошибки:

```json
{
  "error": "Error message"
}
```

Некоторые исключения могут возвращать расширенный формат:

```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR"
}
```
