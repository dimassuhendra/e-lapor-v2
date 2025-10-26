from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import os # Untuk operasi file/path
from werkzeug.utils import secure_filename # Untuk mengamankan nama file
from models import laporan_model
from models import master_data_model
from models import pengumuman_model # Asumsi: Anda akan membuat file ini nanti
from utils.map_helper import get_map_config
from app import app # Untuk mengakses konfigurasi file upload

public_routes = Blueprint('public_routes', __name__)

# Direktori untuk menyimpan file foto laporan (Pastikan folder ini ada di root project)
UPLOAD_FOLDER = 'static/uploads/laporan_foto'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """Mengecek apakah ekstensi file diizinkan."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- A. Halaman Utama ---
@public_routes.route('/')
def index():
    """Halaman utama/landing page untuk warga."""
    
    # Memanggil fungsi model yang sekarang mengembalikan list kosong
    latest_laporan = laporan_model.get_latest_laporan_for_display(limit=8)
    all_laporan_list = laporan_model.get_all_laporan_with_coords() 
    latest_pengumuman = pengumuman_model.get_latest_pengumuman(limit=8)
    
    map_config = get_map_config()
    
    return render_template('public/index.html',
                           latest_laporan=latest_laporan,
                           all_laporan_list=all_laporan_list,
                           latest_pengumuman=latest_pengumuman,
                           map_config=map_config)

# # --- B. Membuat Laporan ---
# @public_routes.route('/buat_laporan', methods=['GET', 'POST'])
# def buat_laporan():
#     kecamatan = master_data_model.get_all_kecamatan()
#     kategori_laporan = master_data_model.get_all_kategori(tipe='LAPORAN')
#     map_config = get_map_config()
    
#     if request.method == 'POST':
#         # 1. Validasi File Foto
#         if 'foto' not in request.files:
#             flash('Foto laporan wajib diunggah.', 'danger')
#             return redirect(request.url)
        
#         file = request.files['foto']
#         if file.filename == '':
#             flash('Foto laporan wajib diunggah.', 'danger')
#             return redirect(request.url)
            
#         if not allowed_file(file.filename):
#             flash('Format file tidak diizinkan. Gunakan PNG, JPG, atau JPEG.', 'danger')
#             return redirect(request.url)

#         filename = secure_filename(file.filename)
#         # Buat path folder jika belum ada
#         os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(file_path)
        
#         # 2. Siapkan Data Laporan
#         data = {
#             'nama_pelapor': request.form.get('nama_pelapor'),
#             'no_whatsapp': request.form.get('no_whatsapp'),
#             'id_kategori': request.form.get('id_kategori'),
#             'nama_jalan': request.form.get('nama_jalan'),
#             'id_kecamatan': request.form.get('id_kecamatan'),
#             'id_kelurahan': request.form.get('id_kelurahan'),
#             'lat_peta': request.form.get('lat_peta'), # Koordinat dari klik peta/input tersembunyi
#             'long_peta': request.form.get('long_peta'),
#             'deskripsi': request.form.get('deskripsi')
#         }

#         # 3. Simpan ke Database
#         nomor, error = laporan_model.insert_laporan(data, file_path)
        
#         if error:
#             flash(f'Gagal membuat laporan: {error}', 'danger')
#         else:
#             flash(f'Laporan Anda berhasil dibuat! Nomor Laporan Anda adalah: {nomor}. Gunakan nomor ini untuk melacak status.', 'success')
#             return redirect(url_for('public_routes.lacak_laporan')) # Redirect ke halaman pelacakan
            
#     return render_template('public/form_lapor.html', 
#                            kecamatan=kecamatan, 
#                            kategori=kategori_laporan, 
#                            map_config=map_config)

# --- B. Halaman Form Lapor/Keluhan (Route Gabungan) ---
@public_routes.route('/lapor', methods=['GET', 'POST'])
def lapor():
    """Menampilkan halaman form Laporan dan Keluhan (Public) dan memproses POST."""
    
    # Ambil data master untuk dropdown
    kategori_laporan = master_data_model.get_all_kategori_laporan()
    jenis_keluhan = master_data_model.get_all_jenis_keluhan()
    data_kecamatan = master_data_model.get_all_kecamatan() 
    
    # --- Penanganan POST (Simpan Data) ---
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        data = request.form
        
        if form_type == 'laporan':
            # 1. Validasi dan Handle File Upload
            foto = request.files.get('foto')
            filename = None

            # Logic: Laporan wajib menyertakan foto
            if not foto or foto.filename == '':
                flash('Foto laporan wajib diunggah untuk pengajuan Laporan.', 'danger')
                return redirect(url_for('public_routes.lapor')) 
                
            if not allowed_file(foto.filename):
                flash('Format file tidak diizinkan. Gunakan PNG, JPG, atau JPEG.', 'danger')
                return redirect(url_for('public_routes.lapor'))

            # Simpan file
            filename = secure_filename(foto.filename)
            # Opsional: Tambahkan unique ID/timestamp ke filename untuk menghindari konflik
            filename = f"{os.urandom(8).hex()}_{filename}" 
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            foto.save(file_path)
            
            # 2. Insert ke model
            nomor, error = laporan_model.insert_laporan(data, filename) 
            
            if nomor:
                flash(f'Laporan Anda berhasil dikirim! Nomor Laporan: <strong>{nomor}</strong>.', 'success')
                return redirect(url_for('public_routes.lacak_laporan', nomor_laporan=nomor))
            else:
                flash(f'Gagal mengirim laporan: {error}.', 'danger')
                
        elif form_type == 'keluhan':
            # Keluhan tidak memerlukan upload file
            nomor, error = laporan_model.insert_keluhan(data)
            if nomor:
                flash(f'Keluhan Anda berhasil dikirim! Nomor Keluhan: <strong>{nomor}</strong>.', 'success')
                return redirect(url_for('public_routes.lacak_laporan', nomor_laporan=nomor))
            else:
                flash(f'Gagal mengirim keluhan: {error}.', 'danger')

        # Jika POST gagal, kembalikan ke GET (dapat ditambahkan logic agar form terisi kembali)
        flash('Terjadi kesalahan saat pemrosesan formulir. Silakan coba lagi.', 'danger')
    
    # --- Tampilan GET ---
    return render_template('public/buat_laporan_keluhan.html', # <-- Nama template yang konsisten
                           kategori_laporan=kategori_laporan,
                           jenis_keluhan=jenis_keluhan,
                           data_kecamatan=data_kecamatan)

# --- D. Melacak Laporan (Gabungan Laporan & Keluhan) ---
@public_routes.route('/lacak-laporan', methods=['GET', 'POST'])
def lacak_laporan():
    status_data = None
    nomor_laporan = None
    
    if request.method == 'POST':
        nomor_laporan = request.form.get('nomor_laporan')
        if nomor_laporan:
            status_data = laporan_model.get_status_by_nomor(nomor_laporan)
            if not status_data:
                flash(f'Nomor laporan/keluhan "{nomor_laporan}" tidak ditemukan atau sudah dihapus.', 'danger')
            else:
                flash(f'Status ditemukan untuk {status_data["tipe"]}!', 'info')
        else:
            flash('Harap masukkan nomor laporan/keluhan.', 'warning')
            
    return render_template('public/lacak_laporan.html', status_data=status_data, nomor_laporan=nomor_laporan)

# --- E. Endpoint AJAX untuk Kelurahan ---
@public_routes.route('/api/kelurahan/<int:id_kecamatan>')
def api_kelurahan(id_kecamatan):
    """Menyediakan daftar kelurahan dalam format JSON berdasarkan ID Kecamatan."""
    kelurahan = master_data_model.get_all_kelurahan_by_kecamatan(id_kecamatan)
    return jsonify(kelurahan)

# --- F. Melihat Pengumuman Publik ---
@public_routes.route('/pengumuman')
def list_pengumuman():
    # Asumsi: Anda akan membuat get_all_pengumuman() di pengumuman_model.py
    # pengumuman_list = pengumuman_model.get_all_pengumuman() 
    return render_template('public/pengumuman.html', pengumuman_list=[]) # Placeholder

# --- G. Melihat Statistik ---
@public_routes.route('/statistik')
def statistik():
    # Asumsi: Anda akan membuat get_laporan_stats() di laporan_model.py
    # stats = laporan_model.get_laporan_stats() 
    return render_template('public/statistik.html', stats_data={}) # Placeholder