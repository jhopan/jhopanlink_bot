# 🚀 PANDUAN SETUP LENGKAP - ShortLink Bot dengan Custom Domain

## 📋 Daftar Isi

1. [Persiapan](#persiapan)
2. [Setup Bot Telegram](#setup-bot-telegram)
3. [Setup Domain & Cloudflare](#setup-domain--cloudflare)
4. [Install di Laptop Linux](#install-di-laptop-linux)
5. [Setup Cloudflare Tunnel](#setup-cloudflare-tunnel)
6. [Menjalankan Bot & Web Server](#menjalankan-bot--web-server)
7. [Testing](#testing)
8. [Custom Domain untuk User Lain](#custom-domain-untuk-user-lain)

---

## 📦 Persiapan

### Yang Anda Butuhkan:

- ✅ Laptop Linux CLI (24/7 online)
- ✅ Domain: `jhopan.id` (sudah dimiliki)
- ✅ Akun Cloudflare (gratis)
- ✅ Python 3.8+ terinstall
- ✅ Akun Telegram

### Yang TIDAK Perlu Dibeli:

- ❌ VPS/Hosting (pakai laptop sendiri)
- ❌ SSL Certificate (gratis dari Cloudflare)
- ❌ IP Public statis (pakai Cloudflare Tunnel)

---

## 🤖 1. Setup Bot Telegram

### Step 1: Buat Bot di Telegram

1. Buka Telegram dan cari **@BotFather**
2. Kirim command: `/newbot`
3. Masukkan nama bot: `ShortLink PMKFT Bot`
4. Masukkan username: `pmkft_shortlink_bot` (harus unik dan diakhiri `_bot`)
5. Copy **token** yang diberikan (contoh: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Setup Bot Commands

Kirim ke @BotFather:

```
/setcommands
```

Pilih bot Anda, lalu paste commands ini:

```
start - Mulai bot
help - Panduan lengkap
about - Info bot
short - Buat short link
qr - Generate QR code
both - Short link + QR code
mystats - Lihat statistik Anda
mylinks - Daftar link Anda
adddomain - Tambah custom domain
```

---

## 🌐 2. Setup Domain & Cloudflare

### Step 1: Transfer Domain ke Cloudflare (Jika Belum)

1. Login ke [Cloudflare](https://dash.cloudflare.com)
2. Klik **Add Site** → masukkan `jhopan.id`
3. Pilih **Free Plan**
4. Cloudflare akan memberikan nameserver (contoh: `ns1.cloudflare.com`)
5. Login ke registrar domain Anda (tempat beli domain)
6. Ganti nameserver dengan nameserver dari Cloudflare
7. Tunggu propagasi (max 24 jam, biasanya < 1 jam)

### Step 2: Setup DNS Records

Di Cloudflare DNS Management, tambahkan record:

**A Record untuk subdomain:**

```
Type: A
Name: s (atau subdomain lain yang Anda mau)
IPv4: 192.0.2.1 (dummy, akan di-override oleh Cloudflare Tunnel)
Proxy status: Proxied (orange cloud) ✅
TTL: Auto
```

**Wildcard (Optional - untuk support multi custom domain user):**

```
Type: A
Name: *
IPv4: 192.0.2.1
Proxy status: Proxied ✅
TTL: Auto
```

### Step 3: SSL/TLS Settings

Di Cloudflare Dashboard:

1. Klik tab **SSL/TLS**
2. Pilih mode: **Full (strict)** atau **Full**
3. Enable **Always Use HTTPS**

---

## 💻 3. Install di Laptop Linux

### Step 1: Clone/Download Project

```bash
cd ~
mkdir -p projects
cd projects
# Jika sudah ada folder QR_Code, masuk ke sana
cd "Bot Telegram/QR_Code"
```

### Step 2: Install Python Dependencies

```bash
# Install pip jika belum ada
sudo apt update
sudo apt install python3-pip python3-venv -y

# Buat virtual environment
python3 -m venv venv

# Aktifkan virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Setup Environment Variables

```bash
# Copy .env.example ke .env
cp .env.example .env

# Edit .env
nano .env
```

Isi dengan konfigurasi Anda:

```env
# Bot Token dari @BotFather
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Web Server Configuration
WEB_SERVER_HOST=0.0.0.0
WEB_SERVER_PORT=5000

# Default Domain (PENTING!)
DEFAULT_DOMAIN=jhopan.id
DEFAULT_SUBDOMAIN=s

# Optional
TINYURL_API_KEY=
DATABASE_URL=sqlite:///shortlink.db
```

Save dengan `Ctrl+O`, `Enter`, lalu `Ctrl+X`

---

## 🔐 4. Setup Cloudflare Tunnel

### Step 1: Install Cloudflared

```bash
# Download cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb

# Install
sudo dpkg -i cloudflared-linux-amd64.deb

# Verify installation
cloudflared --version
```

### Step 2: Login ke Cloudflare

```bash
cloudflared tunnel login
```

Browser akan terbuka (atau copy URL ke browser). Login dan pilih domain `jhopan.id`.

### Step 3: Buat Tunnel

```bash
# Buat tunnel dengan nama "shortlink"
cloudflared tunnel create shortlink

# Akan muncul Tunnel ID dan credentials file location
# Contoh: Tunnel ID: a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6
```

Copy Tunnel ID yang diberikan!

### Step 4: Buat Config File

```bash
# Buat direktori config
mkdir -p ~/.cloudflared

# Buat config file
nano ~/.cloudflared/config.yml
```

Isi dengan (ganti `TUNNEL_ID` dengan ID Anda):

```yaml
tunnel: TUNNEL_ID
credentials-file: /home/YOUR_USERNAME/.cloudflared/TUNNEL_ID.json

ingress:
  - hostname: s.jhopan.id
    service: http://localhost:5000
  - hostname: "*.jhopan.id"
    service: http://localhost:5000
  - service: http_status:404
```

Save file.

### Step 5: Route DNS ke Tunnel

```bash
# Route subdomain s.jhopan.id ke tunnel
cloudflared tunnel route dns shortlink s.jhopan.id

# Route wildcard (optional, untuk custom domain user lain)
cloudflared tunnel route dns shortlink "*.jhopan.id"
```

### Step 6: Test Tunnel

```bash
# Test tunnel
cloudflared tunnel run shortlink
```

Jika sukses, tekan `Ctrl+C` untuk stop. Tunnel siap digunakan!

---

## 🚀 5. Menjalankan Bot & Web Server

### Opsi 1: Manual Run (untuk testing)

**Terminal 1 - Web Server:**

```bash
cd ~/projects/Bot\ Telegram/QR_Code
source venv/bin/activate
python web/server.py
```

**Terminal 2 - Cloudflare Tunnel:**

```bash
cloudflared tunnel run shortlink
```

**Terminal 3 - Telegram Bot:**

```bash
cd ~/projects/Bot\ Telegram/QR_Code
source venv/bin/activate
python run.py
```

### Opsi 2: Run dengan Screen (Recommended)

```bash
# Install screen jika belum
sudo apt install screen -y

# Session 1: Web Server
screen -S webserver
cd ~/projects/Bot\ Telegram/QR_Code
source venv/bin/activate
python web/server.py
# Tekan Ctrl+A, lalu D untuk detach

# Session 2: Cloudflare Tunnel
screen -S tunnel
cloudflared tunnel run shortlink
# Tekan Ctrl+A, lalu D untuk detach

# Session 3: Telegram Bot
screen -S telegram
cd ~/projects/Bot\ Telegram/QR_Code
source venv/bin/activate
python run.py
# Tekan Ctrl+A, lalu D untuk detach

# Untuk reattach ke session:
screen -r webserver
screen -r tunnel
screen -r telegram

# Lihat semua session:
screen -ls
```

### Opsi 3: Setup Systemd Service (Production)

Buat file service untuk Web Server:

```bash
sudo nano /etc/systemd/system/shortlink-web.service
```

Isi:

```ini
[Unit]
Description=ShortLink Web Server
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/projects/Bot Telegram/QR_Code
Environment="PATH=/home/YOUR_USERNAME/projects/Bot Telegram/QR_Code/venv/bin"
ExecStart=/home/YOUR_USERNAME/projects/Bot Telegram/QR_Code/venv/bin/python web/server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Buat file service untuk Telegram Bot:

```bash
sudo nano /etc/systemd/system/shortlink-bot.service
```

Isi:

```ini
[Unit]
Description=ShortLink Telegram Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/projects/Bot Telegram/QR_Code
Environment="PATH=/home/YOUR_USERNAME/projects/Bot Telegram/QR_Code/venv/bin"
ExecStart=/home/YOUR_USERNAME/projects/Bot Telegram/QR_Code/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Install Cloudflare Tunnel sebagai service:

```bash
sudo cloudflared service install
```

Enable dan start semua services:

```bash
sudo systemctl daemon-reload
sudo systemctl enable shortlink-web
sudo systemctl enable shortlink-bot
sudo systemctl enable cloudflared

sudo systemctl start shortlink-web
sudo systemctl start shortlink-bot
sudo systemctl start cloudflared

# Check status
sudo systemctl status shortlink-web
sudo systemctl status shortlink-bot
sudo systemctl status cloudflared
```

---

## ✅ 6. Testing

### Test 1: Web Server

Buka browser dan akses:

```
https://s.jhopan.id
```

Harus muncul homepage dengan stats!

### Test 2: Telegram Bot

1. Buka Telegram
2. Cari bot Anda: `@pmkft_shortlink_bot`
3. Kirim `/start`
4. Bot harus reply dengan welcome message

### Test 3: Create Short Link

Di Telegram, kirim:

```
/short https://www.google.com
```

Bot akan reply dengan short link, contoh:

```
✅ Short Link berhasil dibuat!

🔗 URL Asli:
https://www.google.com

✨ Short Link:
https://s.jhopan.id/abc123
```

### Test 4: Akses Short Link

Buka `https://s.jhopan.id/abc123` di browser → harus redirect ke Google!

### Test 5: Custom Alias

```
/short https://forms.google.com DaftarPengurus2025
```

Hasilnya:

```
https://s.jhopan.id/DaftarPengurus2025
```

---

## 👥 7. Custom Domain untuk User Lain

### Scenario: User punya domain `jeje.id` dan mau pakai di bot Anda

### Step untuk User:

**1. Setup DNS di Cloudflare (user harus transfer domain ke Cloudflare):**

```
Type: CNAME
Name: @ (atau subdomain, misal: link)
Target: s.jhopan.id
Proxy: Proxied (orange cloud)
```

**2. Daftarkan domain di bot:**

Di Telegram, user kirim:

```
/adddomain jeje.id
```

Bot akan simpan domain tersebut ke database.

**3. Pakai domain custom:**

```
/short https://example.com CustomAlias jeje.id
```

Hasilnya:

```
https://jeje.id/CustomAlias
```

### Step untuk Admin (Anda):

Tambahkan DNS record di Cloudflare Anda:

```
Type: CNAME
Name: jeje.id (atau subdomain dari jeje.id)
Target: s.jhopan.id
Proxy: Proxied
```

---

## 📊 Command Reference

```
/start              - Welcome message
/help               - Bantuan lengkap
/about              - Info bot + stats global

/short <URL>                        - Random short code
/short <URL> <alias>                - Custom alias
/short <URL> <alias> <domain>       - Dengan domain custom

/qr <text atau URL>                 - Generate QR code

/both <URL>                         - Short link + QR code
/both <URL> <alias>                 - Dengan custom alias

/mystats            - Statistik Anda
/mylinks            - List link terbaru Anda
/adddomain <domain> - Register custom domain
```

---

## 🔧 Troubleshooting

### Bot tidak respond

```bash
# Check if bot running
sudo systemctl status shortlink-bot

# Check logs
sudo journalctl -u shortlink-bot -f
```

### Web server error

```bash
# Check web server
sudo systemctl status shortlink-web

# Check logs
sudo journalctl -u shortlink-web -f
```

### Short link tidak redirect

```bash
# Check tunnel
sudo systemctl status cloudflared
sudo journalctl -u cloudflared -f

# Test tunnel directly
cloudflared tunnel run shortlink
```

### Database error

```bash
# Check database file
ls -la shortlink.db

# Check permissions
sudo chown YOUR_USERNAME:YOUR_USERNAME shortlink.db
```

---

## 💰 Biaya Total

**100% GRATIS!** 🎉

- ✅ Domain: Sudah punya (`jhopan.id`)
- ✅ Laptop Linux: Sudah punya
- ✅ Cloudflare: Gratis
- ✅ Cloudflare Tunnel: Gratis
- ✅ SSL Certificate: Gratis
- ✅ Bot Telegram: Gratis
- ✅ Python + Libraries: Gratis

**Total: Rp 0,-**

---

## 📞 Support

Jika ada kendala, cek:

1. Log file services
2. Cloudflare dashboard untuk tunnel status
3. Telegram @BotFather untuk bot status

---

**Selamat! Bot shortlink custom domain Anda sudah jalan! 🚀**
