# Deployment Guide

Гайд по развёртыванию BuryatVPN в production.

## 1. Требования

- Linux server (Ubuntu 22.04+)
- Python 3.9+
- Redis
- PostgreSQL (рекомендуется для production)
- Nginx + SSL

## 2. Подготовка сервера

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv redis-server postgresql nginx certbot python3-certbot-nginx
```

## 3. Развёртывание приложения

```bash
git clone https://github.com/svod011929/buryatvpn.git
cd buryatvpn
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Заполните `.env` (минимум: БД, Redis, security keys, admin credentials).

## 4. PostgreSQL

```bash
sudo -u postgres createuser buryatvpn
sudo -u postgres createdb buryatvpn -O buryatvpn
sudo -u postgres psql -c "ALTER USER buryatvpn PASSWORD 'strong_password';"
```

Пример `DATABASE_URL`:

```env
DATABASE_URL=postgresql+asyncpg://buryatvpn:strong_password@127.0.0.1:5432/buryatvpn
```

## 5. systemd unit

Создайте `/etc/systemd/system/buryatvpn.service`:

```ini
[Unit]
Description=BuryatVPN
After=network.target redis.service postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/buryatvpn
Environment=PATH=/opt/buryatvpn/venv/bin
ExecStart=/opt/buryatvpn/venv/bin/python -m app.main
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable buryatvpn
sudo systemctl start buryatvpn
sudo systemctl status buryatvpn
```

## 6. Nginx reverse proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/buryatvpn /etc/nginx/sites-enabled/buryatvpn
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d your-domain.com
```

## 7. Мониторинг и эксплуатация

- Проверка состояния: `GET /health`
- Метрики: `GET /metrics`
- Логи приложения: `journalctl -u buryatvpn -f`

## 8. Резервные копии

Для SQLite доступен API backup endpoint `POST /api/v1/admin/backup`.

Для PostgreSQL используйте `pg_dump` по cron:

```bash
pg_dump -Fc buryatvpn > /var/backups/buryatvpn_$(date +%F).dump
```

## 9. Чеклист перед запуском

- [ ] Установлены безопасные значения всех ключей в `.env`
- [ ] Ограничен доступ к серверу по firewall
- [ ] Включён HTTPS
- [ ] Настроены бэкапы и проверено восстановление
- [ ] Настроен мониторинг и алертинг
