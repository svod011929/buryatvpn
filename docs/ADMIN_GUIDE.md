# Admin Guide

Практические сценарии для администраторов BuryatVPN.

## 1. Авторизация

1. Выполните `POST /api/v1/auth/login`.
2. Сохраните `access_token`.
3. Передавайте его в `Authorization: Bearer <token>`.

## 2. Ежедневные операции

### Проверить состояние системы

- `GET /health`
- `GET /metrics`
- `GET /api/v1/admin/dashboard`

### Управление пользователями

- Просмотр пользователей: `GET /api/v1/users`
- Поиск: `GET /api/v1/users?search=<term>`
- Блокировка: `POST /api/v1/users/<telegram_id>/ban` с `{ "banned": true }`
- Разблокировка: `POST /api/v1/users/<telegram_id>/ban` с `{ "banned": false }`

### Резервная копия SQLite

- `POST /api/v1/admin/backup`
- Рекомендуется запускать регулярно через cron или external scheduler.

## 3. Рекомендации по безопасности

- Используйте длинный и сложный пароль администратора.
- Храните только bcrypt-хэш пароля (`WEB_ADMIN_PASSWORD_HASH`).
- Регулярно ротируйте `JWT_SECRET_KEY` и `SECRET_KEY`.
- Ограничьте доступ к API по IP на уровне reverse proxy.

## 4. Что делать при инциденте

1. Заблокировать подозрительные учётные записи.
2. Проверить логи приложения и nginx.
3. Принудительно сменить admin password hash.
4. Ротировать секреты (`JWT_SECRET_KEY`, `SECRET_KEY`, `ENCRYPTION_KEY`).
5. Проверить целостность БД и наличие свежего backup.

## 5. Полезные команды

```bash
# Логи сервиса
journalctl -u buryatvpn -f

# Статус сервиса
systemctl status buryatvpn

# Перезапуск
systemctl restart buryatvpn
```
