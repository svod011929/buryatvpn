<!-- kododrive-readme-style -->

<div align="center">
  <img src="./assets/readme-header.svg" width="100%" alt="buryatvpn" />
</div>

<br/>

<div align="center">
  <img src="./assets/readme-meta.svg" width="100%" alt="meta" />
</div>

<br/>

<p align="center">
  <a href="https://github.com/svod011929/buryatvpn"><img src="https://img.shields.io/badge/GitHub-buryatvpn-0D1117?style=for-the-badge&logo=github&logoColor=38BDF8" alt="repo" /></a>
  <a href="https://t.me/KodoDrive"><img src="https://img.shields.io/badge/Telegram-@KodoDrive-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="tg" /></a>
  <a href="https://github.com/svod011929"><img src="https://img.shields.io/badge/Author-svod011929-7C3AED?style=for-the-badge&logo=github&logoColor=white" alt="author" /></a>
</p>

<!-- /kododrive-readme-style -->

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

---

<!-- kododrive-projects-block -->

## Проекты KodoDrive

Другие проекты автора: [профиль @svod011929](https://github.com/svod011929) · [Telegram](https://t.me/KodoDrive)

### VPN и инфраструктура

- **BuryatVPN — VPN-сервис + Telegram** ← ты здесь
- [VPN Server Installer — VLESS + TLS](https://github.com/svod011929/vpn-server-installer)
- [3X-UI Auto Installer](https://github.com/svod011929/3x-ui-auto-installer)
- [AWG Bot Installer — AmneziaWG](https://github.com/svod011929/awg-bot-installer)
- [RemnaShop Installer](https://github.com/svod011929/remnashop-installer)
- [VPN Auto Installer — панели](https://github.com/svod011929/vpn-auto-installer)
- [VPNHubBot — Telegram VPN-бот](https://github.com/svod011929/VPNHubBot)

### Telegram и автоматизация

- [KDS Server Panel — SSH из Telegram](https://github.com/svod011929/KDS_Server_Panel)
- [Telegram → VK Poster](https://github.com/svod011929/telegram-to-vk-poster)
- [KDS Parser CryptoBot](https://github.com/svod011929/kds_parser_cryptobot)
- [Auction Bot](https://github.com/svod011929/auction-bot)
- [Invest Bot](https://github.com/svod011929/invest-bot)
- [Crypto Check Bot](https://github.com/svod011929/crypto-check-bot)
- [KodoRefStarsBot](https://github.com/svod011929/KodoRefStarsBot)

### Магазины и финансы

- [KodoCashFlow](https://github.com/svod011929/KodoCashFlow)
- [Telegram Crypto Shop](https://github.com/svod011929/telegram-crypto-shop)
- [TalkProfit](https://github.com/svod011929/talkprofit)

### Сайты

- [KodoDrive Portfolio](https://github.com/svod011929/kododrive-portfolio)
- [kododrive.github.io](https://github.com/svod011929/kododrive.github.io)

<!-- /kododrive-projects-block -->
