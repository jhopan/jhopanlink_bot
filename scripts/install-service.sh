#!/bin/bash

#############################################
# ShortLink Bot - Install as System Service
# Install bot sebagai systemd service
#############################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Please run as root (use sudo)${NC}"
    exit 1
fi

echo -e "${BLUE}=========================================="
echo -e "📦 Installing ShortLink Bot as Service"
echo -e "==========================================${NC}"
echo ""

# Get project root directory (parent of scripts/)
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
INSTALL_DIR="$(dirname "$SCRIPT_DIR")"
echo -e "${BLUE}Installation directory: ${INSTALL_DIR}${NC}"

# Get current user
ACTUAL_USER="${SUDO_USER:-$USER}"
echo -e "${BLUE}Running as user: ${ACTUAL_USER}${NC}"
echo ""

# Create systemd service file for bot
echo -e "${GREEN}[1/4] Creating bot service...${NC}"
cat > /etc/systemd/system/jhopanlink-bot.service << EOF
[Unit]
Description=JhopanLink Telegram Bot
After=network.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/run.py
Restart=always
RestartSec=10
StandardOutput=append:$INSTALL_DIR/logs/bot.log
StandardError=append:$INSTALL_DIR/logs/bot.log

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service file for tunnel
echo -e "${GREEN}[2/4] Creating tunnel service...${NC}"
cat > /etc/systemd/system/jhopanlink-tunnel.service << EOF
[Unit]
Description=Cloudflare Tunnel for JhopanLink
After=network.target

[Service]
Type=simple
User=$ACTUAL_USER
ExecStart=/usr/local/bin/cloudflared tunnel run shortlink
Restart=always
RestartSec=10
StandardOutput=append:$INSTALL_DIR/logs/tunnel.log
StandardError=append:$INSTALL_DIR/logs/tunnel.log

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
echo -e "${GREEN}[3/4] Reloading systemd...${NC}"
systemctl daemon-reload

# Enable services
echo -e "${GREEN}[4/4] Enabling services...${NC}"
systemctl enable jhopanlink-bot.service
systemctl enable jhopanlink-tunnel.service

echo ""
echo -e "${GREEN}=========================================="
echo -e "✅ Installation Complete!"
echo -e "==========================================${NC}"
echo ""
echo -e "${BLUE}Services installed:${NC}"
echo "  • jhopanlink-bot.service"
echo "  • jhopanlink-tunnel.service"
echo ""
echo -e "${BLUE}Control commands:${NC}"
echo "  Start:   sudo systemctl start jhopanlink-bot"
echo "  Stop:    sudo systemctl stop jhopanlink-bot"
echo "  Restart: sudo systemctl restart jhopanlink-bot"
echo "  Status:  sudo systemctl status jhopanlink-bot"
echo "  Logs:    sudo journalctl -u jhopanlink-bot -f"
echo ""
echo "  Start tunnel:   sudo systemctl start jhopanlink-tunnel"
echo "  Stop tunnel:    sudo systemctl stop jhopanlink-tunnel"
echo "  Status tunnel:  sudo systemctl status jhopanlink-tunnel"
echo ""
echo -e "${YELLOW}Note: Services are enabled but not started.${NC}"
echo -e "${YELLOW}Start them with: sudo systemctl start jhopanlink-bot${NC}"
echo ""

