import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'kunci_rahasia_admin_gongcha_2026')

# --- 1. KONFIGURASI DATABASE (AUTO SWITCH) ---
# Jika ada ENV 'DATABASE_URL' (di Vercel/Neon), pakai PostgreSQL.
# Jika tidak ada, pakai SQLite (Local).
database_url = os.environ.get('DATABASE_URL')

if database_url:
    # Fix untuk SQLAlchemy terbaru (postgres:// harus jadi postgresql://)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- 2. KONFIGURASI CLOUDINARY (Untuk Upload Gambar Nanti) ---
cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key = os.environ.get('CLOUDINARY_API_KEY'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
)

# --- MODEL DATABASE ---
class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    period = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.Text, nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    views = db.Column(db.Integer, default=0)

# --- FUNGSI CREATE DB (Hanya jalan di Local/Command Line) ---
def create_db():
    with app.app_context():
        db.create_all()
        # Seeding Data Awal (Hanya jika kosong)
        if not Analytics.query.first():
            db.session.add(Analytics(views=0))
            db.session.commit()
            
        if not Experience.query.first():
            dummy = [
                Experience(role="Store Leader", company="Gong Cha Indonesia", period="Jan 2025 - Present", desc="Leading daily operations at Tunjungan Plaza 6. Spearheaded sales growth initiative."),
                Experience(role="Restaurant Manager", company="Pak 'D' Group", period="Aug 2024 - Oct 2024", desc="Managed staffing, inventory, and sales performance."),
                Experience(role="Senior Tea Barista", company="KOI Thé Indonesia", period="Apr 2018 - Apr 2023", desc="Supervised bar operations and trained new baristas.")
            ]
            db.session.add_all(dummy)
            db.session.commit()

# --- ROUTES ---

@app.route('/')
def home():
    # Counter Views (Error Handling biar ga crash kalau DB belum ready)
    try:
        stats = Analytics.query.first()
        if stats:
            stats.views += 1
            db.session.commit()
        experiences = Experience.query.order_by(Experience.id.desc()).all()
    except:
        experiences = [] # Fallback jika DB error
        
    return render_template('index.html', experiences=experiences)

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        new_msg = Message(name=name, email=email, content=message)
        db.session.add(new_msg)
        db.session.commit()
        flash('Message sent successfully!', 'success')
    except:
        flash('Error sending message. DB Connection failed.', 'error')
    return redirect(url_for('home') + '#contact')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # GANTI PASSWORD INI DI ENV VARIABLES NANTI BIAR AMAN
        admin_user = os.environ.get('ADMIN_USER', 'admin')
        admin_pass = os.environ.get('ADMIN_PASS', 'admin123')
        
        if username == admin_user and password == admin_pass:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    
    try:
        stats = Analytics.query.first()
        views = stats.views if stats else 0
        messages = Message.query.order_by(Message.timestamp.desc()).all()
        experiences = Experience.query.order_by(Experience.id.desc()).all()
        unread_count = Message.query.filter_by(is_read=False).count()
    except:
        views, messages, experiences, unread_count = 0, [], [], 0

    return render_template('dashboard.html', user=session['user'], views=views, messages=messages, experiences=experiences, unread_count=unread_count)

@app.route('/experience/add', methods=['POST'])
def add_experience():
    if 'user' not in session: return redirect(url_for('login'))
    
    role = request.form['role']
    company = request.form['company']
    period = request.form['period']
    desc = request.form['desc']
    
    new_exp = Experience(role=role, company=company, period=period, desc=desc)
    db.session.add(new_exp)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/experience/delete/<int:id>')
def delete_experience(id):
    if 'user' not in session: return redirect(url_for('login'))
    exp = Experience.query.get_or_404(id)
    db.session.delete(exp)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Script init DB untuk Local (Uncomment jika pertama kali run di local)
if __name__ == '__main__':
     create_db()
     app.run(debug=True)