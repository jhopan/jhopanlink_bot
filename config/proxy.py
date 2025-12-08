"""
Proxy configuration untuk Telegram Bot
Gunakan jika Telegram API diblock di network Anda
"""

# Proxy settings (uncomment dan edit jika perlu)
PROXY_URL = None  # Contoh: "http://proxy.example.com:8080"
# PROXY_URL = "socks5://127.0.0.1:1080"  # Untuk SOCKS5 proxy

# Atau gunakan environment variable
import os
if not PROXY_URL:
    PROXY_URL = os.getenv('TELEGRAM_PROXY')
