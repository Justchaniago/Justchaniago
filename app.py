from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os  # <--- JANGAN SAMPAI LUPA INI!

app = Flask(__name__)

# --- KONFIGURASI DATABASE VERCEL ---
database_url = os.environ.get('DATABASE_URL')

if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'kunci-rahasia-default')

db = SQLAlchemy(app)
# ... kode selanjutnya ...
# Konfigurasi Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Kalau belum login, lempar ke sini

# --- MODEL DATA ---
# 1. Tabel Project
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    link = db.Column(db.String(200))

# 2. Tabel User (Admin)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- SETUP DATA AWAL (SEEDING) ---
def seed_data():
    # Cek apakah Admin sudah ada? Kalau belum, buatkan.
    if User.query.count() == 0:
        # Password kita hash (acak) biar aman
        hashed_password = generate_password_hash("admin123", method='pbkdf2:sha256')
        admin = User(username="chaniago", password=hashed_password)
        db.session.add(admin)
        db.session.commit()
        print("User Admin Berhasil Dibuat! (User: chaniago, Pass: admin123)")

# --- ROUTES (JALUR) ---

# 1. Halaman Utama (Portfolio)
@app.route('/')
def home():
    projects = Project.query.all()
    profile = {
        'name': 'Fahrul Roji Chaniago',
        'role': 'Store Leader & Aspiring Developer',
        'bio': 'Bridging Operations & Tech. Mengubah data menjadi keputusan bisnis.',
        'linkedin': 'https://www.linkedin.com/in/fr-chaniago/'
    }
    return render_template('index.html', projects=projects, profile=profile)

# 2. Halaman Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        # Cek apakah user ada DAN password cocok
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login Gagal. Cek username/password.')
            
    return render_template('login.html')

# 3. Halaman Dashboard (Hanya bisa diakses kalau sudah login)
@app.route('/dashboard')
@login_required 
def dashboard():
    projects = Project.query.all()
    return render_template('dashboard.html', user=current_user, projects=projects)

# 4. Fungsi Tambah Project
@app.route('/add_project', methods=['POST'])
@login_required
def add_project():
    title = request.form.get('title')
    category = request.form.get('category')
    description = request.form.get('description')
    link = request.form.get('link')

    new_project = Project(title=title, category=category, description=description, link=link)
    db.session.add(new_project)
    db.session.commit()
    return redirect(url_for('dashboard'))

# 5. Fungsi Hapus Project
@app.route('/delete/<int:id>')
@login_required
def delete_project(id):
    project_to_delete = Project.query.get_or_404(id)
    db.session.delete(project_to_delete)
    db.session.commit()
    return redirect(url_for('dashboard'))

# 6. Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- RUTE RAHASIA UNTUK INISIASI DATABASE (JANGAN DIHAPUS) ---
@app.route('/init_db_rahasia')
def init_db():
    try:
        # Pancing pembuatan tabel
        with app.app_context():
            db.create_all()
            seed_data()
        return "Database berhasil dibuat & User Admin ditambahkan! Silakan kembali ke Home."
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True)