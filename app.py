# app.py
from flask import Flask
from flask_mysqldb import MySQL 
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Inisialisasi Database
mysql = MySQL(app)

# -----------------------------------------------
# IMPORT BLUEPRINTS BARU
# -----------------------------------------------
from routes.admin_auth_routes import admin_auth
from routes.admin_config_routes import admin_config  # BARU: Untuk Kelola Master Data
from routes.public_routes import public_routes        # BARU: Untuk Route Warga (Wajib ada!)


# -----------------------------------------------
# REGISTRASI BLUEPRINTS
# -----------------------------------------------
app.register_blueprint(admin_auth)
app.register_blueprint(admin_config) # Registrasi Konfigurasi Admin
app.register_blueprint(public_routes)  # Registrasi Route Publik


if __name__ == '__main__':
    # Pastikan FLASK_ENV diatur ke development di terminal untuk debug=True
    app.run(debug=True)