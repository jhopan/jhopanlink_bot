"""
Database Manager untuk Short Link System
"""
import sqlite3
import random
import string
from datetime import datetime
from typing import Optional, Dict, List
import os

class DatabaseManager:
    """Manager untuk database operations"""
    
    def __init__(self, db_path: str = "shortlink.db"):
        """
        Initialize database manager
        
        Args:
            db_path: Path ke database SQLite
        """
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table untuk short links
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS short_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code TEXT NOT NULL UNIQUE,
                original_url TEXT NOT NULL,
                custom_alias TEXT,
                domain TEXT DEFAULT 'default',
                clicks INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # Table untuk domains (custom domain users)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_domains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL UNIQUE,
                user_id TEXT NOT NULL,
                telegram_username TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table untuk click analytics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS click_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code TEXT NOT NULL,
                clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                referer TEXT
            )
        ''')
        
        # Index untuk performa
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_short_code ON short_links(short_code)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_domain ON short_links(domain)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_custom_alias ON short_links(custom_alias)')
        
        conn.commit()
        conn.close()
        
        print("✅ Database initialized!")
    
    def generate_short_code(self, length: int = 6) -> str:
        """
        Generate random short code
        
        Args:
            length: Panjang kode
            
        Returns:
            Random short code
        """
        characters = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choice(characters) for _ in range(length))
            # Check if code already exists
            if not self.get_link_by_code(code):
                return code
    
    def create_short_link(
        self, 
        original_url: str, 
        custom_alias: Optional[str] = None,
        domain: str = 'default',
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Create short link
        
        Args:
            original_url: URL asli
            custom_alias: Custom alias (opsional)
            domain: Domain untuk link ini
            user_id: Telegram user ID
            
        Returns:
            Dict dengan info short link
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Generate short code atau gunakan custom alias
            if custom_alias:
                # Validasi custom alias tidak ada
                cursor.execute(
                    'SELECT id FROM short_links WHERE custom_alias = ? AND domain = ?',
                    (custom_alias, domain)
                )
                if cursor.fetchone():
                    conn.close()
                    return {
                        'success': False,
                        'error': f'Alias "{custom_alias}" sudah digunakan untuk domain ini!'
                    }
                short_code = custom_alias
            else:
                short_code = self.generate_short_code()
            
            # Insert ke database
            cursor.execute('''
                INSERT INTO short_links 
                (short_code, original_url, custom_alias, domain, created_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (short_code, original_url, custom_alias, domain, user_id))
            
            conn.commit()
            link_id = cursor.lastrowid
            
            conn.close()
            
            return {
                'success': True,
                'id': link_id,
                'short_code': short_code,
                'original_url': original_url,
                'domain': domain,
                'custom_alias': custom_alias
            }
        
        except sqlite3.IntegrityError as e:
            conn.close()
            return {
                'success': False,
                'error': f'Error: {str(e)}'
            }
    
    def get_link_by_code(self, short_code: str, domain: str = 'default') -> Optional[Dict]:
        """
        Get link by short code
        
        Args:
            short_code: Short code
            domain: Domain
            
        Returns:
            Dict dengan info link atau None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, short_code, original_url, custom_alias, domain, clicks, created_at, is_active
            FROM short_links
            WHERE (short_code = ? OR custom_alias = ?) AND domain = ? AND is_active = 1
        ''', (short_code, short_code, domain))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'short_code': row[1],
                'original_url': row[2],
                'custom_alias': row[3],
                'domain': row[4],
                'clicks': row[5],
                'created_at': row[6],
                'is_active': row[7]
            }
        
        return None
    
    def increment_click(self, short_code: str, domain: str = 'default', 
                       ip_address: str = None, user_agent: str = None, 
                       referer: str = None):
        """
        Increment click counter dan log
        
        Args:
            short_code: Short code
            domain: Domain
            ip_address: IP address pengunjung
            user_agent: User agent
            referer: Referer
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Increment counter
        cursor.execute('''
            UPDATE short_links 
            SET clicks = clicks + 1 
            WHERE (short_code = ? OR custom_alias = ?) AND domain = ?
        ''', (short_code, short_code, domain))
        
        # Log click
        cursor.execute('''
            INSERT INTO click_logs (short_code, ip_address, user_agent, referer)
            VALUES (?, ?, ?, ?)
        ''', (short_code, ip_address, user_agent, referer))
        
        conn.commit()
        conn.close()
    
    def add_custom_domain(self, domain: str, user_id: str, username: str = None) -> Dict:
        """
        Add custom domain untuk user
        
        Args:
            domain: Domain name
            user_id: Telegram user ID
            username: Telegram username
            
        Returns:
            Dict dengan status
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO custom_domains (domain, user_id, telegram_username)
                VALUES (?, ?, ?)
            ''', (domain, user_id, username))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'domain': domain
            }
        
        except sqlite3.IntegrityError:
            conn.close()
            return {
                'success': False,
                'error': 'Domain sudah terdaftar!'
            }
    
    def get_user_links(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Get links created by user
        
        Args:
            user_id: Telegram user ID
            limit: Jumlah maksimal hasil
            
        Returns:
            List of links
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT short_code, original_url, custom_alias, domain, clicks, created_at
            FROM short_links
            WHERE created_by = ? AND is_active = 1
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        links = []
        for row in rows:
            links.append({
                'short_code': row[0],
                'original_url': row[1],
                'custom_alias': row[2],
                'domain': row[3],
                'clicks': row[4],
                'created_at': row[5]
            })
        
        return links
    
    def get_stats(self, user_id: Optional[str] = None) -> Dict:
        """
        Get statistics
        
        Args:
            user_id: Filter by user (opsional)
            
        Returns:
            Dict dengan stats
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('''
                SELECT COUNT(*), SUM(clicks)
                FROM short_links
                WHERE created_by = ? AND is_active = 1
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT COUNT(*), SUM(clicks)
                FROM short_links
                WHERE is_active = 1
            ''')
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            'total_links': row[0] or 0,
            'total_clicks': row[1] or 0
        }
    
    def delete_link(self, short_code: str, user_id: str, domain: str = 'default') -> bool:
        """
        Delete/deactivate link
        
        Args:
            short_code: Short code to delete
            user_id: User ID (untuk validasi ownership)
            domain: Domain
            
        Returns:
            True jika berhasil
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE short_links
            SET is_active = 0
            WHERE (short_code = ? OR custom_alias = ?) 
            AND domain = ? 
            AND created_by = ?
        ''', (short_code, short_code, domain, user_id))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
    
    # Admin methods
    def get_total_links(self) -> int:
        """Get total links count"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM short_links WHERE is_active = 1')
        result = cursor.fetchone()[0]
        conn.close()
        return result
    
    def get_total_clicks(self) -> int:
        """Get total clicks count"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT SUM(clicks) FROM short_links WHERE is_active = 1')
        result = cursor.fetchone()[0] or 0
        conn.close()
        return result
    
    def get_total_users(self) -> int:
        """Get total unique users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(DISTINCT created_by) FROM short_links WHERE is_active = 1')
        result = cursor.fetchone()[0]
        conn.close()
        return result
    
    def get_total_domains(self) -> int:
        """Get total custom domains"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM custom_domains')
        result = cursor.fetchone()[0]
        conn.close()
        return result
    
    def get_all_domains(self, limit: int = 50) -> List[Dict]:
        """Get all custom domains"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT domain, user_id, username, added_at
            FROM custom_domains
            ORDER BY added_at DESC
            LIMIT ?
        ''', (limit,))
        
        domains = []
        for row in cursor.fetchall():
            domains.append({
                'domain': row[0],
                'user_id': row[1],
                'username': row[2],
                'added_at': row[3]
            })
        
        conn.close()
        return domains
    
    def get_recent_links(self, limit: int = 10) -> List[Dict]:
        """Get recent links"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT short_code, original_url, custom_alias, domain, clicks, created_by, created_at
            FROM short_links
            WHERE is_active = 1
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        links = []
        for row in cursor.fetchall():
            links.append({
                'short_code': row[0],
                'original_url': row[1],
                'custom_alias': row[2],
                'domain': row[3],
                'clicks': row[4],
                'user_id': row[5],
                'created_at': row[6]
            })
        
        conn.close()
        return links
    
    def get_active_users(self, limit: int = 10) -> List[Dict]:
        """Get active users with stats"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT created_by, COUNT(*) as link_count, SUM(clicks) as total_clicks
            FROM short_links
            WHERE is_active = 1
            GROUP BY created_by
            ORDER BY link_count DESC
            LIMIT ?
        ''', (limit,))
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'user_id': row[0],
                'link_count': row[1],
                'total_clicks': row[2] or 0
            })
        
        conn.close()
        return users
