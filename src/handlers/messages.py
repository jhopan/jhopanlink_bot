"""
Message handlers untuk bot
"""
from telegram import Update
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

async def short_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk command /short
    
    Format:
    /short <URL> - Generate random short code
    /short <URL> <alias> - Custom alias
    /short <URL> <alias> <domain> - Custom alias dengan domain spesifik
    """
    if not context.args:
        await update.message.reply_text(
            "❌ *Format salah!*\n\n"
            "*Gunakan:*\n"
            "`/short <URL>` - Random short code\n"
            "`/short <URL> <alias>` - Custom alias\n"
            "`/short <URL> <alias> <domain>` - Dengan domain custom\n\n"
            "*Contoh:*\n"
            "`/short https://example.com/very/long/url`\n"
            "`/short https://forms.google.com DaftarPengurus2025`\n"
            "`/short https://forms.google.com pmkft/DaftarPengurus jhopan.id`",
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
        "⏳ Sedang membuat short link...",
        parse_mode='Markdown'
    )
    
    try:
        # Check if web server is running
        web_server_online = await check_web_server_status()
        
        if web_server_online:
            # Use custom domain (primary)
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
                
                await processing_msg.edit_text(
                    "✅ *Short Link berhasil dibuat!*\n\n"
                    f"🔗 *URL Asli:*\n`{url[:60]}{'...' if len(url) > 60 else ''}`\n\n"
                    f"✨ *Short Link:*\n`{short_url}`\n\n"
                    f"📊 *Stats:* 0 clicks\n\n"
                    "━━━━━━━━━━━━━━━━━\n"
                    "💡 *Tip:* Gunakan `/mystats` untuk lihat semua link Anda!",
                    parse_mode='Markdown'
                )
            else:
                await processing_msg.edit_text(
                    f"❌ *Gagal membuat short link!*\n\n"
                    f"Error: {result.get('error', 'Unknown error')}\n\n"
                    "Silakan coba alias lain atau hubungi admin.",
                    parse_mode='Markdown'
                )
        else:
            # Fallback to TinyURL
            short_gen = ShortLinkGenerator()
            short_url = await short_gen.shorten(url, custom_alias)
            
            if short_url:
                await processing_msg.edit_text(
                    "✅ *Short Link berhasil dibuat (via TinyURL)!*\n\n"
                    f"🔗 *URL Asli:*\n`{url[:60]}{'...' if len(url) > 60 else ''}`\n\n"
                    f"✨ *Short Link:*\n`{short_url}`\n\n"
                    "⚠️ *Note:* Web server sedang offline, menggunakan TinyURL sebagai backup.\n\n"
                    "━━━━━━━━━━━━━━━━━\n"
                    "💡 Hubungi admin untuk mengaktifkan domain custom!",
                    parse_mode='Markdown'
                )
            else:
                await processing_msg.edit_text(
                    "❌ *Gagal membuat short link!*\n\n"
                    "Web server offline dan TinyURL juga gagal.\n"
                    "Silakan coba lagi nanti atau hubungi admin.",
                    parse_mode='Markdown'
                )
    
    except Exception as e:
        await processing_msg.edit_text(
            f"❌ *Error:* {str(e)}\n\n"
            "Silakan coba lagi!",
            parse_mode='Markdown'
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

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk pesan teks biasa (auto-detect URL)"""
    text = update.message.text.strip()
    
    # Check if it's a URL
    if is_url(text) or text.startswith('www.'):
        # Auto create short link
        processing_msg = await update.message.reply_text(
            "🔍 URL terdeteksi! Membuat short link...",
            parse_mode='Markdown'
        )
        
        try:
            url = text if text.startswith(('http://', 'https://')) else 'https://' + text
            user_id = str(update.effective_user.id)
            
            # Check if web server is running
            web_server_online = await check_web_server_status()
            
            if web_server_online:
                # Use custom domain
                result = db.create_short_link(
                    original_url=url,
                    user_id=user_id
                )
                
                if result['success']:
                    domain_name = f"{Config.DEFAULT_SUBDOMAIN}.{Config.DEFAULT_DOMAIN}"
                    short_code = result['short_code']
                    short_url = f"https://{domain_name}/{short_code}"
                    
                    await processing_msg.edit_text(
                        "✅ *Short Link berhasil dibuat!*\n\n"
                        f"🔗 *URL Asli:*\n`{text}`\n\n"
                        f"✨ *Short Link:*\n`{short_url}`\n\n"
                        "━━━━━━━━━━━━━━━━━\n"
                        "💡 *Tip:* Gunakan `/both <URL>` untuk mendapatkan QR Code juga!",
                        parse_mode='Markdown'
                    )
                else:
                    raise Exception("Database error")
            else:
                # Fallback to TinyURL
                short_gen = ShortLinkGenerator()
                short_url = await short_gen.shorten(url)
                
                if short_url and short_url != url:
                    await processing_msg.edit_text(
                        "✅ *Short Link berhasil dibuat (via TinyURL)!*\n\n"
                        f"🔗 *URL Asli:*\n`{text}`\n\n"
                        f"✨ *Short Link:*\n`{short_url}`\n\n"
                        "⚠️ *Note:* Web server offline, menggunakan backup.\n"
                        "━━━━━━━━━━━━━━━━━\n"
                        "💡 *Tip:* Gunakan `/both <URL>` untuk mendapatkan QR Code juga!",
                        parse_mode='Markdown'
                    )
                else:
                    await processing_msg.edit_text(
                        "❌ Gagal membuat short link.\n\n"
                        "Silakan coba lagi nanti.",
                        parse_mode='Markdown'
                    )
        
        except Exception as e:
            await processing_msg.edit_text(
                f"❌ *Error:* {str(e)}",
                parse_mode='Markdown'
            )
    else:
        # Not a URL
        await update.message.reply_text(
            "❓ *Perintah tidak dikenali*\n\n"
            "Gunakan:\n"
            "• `/short <URL>` - Membuat short link\n"
            "• `/qr <teks>` - Membuat QR Code\n"
            "• `/both <URL>` - Keduanya\n\n"
            "Atau kirim URL langsung!\n\n"
            "Ketik `/help` untuk bantuan lengkap.",
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
