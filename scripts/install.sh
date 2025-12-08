#!/bin/bash

#######################################################
# LinkHub Bot - Automated Installation Script
# For Linux Systems
#######################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Header
clear
echo -e "${BLUE}"
echo "=============================================="
echo "     LinkHub Bot Installation Script"
echo "     Automated Setup for Production"
echo "=============================================="
echo -e "${NC}"
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_error "This script is designed for Linux systems only!"
    print_info "For Windows, please follow README.md manual setup"
    exit 1
fi

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    print_warning "Please do not run this script as root!"
    exit 1
fi

print_info "Starting installation process..."
echo ""

#######################################################
# Step 1: Check Dependencies
#######################################################

echo -e "${BLUE}[1/8] Checking system dependencies...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed!"
    print_info "Installing Python 3..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
else
    PYTHON_VERSION=$(python3 --version)
    print_success "Python found: $PYTHON_VERSION"
fi

# Check pip
if ! command -v pip3 &> /dev/null; then
    print_info "Installing pip..."
    sudo apt install -y python3-pip
fi

# Check git
if ! command -v git &> /dev/null; then
    print_info "Installing git..."
    sudo apt install -y git
fi

# Check sqlite3
if ! command -v sqlite3 &> /dev/null; then
    print_info "Installing sqlite3..."
    sudo apt install -y sqlite3
fi

print_success "All system dependencies installed!"
echo ""

#######################################################
# Step 2: Get Project Root Directory
#######################################################

# Get script directory and move to parent (project root)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
INSTALL_DIR="$(dirname "$SCRIPT_DIR")"
cd "$INSTALL_DIR"

print_info "Installation directory: $INSTALL_DIR"
echo ""

#######################################################
# Step 3: Create Virtual Environment
#######################################################

echo -e "${BLUE}[2/8] Setting up Python virtual environment...${NC}"

if [ -d "venv" ]; then
    print_warning "Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    print_success "Virtual environment created!"
fi

# Activate virtual environment
source venv/bin/activate
print_success "Virtual environment activated!"
echo ""

#######################################################
# Step 4: Install Python Dependencies
#######################################################

echo -e "${BLUE}[3/8] Installing Python packages...${NC}"

# Upgrade pip first
pip install --upgrade pip setuptools wheel > /dev/null 2>&1

# Install dependencies with better error handling
if pip install -r requirements.txt; then
    print_success "Python packages installed!"
else
    print_error "Failed to install some packages!"
    print_info "Trying with alternative versions..."
    
    # Create alternative requirements
    cat > requirements-alt.txt << 'ALTEOF'
python-telegram-bot>=20.0
python-dotenv>=1.0.0
qrcode[pil]>=7.0
requests>=2.31.0
Pillow>=10.0.0
aiohttp>=3.9.0
Flask>=3.0.0
Flask-CORS>=4.0.0
ALTEOF
    
    if pip install -r requirements-alt.txt; then
        print_success "Python packages installed with alternative versions!"
        rm requirements-alt.txt
    else
        print_error "Installation failed! Please install packages manually"
        deactivate
        exit 1
    fi
fi

echo ""

#######################################################
# Step 5: Configuration Input
#######################################################

echo -e "${BLUE}[4/8] Configuration Setup${NC}"
echo ""

# Check if .env already exists
if [ -f ".env" ]; then
    print_warning ".env file already exists!"
    read -p "Do you want to reconfigure? (y/n): " RECONFIG
    if [[ ! $RECONFIG =~ ^[Yy]$ ]]; then
        print_info "Skipping configuration..."
        CONFIG_DONE=true
    fi
fi

if [ -z "$CONFIG_DONE" ]; then
    echo -e "${YELLOW}Please provide the following information:${NC}"
    echo ""

    # Bot Token
    while true; do
        read -p "🤖 Enter your Telegram Bot Token (from @BotFather): " BOT_TOKEN
        if [ -z "$BOT_TOKEN" ]; then
            print_error "Bot token cannot be empty!"
        else
            break
        fi
    done

    # Default Domain Configuration
    echo ""
    echo -e "${BLUE}Domain Configuration (Optional):${NC}"
    echo "  ℹ️  Anda bisa menggunakan domain sendiri atau domain gratis"
    echo "  ℹ️  Domain gratis: DuckDNS (https://www.duckdns.org)"
    echo "  ℹ️  Atau kosongkan jika hanya ingin pakai TinyURL"
    echo ""
    read -p "🌐 Enter your domain (e.g., jhopan.duckdns.org) [kosongkan = TinyURL only]: " DEFAULT_DOMAIN
    
    if [ -n "$DEFAULT_DOMAIN" ]; then
        # Default Subdomain
        read -p "🔗 Enter your subdomain prefix (e.g., s for s.jhopan.id) [default: s]: " DEFAULT_SUBDOMAIN
        DEFAULT_SUBDOMAIN=${DEFAULT_SUBDOMAIN:-s}
    else
        DEFAULT_SUBDOMAIN=""
        echo "  ⚠️  Tidak ada domain, bot akan menggunakan TinyURL"
    fi

    # Web Server Port
    read -p "🔌 Enter web server port [default: 5000]: " WEB_PORT
    WEB_PORT=${WEB_PORT:-5000}

    # TinyURL API Key (optional fallback)
    echo ""
    echo "🔄 TinyURL Fallback (Optional):"
    echo "   - TinyURL akan digunakan sebagai backup jika web server Anda mati"
    echo "   - Gratis, dapatkan API key di: https://tinyurl.com/app/dev"
    echo "   - Tekan Enter untuk skip (tidak wajib)"
    read -p "🔑 Enter TinyURL API Key (optional): " TINYURL_KEY

    # Create .env file
    cat > .env << EOF
# Telegram Bot Configuration
BOT_TOKEN=$BOT_TOKEN

# Web Server Configuration
WEB_HOST=0.0.0.0
WEB_PORT=$WEB_PORT

# Default Domain for Short Link
DEFAULT_DOMAIN=$DEFAULT_DOMAIN
DEFAULT_SUBDOMAIN=$DEFAULT_SUBDOMAIN

# TinyURL API Key (Optional - Fallback when web server down)
TINYURL_API_KEY=$TINYURL_KEY

# Database
DATABASE_URL=sqlite:///shortlink.db
EOF

    print_success ".env file created!"
    echo ""
fi

#######################################################
# Step 6: Initialize Database
#######################################################

echo -e "${BLUE}[5/8] Initializing database...${NC}"

# Test database initialization
python3 << EOF
from database.db_manager import DatabaseManager
db = DatabaseManager('shortlink.db')
print("Database initialized successfully!")
EOF

print_success "Database ready!"
echo ""

#######################################################
# Step 7: Test Configuration
#######################################################

echo -e "${BLUE}[6/8] Testing configuration...${NC}"

# Test bot configuration
python3 << EOF
from config.config import Config
try:
    Config.validate()
    print("✅ Configuration valid!")
except Exception as e:
    print(f"❌ Configuration error: {e}")
    exit(1)
EOF

print_success "Configuration test passed!"
echo ""

#######################################################
# Step 8: Cloudflare Tunnel Setup (Optional)
#######################################################

echo -e "${BLUE}[7/8] Cloudflare Tunnel Setup${NC}"
echo ""

read -p "Do you want to setup Cloudflare Tunnel now? (y/n): " SETUP_TUNNEL

if [[ $SETUP_TUNNEL =~ ^[Yy]$ ]]; then
    # Check if cloudflared is installed
    if ! command -v cloudflared &> /dev/null; then
        print_info "Installing cloudflared..."
        
        # Detect architecture
        ARCH=$(uname -m)
        if [ "$ARCH" == "x86_64" ]; then
            wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
            sudo dpkg -i cloudflared-linux-amd64.deb
            rm cloudflared-linux-amd64.deb
        elif [ "$ARCH" == "aarch64" ]; then
            wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
            sudo dpkg -i cloudflared-linux-arm64.deb
            rm cloudflared-linux-arm64.deb
        else
            print_error "Unsupported architecture: $ARCH"
            print_info "Please install cloudflared manually"
            TUNNEL_SKIP=true
        fi
        
        if [ -z "$TUNNEL_SKIP" ]; then
            print_success "cloudflared installed!"
        fi
    else
        print_success "cloudflared already installed!"
    fi
    
    if [ -z "$TUNNEL_SKIP" ]; then
        echo ""
        print_info "🚀 Next: Setup Cloudflare Tunnel"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📋 LANGKAH SETUP CLOUDFLARE TUNNEL:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "1️⃣  Login ke Cloudflare:"
        echo "    cloudflared tunnel login"
        echo "    (Browser akan terbuka, pilih domain: $DEFAULT_DOMAIN)"
        echo ""
        echo "2️⃣  Buat tunnel baru:"
        echo "    cloudflared tunnel create shortlink"
        echo "    (Simpan TUNNEL_ID yang muncul!)"
        echo ""
        echo "3️⃣  Buat config file:"
        echo "    mkdir -p ~/.cloudflared"
        echo "    nano ~/.cloudflared/config.yml"
        echo ""
        echo "    Isi config:"
        echo "    ----------------------------------------"
        echo "    tunnel: YOUR_TUNNEL_ID"
        echo "    credentials-file: /home/$(whoami)/.cloudflared/YOUR_TUNNEL_ID.json"
        echo ""
        echo "    ingress:"
        echo "      - hostname: $DEFAULT_SUBDOMAIN.$DEFAULT_DOMAIN"
        echo "        service: http://localhost:$WEB_PORT"
        echo "      - service: http_status:404"
        echo "    ----------------------------------------"
        echo ""
        echo "4️⃣  Route DNS ke tunnel:"
        echo "    cloudflared tunnel route dns shortlink $DEFAULT_SUBDOMAIN.$DEFAULT_DOMAIN"
        echo ""
        echo "5️⃣  Test tunnel:"
        echo "    cloudflared tunnel run shortlink"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "💡 Setelah tunnel jalan, buka tab baru untuk start bot!"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
    fi
else
    print_info "Skipping Cloudflare Tunnel setup"
    print_info "You can set it up later using SETUP_GUIDE.md"
fi

echo ""

#######################################################
# Step 9: Create Systemd Services (Optional)
#######################################################

echo -e "${BLUE}[8/8] Systemd Services Setup${NC}"
echo ""

read -p "Do you want to setup systemd services for auto-start? (y/n): " SETUP_SYSTEMD

if [[ $SETUP_SYSTEMD =~ ^[Yy]$ ]]; then
    USERNAME=$(whoami)
    
    # Web Server Service
    print_info "Creating web server service..."
    sudo tee /etc/systemd/system/linkhub-web.service > /dev/null << EOF
[Unit]
Description=LinkHub Web Server
After=network.target

[Service]
Type=simple
User=$USERNAME
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
ExecStart=$INSTALL_DIR/venv/bin/python web/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Telegram Bot Service
    print_info "Creating telegram bot service..."
    sudo tee /etc/systemd/system/linkhub-bot.service > /dev/null << EOF
[Unit]
Description=LinkHub Telegram Bot
After=network.target

[Service]
Type=simple
User=$USERNAME
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
ExecStart=$INSTALL_DIR/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd
    sudo systemctl daemon-reload
    
    # Enable services
    sudo systemctl enable linkhub-web.service
    sudo systemctl enable linkhub-bot.service
    
    print_success "Systemd services created and enabled!"
    
    echo ""
    print_info "To start services now, run:"
    echo "  sudo systemctl start linkhub-web"
    echo "  sudo systemctl start linkhub-bot"
else
    print_info "Skipping systemd setup"
    print_info "You can start manually using ./scripts/start.sh"
fi

echo ""

#######################################################
# Installation Complete
#######################################################

echo -e "${GREEN}"
echo "=============================================="
echo "     ✅ Installation Complete!"
echo "=============================================="
echo -e "${NC}"
echo ""

# Read configuration from .env file for summary
source .env 2>/dev/null

print_info "Configuration Summary:"
echo "  📁 Install Directory: $INSTALL_DIR"
echo "  🌐 Domain: $DEFAULT_SUBDOMAIN.$DEFAULT_DOMAIN"
echo "  🔌 Web Port: $WEB_PORT"
echo "  💾 Database: $INSTALL_DIR/shortlink.db"
echo ""

print_info "Next Steps:"
echo ""
echo "1️⃣  Start the services:"
if [[ $SETUP_SYSTEMD =~ ^[Yy]$ ]]; then
    echo "   sudo systemctl start linkhub-web"
    echo "   sudo systemctl start linkhub-bot"
    echo ""
    echo "   Check status:"
    echo "   sudo systemctl status linkhub-web"
    echo "   sudo systemctl status linkhub-bot"
else
    echo "   ./scripts/start.sh"
fi
echo ""

echo "2️⃣  Setup Cloudflare Tunnel (if not done):"
echo "   See SETUP_GUIDE.md for detailed instructions"
echo ""

echo "3️⃣  Test your bot:"
echo "   Open Telegram and search for your bot"
echo "   Send /start to begin"
echo ""

echo "4️⃣  Access web interface:"
echo "   http://localhost:$WEB_PORT"
echo "   https://$DEFAULT_SUBDOMAIN.$DEFAULT_DOMAIN (after tunnel setup)"
echo ""

print_info "Useful Commands:"
echo "  View logs: tail -f logs/bot.log logs/webserver.log"
echo "  Check status: ./scripts/check_status.sh"
echo "  Stop services: ./scripts/stop_all.sh"
echo ""

print_info "Documentation:"
echo "  📖 README.md - Overview"
echo "  📖 QUICKSTART.md - Quick reference"
echo "  📖 SETUP_GUIDE.md - Complete guide"
echo ""

echo -e "${GREEN}🎉 Happy Link Shortening!${NC}"
echo ""

# Deactivate virtual environment
deactivate 2>/dev/null || true
