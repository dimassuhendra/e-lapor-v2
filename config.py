import os

class Config:
    # ----------------------------------------------------
    # Konfigurasi Dasar Flask & Keamanan
    # ----------------------------------------------------
    
    # SECRET_KEY haruslah string acak yang panjang dan kompleks. 
    # Gunakan untuk mengamankan session dan fitur Flask lainnya. 
    # PENTING: Ganti string ini dengan milik Anda sendiri dan jaga kerahasiaannya!
    SECRET_KEY = os.environ.get('k3y_r4h4s14_3l4p0r_b4nd4r_l4mpung_2025_5n9hA2qXzYpW8vT7uR6e')

    # ----------------------------------------------------
    # Konfigurasi Database MySQL
    # ----------------------------------------------------
    
    # Kredensial koneksi database
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'  # Ganti
    MYSQL_PASSWORD = '' # Ganti
    MYSQL_DB = 'db_lapor'
    
    # Opsi lain untuk Flask-MySQLdb
    MYSQL_CURSORCLASS = 'DictCursor' # Opsional: Agar hasil query berupa dictionary

    # ----------------------------------------------------
    # Konfigurasi Peta (OpenStreetMap/Leaflet)
    # ----------------------------------------------------
    
    # Koordinat pusat default (Contoh: Pusat Kota Bandar Lampung)
    # Digunakan untuk tampilan peta awal.
    DEFAULT_MAP_LAT = -5.4219  # Latitude Bandar Lampung
    DEFAULT_MAP_LONG = 105.2783 # Longitude Bandar Lampung
    DEFAULT_MAP_ZOOM = 12       # Level zoom default
    
    # URL Tile Server OpenStreetMap
    OSM_TILE_URL = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'