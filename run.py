#!/usr/bin/env python
"""
Script untuk menjalankan bot dan web server sekaligus
"""
import sys
import os
import threading
import time

# Tambahkan root directory ke Python path
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)

from app.bot import TelegramBot
from web.server import app
from config.config import Config

def run_web_server():
    """Jalankan Flask web server"""
    try:
        print("📡 Starting Web Server...")
        print(f"   Host: {Config.WEB_HOST}")
        print(f"   Port: {Config.WEB_PORT}")
        print(f"   URL: http://localhost:{Config.WEB_PORT}")
        print(f"   Public: https://{Config.DEFAULT_SUBDOMAIN}.{Config.DEFAULT_DOMAIN}")
        print("")
        
        app.run(
            host=Config.WEB_HOST,
            port=Config.WEB_PORT,
            debug=False,
            use_reloader=False
        )
    except Exception as e:
        print(f"❌ Web Server Error: {e}")
        sys.exit(1)

def run_telegram_bot():
    """Jalankan Telegram Bot"""
    try:
        time.sleep(2)  # Tunggu web server start dulu
        
        print("🤖 Starting Telegram Bot...")
        print("")
        
        bot = TelegramBot()
        bot.run()
        
    except Exception as e:
        print(f"❌ Bot Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        print("")
        print("=" * 60)
        print("🚀 JhopanLink Bot - Short Link & QR Code Generator")
        print("=" * 60)
        print("")
        
        # Start web server di thread terpisah
        web_thread = threading.Thread(target=run_web_server, daemon=True)
        web_thread.start()
        
        # Run telegram bot di main thread
        run_telegram_bot()
        
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("⏹️  System stopped by user")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Error: {e}")
        print("=" * 60)
        sys.exit(1)
