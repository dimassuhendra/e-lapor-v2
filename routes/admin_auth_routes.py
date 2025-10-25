# routes/admin_auth_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user_model import get_admin_by_email, check_admin_password

# Definisikan Blueprint untuk rute admin
admin_auth = Blueprint('admin_auth', __name__, url_prefix='/admin')

@admin_auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        admin = get_admin_by_email(email)
        
        if admin and check_admin_password(password, admin['password_hash']):
            # Login Berhasil: Set sesi admin
            session['admin_logged_in'] = True
            session['admin_id'] = admin['id_admin']
            session['admin_username'] = admin['username']
            flash('Login berhasil!', 'success')
            return redirect(url_for('admin_auth.dashboard')) # Alihkan ke halaman dashboard
        else:
            flash('Email atau password salah.', 'danger')
    
    return render_template('admin/login.html')

@admin_auth.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    flash('Anda telah keluar.', 'info')
    return redirect(url_for('admin_auth.login'))

@admin_auth.route('/dashboard')
def dashboard():
    # Contoh fungsi untuk rute dashboard (perlu cek sesi)
    if 'admin_logged_in' not in session:
        flash('Anda harus login terlebih dahulu.', 'warning')
        return redirect(url_for('admin_auth.login'))
        
    return render_template('admin/dashboard.html')