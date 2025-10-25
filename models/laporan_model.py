# models/laporan_model.py

from .__init__ import get_db_cursor, close_db_connection
from flask import current_app
from datetime import datetime

# --- Helper: Pembuatan Nomor Laporan Unik ---
def _generate_nomor_laporan(tipe):
    """
    Menghasilkan nomor laporan unik dengan format: [TIPE]-[YYYYMMDD]-[XXX]
    TIPE: 'LP' untuk Laporan, 'KLH' untuk Keluhan.
    XXX: Nomor urut harian.
    """
    date_str = datetime.now().strftime('%Y%m%d')
    prefix = 'LP' if tipe == 'LAPORAN' else 'KLH'
    
    conn, cursor = get_db_cursor()
    if not cursor:
        return None
    
    # Mencari nomor laporan terakhir untuk hari ini berdasarkan tipe
    nomor_pattern = f"{prefix}-{date_str}-%"
    query = f"""
        SELECT nomor_laporan FROM t_laporan 
        WHERE nomor_laporan LIKE %s 
        ORDER BY nomor_laporan DESC LIMIT 1
    """
    
    # Jika tabel dipisah, ganti query jika tipe='KELUHAN'
    if tipe == 'KELUHAN':
        query = f"""
            SELECT nomor_laporan FROM t_keluhan 
            WHERE nomor_laporan LIKE %s 
            ORDER BY nomor_laporan DESC LIMIT 1
        """
        
    cursor.execute(query, [nomor_pattern])
    last_nomor = cursor.fetchone()
    
    if last_nomor:
        # Ambil angka urut terakhir (XXX) dan tambahkan 1
        last_num_str = last_nomor['nomor_laporan'].split('-')[-1]
        next_num = int(last_num_str) + 1
    else:
        # Jika belum ada laporan/keluhan hari ini, mulai dari 1
        next_num = 1
        
    close_db_connection(conn, cursor)
    
    # Format angka urut menjadi 3 digit (001, 002, ...)
    nomor_unik = f"{prefix}-{date_str}-{next_num:03d}"
    return nomor_unik

# -----------------------------------------------
# FUNGSI INSERT LAPORAN (t_laporan)
# -----------------------------------------------

def insert_laporan(data, foto_path, id_admin_nlp=None):
    """
    Menyimpan data laporan baru ke tabel t_laporan.
    data: dict berisi input dari form (nama_pelapor, deskripsi, id_kecamatan, dll.)
    foto_path: path file foto yang diunggah.
    id_admin_nlp: Placeholder untuk ID admin jika NLP dijalankan otomatis (opsional).
    """
    nomor_laporan = _generate_nomor_laporan('LAPORAN')
    if not nomor_laporan:
        return None, "Gagal menghasilkan nomor laporan unik."

    # Placeholder untuk NLP (akan diisi di FASE 4)
    is_mirip = False
    mirip_id = None 

    conn, cursor = get_db_cursor()
    if not cursor:
        return None, "Gagal koneksi database."

    query = """
        INSERT INTO t_laporan (
            nomor_laporan, id_kategori, nama_pelapor, no_whatsapp, deskripsi, foto_path, 
            nama_jalan, id_kecamatan, id_kelurahan, lat_peta, long_peta, tgl_lapor, 
            is_mirip, mirip_id_laporan
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s)
    """
    params = (
        nomor_laporan, data['id_kategori'], data['nama_pelapor'], data.get('no_whatsapp'), 
        data['deskripsi'], foto_path, data['nama_jalan'], data['id_kecamatan'], 
        data['id_kelurahan'], data['lat_peta'], data['long_peta'], is_mirip, mirip_id
    )
    
    try:
        cursor.execute(query, params)
        laporan_id = cursor.lastrowid
        close_db_connection(conn, cursor, commit=True)
        return nomor_laporan, None
    except Exception as e:
        current_app.logger.error(f"Error insert laporan: {e}")
        close_db_connection(conn, cursor)
        return None, "Terjadi kesalahan saat menyimpan laporan."

# -----------------------------------------------
# FUNGSI INSERT KELUHAN (t_keluhan)
# -----------------------------------------------

def insert_keluhan(data):
    """
    Menyimpan data keluhan baru ke tabel t_keluhan.
    data: dict berisi input dari form (nama_pelapor (opsional), deskripsi, dll.)
    """
    nomor_laporan = _generate_nomor_laporan('KELUHAN')
    if not nomor_laporan:
        return None, "Gagal menghasilkan nomor keluhan unik."

    conn, cursor = get_db_cursor()
    if not cursor:
        return None, "Gagal koneksi database."

    query = """
        INSERT INTO t_keluhan (
            nomor_laporan, id_kategori, nama_pelapor, no_whatsapp, deskripsi, tgl_lapor
        ) VALUES (%s, %s, %s, %s, %s, NOW())
    """
    params = (
        nomor_laporan, data['id_kategori'], data.get('nama_pelapor', None), 
        data.get('no_whatsapp', None), data['deskripsi']
    )
    
    try:
        cursor.execute(query, params)
        close_db_connection(conn, cursor, commit=True)
        return nomor_laporan, None
    except Exception as e:
        current_app.logger.error(f"Error insert keluhan: {e}")
        close_db_connection(conn, cursor)
        return None, "Terjadi kesalahan saat menyimpan keluhan."

# -----------------------------------------------
# FUNGSI LAINNYA (untuk FASE 3 lanjutan)
# -----------------------------------------------

def get_status_by_nomor(nomor):
    """
    Mencari laporan atau keluhan berdasarkan nomor unik untuk pelacakan.
    """
    conn, cursor = get_db_cursor()
    if not cursor: return None

    # Asumsikan nomor_laporan dimulai dengan 'LP' untuk Laporan dan 'KLH' untuk Keluhan
    if nomor.startswith('LP-'):
        table = 't_laporan'
        tipe = 'Laporan'
    elif nomor.startswith('KLH-'):
        table = 't_keluhan'
        tipe = 'Keluhan'
    else:
        return None
    
    query = f"SELECT nomor_laporan, status, tgl_lapor, deskripsi, nama_pelapor FROM {table} WHERE nomor_laporan = %s AND is_deleted = 0"
    
    try:
        cursor.execute(query, [nomor])
        result = cursor.fetchone()
        
        if result:
            result['tipe'] = tipe
        
        close_db_connection(conn, cursor)
        return result
    except Exception as e:
        current_app.logger.error(f"Error fetching status: {e}")
        close_db_connection(conn, cursor)
        return None
    
# Fungsi untuk Index.html
def get_latest_laporan_for_display(limit=8):
    """Mengambil N laporan terbaru untuk ditampilkan di carousel. 
    Saat ini mengembalikan list kosong."""
    return []

def get_all_laporan_with_coords():
    """Mengambil semua laporan yang memiliki koordinat untuk peta. 
    Saat ini mengembalikan list kosong."""
    return []

# Fungsi untuk Route Laporan/Keluhan
def insert_laporan(data, file_path):
    """Simulasi insert laporan. Ganti dengan logika database nanti."""
    return None, "Fitur input data belum terhubung ke database."

def insert_keluhan(data):
    """Simulasi insert keluhan. Ganti dengan logika database nanti."""
    return None, "Fitur input data belum terhubung ke database."
    
def get_status_by_nomor(nomor):
    """Simulasi lacak laporan/keluhan."""
    return None # Data tidak ditemukan