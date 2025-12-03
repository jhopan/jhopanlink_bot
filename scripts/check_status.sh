#!/bin/bash

# Script untuk mengecek status semua komponen

echo "=========================================="
echo "📊 ShortLink Bot System Status"
echo "=========================================="

# Function to check process
check_process() {
    if pgrep -f "$1" > /dev/null; then
        echo "✅ $2 is RUNNING"
        return 0
    else
        echo "❌ $2 is STOPPED"
        return 1
    fi
}

# Check Web Server
check_process "web/server.py" "Web Server (Flask)"

# Check Telegram Bot
check_process "run.py" "Telegram Bot"

# Check Cloudflare Tunnel
check_process "cloudflared tunnel" "Cloudflare Tunnel"

echo ""
echo "=========================================="
echo "🌐 Testing Endpoints"
echo "=========================================="

# Test local web server
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ Web Server responding on localhost:5000"
else
    echo "❌ Web Server not responding"
fi

# Test public endpoint (if configured)
source .env 2>/dev/null
if [ ! -z "$DEFAULT_DOMAIN" ] && [ ! -z "$DEFAULT_SUBDOMAIN" ]; then
    DOMAIN="${DEFAULT_SUBDOMAIN}.${DEFAULT_DOMAIN}"
    if curl -s "https://${DOMAIN}/api/health" > /dev/null; then
        echo "✅ Public endpoint responding: https://${DOMAIN}"
    else
        echo "⚠️  Public endpoint not responding: https://${DOMAIN}"
    fi
fi

echo ""
echo "=========================================="
echo "📁 Database Status"
echo "=========================================="

if [ -f "shortlink.db" ]; then
    DB_SIZE=$(du -h shortlink.db | cut -f1)
    echo "✅ Database exists: shortlink.db ($DB_SIZE)"
    
    # Count links in database
    if command -v sqlite3 &> /dev/null; then
        LINK_COUNT=$(sqlite3 shortlink.db "SELECT COUNT(*) FROM short_links;" 2>/dev/null)
        echo "📊 Total links in database: $LINK_COUNT"
    fi
else
    echo "⚠️  Database not found: shortlink.db"
fi

echo ""
echo "=========================================="
