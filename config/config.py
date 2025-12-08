"""
Konfigurasi untuk Bot Telegram
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class"""
    
    # Bot Configuration
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # TinyURL Fallback (when web server is down)
    TINYURL_API_KEY = os.getenv('TINYURL_API_KEY', '')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///shortlink.db')
    
    # Web Server Configuration  
    WEB_HOST = os.getenv('WEB_HOST', '0.0.0.0')
    WEB_PORT = int(os.getenv('WEB_PORT', '5000'))
    
    # Default Domain untuk Short Link
    DEFAULT_DOMAIN = os.getenv('DEFAULT_DOMAIN', 'jhopan.id')
    DEFAULT_SUBDOMAIN = os.getenv('DEFAULT_SUBDOMAIN', 's')  # s.jhopan.id
    
    # Bot Info
    BOT_NAME = "ShortLink & QR Code Bot"
    BOT_VERSION = "2.0.0"
    
    # QR Code Settings
    QR_BOX_SIZE = 10
    QR_BORDER = 4
    QR_ERROR_CORRECTION = 'H'  # L, M, Q, H
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN tidak ditemukan! Silakan set di file .env")
        return True
