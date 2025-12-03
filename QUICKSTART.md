# 🎯 QUICK REFERENCE - Langkah Setup Singkat

## ⚡ Setup Cepat (5 Menit)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup .env

```bash
cp .env.example .env
nano .env
```

Isi minimal:

```env
BOT_TOKEN=YOUR_BOT_TOKEN_FROM_BOTFATHER
DEFAULT_DOMAIN=jhopan.id
DEFAULT_SUBDOMAIN=s
```

### 3. Test Lokal

```bash
# Terminal 1
python web/server.py

# Terminal 2
python run.py
```

Bot sudah jalan! Test di Telegram dengan `/start`

---

## 🌐 Setup Production (Laptop 24/7)

### Langkah 1: Install Cloudflared

```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

### Langkah 2: Login & Buat Tunnel

```bash
cloudflared tunnel login
cloudflared tunnel create shortlink
```

### Langkah 3: Config Tunnel

```bash
nano ~/.cloudflared/config.yml
```

Isi:

```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /home/USERNAME/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: s.jhopan.id
    service: http://localhost:5000
  - hostname: "*.jhopan.id"
    service: http://localhost:5000
  - service: http_status:404
```

### Langkah 4: Route DNS

```bash
cloudflared tunnel route dns shortlink s.jhopan.id
cloudflared tunnel route dns shortlink "*.jhopan.id"
```

### Langkah 5: Run Everything

```bash
# Di folder project
./start_all.sh
```

✅ **DONE!** Bot sudah production ready!

---

## 📝 Command Telegram yang Sering Dipakai

```bash
# Buat short link random
/short https://forms.google.com

# Buat dengan custom alias
/short https://forms.google.com DaftarPMKFT2025

# Short link + QR code
/both https://forms.google.com EventBulan12

# Lihat stats
/mystats

# Lihat semua link
/mylinks
```

---

## 🔍 Troubleshooting Cepat

### Bot tidak respond?

```bash
tail -f logs/bot.log
```

### Link tidak redirect?

```bash
curl http://localhost:5000/api/health
tail -f logs/webserver.log
```

### Check semua status

```bash
./check_status.sh
```

---

## 📚 Dokumentasi Lengkap

Untuk panduan detail, baca: **[SETUP_GUIDE.md](SETUP_GUIDE.md)**

---

## 💡 Tips

1. **Custom Domain User Lain:**

   - User setup CNAME di DNS mereka → `s.jhopan.id`
   - User kirim `/adddomain jeje.id`
   - User pakai: `/short https://... alias jeje.id`

2. **Auto Start di Boot:**

   ```bash
   sudo systemctl enable shortlink-web
   sudo systemctl enable shortlink-bot
   sudo systemctl enable cloudflared
   ```

3. **Monitor Logs Real-time:**
   ```bash
   tail -f logs/*.log
   ```

---

**🎉 Selesai! Sistem sudah jalan 24/7 dengan domain custom sendiri!**
