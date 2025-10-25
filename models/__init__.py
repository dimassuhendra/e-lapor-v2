from app import mysql # Mengambil objek MySQL yang diinisialisasi di app.py
from flask import current_app

def get_db_cursor():
    """Mendapatkan cursor database."""
    try:
        # Mengembalikan objek connection dan cursor
        conn = mysql.connection
        cursor = conn.cursor()
        return conn, cursor
    except Exception as e:
        # Log error jika gagal koneksi
        current_app.logger.error(f"Gagal mendapatkan koneksi DB: {e}")
        return None, None

def close_db_connection(conn, cursor, commit=False):
    """Menutup cursor dan koneksi, dengan opsi commit."""
    if cursor:
        cursor.close()
    if conn:
        if commit:
            conn.commit()
        # Tidak perlu memanggil close() pada koneksi Flask-MySQLdb
        # karena dikelola secara otomatis, tetapi commit harus dipanggil.