# Telegram V2Ray Subscription Aggregator

A real-time Telegram scraper and subscription generator for V2Ray-based
configurations (vless, trojan, ss, hysteria2, tuic, etc).

This project listens to one or more public Telegram channels, extracts
valid proxy configuration URIs, normalizes and deduplicates them, stores
them persistently, and exposes a subscription URL compatible with
V2Ray/Xray clients.

---

## ✨ Key Features

- Real-time scraping from **multiple Telegram channels**
- Supports all common V2Ray protocols:
  vless, trojan, ss, ssr, hysteria2, tuic, etc
- Automatically excludes `vmess://`
- Renames all configs to a **fixed custom name**
- Deduplication based on **UUID (username)**
- Persistent storage using SQLite
- Keeps only the latest N configs (configurable)
- HTTP subscription endpoint:
  - Plain text
  - Base64 encoded
- Ready for Cloudflare Tunnel, VPS, or bot integration

---

## 🧠 How It Works

1. Connects to Telegram using a user account (Telethon / MTProto)
2. Listens to new messages from configured channels
3. Extracts URI-like strings from messages
4. Filters invalid or unwanted configs
5. Renames config names (after `#`) to a fixed value
6. Deduplicates configs using UUID as the unique key
7. Stores configs in SQLite with timestamps
8. Serves configs via an HTTP `/sub` endpoint

---

## 📂 Project Structure

app/
  parser.py              # URI extraction, filtering, rename, dedup key
  config.py              # Environment-based configuration
  http_server.py         # Subscription HTTP endpoint
  telegram/
    listener.py          # Telegram channel listener
  storage/
    sqlite_store.py      # SQLite storage + dedup + trimming
run_step1.py             # Main entry point
.env                     # Runtime configuration

---

## ⚙️ Environment Configuration (.env)

TG_API_ID=YOUR_API_ID
TG_API_HASH=YOUR_API_HASH

TG_CHANNELS=@ConfigsHub,@AnotherChannel

MAX_ITEMS=1000
FIXED_NAME=📱Telegram | @FNET00
DB_PATH=configs.db

---

## 🚀 Installation

pip install telethon python-dotenv aiosqlite fastapi uvicorn

---

## ▶️ Running

python run_step1.py

First run will ask for Telegram login code.

---

## 🔗 Subscription URLs

Base64 (default):
http://127.0.0.1:8000/sub

Plain:
http://127.0.0.1:8000/sub?b64=false

Limit:
http://127.0.0.1:8000/sub?limit=200

---

## ☁️ Deployment

This project requires a long-running process.
Recommended:
- VPS
- Always-on Windows/Linux machine
- Cloudflare Tunnel

Not suitable for:
- GitHub Actions
- Cloudflare Workers

---

## ⚠️ Disclaimer

For educational and personal use only.
You are responsible for compliance with Telegram ToS and local laws.

---

## 📌 License

MIT
