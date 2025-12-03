#!/usr/bin/env python
"""
Script untuk menjalankan bot
"""
import sys
import os

# Tambahkan root directory ke Python path
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)

from app.bot import TelegramBot

if __name__ == "__main__":
    try:
        print("=" * 50)
        print("🤖 ShortLink & QR Code Telegram Bot")
        print("=" * 50)
        
        # Create and run bot
        bot = TelegramBot()
        bot.run()
        
    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("⏹️  Bot dihentikan oleh user")
        print("=" * 50)
        
    except Exception as e:
        print("\n" + "=" * 50)
        print(f"❌ Error: {e}")
        print("=" * 50)
        sys.exit(1)
