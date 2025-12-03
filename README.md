# 🤖 ShortLink & QR Code Telegram Bot

Bot Telegram yang menyediakan layanan **custom short link dengan domain sendiri** dan QR code generator!

## ⭐ Fitur Utama

- 🔗 **Custom Short Link** - Domain sendiri (misal: `s.jhopan.id/DaftarPMKFT`)
- 🎨 **Custom Alias** - Link yang mudah diingat
- 🌐 **Multi Domain** - Support domain custom dari user lain
- 📱 **QR Code Generator** - High quality QR codes
- 📊 **Analytics** - Track clicks untuk setiap link
- 👤 **Personal Dashboard** - Lihat semua link & stats Anda
- 🔒 **Privacy** - Data tersimpan lokal di server Anda
- 💰 **100% Gratis** - Pakai laptop sendiri + Cloudflare Tunnel

## 🎯 Contoh Penggunaan

```
❌ Link Panjang:
https://docs.google.com/forms/d/e/1FAIpQLSc.../viewform

✅ Jadi:
https://s.jhopan.id/DaftarKepengurusanPMKFT2025
atau
https://pmkft.jhopan.id/Daftar
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Environment

```bash
cp .env.example .env
# Edit .env - masukkan Bot Token dan Domain Anda
```

### 3. Jalankan

```bash
# Web Server
python web/server.py

# Bot (terminal terpisah)
python run.py
```

### 4. Setup Production (Linux 24/7)

**📖 Lihat panduan lengkap di: [SETUP_GUIDE.md](SETUP_GUIDE.md)**

## 📖 Command Bot

### Short Link

```
/short <URL>                        - Random code
/short <URL> <alias>                - Custom alias
/short <URL> <alias> <domain>       - Custom domain

Contoh:
/short https://forms.google.com
→ https://s.jhopan.id/abc123

/short https://forms.google.com DaftarPengurus2025
→ https://s.jhopan.id/DaftarPengurus2025
```

### QR Code

```
/qr <text atau URL>                 - Generate QR code
/both <URL> [alias]                 - Short link + QR code
```

### Personal

```
/mystats                            - Statistik Anda
/mylinks                            - List link Anda
/adddomain <domain>                 - Register domain custom
```

## 🌐 Arsitektur

```
User → Telegram Bot → SQLite → Flask Server
                                    ↓
                            Cloudflare Tunnel
                                    ↓
                            Custom Domain (s.jhopan.id)
```

## 💰 Biaya: Rp 0,- (100% Gratis!)

- ✅ Domain: Sudah punya
- ✅ Laptop: Sudah punya
- ✅ Cloudflare: Gratis
- ✅ SSL: Gratis

## 📚 Dokumentasi Lengkap

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Panduan setup production lengkap
- **Database schema** - Lihat `database/db_manager.py`
- **API docs** - Lihat `web/server.py`

## 📁 Struktur

```
├── app/              # Bot application
├── web/              # Flask web server
├── database/         # Database manager
├── src/              # Handlers & utils
├── config/           # Configuration
├── logs/             # Log files
└── SETUP_GUIDE.md    # Setup production guide
```

## 🔧 Scripts

```bash
./start_all.sh      # Start semua (Linux)
./stop_all.sh       # Stop semua
./check_status.sh   # Check status
```

---

**⭐ Star jika berguna! | 🚀 Happy Short Linking!**
