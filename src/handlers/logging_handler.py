"""
Logging handler untuk track semua update dan interaksi
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def log_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log semua update yang diterima"""
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        if update.message:
            text = update.message.text or "[media/file]"
            logger.info(f"📨 Message from @{user.username or user.id} in {chat.type}: {text[:50]}")
        
        elif update.callback_query:
            data = update.callback_query.data
            logger.info(f"🔘 Callback from @{user.username or user.id}: {data}")
        
        elif update.edited_message:
            logger.info(f"✏️  Edited message from @{user.username or user.id}")
    
    except Exception as e:
        logger.error(f"❌ Error logging update: {e}")
