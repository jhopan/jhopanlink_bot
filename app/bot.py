"""
Bot Telegram untuk Short Link dan QR Code Generator
"""
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
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

class TelegramBot:
    """Kelas utama untuk Bot Telegram"""
    
    def __init__(self):
        """Initialize bot"""
        # Validate config
        Config.validate()
        
        # Create application
        self.application = Application.builder().token(Config.BOT_TOKEN).build()
        
        # Setup handlers
        self._setup_handlers()
        
        print(f"✅ {Config.BOT_NAME} v{Config.BOT_VERSION} initialized!")
    
    def _setup_handlers(self):
        """Setup semua handlers untuk bot"""
        
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
        
        # Admin command
        self.application.add_handler(CommandHandler("admin", admin_command))
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(handle_admin_callback, pattern="^admin_"))
        self.application.add_handler(CallbackQueryHandler(button_callback))
        
        # Message handler untuk text
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message)
        )
        
        # Error handler
        self.application.add_error_handler(error_handler)
        
        print("✅ Handlers registered!")
    
    def run(self):
        """Jalankan bot"""
        print(f"🚀 Starting {Config.BOT_NAME}...")
        print("📡 Bot is running. Press Ctrl+C to stop.")
        
        # Start polling
        self.application.run_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        )
    
    async def stop(self):
        """Stop bot"""
        print("⏹️  Stopping bot...")
        await self.application.stop()
        print("✅ Bot stopped!")
