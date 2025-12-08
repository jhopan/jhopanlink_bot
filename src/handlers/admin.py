"""
Admin handlers untuk bot
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_manager import DatabaseManager
from config.config import Config

# Initialize database
db = DatabaseManager()

# Admin user ID (ganti dengan ID Telegram Anda)
ADMIN_ID = "YOUR_TELEGRAM_USER_ID"  # Ganti dengan user ID @jhopan_05

def is_admin(user_id: str) -> bool:
    """Check if user is admin"""
    return str(user_id) == ADMIN_ID

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /admin - Admin menu"""
    user_id = str(update.effective_user.id)
    
    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ *Access Denied*\n\n"
            "Anda tidak memiliki akses admin.",
            parse_mode='Markdown'
        )
        return
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Bot Stats", callback_data="admin_stats"),
            InlineKeyboardButton("👥 User List", callback_data="admin_users")
        ],
        [
            InlineKeyboardButton("🌐 Domain Management", callback_data="admin_domains"),
        ],
        [
            InlineKeyboardButton("🔗 All Links", callback_data="admin_links"),
        ],
        [
            InlineKeyboardButton("❌ Close", callback_data="admin_close")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
🔐 *Admin Panel*

Selamat datang di Admin Panel!
Pilih menu di bawah untuk manage bot.

━━━━━━━━━━━━━━━━━
📊 Bot Statistics
👥 User Management
🌐 Domain Management
🔗 Links Overview
    """
    
    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_admin_stats(query, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics"""
    # Get stats from database
    total_links = db.get_total_links()
    total_clicks = db.get_total_clicks()
    total_users = db.get_total_users()
    total_domains = db.get_total_domains()
    
    keyboard = [
        [InlineKeyboardButton("🔄 Refresh", callback_data="admin_stats")],
        [InlineKeyboardButton("🔙 Back to Admin Menu", callback_data="admin_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""
📊 *Bot Statistics*

━━━━━━━━━━━━━━━━━
🔗 *Total Links:* `{total_links}`
👆 *Total Clicks:* `{total_clicks}`
👥 *Total Users:* `{total_users}`
🌐 *Custom Domains:* `{total_domains}`

━━━━━━━━━━━━━━━━━
*Average:* {total_clicks / total_links if total_links > 0 else 0:.1f} clicks per link
    """
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_admin_domains(query, context: ContextTypes.DEFAULT_TYPE):
    """Show domain management"""
    domains = db.get_all_domains()
    
    keyboard = [
        [InlineKeyboardButton("➕ Add Subdomain", callback_data="admin_add_subdomain")],
        [InlineKeyboardButton("🔙 Back to Admin Menu", callback_data="admin_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
🌐 *Domain Management*

━━━━━━━━━━━━━━━━━
*Custom Domains:*

"""
    
    if domains:
        for idx, domain in enumerate(domains, 1):
            message += f"{idx}. `{domain['domain']}`\n"
            message += f"   Owner: {domain['username']}\n"
            message += f"   Added: {domain['added_at'][:10]}\n\n"
    else:
        message += "_No custom domains yet_\n"
    
    message += """
━━━━━━━━━━━━━━━━━
💡 *Subdomain Gratis via Cloudflare:*
Bisa unlimited subdomain!
Contoh: user1.jhopan.my.id, user2.jhopan.my.id
    """
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_admin_links(query, context: ContextTypes.DEFAULT_TYPE):
    """Show recent links"""
    links = db.get_recent_links(limit=10)
    
    keyboard = [
        [InlineKeyboardButton("🔄 Refresh", callback_data="admin_links")],
        [InlineKeyboardButton("🔙 Back to Admin Menu", callback_data="admin_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
🔗 *Recent Links*

━━━━━━━━━━━━━━━━━
"""
    
    if links:
        for idx, link in enumerate(links, 1):
            short_code = link['custom_alias'] or link['short_code']
            message += f"{idx}. `{link['domain']}/{short_code}`\n"
            message += f"   👤 User: {link['user_id']}\n"
            message += f"   👆 Clicks: {link['clicks']}\n\n"
    else:
        message += "_No links yet_\n"
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_admin_users(query, context: ContextTypes.DEFAULT_TYPE):
    """Show active users"""
    users = db.get_active_users(limit=10)
    
    keyboard = [
        [InlineKeyboardButton("🔄 Refresh", callback_data="admin_users")],
        [InlineKeyboardButton("🔙 Back to Admin Menu", callback_data="admin_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
👥 *Active Users*

━━━━━━━━━━━━━━━━━
"""
    
    if users:
        for idx, user in enumerate(users, 1):
            message += f"{idx}. User ID: `{user['user_id']}`\n"
            message += f"   Links: {user['link_count']}\n"
            message += f"   Clicks: {user['total_clicks']}\n\n"
    else:
        message += "_No users yet_\n"
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin callback queries"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    
    # Check admin
    if not is_admin(user_id):
        await query.answer("❌ Access Denied", show_alert=True)
        return
    
    await query.answer()
    
    callback_data = query.data
    
    if callback_data == "admin_stats":
        await handle_admin_stats(query, context)
    elif callback_data == "admin_domains":
        await handle_admin_domains(query, context)
    elif callback_data == "admin_links":
        await handle_admin_links(query, context)
    elif callback_data == "admin_users":
        await handle_admin_users(query, context)
    elif callback_data == "admin_menu":
        # Back to admin menu
        keyboard = [
            [
                InlineKeyboardButton("📊 Bot Stats", callback_data="admin_stats"),
                InlineKeyboardButton("👥 User List", callback_data="admin_users")
            ],
            [
                InlineKeyboardButton("🌐 Domain Management", callback_data="admin_domains"),
            ],
            [
                InlineKeyboardButton("🔗 All Links", callback_data="admin_links"),
            ],
            [
                InlineKeyboardButton("❌ Close", callback_data="admin_close")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = """
🔐 *Admin Panel*

Pilih menu di bawah untuk manage bot.
        """
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif callback_data == "admin_close":
        await query.delete_message()
