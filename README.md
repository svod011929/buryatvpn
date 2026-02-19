# BuryatVPN

🚀 Современный VPN-сервис с Telegram-ботом и веб-API для администрирования.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Что внутри

- Telegram-бот (aiogram) для клиентского взаимодействия.
- REST API (Flask) для админских операций.
- Асинхронная работа с БД через SQLAlchemy.
- Redis-кэш и monitoring endpoints (`/health`, `/metrics`).
- Базовые механизмы безопасности: JWT, rate limiting, security headers.

## Структура проекта

```text
buryatvpn/
├── app/                 # Бизнес-логика, API, бот, БД, сервисы
├── config/              # Настройки и логирование
├── docs/                # Документация
├── migrations/          # Миграции (заготовка)
├── monitoring/          # Конфиги мониторинга
└── tests/               # Тесты
```

## Быстрый старт

### 1) Подготовка проекта

```bash
git clone https://github.com/svod011929/buryatvpn.git
cd buryatvpn
```

### 2) Автоустановка (рекомендуется)

```bash
./scripts/install.sh
```

Для dev-режима:

```bash
./scripts/install.sh --with-dev
```

### 3) Минимальные переменные

Заполните в `.env`:

- `BOT_TOKEN`
- `SECRET_KEY`
- `ENCRYPTION_KEY` (валидный Fernet key)
- `JWT_SECRET_KEY`
- `WEB_ADMIN_EMAIL`
- `WEB_ADMIN_PASSWORD_HASH`

> Для локальной разработки можно оставить SQLite: `DATABASE_URL=sqlite:///data/database.db`.

### 4) Запуск

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

- [Установка (auto-installer)](docs/INSTALL.md)
- [API reference](docs/API.md)
- [Гайд по деплою](docs/DEPLOYMENT.md)
- [Админ-операции](docs/ADMIN_GUIDE.md)
- [Архитектура](docs/ARCHITECTURE.md)
- [Конфигурация окружения](docs/CONFIGURATION.md)

## Разработка

```bash
pip install -r requirements-dev.txt
pre-commit install
pytest
black .
isort .
```

## Мониторинг

- Health-check: `GET /health`
- Prometheus metrics: `GET /metrics`

## Лицензия

MIT — см. [LICENSE](LICENSE).
