"""
Utility untuk membuat QR Code
"""
import qrcode
from io import BytesIO
from PIL import Image

class QRCodeGenerator:
    """Generator untuk membuat QR Code"""
    
    def __init__(self, box_size=10, border=4, error_correction='H'):
        """
        Initialize QR Code generator
        
        Args:
            box_size: Ukuran setiap box dalam QR code
            border: Ukuran border (minimum 4)
            error_correction: Level error correction (L, M, Q, H)
        """
        self.box_size = box_size
        self.border = border
        
        # Mapping error correction
        error_levels = {
            'L': qrcode.constants.ERROR_CORRECT_L,
            'M': qrcode.constants.ERROR_CORRECT_M,
            'Q': qrcode.constants.ERROR_CORRECT_Q,
            'H': qrcode.constants.ERROR_CORRECT_H
        }
        self.error_correction = error_levels.get(error_correction, qrcode.constants.ERROR_CORRECT_H)
    
    def generate(self, data: str, fill_color='black', back_color='white') -> BytesIO:
        """
        Generate QR Code dari data
        
        Args:
            data: Data yang akan di-encode ke QR Code
            fill_color: Warna foreground
            back_color: Warna background
            
        Returns:
            BytesIO object berisi image QR Code
        """
        # Buat QR Code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=self.error_correction,
            box_size=self.box_size,
            border=self.border,
        )
        
        # Tambahkan data
        qr.add_data(data)
        qr.make(fit=True)
        
        # Buat image
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        
        # Convert ke BytesIO
        bio = BytesIO()
        bio.name = 'qrcode.png'
        img.save(bio, 'PNG')
        bio.seek(0)
        
        return bio
    
    def generate_with_logo(self, data: str, logo_path: str = None) -> BytesIO:
        """
        Generate QR Code dengan logo di tengah
        
        Args:
            data: Data yang akan di-encode
            logo_path: Path ke file logo
            
        Returns:
            BytesIO object berisi image QR Code dengan logo
        """
        # Generate QR Code dasar
        qr = qrcode.QRCode(
            version=1,
            error_correction=self.error_correction,
            box_size=self.box_size,
            border=self.border,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        
        # Jika ada logo, tambahkan di tengah
        if logo_path:
            try:
                logo = Image.open(logo_path)
                
                # Hitung ukuran logo (maksimal 1/4 dari QR code)
                qr_width, qr_height = img.size
                logo_size = min(qr_width, qr_height) // 4
                
                # Resize logo
                logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                
                # Hitung posisi tengah
                logo_pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
                
                # Paste logo
                img.paste(logo, logo_pos)
            except Exception as e:
                print(f"Error menambahkan logo: {e}")
        
        # Convert ke BytesIO
        bio = BytesIO()
        bio.name = 'qrcode.png'
        img.save(bio, 'PNG')
        bio.seek(0)
        
        return bio
