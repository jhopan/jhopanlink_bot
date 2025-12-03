"""
Command handlers untuk bot
"""
from telegram import Update
from telegram.ext import ContextTypes
from database.db_manager import DatabaseManager
from config.config import Config

# Initialize database
db = DatabaseManager()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /start"""
    welcome_message = f"""
🤖 *Selamat datang di ShortLink & QR Code Bot!*

Bot ini dapat membantu Anda:
✅ Membuat Short Link dari URL panjang (GRATIS!)
✅ Custom alias untuk link yang mudah diingat
✅ Support custom domain Anda sendiri
✅ Generate QR Code dari teks atau URL
✅ Analytics & tracking clicks

📝 *Cara Penggunaan:*

*Short Link (Random):*
`/short https://example.com/very/long/url`

*Short Link (Custom Alias):*
`/short https://forms.google.com DaftarPengurus2025`
→ Jadi: `{Config.DEFAULT_SUBDOMAIN}.{Config.DEFAULT_DOMAIN}/DaftarPengurus2025`

*Dengan Domain Custom:*
`/short https://forms.google.com pmkft/Daftar jhopan.id`

*QR Code:*
`/qr https://example.com`

*Short Link + QR Code:*
`/both https://example.com CustomName`

*Lihat Stats & Link Anda:*
`/mystats` - Lihat semua link Anda
`/mylinks` - List link terbaru

━━━━━━━━━━━━━━━━━
Ketik `/help` untuk panduan lengkap! 🚀
    """
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /help"""
    help_message = """
📖 *Panduan Penggunaan Bot*

━━━━━━━━━━━━━━━━━
*1️⃣ Short Link*
━━━━━━━━━━━━━━━━━
Memperpendek URL panjang menjadi URL pendek

*Format:*
`/short <URL>`

*Contoh:*
`/short https://www.example.com/very/long/url/path`

Atau langsung kirim URL tanpa command!

━━━━━━━━━━━━━━━━━
*2️⃣ QR Code*
━━━━━━━━━━━━━━━━━
Generate QR Code dari teks atau URL

*Format:*
`/qr <teks atau URL>`

*Contoh:*
`/qr https://example.com`
`/qr Halo, ini QR Code saya!`
`/qr +628123456789`

━━━━━━━━━━━━━━━━━
*3️⃣ Both (Short Link + QR Code)*
━━━━━━━━━━━━━━━━━
Membuat short link dan QR code sekaligus

*Format:*
`/both <URL>`

*Contoh:*
`/both https://www.example.com/very/long/url`

━━━━━━━━━━━━━━━━━
*📌 Tips:*
• URL otomatis ditambahkan https:// jika belum ada
• QR Code berformat PNG resolusi tinggi
• Short link menggunakan layanan gratis yang reliable

*Command Lain:*
/start - Mulai bot
/help - Bantuan
/about - Tentang bot

━━━━━━━━━━━━━━━━━
Butuh bantuan? Hubungi developer! 💬
    """
    
    await update.message.reply_text(
        help_message,
        parse_mode='Markdown'
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /about"""
    stats = db.get_stats()
    
    about_message = f"""
ℹ️ *Tentang Bot*

*Nama:* ShortLink & QR Code Bot
*Versi:* {Config.BOT_VERSION}
*Dibuat:* Desember 2025

━━━━━━━━━━━━━━━━━
*Fitur Utama:*
✨ Short Link Generator (Custom Domain!)
✨ Custom Alias untuk Link
✨ QR Code Generator
✨ Click Analytics & Tracking
✨ Multi-Domain Support
✨ 100% Gratis & Open Source

━━━━━━━━━━━━━━━━━
*Teknologi:*
• Python Telegram Bot
• Flask Web Server
• SQLite Database
• Cloudflare Tunnel
• Custom Domain Support

━━━━━━━━━━━━━━━━━
*Stats Global:*
📊 Total Links: {stats['total_links']}
👆 Total Clicks: {stats['total_clicks']}

━━━━━━━━━━━━━━━━━
*Privacy:*
🔒 Data tersimpan lokal di server
🔒 Tidak ada tracking identitas pribadi
🔒 Open source & dapat di-audit

Terima kasih sudah menggunakan bot ini! 🙏
    """
    
    await update.message.reply_text(
        about_message,
        parse_mode='Markdown'
    )

async def mystats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /mystats - Stats user"""
    user_id = str(update.effective_user.id)
    stats = db.get_stats(user_id=user_id)
    
    stats_message = f"""
📊 *Statistik Anda*

━━━━━━━━━━━━━━━━━
🔗 *Total Link Dibuat:* {stats['total_links']}
👆 *Total Klik:* {stats['total_clicks']}
📈 *Rata-rata Klik/Link:* {stats['total_clicks'] // stats['total_links'] if stats['total_links'] > 0 else 0}

━━━━━━━━━━━━━━━━━
💡 *Tip:* Gunakan `/mylinks` untuk lihat daftar link Anda!
    """
    
    await update.message.reply_text(
        stats_message,
        parse_mode='Markdown'
    )

async def mylinks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /mylinks - List user links"""
    user_id = str(update.effective_user.id)
    links = db.get_user_links(user_id, limit=10)
    
    if not links:
        await update.message.reply_text(
            "❌ *Anda belum membuat link apapun!*\n\n"
            "Gunakan `/short <URL>` untuk membuat link pertama Anda! 🚀",
            parse_mode='Markdown'
        )
        return
    
    message = "📋 *Link Terbaru Anda:*\n\n"
    
    for idx, link in enumerate(links, 1):
        domain_name = link['domain'] if link['domain'] != 'default' else f"{Config.DEFAULT_SUBDOMAIN}.{Config.DEFAULT_DOMAIN}"
        short_code = link['custom_alias'] or link['short_code']
        short_url = f"https://{domain_name}/{short_code}"
        
        message += f"*{idx}.* `{short_url}`\n"
        message += f"   📊 {link['clicks']} clicks\n"
        message += f"   🔗 {link['original_url'][:40]}...\n\n"
    
    message += "━━━━━━━━━━━━━━━━━\n"
    message += f"Menampilkan {len(links)} link terbaru\n"
    message += "Gunakan `/mystats` untuk statistik lengkap!"
    
    await update.message.reply_text(
        message,
        parse_mode='Markdown'
    )

async def adddomain_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /adddomain - Add custom domain"""
    if not context.args:
        await update.message.reply_text(
            "❌ *Format salah!*\n\n"
            "*Gunakan:* `/adddomain <domain>`\n\n"
            "*Contoh:*\n"
            "`/adddomain jhopan.id`\n"
            "`/adddomain jeje.id`\n\n"
            "━━━━━━━━━━━━━━━━━\n"
            "📌 *Catatan:*\n"
            "• Domain harus sudah pointing ke server\n"
            "• Setup DNS di Cloudflare dulu\n"
            "• Setelah add, bisa pakai di `/short`",
            parse_mode='Markdown'
        )
        return
    
    domain = context.args[0].lower().strip()
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "unknown"
    
    result = db.add_custom_domain(domain, user_id, username)
    
    if result['success']:
        await update.message.reply_text(
            f"✅ *Domain berhasil ditambahkan!*\n\n"
            f"🌐 *Domain:* `{domain}`\n\n"
            "━━━━━━━━━━━━━━━━━\n"
            "*Cara Pakai:*\n"
            f"`/short https://example.com alias {domain}`\n\n"
            "Link Anda akan menjadi:\n"
            f"`{domain}/alias`",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"❌ *Gagal menambahkan domain!*\n\n"
            f"Error: {result.get('error', 'Unknown error')}",
            parse_mode='Markdown'
        )

