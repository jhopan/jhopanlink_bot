# 🔗 JhopanLink Bot

> **Custom Short Link & QR Code Generator** - Telegram Bot dengan domain sendiri!

Bot Telegram yang menyediakan layanan **short link dengan custom domain** dan **QR code generator**. Deploy di laptop/server sendiri menggunakan Cloudflare Tunnel (gratis, tanpa port forwarding).

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot%20API-20.7-blue.svg)](https://python-telegram-bot.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ⭐ Fitur Utama

- 🔗 **Custom Short Link** - Domain sendiri (contoh: `s.jhopan.id/DaftarPMK`)
- 🔄 **Smart Fallback** - Otomatis pakai TinyURL jika web server mati
- 🎨 **Custom Alias** - Buat link yang mudah diingat
- 🌐 **Multi Domain** - Support domain custom dari user lain
- 📱 **QR Code Generator** - High quality QR codes dengan logo
- 📊 **Analytics** - Track jumlah klik untuk setiap link
- 👤 **Personal Dashboard** - Lihat semua link & statistik Anda
- 🔒 **Privacy First** - Data tersimpan lokal di server Anda sendiri
- 💰 **100% Gratis** - Self-hosted dengan Cloudflare Tunnel gratis
- 🚀 **Easy Setup** - Script install otomatis dengan guided setup

---

## 🎯 Demo

**Before:**

```
❌ https://docs.google.com/forms/d/e/1FAIpQLScXYZ123.../viewform?usp=sf_link
```

**After:**

```
✅ https://s.jhopan.id/DaftarKepengurusan2025
✅ https://pmkft.jhopan.id/Daftar
```

---

## 📋 Requirements

- **Python 3.9+** (tested on 3.13)
- **Domain** yang sudah terdaftar di Cloudflare
- **Linux/Windows Server** atau laptop yang bisa running 24/7
- **Telegram Bot Token** dari [@BotFather](https://t.me/BotFather)
- **Cloudflare Account** (gratis)

---

## 🚀 Quick Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/jhopan/jhopanlink_bot.git
cd jhopanlink_bot
```

### 2️⃣ Run Install Script

```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

Script akan otomatis:

- ✅ Install Python dependencies
- ✅ Setup virtual environment
- ✅ Konfigurasi `.env` (interaktif)
- ✅ Inisialisasi database SQLite
- ✅ Setup TinyURL fallback (optional)

**Saat instalasi, Anda akan ditanya:**

1. **Bot Token** - Dari @BotFather (wajib)
2. **Domain** - Kosongkan untuk TinyURL-only, atau:
   - Domain gratis: `namaanda.duckdns.org`
   - Domain sendiri: `jhopan.id`
3. **TinyURL API Key** - Optional (tekan Enter untuk skip)

### 3️⃣ Setup Cloudflare Tunnel (jika pakai domain sendiri)

```bash
# Login ke Cloudflare
cloudflared tunnel login

# Buat tunnel
cloudflared tunnel create shortlink

# Edit config
nano ~/.cloudflared/config.yml
```

**Config example:**

```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /home/username/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: s.yourdomain.com
    service: http://localhost:5000
  - service: http_status:404
```

```bash
# Route DNS
cloudflared tunnel route dns shortlink s.yourdomain.com
```

### 4️⃣ Start Bot

**Option A: Simple Start (Foreground)**

```bash
chmod +x scripts/start.sh
./scripts/start.sh
```

**Option B: Run as Systemd Service (Production)**

```bash
sudo ./scripts/install-service.sh
sudo systemctl start jhopanlink-bot
sudo systemctl start jhopanlink-tunnel
sudo systemctl enable jhopanlink-bot  # Auto-start on boot
```

**Option C: Create Shortcuts (Recommended)**

```bash
./scripts/create-aliases.sh
source ~/.bashrc

# Sekarang bisa pakai:
jlink-start
jlink-stop
jlink-logs
jlink-status
```

---

## 📦 Project Structure

```
jhopanlink_bot/
├── app/
│   ├── bot.py              # Telegram bot main class
│   └── main.py             # Entry point
├── config/
│   └── config.py           # Configuration management
├── database/
│   └── db_manager.py       # SQLite database operations
├── src/
│   ├── handlers/
│   │   ├── commands.py     # Command handlers (/start, /help, etc)
│   │   └── messages.py     # Message handlers (URL processing)
│   └── utils/
│       ├── qr_generator.py # QR code generation
│       └── shortlink_generator.py
├── web/
│   └── server.py           # Flask web server (redirect handler)
├── scripts/
│   ├── install.sh          # Main installation script
│   ├── start.sh            # Start bot (simple)
│   ├── install-service.sh  # Install as systemd service
│   ├── create-aliases.sh   # Create command shortcuts
│   ├── check_status.sh     # Check running status
│   └── stop_all.sh         # Stop all services
├── .env.example            # Environment variables template
├── requirements.txt        # Python dependencies
└── run.py                  # Run bot + web server
```

---

## 🎮 Bot Commands

| Command                | Description              |
| ---------------------- | ------------------------ |
| `/start`               | Mulai menggunakan bot    |
| `/help`                | Lihat panduan penggunaan |
| `/about`               | Info tentang bot         |
| `/short <url> [alias]` | Buat short link          |
| `/qr <url>`            | Generate QR code         |
| `/both <url> [alias]`  | Short link + QR code     |
| `/stats`               | Lihat statistik Anda     |
| `/mylinks`             | Daftar semua link Anda   |
| `/adddomain <domain>`  | Tambah custom domain     |

**Auto-detect URL:** Kirim URL langsung tanpa command untuk short link otomatis.

---

## ⚙️ Configuration

Edit file `.env`:

```env
# Telegram Bot
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Web Server
WEB_HOST=0.0.0.0
WEB_PORT=5000

# Domain Settings (OPSIONAL)
# Kosongkan jika hanya pakai TinyURL
# Domain gratis: duckdns.org (https://www.duckdns.org)
DEFAULT_DOMAIN=
DEFAULT_SUBDOMAIN=s

# TinyURL API (Opsional - Fallback)
TINYURL_API_KEY=your_tinyurl_api_key
```

### Domain Options

**Opsi 1: Tanpa Domain (TinyURL Only)**

Kosongkan `DEFAULT_DOMAIN`, bot akan otomatis pakai TinyURL:

```env
DEFAULT_DOMAIN=
```

**Opsi 2: Domain Gratis**

Gunakan layanan domain gratis:

- **DuckDNS** (Recommended): https://www.duckdns.org
  - Gratis subdomain `.duckdns.org`
  - Contoh: `jhopan.duckdns.org`
- **Afraid.org**: https://freedns.afraid.org
  - Banyak pilihan domain gratis

**Opsi 3: Domain Sendiri**

Jika punya domain berbayar (Namecheap, Cloudflare, dll):

```env
DEFAULT_DOMAIN=jhopan.id
DEFAULT_SUBDOMAIN=s
```

---

## 🛠️ Management Commands

### Using Scripts

```bash
# Start (foreground)
./scripts/start.sh

# Check status
./scripts/check_status.sh

# Stop
./scripts/stop_all.sh
```

### Using Systemd (if installed as service)

```bash
# Start
sudo systemctl start jhopanlink-bot
sudo systemctl start jhopanlink-tunnel

# Stop
sudo systemctl stop jhopanlink-bot

# Restart
sudo systemctl restart jhopanlink-bot

# Status
sudo systemctl status jhopanlink-bot

# Logs
sudo journalctl -u jhopanlink-bot -f
```

### Using Aliases (if created)

```bash
jlink-start          # Start bot
jlink-stop           # Stop bot
jlink-restart        # Restart bot
jlink-logs           # View logs (live)
jlink-status         # Check status
jlink-cd             # Go to bot directory
jlink-tunnel         # Start tunnel manually
jlink-tunnel-status  # Check tunnel status
```

---

## 🌐 Web Interface

Setelah bot jalan, akses web interface:

- **Local:** http://localhost:5000
- **Public:** https://s.yourdomain.com

**Features:**

- Homepage dengan statistik total
- API endpoint untuk membuat link
- Auto redirect untuk short links
- Custom domain support

**API Example:**

```bash
curl -X POST http://localhost:5000/api/create \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/very/long/url",
    "alias": "mylink",
    "user_id": 123456789
  }'
```

---

## 🗄️ Database Schema

SQLite database dengan 3 tabel:

### `short_links`

- `id` - Primary key
- `short_code` - 6-char unique code
- `original_url` - Target URL
- `custom_alias` - Custom alias (optional)
- `domain` - Domain name
- `user_id` - Telegram user ID
- `created_at` - Timestamp
- `clicks` - Click counter

### `custom_domains`

- `id` - Primary key
- `domain` - Domain name
- `user_id` - Owner user ID
- `added_at` - Timestamp

### `click_logs`

- `id` - Primary key
- `link_id` - Foreign key to short_links
- `clicked_at` - Timestamp
- `ip_address` - Visitor IP (optional)
- `user_agent` - Browser info (optional)

---

## 🔄 Smart Fallback System

Bot ini punya sistem fallback otomatis untuk memastikan short link tetap berfungsi:

### Primary: Custom Domain (jika ada)

- ✅ Link pakai domain sendiri (contoh: s.jhopan.id/xxx)
- ✅ Full control & analytics
- ✅ Custom alias support
- ✅ No dependency ke third-party

### Fallback: TinyURL (Automatic)

- 🔄 Aktif ketika:
  - Web server mati
  - Tidak ada custom domain (DEFAULT_DOMAIN kosong)
- 🔄 Bot auto-detect server status
- 🔄 Transparent untuk user
- ⚠️ Link jadi `tinyurl.com/xxx`

**Flow:**

```
User → Bot → Check Custom Domain
              ├─ ✅ Ada Domain + Server Online  → s.jhopan.id/xxx (Primary)
              ├─ ❌ Server Offline              → tinyurl.com/xxx (Fallback)
              └─ ❌ No Domain                   → tinyurl.com/xxx (Fallback)
```

**Setup TinyURL API Key (Optional):**

1. Daftar gratis di: https://tinyurl.com/app/dev
2. Dapatkan API key
3. Tambahkan saat instalasi atau edit `.env`: `TINYURL_API_KEY=your_key`

**Mode TinyURL-Only:**

Jika tidak punya domain, kosongkan saja `DEFAULT_DOMAIN`:

```env
DEFAULT_DOMAIN=
```

Bot akan selalu pakai TinyURL (tanpa web server).

---

## 🔒 Security & Privacy

- ✅ **Data Ownership** - Semua data di server Anda sendiri
- ✅ **Smart Fallback** - Tetap berfungsi meski server down
- ✅ **SSL/TLS** - Automatic HTTPS via Cloudflare
- ✅ **Private Logs** - Click analytics tersimpan lokal
- ✅ **No Tracking** - Tidak ada tracking eksternal

---

## 🐛 Troubleshooting

### Bot tidak start

```bash
# Check logs
tail -f logs/bot.log

# Check Python
python --version  # Harus 3.9+

# Check venv
source venv/bin/activate
pip install -r requirements.txt
```

### Web server error

```bash
# Check port
sudo lsof -i :5000

# Check logs
tail -f logs/webserver.log

# Test manual
python run.py
```

### Cloudflare Tunnel error

```bash
# Check tunnel
cloudflared tunnel list

# Check config
cat ~/.cloudflared/config.yml

# Test tunnel
cloudflared tunnel run shortlink
```

### Module not found error

```bash
# Run with correct path
export PYTHONPATH=/path/to/jhopanlink_bot:$PYTHONPATH
python run.py
```

---

## 🚀 Production Deployment

### Recommended Setup

1. **Install as systemd service** (auto-restart, auto-start on boot)

```bash
sudo ./scripts/install-service.sh
sudo systemctl enable jhopanlink-bot
sudo systemctl enable jhopanlink-tunnel
```

2. **Create aliases** for easy management

```bash
./scripts/create-aliases.sh
```

3. **Setup log rotation** (optional)

```bash
sudo nano /etc/logrotate.d/jhopanlink
```

```
/path/to/jhopanlink_bot/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

4. **Monitor with systemd**

```bash
# Auto-restart on failure
sudo systemctl status jhopanlink-bot
```

---

## 📊 Performance

- ⚡ **Fast Response** - < 100ms redirect time
- 💾 **Lightweight** - ~50MB RAM usage
- 🔄 **Concurrent** - Handle 100+ requests/second
- 📈 **Scalable** - SQLite → PostgreSQL jika perlu

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Jhopan**

- GitHub: [@jhopan](https://github.com/jhopan)
- Domain: [jhopan.id](https://jhopan.id)

---

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot framework
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Cloudflare](https://www.cloudflare.com/) - Tunnel & DNS services
- [QRCode](https://github.com/lincolnloop/python-qrcode) - QR code generation

---

## 📮 Support

Jika ada pertanyaan atau butuh bantuan:

- 🐛 [Open an issue](https://github.com/jhopan/jhopanlink_bot/issues)
- 💬 [Discussions](https://github.com/jhopan/jhopanlink_bot/discussions)

---

**Made with ❤️ for easy link sharing**
