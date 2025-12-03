#!/bin/bash

#############################################
# ShortLink Bot - Create Aliases
# Membuat alias untuk perintah cepat
#############################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================="
echo -e "🔧 Creating Command Aliases"
echo -e "==========================================${NC}"
echo ""

# Get project root directory (parent of scripts/)
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
INSTALL_DIR="$(dirname "$SCRIPT_DIR")"

# Detect shell
SHELL_RC=""
if [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
else
    echo -e "${RED}❌ Shell configuration file not found!${NC}"
    exit 1
fi

echo -e "${BLUE}Shell config: ${SHELL_RC}${NC}"
echo ""

# Check if aliases already exist
if grep -q "# JhopanLink Bot Aliases" "$SHELL_RC"; then
    echo -e "${YELLOW}⚠️  Aliases already exist!${NC}"
    echo ""
    read -p "Replace existing aliases? (y/n): " REPLACE
    if [ "$REPLACE" != "y" ]; then
        echo -e "${BLUE}Exiting...${NC}"
        exit 0
    fi
    # Remove old aliases
    sed -i '/# JhopanLink Bot Aliases/,/# End JhopanLink Bot Aliases/d' "$SHELL_RC"
fi

# Add aliases
echo -e "${GREEN}Adding aliases to ${SHELL_RC}...${NC}"
cat >> "$SHELL_RC" << EOF

# JhopanLink Bot Aliases
alias jlink-start='cd $INSTALL_DIR && ./scripts/start.sh'
alias jlink-stop='cd $INSTALL_DIR && pkill -f "python.*run.py" || echo "Not running"'
alias jlink-restart='jlink-stop && sleep 2 && jlink-start'
alias jlink-logs='tail -f $INSTALL_DIR/logs/bot.log'
alias jlink-status='systemctl status jhopanlink-bot 2>/dev/null || (pgrep -f "python.*run.py" > /dev/null && echo "✅ Running" || echo "❌ Not running")'
alias jlink-cd='cd $INSTALL_DIR'
alias jlink-tunnel='cloudflared tunnel run shortlink'
alias jlink-tunnel-status='systemctl status jhopanlink-tunnel 2>/dev/null || (pgrep -f "cloudflared.*tunnel" > /dev/null && echo "✅ Running" || echo "❌ Not running")'
# End JhopanLink Bot Aliases
EOF

echo ""
echo -e "${GREEN}=========================================="
echo -e "✅ Aliases Created!"
echo -e "==========================================${NC}"
echo ""
echo -e "${BLUE}Available commands:${NC}"
echo "  jlink-start          - Start the bot"
echo "  jlink-stop           - Stop the bot"
echo "  jlink-restart        - Restart the bot"
echo "  jlink-logs           - View bot logs"
echo "  jlink-status         - Check bot status"
echo "  jlink-cd             - Go to bot directory"
echo "  jlink-tunnel         - Start Cloudflare tunnel"
echo "  jlink-tunnel-status  - Check tunnel status"
echo ""
echo -e "${YELLOW}⚠️  To use aliases now, run:${NC}"
echo -e "${GREEN}source ${SHELL_RC}${NC}"
echo ""
echo -e "${BLUE}Or restart your terminal.${NC}"
echo ""

