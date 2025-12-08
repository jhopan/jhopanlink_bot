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
    elif user_state == 'waiting_custom_alias':
        await process_custom_alias(update, context, text)
    elif user_state == 'waiting_shortlink_tinyurl':
        await process_shortlink_tinyurl(update, context, text)
    elif user_state == 'waiting_subdomain_request':
        await process_subdomain_request(update, context, text)
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
    """Process short link dengan default domain - step 1: terima URL, tampilkan pilihan"""
    url = text.strip()
    
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Simpan URL ke context
    context.user_data['pending_url'] = url
    context.user_data['state'] = 'choosing_alias_type'
    
    # Tampilkan pilihan: Random atau Custom
    keyboard = [
        [
            InlineKeyboardButton("🎲 Random Code", callback_data="alias_random"),
            InlineKeyboardButton("✏️ Custom Alias", callback_data="alias_custom")
        ],
        [
            InlineKeyboardButton("❌ Cancel", callback_data="back_to_main")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Tampilkan preview URL dan pilihan
    url_preview = url if len(url) <= 60 else url[:57] + "..."
    message = f"""
🔗 *URL Diterima!*

`{url_preview}`

━━━━━━━━━━━━━━━━━━━━━━

*Pilih jenis short link:*

🎲 *Random Code*
   Generate code otomatis
   Contoh: `s.jhopan.my.id/abc123`

✏️ *Custom Alias*
   Pilih alias sendiri
   Contoh: `s.jhopan.my.id/googlejhosua`

━━━━━━━━━━━━━━━━━━━━━━
Pilih salah satu tombol di atas
    """
    
    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def process_custom_alias(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Process custom alias input dan buat short link"""
    alias = text.strip()
    url = context.user_data.get('pending_url')
    
    if not url:
        await update.message.reply_text(
            "❌ Error: URL tidak ditemukan. Silakan mulai lagi.",
            reply_markup=get_back_button()
        )
        return
    
    # Validate alias format
    if len(alias) < 3:
        await update.message.reply_text(
            "❌ Alias terlalu pendek! Minimal 3 karakter.\n\nSilakan coba lagi:",
            reply_markup=get_back_button()
        )
        return
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', alias):
        await update.message.reply_text(
            "❌ Alias hanya boleh mengandung huruf, angka, - dan _\n\nSilakan coba lagi:",
            reply_markup=get_back_button()
        )
        return
    
    user_id = str(update.effective_user.id)
    
    processing_msg = await update.message.reply_text(
        "⏳ Sedang membuat short link dengan custom alias...",
        parse_mode='Markdown'
    )
    
    try:
        # Create short link dengan custom alias
        result = db.create_short_link(
            original_url=url,
            custom_alias=alias,
            domain='default',
            user_id=user_id
        )
        
        if result['success']:
            domain_name = f"{Config.DEFAULT_SUBDOMAIN}.{Config.DEFAULT_DOMAIN}"
            short_code = result['custom_alias']
            short_url = f"https://{domain_name}/{short_code}"
            
            url_preview = url if len(url) <= 50 else url[:47] + "..."
            
            message = f"""
✅ *Short Link Berhasil Dibuat!*

━━━━━━━━━━━━━━━━━
🔗 *Short URL:*
`{short_url}`

📊 *Original URL:*
{url_preview}

✏️ *Alias:* `{short_code}` (Custom)

━━━━━━━━━━━━━━━━━
✨ Link sudah siap digunakan!
            """
            
            await processing_msg.edit_text(
                message,
                parse_mode='Markdown',
                reply_markup=get_back_button()
            )
        else:
            error_msg = result.get('error', 'Unknown error')
            await processing_msg.edit_text(
                f"❌ Gagal membuat short link!\n\n{error_msg}\n\nSilakan coba alias lain:",
                reply_markup=get_back_button()
            )
            return  # Don't clear state, biar bisa coba lagi
    
    except Exception as e:
        await processing_msg.edit_text(
            f"❌ Error: {str(e)}",
            reply_markup=get_back_button()
        )
    
    # Clear state
    context.user_data['state'] = None
    context.user_data['pending_url'] = None

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
            url_preview = url if len(url) <= 60 else url[:57] + "..."
            message = f"""
✅ *Short Link Berhasil Dibuat!*

━━━━━━━━━━━━━━━━━
🔗 *Short URL (TinyURL):*
`{short_url}`

📏 *Original URL:*
`{url_preview}`

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
            text_preview = text if len(text) <= 100 else text[:97] + "..."
            caption = f"""
✅ *QR Code Berhasil Dibuat!*

━━━━━━━━━━━━━━━━━
📱 *Content:*
`{text_preview}`

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
            url_preview = url if len(url) <= 60 else url[:57] + "..."
            caption = f"""
✅ *Short Link + QR Code Berhasil Dibuat!*

━━━━━━━━━━━━━━━━━
🔗 *Short URL:*
`{short_url}`

📊 *Original URL:*
`{url_preview}`

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

async def process_subdomain_request(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Process subdomain request - kirim ke admin"""
    import re
    from config.config import Config
    
    subdomain = text.lower().strip()
    
    # Validate subdomain format
    if not re.match(r'^[a-z0-9-]{3,20}$', subdomain):
        await update.message.reply_text(
            "❌ *Subdomain tidak valid!*\n\n"
            "*Rules:*\n"
            "• Huruf kecil saja (a-z)\n"
            "• Boleh angka (0-9)\n"
            "• Boleh tanda hubung (-)\n"
            "• Minimal 3 karakter\n"
            "• Maksimal 20 karakter\n\n"
            "*Contoh valid:* mylink, promo2024, my-brand\n\n"
            "Silakan coba lagi atau ketik /cancel",
            parse_mode='Markdown',
            reply_markup=get_back_button()
        )
        return
    
    # Check jika subdomain sudah ada di database
    existing = db.check_subdomain_exists(subdomain)
    if existing:
        await update.message.reply_text(
            f"❌ *Subdomain sudah digunakan!*\n\n"
            f"Subdomain `{subdomain}` sudah diambil oleh user lain.\n\n"
            "Silakan pilih nama lain atau ketik /cancel",
            parse_mode='Markdown',
            reply_markup=get_back_button()
        )
        return
    
    # Get user info
    user_id = context.user_data.get('user_id', update.effective_user.id)
    username = context.user_data.get('username', update.effective_user.username or "User")
    user_full_name = update.effective_user.full_name
    default_domain = Config.DEFAULT_DOMAIN if Config.DEFAULT_DOMAIN else "jhopan.my.id"
    
    # Kirim notifikasi ke admin
    from src.handlers.admin import ADMIN_ID
    
    admin_message = f"""
🎁 *SUBDOMAIN REQUEST*

━━━━━━━━━━━━━━━━━
👤 *User Info:*
• Name: {user_full_name}
• Username: @{username}
• User ID: `{user_id}`

━━━━━━━━━━━━━━━━━
🌐 *Subdomain Request:*
• Subdomain: `{subdomain}`
• Full Domain: `{subdomain}.{default_domain}`

━━━━━━━━━━━━━━━━━
*Action Required:*
1. Setup DNS CNAME di Cloudflare
2. Tambah ke Cloudflare Tunnel config
3. Inform user setelah setup selesai

*Command untuk approve:*
`/approve_subdomain {subdomain} {user_id}`
    """
    
    try:
        # Kirim ke admin via bot
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_message,
            parse_mode='Markdown'
        )
        
        # Confirm ke user
        await update.message.reply_text(
            f"✅ *Request Berhasil Dikirim!*\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"🌐 *Subdomain:* `{subdomain}.{default_domain}`\n\n"
            f"📩 *Status:* Menunggu approval admin\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"*Next Steps:*\n"
            f"1. Admin akan setup subdomain Anda\n"
            f"2. Proses setup: 1-2 hari kerja\n"
            f"3. Anda akan diinfokan saat sudah siap\n\n"
            f"💡 *Tip:* Hubungi @jhopan_05 jika urgent!",
            parse_mode='Markdown',
            reply_markup=get_back_button()
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Gagal mengirim request ke admin!\n\n"
            f"Silakan hubungi admin langsung: @jhopan_05\n\n"
            f"Info subdomain: `{subdomain}.{default_domain}`",
            parse_mode='Markdown',
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
