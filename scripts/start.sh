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

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}=========================================="
echo -e "🚀 Starting ShortLink Bot"
echo -e "==========================================${NC}"
echo ""

# Check virtual environment
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo -e "${YELLOW}Run: ./install.sh first${NC}"
    exit 1
fi

# Check .env file
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Configuration file (.env) not found!${NC}"
    echo -e "${YELLOW}Run: ./install.sh first${NC}"
    exit 1
fi

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

