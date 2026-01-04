import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'kunci_rahasia_admin_gongcha_2026')
app.permanent_session_lifetime = timedelta(days=365)

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


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    icon = db.Column(db.String(200), nullable=True)


class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(300), nullable=True)
    link_url = db.Column(db.String(300), nullable=True)


# --- SIMPLE TRANSLATIONS ---
TRANSLATIONS = {
    'en': {
        'hero_desc': 'I build practical web apps and tools that simplify operations and deliver measurable results.<br>Portfolio of projects, operational automation, and production-ready code.',
        'capabilities': 'Capabilities',
        'tech_stack': 'Tech Stack',
        'project_showcase': 'Project Showcase',
        'contact_title': "Let's Collaborate",
        'contact_sub': "Have a project in mind or just want to discuss tea and code? My inbox is open.",
        'send_message': 'Send a message',
        'i_reply': "I'll reply as soon as I can.",
        'placeholder_name': 'Your name',
        'placeholder_email': 'you@domain.com',
        'placeholder_message': 'Briefly describe your project or question...',
        'btn_send': 'Send Message'
    },
    'id': {
        'hero_desc': 'Saya membangun aplikasi web praktis dan alat yang menyederhanakan operasional dan memberikan hasil yang terukur.<br>Portofolio proyek, otomasi operasional, dan kode siap produksi.',
        'capabilities': 'Kemampuan',
        'tech_stack': 'Tech Stack',
        'project_showcase': 'Proyek Unggulan',
        'contact_title': 'Mari Berkolaborasi',
        'contact_sub': 'Punya proyek atau ingin bicara tentang teh dan kode? Kotak masuk saya terbuka.',
        'send_message': 'Kirim pesan',
        'i_reply': 'Saya akan membalas secepatnya.',
        'placeholder_name': 'Nama Anda',
        'placeholder_email': 'email@domain.com',
        'placeholder_message': 'Jelaskan singkat proyek atau pertanyaan Anda...',
        'btn_send': 'Kirim'
    }
}

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

        # Seed Services (capabilities) if empty
        if not Service.query.first():
            services_dummy = [
                Service(title="Website Development", icon="bi-laptop"),
                Service(title="Branding & Design", icon="bi-palette"),
                Service(title="Consultation & Strategy", icon="bi-clipboard-check")
            ]
            db.session.add_all(services_dummy)
            db.session.commit()

# --- ROUTES ---

@app.route('/')
def home():
    # Ensure language is set: check session first, then cookie
    if 'lang' not in session:
        cookie_lang = request.cookies.get('lang')
        if cookie_lang and cookie_lang in TRANSLATIONS:
            session['lang'] = cookie_lang
        else:
            return redirect(url_for('choose_language'))
    # Counter Views (Error Handling biar ga crash kalau DB belum ready)
    try:
        stats = Analytics.query.first()
        if stats:
            stats.views += 1
            db.session.commit()
        experiences = Experience.query.order_by(Experience.id.desc()).all()
        services = Service.query.order_by(Service.id.desc()).all()
        portfolios = Portfolio.query.order_by(Portfolio.id.desc()).all()
    except:
        experiences = [] # Fallback jika DB error
        services = []
        portfolios = []
        
    # translations
    lang = session.get('lang', 'en')
    texts = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    return render_template('index.html', experiences=experiences, services=services, portfolios=portfolios, texts=texts, lang=lang)


@app.route('/choose-language')
def choose_language():
    return render_template('choose_language.html')


@app.route('/set-language/<lang>')
def set_language(lang):
    if lang not in TRANSLATIONS:
        lang = 'en'
    session.permanent = True
    session['lang'] = lang
    resp = make_response(redirect(url_for('home')))
    # set cookie for one year
    resp.set_cookie('lang', lang, max_age=60*60*24*365)
    return resp

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
        services = Service.query.order_by(Service.id.desc()).all()
        portfolios = Portfolio.query.order_by(Portfolio.id.desc()).all()
    except:
        views, messages, experiences, unread_count = 0, [], [], 0
        services, portfolios = [], []

    return render_template('dashboard.html', user=session['user'], views=views, messages=messages, experiences=experiences, unread_count=unread_count, services=services, portfolios=portfolios)

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


@app.route('/service/add', methods=['POST'])
def add_service():
    if 'user' not in session: return redirect(url_for('login'))

    title = request.form.get('title')
    icon = request.form.get('icon')

    new_svc = Service(title=title, icon=icon)
    db.session.add(new_svc)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/service/delete/<int:id>')
def delete_service(id):
    if 'user' not in session: return redirect(url_for('login'))
    svc = Service.query.get_or_404(id)
    db.session.delete(svc)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/portfolio/add', methods=['POST'])
def add_portfolio():
    if 'user' not in session: return redirect(url_for('login'))

    title = request.form.get('title')
    category = request.form.get('category')
    image_url = request.form.get('image_url')
    link_url = request.form.get('link_url')

    new_pf = Portfolio(title=title, category=category, image_url=image_url, link_url=link_url)
    db.session.add(new_pf)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/portfolio/delete/<int:id>')
def delete_portfolio(id):
    if 'user' not in session: return redirect(url_for('login'))
    pf = Portfolio.query.get_or_404(id)
    db.session.delete(pf)
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
# --- ROUTE RAHASIA UNTUK SETUP DB DI VERCEL ---
@app.route('/init-db')
def init_db():
    try:
        # Coba buat semua tabel
        db.create_all()
        
        # Cek apakah tabel Experience sudah ada, kalau kosong isi dummy
        if not Experience.query.first():
            dummy = [
                Experience(role="Store Leader", company="Gong Cha Indonesia", period="Jan 2025 - Present", desc="Leading daily operations at Tunjungan Plaza 6. Spearheaded sales growth initiative."),
                Experience(role="Restaurant Manager", company="Pak 'D' Group", period="Aug 2024 - Oct 2024", desc="Managed staffing, inventory, and sales performance."),
                Experience(role="Senior Tea Barista", company="KOI Thé Indonesia", period="Apr 2018 - Apr 2023", desc="Supervised bar operations and trained new baristas.")
            ]
            db.session.add_all(dummy)
            db.session.commit()
            # Also seed Services (capabilities) and Portfolios
            if not Service.query.first():
                services_dummy = [
                    Service(title="Website Development", icon="bi-laptop"),
                    Service(title="Branding & Design", icon="bi-palette"),
                    Service(title="Consultation & Strategy", icon="bi-clipboard-check")
                ]
                db.session.add_all(services_dummy)

            if not Portfolio.query.first():
                portfolios_dummy = [
                    Portfolio(title="Personal Website", category="Web App", image_url="/static/images/portfolio1.jpg", link_url="https://example.com"),
                    Portfolio(title="Brand Identity", category="Design", image_url="/static/images/portfolio2.jpg", link_url="https://example.com"),
                    Portfolio(title="Landing Page", category="Web", image_url="/static/images/portfolio3.jpg", link_url="https://example.com")
                ]
                db.session.add_all(portfolios_dummy)

            db.session.commit()
            return "Database initialized successfully! Tables created & Dummy data added."
        
        return "Database already exists. Tables are ready."
    except Exception as e:
        return f"Error initializing database: {str(e)}"

# Script init DB untuk Local (Uncomment jika pertama kali run di local)
if __name__ == '__main__':
     create_db()
     app.run(debug=True)