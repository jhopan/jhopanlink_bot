#!/bin/bash

# Script untuk menjalankan semua komponen ShortLink Bot
# Usage: ./start_all.sh

echo "=========================================="
echo "🚀 Starting ShortLink Bot System"
echo "=========================================="

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and configure it"
    exit 1
fi

# Function to check if process is running
check_process() {
    if pgrep -f "$1" > /dev/null; then
        echo "✅ $2 is running"
        return 0
    else
        echo "❌ $2 is not running"
        return 1
    fi
}

# Start Web Server in background
echo ""
echo "📡 Starting Web Server..."
python web/server.py > logs/webserver.log 2>&1 &
WEB_PID=$!
echo "Web Server PID: $WEB_PID"
sleep 2

# Start Telegram Bot in background
echo ""
echo "🤖 Starting Telegram Bot..."
python run.py > logs/bot.log 2>&1 &
BOT_PID=$!
echo "Bot PID: $BOT_PID"
sleep 2

# Check Cloudflare Tunnel
echo ""
echo "🔐 Checking Cloudflare Tunnel..."
if check_process "cloudflared tunnel run" "Cloudflare Tunnel"; then
    echo "Cloudflare Tunnel already running"
else
    echo "⚠️  Cloudflare Tunnel not running!"
    echo "Please start manually: cloudflared tunnel run shortlink"
    echo "Or install as service: sudo cloudflared service install"
fi

# Summary
echo ""
echo "=========================================="
echo "📊 System Status"
echo "=========================================="
check_process "web/server.py" "Web Server"
check_process "run.py" "Telegram Bot"
check_process "cloudflared tunnel" "Cloudflare Tunnel"

echo ""
echo "=========================================="
echo "📝 Logs Location"
echo "=========================================="
echo "Web Server: logs/webserver.log"
echo "Telegram Bot: logs/bot.log"

echo ""
echo "=========================================="
echo "💡 Useful Commands"
echo "=========================================="
echo "Stop all: ./stop_all.sh"
echo "View web logs: tail -f logs/webserver.log"
echo "View bot logs: tail -f logs/bot.log"
echo "Check status: ./check_status.sh"

echo ""
echo "✅ All components started!"
echo "=========================================="
