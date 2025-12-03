# 🚀 Quick Command Reference

Setelah instalasi selesai, gunakan script-script berikut:

## 📦 Installation Scripts

### 1. `install.sh`
Script instalasi utama (yang sudah ada)
```bash
./install.sh
```
- Install dependencies
- Setup virtual environment
- Konfigurasi .env
- Inisialisasi database

---

## ⚡ Running Scripts

### 2. `start.sh`
**Start bot & web server** (cara paling simple!)
```bash
./start.sh
```
- Jalankan bot + web server sekaligus
- Foreground process (Ctrl+C untuk stop)
- Otomatis check venv dan .env

**Atau langsung:**
```bash
python run.py
```

---

## 🔧 System Integration

### 3. `install-service.sh`
**Install sebagai systemd service** (auto-start saat boot)
```bash
sudo ./install-service.sh
```

**Setelah install, control dengan:**
```bash
# Start
sudo systemctl start jhopanlink-bot
sudo systemctl start jhopanlink-tunnel

# Stop
sudo systemctl stop jhopanlink-bot
sudo systemctl stop jhopanlink-tunnel

# Status
sudo systemctl status jhopanlink-bot
sudo systemctl status jhopanlink-tunnel

# View logs
sudo journalctl -u jhopanlink-bot -f
sudo journalctl -u jhopanlink-tunnel -f

# Auto-start on boot
sudo systemctl enable jhopanlink-bot
sudo systemctl enable jhopanlink-tunnel
```

---

### 4. `create-aliases.sh`
**Buat command shortcuts** untuk akses cepat
```bash
./create-aliases.sh
source ~/.bashrc  # atau restart terminal
```

**Aliases yang tersedia:**
```bash
jlink-start          # Start bot
jlink-stop           # Stop bot
jlink-restart        # Restart bot
jlink-logs           # View logs (live)
jlink-status         # Check status
jlink-cd             # Go to bot directory
jlink-tunnel         # Start Cloudflare tunnel
jlink-tunnel-status  # Check tunnel status
```

**Contoh penggunaan:**
```bash
# Dari directory mana saja, langsung:
jlink-start
jlink-logs
jlink-stop
```

---

## 📋 Recommended Workflow

### Development (Manual Control)
```bash
# 1. Install
./install.sh

# 2. Setup aliases (optional)
./create-aliases.sh
source ~/.bashrc

# 3. Start
./start.sh  # atau: python run.py
```

### Production (Auto-Start)
```bash
# 1. Install
./install.sh

# 2. Install as service
sudo ./install-service.sh

# 3. Start services
sudo systemctl start jhopanlink-bot
sudo systemctl start jhopanlink-tunnel

# 4. Enable auto-start
sudo systemctl enable jhopanlink-bot
sudo systemctl enable jhopanlink-tunnel

# 5. Create aliases (optional)
./create-aliases.sh
```

---

## 🛠️ Troubleshooting

### Check if running
```bash
# Manual check
ps aux | grep "python.*run.py"
ps aux | grep cloudflared

# Or with aliases
jlink-status
jlink-tunnel-status
```

### View logs
```bash
# Manual
tail -f logs/bot.log

# With aliases
jlink-logs
```

### Restart
```bash
# Manual (systemd)
sudo systemctl restart jhopanlink-bot

# Manual (script)
pkill -f "python.*run.py"
./start.sh

# With aliases
jlink-restart
```

---

## 📁 File Permissions

Pastikan script executable:
```bash
chmod +x install.sh
chmod +x start.sh
chmod +x install-service.sh
chmod +x create-aliases.sh
chmod +x stop_all.sh
chmod +x check_status.sh
```

---

## 🎯 Summary

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `install.sh` | First-time setup | Sekali di awal |
| `start.sh` | Run bot manually | Testing, development |
| `install-service.sh` | Install as service | Production, auto-start |
| `create-aliases.sh` | Create shortcuts | Quality of life |

**Paling simple untuk production:**
1. `./install.sh`
2. `sudo ./install-service.sh`
3. `sudo systemctl start jhopanlink-bot jhopanlink-tunnel`
4. Done! ✅
