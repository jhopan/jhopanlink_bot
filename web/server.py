"""
Flask Web Server untuk Short Link Redirect
"""
from flask import Flask, redirect, request, jsonify, render_template_string
from flask_cors import CORS
from database.db_manager import DatabaseManager
from config.config import Config
import os

app = Flask(__name__)
CORS(app)

# Initialize database
db = DatabaseManager()

# HTML Template untuk 404
NOT_FOUND_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>404 - Link Not Found</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            text-align: center;
            padding: 40px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        h1 { font-size: 72px; margin: 0; }
        p { font-size: 24px; }
        a { color: #fff; text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>404</h1>
        <p>😔 Link tidak ditemukan</p>
        <p style="font-size: 16px; margin-top: 20px;">
            Link yang Anda cari tidak ada atau sudah tidak aktif.
        </p>
    </div>
</body>
</html>
"""

# HTML Template untuk homepage
HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ShortLink Service</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            width: 100%;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 32px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 16px;
        }
        .stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-number {
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .stat-label {
            font-size: 14px;
            opacity: 0.9;
        }
        .features {
            margin-top: 30px;
        }
        .feature {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        .feature-icon {
            font-size: 24px;
            margin-right: 15px;
        }
        .feature-text {
            flex: 1;
        }
        .feature-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 3px;
        }
        .feature-desc {
            font-size: 14px;
            color: #666;
        }
        .cta {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            text-align: center;
        }
        .cta-title {
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        .cta-text {
            font-size: 14px;
            color: #666;
            margin-bottom: 15px;
        }
        .telegram-link {
            display: inline-block;
            background: #0088cc;
            color: white;
            padding: 12px 30px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: bold;
            transition: transform 0.2s;
        }
        .telegram-link:hover {
            transform: scale(1.05);
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            color: #999;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 ShortLink Service</h1>
        <p class="subtitle">Powered by Telegram Bot</p>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number">{{ stats.total_links }}</div>
                <div class="stat-label">Total Links</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{{ stats.total_clicks }}</div>
                <div class="stat-label">Total Clicks</div>
            </div>
        </div>
        
        <div class="features">
            <div class="feature">
                <div class="feature-icon">⚡</div>
                <div class="feature-text">
                    <div class="feature-title">Cepat & Mudah</div>
                    <div class="feature-desc">Perpendek link dalam hitungan detik</div>
                </div>
            </div>
            
            <div class="feature">
                <div class="feature-icon">🎨</div>
                <div class="feature-text">
                    <div class="feature-title">Custom Alias</div>
                    <div class="feature-desc">Buat link dengan nama yang Anda inginkan</div>
                </div>
            </div>
            
            <div class="feature">
                <div class="feature-icon">🌐</div>
                <div class="feature-text">
                    <div class="feature-title">Multi Domain</div>
                    <div class="feature-desc">Support custom domain Anda sendiri</div>
                </div>
            </div>
            
            <div class="feature">
                <div class="feature-icon">📊</div>
                <div class="feature-text">
                    <div class="feature-title">Analytics</div>
                    <div class="feature-desc">Track jumlah klik untuk setiap link</div>
                </div>
            </div>
        </div>
        
        <div class="cta">
            <div class="cta-title">Mulai Sekarang!</div>
            <div class="cta-text">Gunakan bot Telegram kami untuk membuat short link</div>
            <a href="#" class="telegram-link">🤖 Open Telegram Bot</a>
        </div>
        
        <div class="footer">
            <p>Made with ❤️ | Version {{ version }}</p>
        </div>
    </div>
</body>
</html>
"""

def get_domain_from_request():
    """Extract domain dari request"""
    host = request.host
    # Remove port if exists
    domain = host.split(':')[0]
    return domain

@app.route('/')
def home():
    """Homepage dengan stats"""
    stats = db.get_stats()
    return render_template_string(
        HOME_TEMPLATE, 
        stats=stats,
        version=Config.BOT_VERSION
    )

@app.route('/<path:short_code>')
def redirect_link(short_code):
    """
    Redirect short link ke URL asli
    
    Args:
        short_code: Short code atau custom alias
    """
    # Get domain dari request
    domain = get_domain_from_request()
    
    print(f"🔍 Redirect request: domain={domain}, code={short_code}")
    
    # Get link dari database
    link = db.get_link_by_code(short_code, domain)
    
    if not link:
        # Coba dengan default domain
        print(f"   Trying with default domain...")
        link = db.get_link_by_code(short_code, 'default')
    
    if link:
        print(f"✅ Link found: {link['original_url']}")
        # Log click dengan info
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', '')
        referer = request.headers.get('Referer', '')
        
        db.increment_click(
            short_code, 
            link['domain'],
            ip_address=ip_address,
            user_agent=user_agent,
            referer=referer
        )
        
        # Redirect ke URL asli
        return redirect(link['original_url'], code=302)
    else:
        # Link tidak ditemukan
        print(f"❌ Link not found: domain={domain}, code={short_code}")
        return render_template_string(NOT_FOUND_TEMPLATE), 404

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'shortlink',
        'version': Config.BOT_VERSION
    })

@app.route('/api/stats')
def api_stats():
    """API endpoint untuk stats"""
    stats = db.get_stats()
    return jsonify(stats)

@app.route('/api/create', methods=['POST'])
def api_create_link():
    """
    API endpoint untuk create link (untuk bot)
    
    Request body:
    {
        "url": "https://example.com",
        "alias": "custom-name",  // optional
        "domain": "jhopan.id",   // optional
        "user_id": "123456"      // optional
    }
    """
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({
            'success': False,
            'error': 'URL required'
        }), 400
    
    result = db.create_short_link(
        original_url=data['url'],
        custom_alias=data.get('alias'),
        domain=data.get('domain', 'default'),
        user_id=data.get('user_id')
    )
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400

@app.route('/api/link/<short_code>')
def api_get_link(short_code):
    """
    Get link info by short code
    """
    domain = request.args.get('domain', 'default')
    link = db.get_link_by_code(short_code, domain)
    
    if link:
        return jsonify(link)
    else:
        return jsonify({
            'error': 'Link not found'
        }), 404

def run_server(host='0.0.0.0', port=5000, debug=False):
    """
    Run Flask server
    
    Args:
        host: Host address
        port: Port number
        debug: Debug mode
    """
    print("=" * 50)
    print(f"🌐 Starting Web Server on {host}:{port}")
    print("=" * 50)
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_server(
        host=Config.WEB_SERVER_HOST,
        port=Config.WEB_SERVER_PORT,
        debug=True
    )
