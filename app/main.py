"""
Main entry point untuk bot
"""
import sys
import os

# Tambahkan root directory ke Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.bot import TelegramBot

def main():
    """Main function"""
    try:
        # Create and run bot
        bot = TelegramBot()
        bot.run()
        
    except KeyboardInterrupt:
        print("\n⏹️  Bot dihentikan oleh user")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
