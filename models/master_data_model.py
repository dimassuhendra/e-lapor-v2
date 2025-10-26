# models/master_data_model.py

from .__init__ import get_db_cursor, close_db_connection
from flask import current_app

# --- Helper Function untuk GET ALL ---
def get_all_data(table_name, filter_col=None, filter_val=None):
    """Mengambil semua baris dari tabel master tertentu."""
    conn, cursor = get_db_cursor()
    if not cursor:
        return []
    
    query = f"SELECT * FROM `{table_name}`"
    params = []
    
    if filter_col and filter_val is not None:
        query += f" WHERE `{filter_col}` = %s"
        params.append(filter_val)
        
    try:
        cursor.execute(query, params)
        data = cursor.fetchall()
    except Exception as e:
        current_app.logger.error(f"Error fetching data from {table_name}: {e}")
        data = []
        
    close_db_connection(conn, cursor)
    return data

# --- Kecamatan Functions ---

def get_all_kecamatan():
    """Mengambil semua data kecamatan."""
    return get_all_data('m_kecamatan')

def add_kecamatan(nama, lat, long):
    """Menambahkan kecamatan baru."""
    conn, cursor = get_db_cursor()
    if not cursor: return False
    
    query = "INSERT INTO m_kecamatan (nama_kecamatan, latitude, longitude) VALUES (%s, %s, %s)"
    try:
        cursor.execute(query, (nama, lat, long))
        close_db_connection(conn, cursor, commit=True)
        return True
    except Exception as e:
        current_app.logger.error(f"Error adding kecamatan: {e}")
        close_db_connection(conn, cursor)
        return False

def get_kecamatan_by_id(id_kecamatan):
    """Mengambil data kecamatan tunggal berdasarkan ID."""
    conn, cursor = get_db_cursor()
    if not cursor: return None
    
    query = "SELECT latitude, longitude FROM m_kecamatan WHERE id_kecamatan = %s"
    try:
        cursor.execute(query, [id_kecamatan])
        data = cursor.fetchone()
    except Exception as e:
        current_app.logger.error(f"Error fetching kecamatan by ID: {e}")
        data = None
        
    close_db_connection(conn, cursor)
    return data

# --- Kelurahan Functions ---

def get_all_kelurahan_by_kecamatan(id_kecamatan):
    """Mengambil semua kelurahan berdasarkan ID kecamatan."""
    return get_all_data('m_kelurahan', 'id_kecamatan', id_kecamatan)

def add_kelurahan(id_kecamatan, nama):
    """Menambahkan kelurahan baru."""
    conn, cursor = get_db_cursor()
    if not cursor: return False
    
    query = "INSERT INTO m_kelurahan (id_kecamatan, nama_kelurahan) VALUES (%s, %s)"
    try:
        cursor.execute(query, (id_kecamatan, nama))
        close_db_connection(conn, cursor, commit=True)
        return True
    except Exception as e:
        current_app.logger.error(f"Error adding kelurahan: {e}")
        close_db_connection(conn, cursor)
        return False

# --- Kategori Functions ---

def get_all_kategori(tipe=None):
    """Mengambil semua kategori, opsional filter berdasarkan tipe ('LAPORAN' atau 'KELUHAN')."""
    if tipe in ['LAPORAN', 'KELUHAN']:
        return get_all_data('m_kategori', 'tipe', tipe)
    return get_all_data('m_kategori')

def get_all_kategori_laporan():
    """Mengambil kategori khusus Laporan (tipe='LAPORAN')."""
    # Panggil fungsi umum dengan filter
    return get_all_kategori(tipe='LAPORAN')

def get_all_jenis_keluhan():
    """Mengambil kategori khusus Keluhan/Pertanyaan (tipe='KELUHAN')."""
    # Panggil fungsi umum dengan filter
    return get_all_kategori(tipe='KELUHAN')

def add_kategori(nama, tipe):
    """Menambahkan kategori baru (tipe LAPORAN atau KELUHAN)."""
    conn, cursor = get_db_cursor()
    if not cursor: return False
    
    query = "INSERT INTO m_kategori (nama_kategori, tipe) VALUES (%s, %s)"
    try:
        cursor.execute(query, (nama, tipe))
        close_db_connection(conn, cursor, commit=True)
        return True
    except Exception as e:
        current_app.logger.error(f"Error adding kategori: {e}")
        close_db_connection(conn, cursor)
        return False

# --- Dinas Functions ---

def get_all_dinas():
    """Mengambil semua data dinas terkait."""
    return get_all_data('m_dinas')

def add_dinas(nama, no_whatsapp):
    """Menambahkan dinas terkait baru."""
    conn, cursor = get_db_cursor()
    if not cursor: return False
    
    query = "INSERT INTO m_dinas (nama_dinas, no_whatsapp) VALUES (%s, %s)"
    try:
        cursor.execute(query, (nama, no_whatsapp))
        close_db_connection(conn, cursor, commit=True)
        return True
    except Exception as e:
        current_app.logger.error(f"Error adding dinas: {e}")
        close_db_connection(conn, cursor)
        return False

# --- Fungsi DELETE (Contoh untuk Kategori, bisa disesuaikan dengan kebutuhan soft delete) ---

def delete_kategori(id_kategori):
    """Menghapus kategori berdasarkan ID (Hard Delete untuk data master yang tidak berdampak transaksi)."""
    conn, cursor = get_db_cursor()
    if not cursor: return False
    
    query = "DELETE FROM m_kategori WHERE id_kategori = %s"
    try:
        cursor.execute(query, [id_kategori])
        close_db_connection(conn, cursor, commit=True)
        return True
    except Exception as e:
        # Jika kategori sudah digunakan di t_laporan, MySQL akan menolak (Foreign Key Constraint)
        current_app.logger.error(f"Error deleting kategori {id_kategori}: {e}")
        close_db_connection(conn, cursor)
        return False