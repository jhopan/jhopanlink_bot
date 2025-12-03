#!/bin/bash

# Script untuk menghentikan semua komponen ShortLink Bot

echo "=========================================="
echo "⏹️  Stopping ShortLink Bot System"
echo "=========================================="

# Stop Web Server
echo "Stopping Web Server..."
pkill -f "python web/server.py"
if [ $? -eq 0 ]; then
    echo "✅ Web Server stopped"
else
    echo "⚠️  Web Server not running"
fi

# Stop Telegram Bot
echo "Stopping Telegram Bot..."
pkill -f "python run.py"
if [ $? -eq 0 ]; then
    echo "✅ Telegram Bot stopped"
else
    echo "⚠️  Telegram Bot not running"
fi

# Note about Cloudflare Tunnel
echo ""
echo "📝 Note: Cloudflare Tunnel tidak dihentikan (jika running as service)"
echo "Untuk stop tunnel: sudo systemctl stop cloudflared"

echo ""
echo "✅ All components stopped!"
echo "=========================================="
