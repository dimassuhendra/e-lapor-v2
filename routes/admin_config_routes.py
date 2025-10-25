# routes/admin_config_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from models import master_data_model

# Definisikan Blueprint untuk konfigurasi Admin
admin_config = Blueprint('admin_config', __name__, url_prefix='/admin/config')

# --- Dekorator untuk Cek Login ---
def admin_login_required(f):
    """Dekorator untuk memastikan hanya Admin yang sudah login yang bisa mengakses route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Anda harus login terlebih dahulu untuk mengakses halaman ini.', 'warning')
            return redirect(url_for('admin_auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Route Utama Konfigurasi ---
@admin_config.route('/')
@admin_login_required
def index():
    """Menampilkan halaman utama konfigurasi data master."""
    
    # Ambil semua data master untuk ditampilkan
    kecamatan_data = master_data_model.get_all_kecamatan()
    kelurahan_data = master_data_model.get_all_data('m_kelurahan') # Ambil semua kelurahan
    kategori_laporan = master_data_model.get_all_kategori(tipe='LAPORAN')
    kategori_keluhan = master_data_model.get_all_kategori(tipe='KELUHAN')
    dinas_data = master_data_model.get_all_dinas()
    
    # Kelompokkan kelurahan berdasarkan kecamatan (untuk tampilan yang lebih baik)
    kelurahan_by_kec = {}
    for kel in kelurahan_data:
        kec_id = kel['id_kecamatan']
        if kec_id not in kelurahan_by_kec:
            kelurahan_by_kec[kec_id] = []
        kelurahan_by_kec[kec_id].append(kel)

    return render_template('admin/master_data_config.html',
                           kecamatan=kecamatan_data,
                           kelurahan_by_kec=kelurahan_by_kec,
                           kategori_lap=kategori_laporan,
                           kategori_kel=kategori_keluhan,
                           dinas=dinas_data)

# --- Route Aksi (Contoh: Menambah Kategori) ---
@admin_config.route('/kategori/add', methods=['POST'])
@admin_login_required
def add_kategori():
    """Menambahkan kategori baru (Laporan atau Keluhan)."""
    nama = request.form.get('nama_kategori')
    tipe = request.form.get('tipe_kategori') # 'LAPORAN' atau 'KELUHAN'
    
    if nama and tipe:
        if master_data_model.add_kategori(nama, tipe):
            flash(f'Kategori "{nama}" berhasil ditambahkan.', 'success')
        else:
            flash('Gagal menambahkan kategori. Mungkin nama sudah ada.', 'danger')
    else:
        flash('Nama dan Tipe kategori tidak boleh kosong.', 'danger')
        
    return redirect(url_for('admin_config.index'))

# --- Route Aksi (Contoh: Menghapus Kategori) ---
@admin_config.route('/kategori/delete/<int:id_kategori>', methods=['POST'])
@admin_login_required
def delete_kategori(id_kategori):
    """Menghapus kategori berdasarkan ID."""
    
    if master_data_model.delete_kategori(id_kategori):
        flash('Kategori berhasil dihapus.', 'success')
    else:
        flash('Gagal menghapus kategori. Pastikan kategori tidak sedang digunakan oleh Laporan/Keluhan yang sudah ada.', 'danger')
        
    return redirect(url_for('admin_config.index'))
    
# CATATAN: Anda harus membuat route POST yang serupa untuk:
# 1. Menambah Kecamatan
# 2. Menambah Kelurahan
# 3. Menambah Dinas
# 4. Fungsi Edit/Update untuk semua data master.