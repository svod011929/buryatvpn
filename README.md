# BuryatVPN

🚀 **Современный VPN сервис с Telegram ботом и веб-панелью администратора**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🌟 Особенности

- 🤖 **Telegram бот** для управления подписками
- 🌐 **Веб-панель администратора** с современным интерфейсом
- 💳 **Множественные способы оплаты** (YooKassa, CryptoPay, коды оплаты)
- 🔒 **Высокий уровень безопасности** с шифрованием данных
- 📊 **Система аналитики** и мониторинга
- 🎁 **Пробные периоды** и реферальная система
- ⚡ **Высокая производительность** с кэшированием Redis
- 🔧 **X-UI интеграция** для управления VPN серверами

## 🏗️ Архитектура

Проект построен на принципах чистой архитектуры:

```
buryatvpn/
├── 📁 app/                    # Основное приложение
│   ├── 📁 api/               # REST API (Flask)
│   ├── 📁 bot/               # Telegram бот (aiogram)
│   ├── 📁 core/              # Основная бизнес-логика
│   ├── 📁 database/          # Работа с БД
│   └── 📁 services/          # Внешние сервисы
├── 📁 config/                # Конфигурация
├── 📁 migrations/            # Миграции БД
├── 📁 monitoring/            # Мониторинг и метрики
├── 📁 tests/                 # Тесты
└── 📁 docs/                  # Документация
```

## 🚀 Быстрый старт

### Требования

- Python 3.9+
- Redis Server
- SQLite (или PostgreSQL для продакшена)

### Установка

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/svod011929/buryatvpn.git
   cd buryatvpn
   ```

2. **Создайте виртуальное окружение:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или venv\Scripts\activate  # Windows
   ```

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Настройте переменные окружения:**
   ```bash
   cp .env.example .env
   # Отредактируйте .env файл с вашими настройками
   ```

5. **Инициализируйте базу данных:**
   ```bash
   python -m app.database.init_db
   ```

6. **Запустите сервисы:**
   ```bash
   # Запуск бота
   python -m app.bot.main

   # Запуск веб-панели (в другом терминале)
   python -m app.api.main
   ```

## ⚙️ Конфигурация

### Основные переменные окружения

```env
# Telegram Bot
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789,987654321

# База данных
DATABASE_URL=sqlite:///data/database.db

# Redis
REDIS_URL=redis://localhost:6379/0

# Безопасность
SECRET_KEY=your-super-secret-key
ENCRYPTION_KEY=your-encryption-key

# Веб-панель
WEB_HOST=0.0.0.0
WEB_PORT=8000
WEB_ADMIN_EMAIL=admin@example.com
WEB_ADMIN_PASSWORD_HASH=your-bcrypt-hash

# Платежные системы
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_API_KEY=your_api_key
CRYPTOPAY_API_TOKEN=your_token
```

## 🔧 Разработка

### Настройка среды разработки

```bash
# Установка dev зависимостей
pip install -r requirements-dev.txt

# Настройка pre-commit хуков
pre-commit install

# Запуск тестов
pytest

# Форматирование кода
black .
isort .
```

### Структура базы данных

```sql
-- Пользователи
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    trial_used BOOLEAN DEFAULT FALSE,
    referral_code VARCHAR(50) UNIQUE,
    referred_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Подписки
CREATE TABLE subscriptions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    server_id INTEGER REFERENCES servers(id),
    tariff_id INTEGER REFERENCES tariffs(id),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    vless_config TEXT
);
```

## 📊 Мониторинг

Проект включает встроенный мониторинг:

- **Prometheus метрики** на `/metrics`
- **Health checks** на `/health`
- **Логирование** с ротацией в `logs/`
- **Grafana дашборды** в `monitoring/grafana/`

## 🔒 Безопасность

- ✅ Все конфиденциальные данные зашифрованы
- ✅ SSL/TLS проверка включена
- ✅ Rate limiting для API
- ✅ CSRF и XSS защита
- ✅ Валидация входящих данных
- ✅ Аудит логирование

## 🧪 Тестирование

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=app

# Только юнит тесты
pytest tests/unit/

# Только интеграционные тесты
pytest tests/integration/
```

## 📚 API Документация

API документация доступна по адресу `/docs` после запуска веб-сервера.

Основные эндпоинты:
- `GET /api/v1/users` - Список пользователей
- `POST /api/v1/subscriptions` - Создание подписки
- `GET /api/v1/servers` - Список серверов
- `GET /metrics` - Prometheus метрики
- `GET /health` - Health check

## 🐳 Docker

```bash
# Сборка образа
docker build -t buryatvpn .

# Запуск с docker-compose
docker-compose up -d
```

## 📈 Деплой

### Production готовность

- [ ] Настроить PostgreSQL вместо SQLite
- [ ] Настроить Nginx reverse proxy
- [ ] Настроить SSL сертификаты
- [ ] Настроить backup стратегию
- [ ] Настроить мониторинг в продакшене

## 🤝 Участие в разработке

1. Fork репозиторий
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE).

## 🆘 Поддержка

Если у вас есть вопросы или проблемы:

- 📧 Email: support@buryatvpn.com
- 💬 Telegram: @buryatvpn_support
- 🐛 Issues: [GitHub Issues](https://github.com/svod011929/buryatvpn/issues)

## 🙏 Благодарности

- [aiogram](https://github.com/aiogram/aiogram) - для Telegram бота
- [Flask](https://flask.palletsprojects.com/) - для веб-интерфейса
- [SQLAlchemy](https://www.sqlalchemy.org/) - для работы с БД
- [Redis](https://redis.io/) - для кэширования

---

⭐ **Поставьте звезду, если проект оказался полезным!**
