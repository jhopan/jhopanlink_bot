#!/bin/bash

#############################################
# ShortLink Bot - Start Script
# Menjalankan bot dan web server
#############################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get project root directory (parent of scripts/)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo -e "${BLUE}=========================================="
echo -e "🚀 Starting ShortLink Bot"
echo -e "==========================================${NC}"
echo ""

# Check virtual environment
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo -e "${YELLOW}Run: ./scripts/install.sh first${NC}"
    exit 1
fi

# Check .env file
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Configuration file (.env) not found!${NC}"
    echo -e "${YELLOW}Run: ./scripts/install.sh first${NC}"
    exit 1
fi

# Load .env and check critical variables
source .env

# Check BOT_TOKEN
if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" = "your_bot_token_here" ]; then
    echo -e "${RED}❌ BOT_TOKEN tidak ditemukan atau belum diset!${NC}"
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}📋 CARA MENDAPATKAN BOT TOKEN:${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "1️⃣  Buka Telegram dan cari: @BotFather"
    echo "2️⃣  Kirim command: /newbot"
    echo "3️⃣  Ikuti instruksi:"
    echo "    - Nama bot: JhopanLink Bot (atau nama lain)"
    echo "    - Username: jhopanlink_bot (harus unik)"
    echo "4️⃣  Copy token yang diberikan"
    echo "5️⃣  Edit file .env:"
    echo "    nano .env"
    echo "    Ganti: BOT_TOKEN=paste_token_disini"
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
fi

# Check if Cloudflare Tunnel is running
echo -e "${BLUE}🔍 Checking services...${NC}"
echo ""

if ! pgrep -f "cloudflared.*tunnel" > /dev/null; then
    echo -e "${YELLOW}⚠️  Cloudflare Tunnel tidak berjalan!${NC}"
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}🔧 SHORT LINK AKAN TETAP BERFUNGSI TAPI:${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "• Link hanya bisa diakses dari localhost"
    echo "• Domain custom (s.$DEFAULT_DOMAIN) tidak akan berfungsi"
    echo "• Bot akan fallback ke TinyURL untuk short link"
    echo ""
    echo -e "${GREEN}💡 Untuk mengaktifkan domain custom:${NC}"
    echo ""
    echo "   Buka terminal baru dan jalankan:"
    echo -e "   ${BLUE}cloudflared tunnel run shortlink${NC}"
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    read -p "Lanjutkan tanpa Cloudflare Tunnel? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        echo -e "${BLUE}Exiting... Start Cloudflare Tunnel dulu!${NC}"
        exit 0
    fi
else
    echo -e "${GREEN}✅ Cloudflare Tunnel: Running${NC}"
fi

echo ""

# Create logs directory
mkdir -p logs

# Activate virtual environment
source venv/bin/activate

# Check if already running
if pgrep -f "python.*run.py" > /dev/null; then
    echo -e "${YELLOW}⚠️  Bot is already running!${NC}"
    echo ""
    read -p "Stop and restart? (y/n): " RESTART
    if [ "$RESTART" = "y" ]; then
        echo -e "${YELLOW}Stopping existing processes...${NC}"
        pkill -f "python.*run.py" || true
        pkill -f "python.*web/server.py" || true
        sleep 2
    else
        echo -e "${BLUE}Exiting...${NC}"
        exit 0
    fi
fi

# Start the application
echo -e "${GREEN}🚀 Starting application...${NC}"
echo ""

# Run the bot (will start both bot and web server)
python run.py

