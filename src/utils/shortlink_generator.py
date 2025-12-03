"""
Utility untuk membuat Short Link
"""
import aiohttp
import requests
from typing import Optional
from urllib.parse import quote

class ShortLinkGenerator:
    """Generator untuk membuat short link"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize Short Link generator
        
        Args:
            api_key: API key untuk TinyURL (opsional)
        """
        self.api_key = api_key
    
    async def shorten_with_tinyurl(self, url: str, alias: str = None) -> Optional[str]:
        """
        Shorten URL menggunakan TinyURL API
        
        Args:
            url: URL yang akan diperpendek
            alias: Custom alias (opsional)
            
        Returns:
            Short URL atau None jika gagal
        """
        if not self.api_key:
            return None
            
        try:
            api_url = "https://api.tinyurl.com/create"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "url": url,
                "domain": "tinyurl.com"
            }
            
            if alias:
                data["alias"] = alias
            
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('data', {}).get('tiny_url')
                    
            return None
        except Exception as e:
            print(f"Error dengan TinyURL: {e}")
            return None
    
    async def shorten_with_isgd(self, url: str) -> Optional[str]:
        """
        Shorten URL menggunakan is.gd (gratis, tanpa API key)
        
        Args:
            url: URL yang akan diperpendek
            
        Returns:
            Short URL atau None jika gagal
        """
        try:
            api_url = f"https://is.gd/create.php?format=simple&url={quote(url)}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        short_url = await response.text()
                        return short_url.strip()
            
            return None
        except Exception as e:
            print(f"Error dengan is.gd: {e}")
            return None
    
    async def shorten_with_vgd(self, url: str) -> Optional[str]:
        """
        Shorten URL menggunakan v.gd (alternatif is.gd)
        
        Args:
            url: URL yang akan diperpendek
            
        Returns:
            Short URL atau None jika gagal
        """
        try:
            api_url = f"https://v.gd/create.php?format=simple&url={quote(url)}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        short_url = await response.text()
                        return short_url.strip()
            
            return None
        except Exception as e:
            print(f"Error dengan v.gd: {e}")
            return None
    
    async def shorten(self, url: str, alias: str = None) -> str:
        """
        Shorten URL dengan prioritas: TinyURL -> is.gd -> v.gd
        
        Args:
            url: URL yang akan diperpendek
            alias: Custom alias (hanya untuk TinyURL)
            
        Returns:
            Short URL atau URL asli jika semua gagal
        """
        # Validasi URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Coba TinyURL jika ada API key
        if self.api_key:
            result = await self.shorten_with_tinyurl(url, alias)
            if result:
                return result
        
        # Coba is.gd
        result = await self.shorten_with_isgd(url)
        if result:
            return result
        
        # Coba v.gd sebagai backup
        result = await self.shorten_with_vgd(url)
        if result:
            return result
        
        # Jika semua gagal, return URL asli
        return url
    
    def shorten_sync(self, url: str) -> str:
        """
        Versi synchronous dari shorten (untuk keperluan testing)
        
        Args:
            url: URL yang akan diperpendek
            
        Returns:
            Short URL atau URL asli jika gagal
        """
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            api_url = f"https://is.gd/create.php?format=simple&url={quote(url)}"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                return response.text.strip()
        except Exception as e:
            print(f"Error: {e}")
        
        return url
