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
    elif callback_data == "shortlink_default":
        await handle_shortlink_default(query, context)
    elif callback_data == "shortlink_custom":
        await handle_shortlink_custom(query, context)
    elif callback_data == "request_subdomain":
        await handle_request_subdomain(query, context)
    elif callback_data == "custom_domain_own":
        await handle_custom_domain_own(query, context)
    elif callback_data == "shortlink_tinyurl":
        await handle_shortlink_tinyurl(query, context)
    elif callback_data == "alias_random":
        await handle_alias_random(query, context)
    elif callback_data == "alias_custom":
        await handle_alias_custom(query, context)
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
    """Menu untuk membuat short link dengan pilihan domain"""
    keyboard = [
        [
            InlineKeyboardButton("🌐 Pakai Default Domain", callback_data="shortlink_default"),
        ],
        [
            InlineKeyboardButton("🎯 Custom Domain/Subdomain", callback_data="shortlink_custom"),
        ],
        [
            InlineKeyboardButton("📱 TinyURL (No Domain)", callback_data="shortlink_tinyurl")
        ],
        [
            InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Get default domain info
    default_domain = Config.DEFAULT_DOMAIN
    subdomain = Config.DEFAULT_SUBDOMAIN
    
    if default_domain:
        domain_info = f"`{subdomain}.{default_domain}`"
    else:
        domain_info = "_(Belum ada, akan pakai TinyURL)_"
    
    message = f"""
🔗 *Short Link Generator*

Pilih domain yang ingin digunakan:

━━━━━━━━━━━━━━━━━
🌐 *Default Domain*
   Domain: {domain_info}
   Gratis untuk semua user

🎯 *Custom Domain/Subdomain*
   Pakai domain sendiri atau
   request subdomain gratis
   
📱 *TinyURL*
   Link via TinyURL.com
   Tidak perlu domain

━━━━━━━━━━━━━━━━━
Ketik /cancel untuk batal
    """
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # Clear state
    context.user_data['state'] = None

async def handle_shortlink_default(query, context: ContextTypes.DEFAULT_TYPE):
    """User pilih default domain"""
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    default_domain = Config.DEFAULT_DOMAIN
    subdomain = Config.DEFAULT_SUBDOMAIN
    
    if default_domain:
        full_domain = f"{subdomain}.{default_domain}"
        message = f"""
🌐 *Short Link - Default Domain*

━━━━━━━━━━━━━━━━━━━━━━
📍 *Subdomain Aktif*
   `{subdomain}`

🌐 *Domain Utama*
   `{default_domain}`

🔗 *Full URL Domain*
   `{full_domain}`

✅ *Status*
   Aktif dan siap digunakan

⚡ *Fitur*
   • SSL/TLS Enabled
   • Cloudflare Protected
   • Unlimited Short Links
   • Custom Alias Support
   • Analytics & Stats

━━━━━━━━━━━━━━━━━━━━━━

📤 *Cara Pakai:*
Silakan kirim URL yang ingin diperpendek.
Contoh: `https://example.com/long/url`

Setelah kirim URL, kamu bisa pilih:
• Random code (otomatis)
• Custom alias (pilih sendiri)

━━━━━━━━━━━━━━━━━━━━━━
Ketik /cancel untuk batal
        """
        context.user_data['state'] = 'waiting_shortlink_default'
        context.user_data['domain_choice'] = 'default'
    else:
        message = """
⚠️ *Default Domain Belum Tersedia*

Domain default belum dikonfigurasi.
Silakan pilih opsi lain:

• 🎯 Custom Domain (hubungi admin)
• 📱 TinyURL (langsung pakai)
        """
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_alias_random(query, context: ContextTypes.DEFAULT_TYPE):
    """User pilih random code - langsung generate short link"""
    url = context.user_data.get('pending_url')
    
    if not url:
        await query.edit_message_text(
            "❌ Error: URL tidak ditemukan. Silakan mulai lagi dari /start",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")
            ]])
        )
        return
    
    user_id = str(query.from_user.id)
    
    await query.edit_message_text(
        "⏳ Sedang membuat short link dengan random code...",
        parse_mode='Markdown'
    )
    
    try:
        # Create short link dengan random code (no custom alias)
        result = db.create_short_link(
            original_url=url,
            custom_alias=None,  # Random code
            domain='default',
            user_id=user_id
        )
        
        if result['success']:
            domain_name = f"{Config.DEFAULT_SUBDOMAIN}.{Config.DEFAULT_DOMAIN}"
            short_code = result['short_code']
            short_url = f"https://{domain_name}/{short_code}"
            
            url_preview = url if len(url) <= 50 else url[:47] + "..."
            
            message = f"""
✅ *Short Link Berhasil Dibuat!*

━━━━━━━━━━━━━━━━━
🔗 *Short URL:*
`{short_url}`

📊 *Original URL:*
{url_preview}

🎲 *Code:* `{short_code}` (Random)

━━━━━━━━━━━━━━━━━
✨ Link sudah siap digunakan!
            """
            
            keyboard = [
                [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
            ]
            
            await query.edit_message_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                f"❌ Gagal membuat short link!\n\n{result.get('error', 'Unknown error')}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")
                ]])
            )
    
    except Exception as e:
        await query.edit_message_text(
            f"❌ Error: {str(e)}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")
            ]])
        )
    
    # Clear state
    context.user_data['state'] = None
    context.user_data['pending_url'] = None

async def handle_alias_custom(query, context: ContextTypes.DEFAULT_TYPE):
    """User pilih custom alias - minta input alias"""
    url = context.user_data.get('pending_url')
    
    if not url:
        await query.edit_message_text(
            "❌ Error: URL tidak ditemukan. Silakan mulai lagi dari /start",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")
            ]])
        )
        return
    
    url_preview = url if len(url) <= 50 else url[:47] + "..."
    
    message = f"""
✏️ *Custom Alias*

━━━━━━━━━━━━━━━━━
📌 *URL:*
{url_preview}

━━━━━━━━━━━━━━━━━

Silakan kirim alias yang Anda inginkan.

*Contoh:*
• `googlejhosua`
• `FormDaftar`
• `LinkBioKu`

*Hasil:*
`s.jhopan.my.id/googlejhosua`

*Aturan:*
• Minimal 3 karakter
• Hanya huruf, angka, - dan _
• Belum dipakai user lain

━━━━━━━━━━━━━━━━━
Ketik /cancel untuk batal
    """
    
    context.user_data['state'] = 'waiting_custom_alias'
    
    keyboard = [
        [InlineKeyboardButton("❌ Cancel", callback_data="back_to_main")]
    ]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_shortlink_custom(query, context: ContextTypes.DEFAULT_TYPE):
    """User mau pakai custom domain - bisa request subdomain atau custom domain"""
    keyboard = [
        [
            InlineKeyboardButton("🎁 Request Subdomain Gratis", callback_data="request_subdomain")
        ],
        [
            InlineKeyboardButton("🌐 Pakai Domain Sendiri", callback_data="custom_domain_own")
        ],
        [
            InlineKeyboardButton("📩 Hubungi Admin", url="https://t.me/jhopan_05")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="menu_shortlink")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    default_domain = Config.DEFAULT_DOMAIN if Config.DEFAULT_DOMAIN else "jhopan.my.id"
    
    message = f"""
🎯 *Custom Domain / Subdomain*

━━━━━━━━━━━━━━━━━
*Pilihan Tersedia:*

🎁 *Subdomain Gratis*
   Format: `nama-anda.{default_domain}`
   • Gratis selamanya
   • Setup 1-2 hari
   • SSL/TLS included

🌐 *Custom Domain Sendiri*
   Format: `link.domain-anda.com`
   • Pakai domain sendiri
   • Butuh akses Cloudflare

━━━━━━━━━━━━━━━━━
👤 *Admin:* @jhopan_05

💡 *Note:*
Subdomain gratis unlimited via Cloudflare!

Pilih opsi di bawah untuk melanjutkan:
    """
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_request_subdomain(query, context: ContextTypes.DEFAULT_TYPE):
    """Handle request subdomain gratis"""
    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data="shortlink_custom")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    default_domain = Config.DEFAULT_DOMAIN if Config.DEFAULT_DOMAIN else "jhopan.my.id"
    user_id = query.from_user.id
    username = query.from_user.username or "User"
    
    message = f"""
🎁 *Request Subdomain Gratis*

━━━━━━━━━━━━━━━━━
Silakan kirim nama subdomain yang Anda inginkan.

*Format:*
Hanya nama subdomain (tanpa domain utama)

*Contoh:*
`mybrand`  → `mybrand.{default_domain}`
`linkku`   → `linkku.{default_domain}`
`promo`    → `promo.{default_domain}`

━━━━━━━━━━━━━━━━━
*Rules:*
• Huruf kecil saja (a-z)
• Boleh angka (0-9)
• Boleh tanda hubung (-)
• Minimal 3 karakter
• Maksimal 20 karakter

*Contoh VALID:*
✅ `mylink`
✅ `promo2024`
✅ `my-brand`

*Contoh TIDAK VALID:*
❌ `MyLink` (ada huruf besar)
❌ `my_link` (pakai underscore)
❌ `ab` (terlalu pendek)

━━━━━━━━━━━━━━━━━
📩 *Request akan dikirim ke admin:*
@jhopan_05

Ketik /cancel untuk batal
    """
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # Set state untuk menunggu input subdomain
    context.user_data['state'] = 'waiting_subdomain_request'
    context.user_data['user_id'] = user_id
    context.user_data['username'] = username

async def handle_custom_domain_own(query, context: ContextTypes.DEFAULT_TYPE):
    """Handle custom domain sendiri - perlu setup DNS"""
    keyboard = [
        [
            InlineKeyboardButton("📩 Hubungi Admin", url="https://t.me/jhopan_05")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="shortlink_custom")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
🌐 *Custom Domain Sendiri*

━━━━━━━━━━━━━━━━━
Untuk menggunakan domain Anda sendiri, ikuti langkah berikut:

*Persyaratan:*
1️⃣ Punya domain sendiri (dari Namecheap, GoDaddy, dll)
2️⃣ Domain sudah terhubung ke Cloudflare
3️⃣ Akses ke dashboard Cloudflare

━━━━━━━━━━━━━━━━━
*Langkah Setup:*

*A. Setup DNS (di Cloudflare):*
1. Login ke dashboard.cloudflare.com
2. Pilih domain Anda
3. Masuk ke menu "DNS" → "Records"
4. Tambah record CNAME:
   • Type: `CNAME`
   • Name: `link` (atau subdomain lain)
   • Target: `s.jhopan.my.id`
   • Proxy: Enabled (orange cloud)
5. Save

*B. Hubungi Admin:*
Kirim info berikut ke @jhopan_05:
```
Domain: link.domain-anda.com
User ID: [akan otomatis]
Tujuan: Short link bot
```

━━━━━━━━━━━━━━━━━
*Estimasi Waktu:*
• DNS propagation: 5-10 menit
• Admin setup: 1-2 hari kerja

*Biaya:*
• Gratis (gunakan domain Anda)

Klik "📩 Hubungi Admin" untuk bantuan!
    """
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_shortlink_tinyurl(query, context: ContextTypes.DEFAULT_TYPE):
    """User pilih TinyURL"""
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
📱 *Short Link - TinyURL*

Silakan kirim URL yang ingin diperpendek.
Link akan dibuat via TinyURL.com

*Format:*
Kirim URL saja → Random code
`https://example.com/long/url`

Kirim URL + spasi + alias → Custom alias (jika tersedia)
`https://example.com myalias`

*Contoh:*
`https://forms.google.com/form/123456`
Hasil: `tinyurl.com/abc123`

━━━━━━━━━━━━━━━━━
⚠️ *Note:*
• Analytics hanya di TinyURL
• Tidak ada custom domain
• Gratis dan cepat

Ketik /cancel untuk batal
    """
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    context.user_data['state'] = 'waiting_shortlink_tinyurl'
    context.user_data['domain_choice'] = 'tinyurl'

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
