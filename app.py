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
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    details = db.Column(db.Text, nullable=True)  # JSON or detailed HTML


class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(300), nullable=True)
    link_url = db.Column(db.String(300), nullable=True)


# --- SIMPLE TRANSLATIONS ---
TRANSLATIONS = {
    'en': {
        'navbar_home': 'Home',
        'navbar_about': 'About',
        'navbar_capabilities': 'Capabilities',
        'navbar_projects': 'Projects',
        'navbar_contact': 'Contact',
        'hero_hi': "Hi. I'm Chaniago.",
        'hero_role': 'A <span class="highlight">Developer.</span>',
        'hero_desc': 'I build practical web apps and tools that simplify operations and deliver measurable results.<br>Portfolio of projects, operational automation, and production-ready code.',
        'about_title': "I'm a <span class=\"highlight\">Software Engineer</span> who builds affordable digital solutions.",
        'about_p1': "I believe that going digital shouldn't cost a fortune. My mission is to help businesses establish their online presence with professional-grade web applications at accessible, under-market rates.",
        'about_p2': "I leverage efficient code (Python & Flask) to cut unnecessary costs, delivering premium results so you can grow without the financial burden.",
        'capabilities': 'Capabilities',
        'capabilities_desc': 'What I build — focused, practical projects and technical skills.',
        'tech_stack': 'Tech Stack',
        'tech_stack_desc': 'Tools and frameworks I use regularly.',
        'project_showcase': 'Project Showcase',
        'project_showcase_desc': 'Selected projects demonstrating practical results and outcomes.',
        'no_capabilities': 'No capabilities added yet.',
        'no_projects': 'No projects yet — add some from the dashboard.',
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
        'navbar_home': 'Beranda',
        'navbar_about': 'Tentang',
        'navbar_capabilities': 'Kemampuan',
        'navbar_projects': 'Proyek',
        'navbar_contact': 'Kontak',
        'hero_hi': "Halo. Saya Chaniago.",
        'hero_role': 'Seorang <span class="highlight">Developer.</span>',
        'hero_desc': 'Saya membangun aplikasi web praktis dan alat yang menyederhanakan operasional dan memberikan hasil yang terukur.<br>Portofolio proyek, otomasi operasional, dan kode siap produksi.',
        'about_title': 'Saya seorang <span class=\"highlight\">Software Engineer</span> yang membangun solusi digital terjangkau.',
        'about_p1': 'Saya percaya bahwa digitalisasi tidak harus mahal. Misi saya adalah membantu bisnis membangun kehadiran online mereka dengan aplikasi web berkualitas profesional di harga yang terjangkau dan di bawah pasaran.',
        'about_p2': 'Saya memanfaatkan kode yang efisien (Python & Flask) untuk memangkas biaya yang tidak perlu, memberikan hasil premium sehingga Anda dapat berkembang tanpa beban finansial.',
        'capabilities': 'Kemampuan',
        'capabilities_desc': 'Apa yang saya bangun — proyek fokus, praktis, dan skill teknis.',
        'tech_stack': 'Teknologi',
        'tech_stack_desc': 'Tools dan framework yang sering saya gunakan.',
        'project_showcase': 'Proyek Unggulan',
        'project_showcase_desc': 'Proyek pilihan yang menunjukkan hasil nyata dan berdampak.',
        'no_capabilities': 'Belum ada kemampuan yang ditambahkan.',
        'no_projects': 'Belum ada proyek — tambahkan dari dashboard.',
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
                Service(
                    title="Website Development",
                    icon="bi-laptop",
                    slug="website-development",
                    description="Building fast, responsive, and scalable web applications tailored to your business needs.",
                    details="""<h3>Full-Stack Web Development</h3>
                    <p>I create modern web applications using Python, Flask, React, and PostgreSQL. From concept to deployment, I handle the entire development lifecycle.</p>
                    <h4>What I Offer:</h4>
                    <ul>
                        <li><strong>Custom Web Applications</strong> - Tailored solutions for your unique business requirements</li>
                        <li><strong>E-Commerce Platforms</strong> - Complete online stores with payment integration</li>
                        <li><strong>API Development</strong> - RESTful APIs for mobile apps and third-party integrations</li>
                        <li><strong>Database Design</strong> - Efficient and scalable database architecture</li>
                        <li><strong>Cloud Deployment</strong> - Hosting on AWS, Vercel, or your preferred platform</li>
                    </ul>
                    <h4>Technologies:</h4>
                    <p>Python • Flask • JavaScript • React • PostgreSQL • Docker • AWS • Git</p>"""
                ),
                Service(
                    title="Branding & Design",
                    icon="bi-palette",
                    slug="branding-design",
                    description="Creating cohesive visual identities that make your brand memorable and professional.",
                    details="""<h3>Brand Identity & UI/UX Design</h3>
                    <p>I design clean, modern interfaces that prioritize user experience while reflecting your brand's personality.</p>
                    <h4>What I Offer:</h4>
                    <ul>
                        <li><strong>Logo Design</strong> - Unique and memorable brand marks</li>
                        <li><strong>UI/UX Design</strong> - User-centered interface design</li>
                        <li><strong>Responsive Design</strong> - Mobile-first approach for all devices</li>
                        <li><strong>Design Systems</strong> - Consistent components and style guides</li>
                        <li><strong>Prototyping</strong> - Interactive mockups before development</li>
                    </ul>
                    <h4>Tools:</h4>
                    <p>Figma • Adobe XD • Photoshop • Illustrator</p>"""
                ),
                Service(
                    title="Consultation & Strategy",
                    icon="bi-clipboard-check",
                    slug="consultation-strategy",
                    description="Strategic planning and technical consultation to help you make informed decisions about your digital presence.",
                    details="""<h3>Technical Consultation & Digital Strategy</h3>
                    <p>Not sure where to start? I help businesses understand their technical needs and create actionable roadmaps.</p>
                    <h4>What I Offer:</h4>
                    <ul>
                        <li><strong>Tech Stack Selection</strong> - Choosing the right tools for your project</li>
                        <li><strong>Project Planning</strong> - Breaking down complex projects into phases</li>
                        <li><strong>Cost Analysis</strong> - Budget-friendly solutions without compromising quality</li>
                        <li><strong>Performance Audit</strong> - Reviewing existing systems for improvements</li>
                        <li><strong>Training & Support</strong> - Ongoing guidance for your team</li>
                    </ul>
                    <h4>Approach:</h4>
                    <p>Practical advice • Cost-effective solutions • Long-term thinking</p>"""
                )
            ]
            db.session.add_all(services_dummy)
            db.session.commit()
        
        # Seed Portfolio if empty
        if not Portfolio.query.first():
            portfolios_dummy = [
                Portfolio(
                    title="Senja Coffee E-Commerce",
                    category="Full-Stack Web App",
                    image_url="/static/images/Homepage_coffe_senja.png",
                    link_url="https://senja-coffee-demo.vercel.app"
                )
            ]
            db.session.add_all(portfolios_dummy)
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
            session['lang'] = 'en'  # Set default language
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

@app.route('/capability/<slug>')
def capability_detail(slug):
    # Get language
    lang = session.get('lang', 'en')
    texts = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    
    # Get capability by slug
    capability = Service.query.filter_by(slug=slug).first_or_404()
    
    return render_template('capability_detail.html', capability=capability, texts=texts, lang=lang)



@app.route('/choose-language')



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

# --- ROUTE UNTUK UPDATE PORTFOLIO DI PRODUCTION ---
@app.route('/update-portfolio-prod')
def update_portfolio_prod():
    try:
        # Cari portfolio pertama atau yang spesifik
        portfolio = Portfolio.query.first()
        
        if portfolio:
            # Update dengan data baru
            portfolio.title = "Senja Coffee E-Commerce"
            portfolio.category = "Full-Stack Web App"
            portfolio.image_url = "/static/images/Homepage_coffe_senja.png"
            portfolio.link_url = "https://senja-coffee-demo.vercel.app"
            db.session.commit()
            return f"✅ Portfolio updated successfully!<br>Title: {portfolio.title}<br>Image: {portfolio.image_url}"
        else:
            # Kalau belum ada, buat baru
            new_portfolio = Portfolio(
                title="Senja Coffee E-Commerce",
                category="Full-Stack Web App",
                image_url="/static/images/Homepage_coffe_senja.png",
                link_url="https://senja-coffee-demo.vercel.app"
            )
            db.session.add(new_portfolio)
            db.session.commit()
            return "✅ New portfolio created successfully!"
    except Exception as e:
        return f"❌ Error updating portfolio: {str(e)}"

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
                    Portfolio(
                        title="Senja Coffee E-Commerce",
                        category="Full-Stack Web App",
                        image_url="/static/images/Homepage_coffe_senja.png",
                        link_url="https://senja-coffee-demo.vercel.app"
                    )
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
    app.run(debug=True, port=5001)