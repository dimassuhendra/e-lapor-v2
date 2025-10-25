# utils/map_helper.py

from flask import current_app

def get_map_config():
    """
    Mengambil konfigurasi peta dari config.py dan menyediakannya dalam bentuk dictionary 
    untuk digunakan oleh Jinja/JavaScript di frontend.
    """
    # Mengambil nilai konfigurasi yang sudah didefinisikan di config.py
    try:
        config = {
            'DEFAULT_LAT': current_app.config.get('DEFAULT_MAP_LAT'),
            'DEFAULT_LONG': current_app.config.get('DEFAULT_MAP_LONG'),
            'DEFAULT_ZOOM': current_app.config.get('DEFAULT_MAP_ZOOM'),
            'TILE_URL': current_app.config.get('OSM_TILE_URL')
        }
    except Exception as e:
        # Jika current_app tidak tersedia (misal saat testing di luar context), gunakan default
        config = {
            'DEFAULT_LAT': -5.4219,
            'DEFAULT_LONG': 105.2783,
            'DEFAULT_ZOOM': 12,
            'TILE_URL': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
        }
        current_app.logger.warning(f"Menggunakan konfigurasi peta default karena error: {e}")
        
    return config

def get_kecamatan_coordinates(kecamatan_id):
    """
    Mengambil koordinat (lat/long) pusat kecamatan dari database 
    untuk memusatkan peta saat form laporan dibuka.
    """
    # Menggunakan model data master yang sudah ada
    from models.master_data_model import get_all_data # Diimpor di sini untuk menghindari circular dependency
    
    conn, cursor = get_all_data('m_kecamatan', 'id_kecamatan', kecamatan_id)
    
    # Fungsi get_all_data mengembalikan list of dicts. Karena kita mencari berdasarkan PK, hasilnya 
    # seharusnya hanya satu atau nol.
    if conn and len(conn) > 0:
        return {'lat': conn[0]['latitude'], 'long': conn[0]['longitude']}
    
    # Jika tidak ditemukan, kembalikan koordinat default kota
    return {
        'lat': current_app.config.get('DEFAULT_MAP_LAT'),
        'long': current_app.config.get('DEFAULT_MAP_LONG')
    }

# CATATAN PENTING: Untuk fungsi get_kecamatan_coordinates, Anda harus memastikan 
# fungsi di master_data_model.py diperbarui agar bisa mengambil data berdasarkan ID.
# Atau, Anda bisa membuat fungsi get_kecamatan_by_id() khusus di master_data_model.py 
# yang lebih efisien.