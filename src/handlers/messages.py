"""
Message handlers untuk bot
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.utils import QRCodeGenerator, ShortLinkGenerator
from config.config import Config
from database.db_manager import DatabaseManager
import re
import aiohttp

# Initialize generators
qr_gen = QRCodeGenerator(
    box_size=Config.QR_BOX_SIZE,
    border=Config.QR_BORDER,
    error_correction=Config.QR_ERROR_CORRECTION
)

# Initialize database
db = DatabaseManager()

async def check_web_server_status():
    """Check if web server is running"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://localhost:{Config.WEB_PORT}/api/health",
                timeout=aiohttp.ClientTimeout(total=2)
            ) as response:
                return response.status == 200
    except:
        return False

def is_url(text: str) -> bool:
    """Check if text is a URL"""
    url_pattern = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    # Check if starts with common patterns
    if text.startswith(('http://', 'https://', 'www.')):
        return True
    
    return re.match(url_pattern, text) is not None

def get_back_button():
    """Return back to main menu button"""
    keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]]
    return InlineKeyboardMarkup(keyboard)

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages based on user state"""
    text = update.message.text.strip()
    user_state = context.user_data.get('state')
    
    # Cancel command
    if text.lower() == '/cancel':
        context.user_data['state'] = None
        await update.message.reply_text(
            "❌ Operasi dibatalkan.\n\nKetik /start untuk kembali ke menu utama.",
            reply_markup=get_back_button()
        )
        return
    
    # Route based on state
    if user_state == 'waiting_shortlink_default':
        await process_shortlink_default(update, context, text)
    elif user_state == 'waiting_shortlink_tinyurl':
        await process_shortlink_tinyurl(update, context, text)
    elif user_state == 'waiting_qr_text':
        await process_qr_input(update, context, text)
    elif user_state == 'waiting_both_url':
        await process_both_input(update, context, text)
    elif user_state == 'waiting_domain':
        await process_domain_input(update, context, text)
    else:
        # Default: auto-detect URL
        if is_url(text):
            context.user_data['state'] = 'waiting_shortlink_default'
            context.user_data['domain_choice'] = 'default'
            await process_shortlink_default(update, context, text)
        else:
            await update.message.reply_text(
                "❓ Tidak mengerti perintah Anda.\n\n"
                "Ketik /start untuk melihat menu atau kirim URL untuk membuat short link.",
                reply_markup=get_back_button()
            )

async def process_shortlink_default(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Process short link dengan default domain"""
    # Parse input: URL atau URL + alias
    parts = text.split(maxsplit=1)
    url = parts[0]
    custom_alias = parts[1] if len(parts) > 1 else None
    
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    user_id = str(update.effective_user.id)
    
    processing_msg = await update.message.reply_text(
        "⏳ Sedang membuat short link...",
        parse_mode='Markdown'
    )
    
    try:
        # Check if web server is running
        web_server_online = await check_web_server_status()
        
        if web_server_online and Config.DEFAULT_DOMAIN:
            # Use custom domain (primary)
            result = db.create_short_link(
                original_url=url,
                custom_alias=custom_alias,
                domain='default',
                user_id=user_id
            )
            
            if result['success']:
                domain_name = f"{Config.DEFAULT_SUBDOMAIN}.{Config.DEFAULT_DOMAIN}"
                short_code = result['custom_alias'] or result['short_code']
                short_url = f"https://{domain_name}/{short_code}"
                
                message = f"""
✅ *Short Link Berhasil Dibuat!*

━━━━━━━━━━━━━━━━━
🔗 *Short URL:*
`{short_url}`

📊 *Original URL:*
{url[:50]}{"..." if len(url) > 50 else ""}

━━━━━━━━━━━━━━━━━
✨ Link sudah siap digunakan!
Klik link untuk test redirect.
                """
                
                await processing_msg.edit_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=get_back_button()
                )
            else:
                await processing_msg.edit_text(
                    f"❌ Gagal membuat short link!\n\n{result.get('error', 'Unknown error')}",
                    reply_markup=get_back_button()
                )
        else:
            # Fallback to TinyURL
            await processing_msg.edit_text(
                "⚠️ Default domain tidak tersedia.\n\n"
                "Gunakan TinyURL atau hubungi admin untuk custom domain.",
                reply_markup=get_back_button()
            )
    
    except Exception as e:
        await processing_msg.edit_text(
            f"❌ Error: {str(e)}",
            reply_markup=get_back_button()
        )
    
    # Clear state
    context.user_data['state'] = None

async def process_shortlink_tinyurl(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Process short link dengan TinyURL"""
    parts = text.split(maxsplit=1)
    url = parts[0]
    custom_alias = parts[1] if len(parts) > 1 else None
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    processing_msg = await update.message.reply_text(
        "⏳ Sedang membuat short link via TinyURL...",
        parse_mode='Markdown'
    )
    
    try:
        shortlink_gen = ShortLinkGenerator()
        short_url = shortlink_gen.create_tinyurl(url, custom_alias)
        
        if short_url:
            message = f"""
✅ *Short Link Berhasil Dibuat!*

━━━━━━━━━━━━━━━━━
🔗 *Short URL (TinyURL):*
`{short_url}`

📊 *Original URL:*
{url[:50]}{"..." if len(url) > 50 else ""}

━━━━━━━━━━━━━━━━━
📱 Link via TinyURL.com
            """
            
            await processing_msg.edit_text(
                message,
                parse_mode='Markdown',
                reply_markup=get_back_button()
            )
        else:
            await processing_msg.edit_text(
                "❌ Gagal membuat short link dengan TinyURL!",
                reply_markup=get_back_button()
            )
    
    except Exception as e:
        await processing_msg.edit_text(
            f"❌ Error: {str(e)}",
            reply_markup=get_back_button()
        )
    
    context.user_data['state'] = None

async def process_qr_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Process QR code generation from user input"""
    processing_msg = await update.message.reply_text(
        "⏳ Sedang membuat QR Code...",
        parse_mode='Markdown'
    )
    
    try:
        # Generate QR code
        qr_image = qr_gen.generate(text)
        
        if qr_image:
            caption = f"""
✅ *QR Code Berhasil Dibuat!*

━━━━━━━━━━━━━━━━━
📱 *Content:*
{text[:100]}{"..." if len(text) > 100 else ""}

━━━━━━━━━━━━━━━━━
Scan QR code untuk akses content.
            """
            
            await update.message.reply_photo(
                photo=qr_image,
                caption=caption,
                parse_mode='Markdown',
                reply_markup=get_back_button()
            )
            
            await processing_msg.delete()
        else:
            await processing_msg.edit_text(
                "❌ Gagal membuat QR Code!",
                reply_markup=get_back_button()
            )
    
    except Exception as e:
        await processing_msg.edit_text(
            f"❌ Error: {str(e)}",
            reply_markup=get_back_button()
        )
    
    # Clear state
    context.user_data['state'] = None

async def process_both_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Process short link + QR code creation"""
    # Parse input
    parts = text.split(maxsplit=1)
    url = parts[0]
    custom_alias = parts[1] if len(parts) > 1 else None
    
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    user_id = str(update.effective_user.id)
    
    processing_msg = await update.message.reply_text(
        "⏳ Sedang membuat short link + QR code...",
        parse_mode='Markdown'
    )
    
    try:
        # Check web server
        web_server_online = await check_web_server_status()
        
        if web_server_online and Config.DEFAULT_DOMAIN:
            # Create short link
            result = db.create_short_link(
                original_url=url,
                custom_alias=custom_alias,
                domain='default',
                user_id=user_id
            )
            
            if result['success']:
                domain_name = f"{Config.DEFAULT_SUBDOMAIN}.{Config.DEFAULT_DOMAIN}"
                short_code = result['custom_alias'] or result['short_code']
                short_url = f"https://{domain_name}/{short_code}"
            else:
                await processing_msg.edit_text(
                    f"❌ Gagal membuat short link!\n\n{result.get('error', 'Unknown error')}",
                    reply_markup=get_back_button()
                )
                return
        else:
            # Fallback to TinyURL
            shortlink_gen = ShortLinkGenerator()
            short_url = shortlink_gen.create_tinyurl(url, custom_alias)
            
            if not short_url:
                await processing_msg.edit_text(
                    "❌ Gagal membuat short link!",
                    reply_markup=get_back_button()
                )
                return
        
        # Generate QR code for short URL
        qr_image = qr_gen.generate(short_url)
        
        if qr_image:
            caption = f"""
✅ *Short Link + QR Code Berhasil Dibuat!*

━━━━━━━━━━━━━━━━━
🔗 *Short URL:*
`{short_url}`

📊 *Original URL:*
{url[:50]}{"..." if len(url) > 50 else ""}

━━━━━━━━━━━━━━━━━
📱 Scan QR code untuk akses link.
            """
            
            await update.message.reply_photo(
                photo=qr_image,
                caption=caption,
                parse_mode='Markdown',
                reply_markup=get_back_button()
            )
            
            await processing_msg.delete()
        else:
            await processing_msg.edit_text(
                "❌ Gagal membuat QR Code!",
                reply_markup=get_back_button()
            )
    
    except Exception as e:
        await processing_msg.edit_text(
            f"❌ Error: {str(e)}",
            reply_markup=get_back_button()
        )
    
    # Clear state
    context.user_data['state'] = None

async def process_domain_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Process custom domain addition"""
    domain = text.lower().strip()
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "unknown"
    
    processing_msg = await update.message.reply_text(
        "⏳ Menambahkan domain...",
        parse_mode='Markdown'
    )
    
    try:
        result = db.add_custom_domain(domain, user_id, username)
        
        if result['success']:
            message = f"""
✅ *Domain Berhasil Ditambahkan!*

━━━━━━━━━━━━━━━━━
🌐 *Domain:* `{domain}`

*Cara Pakai:*
Saat membuat short link, tambahkan domain di akhir:
`https://example.com myalias {domain}`

Link akan jadi: `{domain}/myalias`
            """
            
            await processing_msg.edit_text(
                message,
                parse_mode='Markdown',
                reply_markup=get_back_button()
            )
        else:
            await processing_msg.edit_text(
                f"❌ Gagal menambahkan domain!\n\n{result.get('error', 'Unknown error')}",
                reply_markup=get_back_button()
            )
    
    except Exception as e:
        await processing_msg.edit_text(
            f"❌ Error: {str(e)}",
            reply_markup=get_back_button()
        )
    
    # Clear state
    context.user_data['state'] = None

# Old command handlers kept for backward compatibility (direct /command usage)
async def short_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Legacy /short command - redirects to menu-based flow"""
    if context.args:
        # If arguments provided, process directly
        text = ' '.join(context.args)
        context.user_data['state'] = 'waiting_shortlink_default'
        context.user_data['domain_choice'] = 'default'
        await process_shortlink_default(update, context, text)
    else:
        # Show usage
        await update.message.reply_text(
            "💡 Silakan kirim URL yang ingin diperpendek, atau gunakan /start untuk menu interaktif.",
            reply_markup=get_back_button()
        )

async def qr_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /qr"""
    if not context.args:
        await update.message.reply_text(
            "❌ *Format salah!*\n\n"
            "Gunakan: `/qr <teks atau URL>`\n\n"
            "Contoh:\n"
            "`/qr https://example.com`\n"
            "`/qr Halo, ini QR Code saya!`",
            parse_mode='Markdown'
        )
        return
    
    data = ' '.join(context.args)
    
    # Send processing message
    processing_msg = await update.message.reply_text(
        "⏳ Sedang membuat QR Code...",
        parse_mode='Markdown'
    )
    
    try:
        # Generate QR Code
        qr_image = qr_gen.generate(data)
        
        # Delete processing message
        await processing_msg.delete()
        
        # Send QR Code
        caption = (
            "✅ *QR Code berhasil dibuat!*\n\n"
            f"📝 *Data:*\n`{data[:100]}{'...' if len(data) > 100 else ''}`"
        )
        
        await update.message.reply_photo(
            photo=qr_image,
            caption=caption,
            parse_mode='Markdown'
        )
    
    except Exception as e:
        await processing_msg.edit_text(
            f"❌ *Error:* {str(e)}\n\n"
            "Silakan coba lagi!",
            parse_mode='Markdown'
        )

async def both_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk command /both (short link + QR code)
    
    Format sama seperti /short
    """
    if not context.args:
        await update.message.reply_text(
            "❌ *Format salah!*\n\n"
            "*Gunakan:*\n"
            "`/both <URL>` - Random short code + QR\n"
            "`/both <URL> <alias>` - Custom alias + QR\n\n"
            "*Contoh:*\n"
            "`/both https://example.com/very/long/url`\n"
            "`/both https://forms.google.com DaftarPengurus2025`",
            parse_mode='Markdown'
        )
        return
    
    # Parse arguments
    url = context.args[0]
    custom_alias = context.args[1] if len(context.args) > 1 else None
    custom_domain = context.args[2] if len(context.args) > 2 else 'default'
    
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    user_id = str(update.effective_user.id)
    
    # Send processing message
    processing_msg = await update.message.reply_text(
        "⏳ Sedang membuat short link dan QR Code...",
        parse_mode='Markdown'
    )
    
    try:
        # Create short link in database
        result = db.create_short_link(
            original_url=url,
            custom_alias=custom_alias,
            domain=custom_domain,
            user_id=user_id
        )
        
        if result['success']:
            # Build short URL
            if custom_domain == 'default':
                domain_name = f"{Config.DEFAULT_SUBDOMAIN}.{Config.DEFAULT_DOMAIN}"
            else:
                domain_name = custom_domain
            
            short_code = result['custom_alias'] or result['short_code']
            short_url = f"https://{domain_name}/{short_code}"
            
            # Generate QR Code from short link
            qr_image = qr_gen.generate(short_url)
            
            # Delete processing message
            await processing_msg.delete()
            
            # Send result
            caption = (
                "✅ *Short Link + QR Code berhasil dibuat!*\n\n"
                f"🔗 *URL Asli:*\n`{url[:50]}{'...' if len(url) > 50 else ''}`\n\n"
                f"✨ *Short Link:*\n`{short_url}`\n\n"
                "━━━━━━━━━━━━━━━━━\n"
                "QR Code di atas mengarah ke short link! 📱"
            )
            
            await update.message.reply_photo(
                photo=qr_image,
                caption=caption,
                parse_mode='Markdown'
            )
        else:
            await processing_msg.edit_text(
                f"❌ *Gagal membuat short link!*\n\n"
                f"Error: {result.get('error', 'Unknown error')}",
                parse_mode='Markdown'
            )
    
    except Exception as e:
        await processing_msg.edit_text(
            f"❌ *Error:* {str(e)}\n\n"
            "Silakan coba lagi!",
            parse_mode='Markdown'
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk error"""
    print(f'Update {update} caused error {context.error}')
    
    if update and update.message:
        await update.message.reply_text(
            "❌ *Terjadi kesalahan!*\n\n"
            "Silakan coba lagi atau hubungi admin.",
            parse_mode='Markdown'
        )
