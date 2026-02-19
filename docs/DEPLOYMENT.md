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
