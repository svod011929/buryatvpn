# BuryatVPN Deployment Guide

## Requirements

- Python 3.9+
- Redis Server
- PostgreSQL (for production) or SQLite (for development)
- Nginx (for production)
- SSL certificates (Let's Encrypt recommended)

## Production Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv redis-server postgresql nginx certbot

# Create user for application
sudo useradd -m -s /bin/bash buryatvpn
sudo su - buryatvpn
```

### 2. Application Setup

```bash
# Clone repository
git clone https://github.com/svod011929/buryatvpn.git
cd buryatvpn

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

### 3. Database Setup

```bash
# PostgreSQL setup
sudo -u postgres createuser buryatvpn
sudo -u postgres createdb buryatvpn -O buryatvpn
sudo -u postgres psql -c "ALTER USER buryatvpn PASSWORD 'secure_password';"

# Run migrations
python -m alembic upgrade head
```

### 4. Systemd Services

Create `/etc/systemd/system/buryatvpn.service`:

```ini
[Unit]
Description=BuryatVPN Service
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=buryatvpn
WorkingDirectory=/home/buryatvpn/buryatvpn
Environment=PATH=/home/buryatvpn/buryatvpn/venv/bin
ExecStart=/home/buryatvpn/buryatvpn/venv/bin/python -m app.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable buryatvpn
sudo systemctl start buryatvpn
```

### 5. Nginx Configuration

Create `/etc/nginx/sites-available/buryatvpn`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # API and webhook
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /webhook {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Static files
    location /static/ {
        alias /home/buryatvpn/buryatvpn/static/;
        expires 30d;
    }

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
}
```

### 6. SSL Certificate

```bash
sudo certbot --nginx -d your-domain.com
```

### 7. Monitoring Setup

```bash
# Start monitoring services
docker-compose up -d prometheus grafana

# Configure Grafana
# Access http://your-domain.com:3000
# Default login: admin/admin
```

### 8. Backup Strategy

Create backup script `/home/buryatvpn/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/buryatvpn/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump buryatvpn > $BACKUP_DIR/db_$DATE.sql

# Application backup
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /home/buryatvpn/buryatvpn

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

Add to crontab:
```bash
0 2 * * * /home/buryatvpn/backup.sh
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Configure firewall (ufw)
- [ ] Enable fail2ban
- [ ] Regular security updates
- [ ] Monitor logs
- [ ] Use strong SSL configuration
- [ ] Regular backups
- [ ] Monitor resource usage

## Troubleshooting

### Check logs
```bash
# Application logs
sudo journalctl -u buryatvpn -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### Common issues
1. Database connection errors - check credentials and PostgreSQL status
2. Redis connection errors - ensure Redis is running
3. Permission errors - check file ownership and permissions
4. SSL certificate errors - verify certificate validity
