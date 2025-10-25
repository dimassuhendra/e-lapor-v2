from .__init__ import get_db_cursor, close_db_connection
import bcrypt

def get_admin_by_email(email):
    """Mengambil data admin berdasarkan email untuk proses login."""
    conn, cursor = get_db_cursor()
    if not cursor:
        return None
    
    # Query untuk mengambil semua data admin (termasuk password_hash)
    query = "SELECT id_admin, username, email, password_hash FROM s_admin WHERE email = %s"
    cursor.execute(query, [email])
    admin_data = cursor.fetchone()
    
    close_db_connection(conn, cursor)
    return admin_data

def check_admin_password(password_input, password_hash_db):
    """Memverifikasi password yang dimasukkan dengan hash yang tersimpan."""
    # Pastikan password_hash_db di-encode menjadi bytes
    password_hash_bytes = password_hash_db.encode('utf-8')
    password_input_bytes = password_input.encode('utf-8')
    
    # Membandingkan hash
    return bcrypt.checkpw(password_input_bytes, password_hash_bytes)

# CATATAN: Anda perlu menambahkan fungsi untuk membuat user admin pertama (seeding data) 
# karena saat ini database Anda masih kosong!