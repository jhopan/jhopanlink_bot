# 📚 Dokumentasi Index

Selamat datang di ShortLink & QR Code Bot! Pilih dokumentasi sesuai kebutuhan Anda:

## 🚀 Mulai Cepat

### Baru Pertama Kali?

👉 **[README.md](README.md)** - Mulai di sini! Overview lengkap sistem

### Mau Langsung Setup?

👉 **[QUICKSTART.md](QUICKSTART.md)** - Setup cepat 5 menit

### Setup Production (24/7)?

👉 **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Panduan lengkap step-by-step

### Mau Lihat Summary?

👉 **[SUMMARY.md](SUMMARY.md)** - Overview teknis & arsitektur

---

## 📖 Dokumentasi Lengkap

| File                                 | Untuk Siapa | Isi                             |
| ------------------------------------ | ----------- | ------------------------------- |
| **[README.md](README.md)**           | Semua user  | Overview, fitur, quick start    |
| **[QUICKSTART.md](QUICKSTART.md)**   | Developer   | Setup cepat & command reference |
| **[SETUP_GUIDE.md](SETUP_GUIDE.md)** | Sysadmin    | Production setup lengkap        |
| **[SUMMARY.md](SUMMARY.md)**         | Developer   | Arsitektur & struktur sistem    |

---

## 🎯 Berdasarkan Tujuan

### Saya Mau Testing Lokal

1. Baca: [QUICKSTART.md](QUICKSTART.md)
2. Install dependencies
3. Setup .env
4. Run bot & web server
5. Test di Telegram

### Saya Mau Deploy Production

1. Baca: [SETUP_GUIDE.md](SETUP_GUIDE.md)
2. Setup Cloudflare
3. Install Cloudflared
4. Setup Tunnel
5. Run as service

### Saya Mau Paham Teknisnya

1. Baca: [SUMMARY.md](SUMMARY.md)
2. Lihat code di:
   - `database/db_manager.py`
   - `web/server.py`
   - `src/handlers/`

### Saya Mau Custom/Modifikasi

1. Baca struktur di [SUMMARY.md](SUMMARY.md)
2. Edit sesuai kebutuhan:
   - Bot commands: `src/handlers/commands.py`
   - Web server: `web/server.py`
   - Database: `database/db_manager.py`
   - Config: `config/config.py`

---

## 💻 File Penting Lainnya

### Configuration

- `.env.example` - Template environment variables
- `config/config.py` - Centralized configuration

### Scripts

- `run.py` - Run bot
- `start_all.sh` - Start semua (Linux)
- `stop_all.sh` - Stop semua (Linux)
- `check_status.sh` - Check status (Linux)

### Dependencies

- `requirements.txt` - Python packages

---

## 🆘 Troubleshooting

### Bot tidak jalan?

1. Check logs: `tail -f logs/bot.log`
2. Lihat [QUICKSTART.md](QUICKSTART.md) → Troubleshooting

### Link tidak redirect?

1. Check web server: `curl http://localhost:5000/api/health`
2. Lihat [SETUP_GUIDE.md](SETUP_GUIDE.md) → Troubleshooting

### Mau setup custom domain?

Lihat [SETUP_GUIDE.md](SETUP_GUIDE.md) → Custom Domain untuk User Lain

---

## 📞 Need Help?

1. ✅ Baca dokumentasi yang sesuai di atas
2. ✅ Check code comments
3. ✅ Lihat logs di folder `logs/`
4. ✅ Create issue di repository

---

**Happy Coding! 🚀**
