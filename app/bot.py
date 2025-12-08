"""
Bot Telegram untuk Short Link dan QR Code Generator
"""
import logging
import time
from datetime import datetime
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from telegram.request import HTTPXRequest
from telegram.error import NetworkError, TimedOut
from config.config import Config
from src.handlers import (
    start_command,
    help_command,
    about_command,
    mystats_command,
    mylinks_command,
    adddomain_command,
    short_command,
    qr_command,
    both_command,
    handle_text_message,
    error_handler
)
from src.handlers.callbacks import button_callback
from src.handlers.admin import admin_command, handle_admin_callback
from src.handlers.logging_handler import log_update

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    """Kelas utama untuk Bot Telegram"""
    
    def __init__(self):
        """Initialize bot"""
        # Validate config
        Config.validate()
        
        # Check if proxy is configured
        try:
            from config.proxy import PROXY_URL
            proxy_url = PROXY_URL
        except ImportError:
            proxy_url = None
        
        # Create request object with or without proxy
        if proxy_url:
            print(f"🔒 Using proxy: {proxy_url}")
            request = HTTPXRequest(
                proxy=proxy_url,
                connection_pool_size=8,
                connect_timeout=30.0,
                read_timeout=30.0
            )
        else:
            # Create request with longer timeout
            request = HTTPXRequest(
                connection_pool_size=8,
                connect_timeout=30.0,
                read_timeout=30.0
            )
        
        # Create application with request config
        self.application = Application.builder()\
            .token(Config.BOT_TOKEN)\
            .request(request)\
            .build()
        
        # Setup handlers
        self._setup_handlers()
        
        print(f"✅ {Config.BOT_NAME} v{Config.BOT_VERSION} initialized!")
    
    def _setup_handlers(self):
        """Setup semua handlers untuk bot"""
        
        logger.info("📝 Registering handlers...")
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", start_command))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(CommandHandler("about", about_command))
        self.application.add_handler(CommandHandler("short", short_command))
        self.application.add_handler(CommandHandler("qr", qr_command))
        self.application.add_handler(CommandHandler("both", both_command))
        self.application.add_handler(CommandHandler("mystats", mystats_command))
        self.application.add_handler(CommandHandler("mylinks", mylinks_command))
        self.application.add_handler(CommandHandler("adddomain", adddomain_command))
        logger.info("   ✓ Command handlers registered")
        
        # Admin command
        self.application.add_handler(CommandHandler("admin", admin_command))
        logger.info("   ✓ Admin handlers registered")
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(handle_admin_callback, pattern="^admin_"))
        self.application.add_handler(CallbackQueryHandler(button_callback))
        logger.info("   ✓ Callback query handlers registered")
        
        # Message handler untuk text
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message)
        )
        logger.info("   ✓ Message handlers registered")
        
        # Logging middleware (runs before other handlers)
        self.application.add_handler(
            MessageHandler(filters.ALL, log_update),
            group=-1  # Run first
        )
        self.application.add_handler(
            CallbackQueryHandler(log_update),
            group=-1  # Run first
        )
        logger.info("   ✓ Logging handlers registered")
        
        # Error handler
        self.application.add_error_handler(error_handler)
        logger.info("   ✓ Error handler registered")
        
        print("✅ Handlers registered!")
    
    def run(self):
        """Jalankan bot dengan auto-reconnect"""
        print(f"🚀 Starting {Config.BOT_NAME}...")
        print("📡 Bot is running. Press Ctrl+C to stop.")
        
        retry_count = 0
        max_retries = 999999  # Unlimited retries
        
        while True:
            try:
                logger.info("🔌 Connecting to Telegram servers...")
                
                # Start polling
                self.application.run_polling(
                    allowed_updates=["message", "callback_query"],
                    drop_pending_updates=True
                )
                
                # If we get here, polling stopped normally
                break
                
            except (NetworkError, TimedOut) as e:
                retry_count += 1
                wait_time = min(retry_count * 5, 60)  # Max 60 seconds
                
                logger.error(f"❌ Network error: {e}")
                logger.warning(f"⏳ Retry {retry_count}/{max_retries} - Waiting {wait_time}s before reconnect...")
                
                print(f"\n{'='*60}")
                print(f"⚠️  NETWORK ERROR DETECTED")
                print(f"{'='*60}")
                print(f"Error: {str(e)[:100]}")
                print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Retry: {retry_count} (will retry in {wait_time}s)")
                print(f"{'='*60}\n")
                
                time.sleep(wait_time)
                
            except KeyboardInterrupt:
                logger.info("👋 Received stop signal")
                print("\n⏹️  Stopping bot...")
                break
                
            except Exception as e:
                retry_count += 1
                logger.error(f"❌ Unexpected error: {e}", exc_info=True)
                
                print(f"\n{'='*60}")
                print(f"❌ UNEXPECTED ERROR")
                print(f"{'='*60}")
                print(f"Error: {str(e)}")
                print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Retry: {retry_count}")
                print(f"{'='*60}\n")
                
                if retry_count >= 10:
                    logger.critical("Too many errors, stopping bot")
                    break
                
                time.sleep(10)
    
    async def stop(self):
        """Stop bot"""
        print("⏹️  Stopping bot...")
        await self.application.stop()
        print("✅ Bot stopped!")
