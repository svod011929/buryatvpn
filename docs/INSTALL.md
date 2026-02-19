# Auto Installation

Для быстрого развёртывания используйте скрипт:

```bash
./scripts/install.sh
```

## Что делает скрипт

- создаёт `.venv` (если ещё нет),
- обновляет `pip/setuptools/wheel`,
- устанавливает зависимости из `requirements.txt`,
- при необходимости ставит dev-зависимости,
- создаёт `.env` из `.env.example` (если `.env` отсутствует),
- создаёт каталоги `data/`, `logs/`, `backups/`.

## Параметры

```bash
./scripts/install.sh --help
```

- `--with-dev` — добавить `requirements-dev.txt`
- `--system-packages` — установить системные пакеты через `apt`
- `--python <bin>` — выбрать python бинарь (например `python3.11`)
- `--skip-env-template` — не создавать `.env` автоматически

## Примеры

```bash
# Базовая установка
./scripts/install.sh

# Для разработки
./scripts/install.sh --with-dev

# На чистом Ubuntu сервере
./scripts/install.sh --system-packages
```

## После установки

1. Проверьте и заполните `.env`.
2. Активируйте окружение:
   ```bash
   source .venv/bin/activate
   ```
3. Запустите приложение:
   ```bash
   python -m app.main
   ```
