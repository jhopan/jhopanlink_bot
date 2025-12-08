"""
Callback query handlers untuk inline keyboard buttons
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.db_manager import DatabaseManager
from config.config import Config

# Initialize database
db = DatabaseManager()

# Conversation states
WAITING_URL, WAITING_ALIAS, WAITING_QR_TEXT, WAITING_DOMAIN = range(4)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk semua button callback"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    # Route ke handler yang sesuai
    if callback_data == "menu_shortlink":
        await handle_shortlink_menu(query, context)
    elif callback_data == "menu_qr":
        await handle_qr_menu(query, context)
    elif callback_data == "menu_both":
        await handle_both_menu(query, context)
    elif callback_data == "menu_stats":
        await handle_stats_menu(query, context)
    elif callback_data == "menu_mylinks":
        await handle_mylinks_menu(query, context)
    elif callback_data == "menu_adddomain":
        await handle_adddomain_menu(query, context)
    elif callback_data == "menu_help":
        await handle_help_menu(query, context)
    elif callback_data == "back_to_main":
        await back_to_main_menu(query, context)

async def handle_shortlink_menu(query, context: ContextTypes.DEFAULT_TYPE):
    """Menu untuk membuat short link"""
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
🔗 *Short Link Generator*

Silakan kirim URL yang ingin diperpendek.

*Format:*
Kirim URL saja → Random code
`https://example.com/long/url`

Kirim URL + spasi + alias → Custom alias
`https://example.com myalias`

*Contoh:*
`https://forms.google.com/form/123456`
atau
`https://forms.google.com/form/123456 FormDaftar`

━━━━━━━━━━━━━━━━━
Ketik /cancel untuk batal
    """
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # Set state: waiting for URL
    context.user_data['state'] = 'waiting_shortlink_url'

async def handle_qr_menu(query, context: ContextTypes.DEFAULT_TYPE):
    """Menu untuk membuat QR code"""
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
📱 *QR Code Generator*

Silakan kirim URL atau teks yang ingin dijadikan QR Code.

*Contoh:*
`https://example.com`
`https://wa.me/628123456789`
`Teks bebas untuk QR Code`

━━━━━━━━━━━━━━━━━
Ketik /cancel untuk batal
    """
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # Set state: waiting for QR text
    context.user_data['state'] = 'waiting_qr_text'

async def handle_both_menu(query, context: ContextTypes.DEFAULT_TYPE):
    """Menu untuk membuat short link + QR code"""
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
🔗📱 *Short Link + QR Code*

Silakan kirim URL yang ingin diperpendek dan dibuatkan QR Code.

*Format:*
Kirim URL saja → Random code
`https://example.com/long/url`

Kirim URL + spasi + alias → Custom alias
`https://example.com myalias`

━━━━━━━━━━━━━━━━━
Ketik /cancel untuk batal
    """
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # Set state: waiting for URL (both)
    context.user_data['state'] = 'waiting_both_url'

async def handle_stats_menu(query, context: ContextTypes.DEFAULT_TYPE):
    """Tampilkan statistik user"""
    user_id = str(query.from_user.id)
    stats = db.get_user_stats(user_id)
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if not stats:
        message = """
📊 *Your Statistics*

Anda belum memiliki link apapun.
Klik "🔗 Short Link" untuk membuat link pertama Anda!
        """
    else:
        message = f"""
📊 *Your Statistics*

━━━━━━━━━━━━━━━━━
📈 *Total Links:* `{stats['total_links']}`
👆 *Total Clicks:* `{stats['total_clicks']}`
🌐 *Custom Domains:* `{stats['total_domains']}`

━━━━━━━━━━━━━━━━━
*Top Links:*
        """
        
        # Get top 5 links
        top_links = db.get_user_links(user_id, limit=5)
        for idx, link in enumerate(top_links, 1):
            domain_name = link['domain'] if link['domain'] != 'default' else f"{Config.DEFAULT_SUBDOMAIN}.{Config.DEFAULT_DOMAIN}"
            short_code = link['custom_alias'] or link['short_code']
            short_url = f"https://{domain_name}/{short_code}"
            
            message += f"\n*{idx}.* `{short_url}`"
            message += f"\n   📊 {link['clicks']} clicks\n"
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_mylinks_menu(query, context: ContextTypes.DEFAULT_TYPE):
    """Tampilkan daftar link user"""
    user_id = str(query.from_user.id)
    links = db.get_user_links(user_id, limit=10)
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if not links:
        message = """
📋 *Your Links*

Anda belum memiliki link apapun.
Klik "🔗 Short Link" untuk membuat link pertama Anda!
        """
    else:
        message = f"""
📋 *Your Links*

Total: {len(links)} links

━━━━━━━━━━━━━━━━━
        """
        
        for idx, link in enumerate(links, 1):
            domain_name = link['domain'] if link['domain'] != 'default' else f"{Config.DEFAULT_SUBDOMAIN}.{Config.DEFAULT_DOMAIN}"
            short_code = link['custom_alias'] or link['short_code']
            short_url = f"https://{domain_name}/{short_code}"
            
            message += f"\n*{idx}.* `{short_url}`"
            message += f"\n   📊 {link['clicks']} clicks"
            message += f"\n   🔗 {link['original_url'][:35]}...\n"
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_adddomain_menu(query, context: ContextTypes.DEFAULT_TYPE):
    """Menu untuk menambah custom domain"""
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
🌐 *Add Custom Domain*

Silakan kirim nama domain yang ingin ditambahkan.

*Contoh:*
`jhopan.id`
`mysite.com`

*Catatan:*
• Domain harus sudah pointing ke server Anda
• Setup DNS di Cloudflare terlebih dahulu
• Setelah ditambahkan, bisa digunakan di pembuatan short link

━━━━━━━━━━━━━━━━━
Ketik /cancel untuk batal
    """
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # Set state: waiting for domain
    context.user_data['state'] = 'waiting_domain'

async def handle_help_menu(query, context: ContextTypes.DEFAULT_TYPE):
    """Tampilkan help menu"""
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
ℹ️ *Help & Tutorial*

━━━━━━━━━━━━━━━━━
*🔗 Short Link*
Perpendek URL panjang menjadi pendek
• Klik "🔗 Short Link"
• Kirim URL Anda
• Dapatkan link pendek + analytics

*📱 QR Code*
Buat QR Code dari URL atau teks
• Klik "📱 QR Code"  
• Kirim URL/teks
• Download QR Code

*🔗📱 Short Link + QR*
Dapat keduanya sekaligus!
• Link pendek
• QR Code untuk link tersebut

*📊 Statistics*
Lihat performa link Anda:
• Total links & clicks
• Top performing links
• Domain yang digunakan

*🌐 Custom Domain*
Gunakan domain sendiri:
• Contoh: link.jhopan.id/abc
• Full analytics & kontrol
• Branding sendiri

━━━━━━━━━━━━━━━━━
*Tips:*
• Link bisa dicustom aliasnya
• Send URL langsung (tanpa klik menu)
• Track semua click di /stats
• Domain gratis: duckdns.org

Butuh bantuan? Contact: @jhopan
    """
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def back_to_main_menu(query, context: ContextTypes.DEFAULT_TYPE):
    """Kembali ke main menu"""
    keyboard = [
        [
            InlineKeyboardButton("🔗 Short Link", callback_data="menu_shortlink"),
            InlineKeyboardButton("📱 QR Code", callback_data="menu_qr")
        ],
        [
            InlineKeyboardButton("🔗📱 Short Link + QR", callback_data="menu_both")
        ],
        [
            InlineKeyboardButton("📊 My Stats", callback_data="menu_stats"),
            InlineKeyboardButton("📋 My Links", callback_data="menu_mylinks")
        ],
        [
            InlineKeyboardButton("🌐 Add Domain", callback_data="menu_adddomain"),
            InlineKeyboardButton("ℹ️ Help", callback_data="menu_help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
🤖 *ShortLink & QR Code Bot*

Pilih menu di bawah ini untuk mulai:
    """
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # Clear state
    context.user_data['state'] = None
