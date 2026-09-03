import streamlit as st
from datetime import datetime
import sqlite3
import re
import random
from pathlib import Path
from PIL import Image

# === CONFIGURATION ===

APP_NAME = "NEXERA"
TAGLINE = "Step Into Your Next Era"

SUPPORT_EMAIL = "nexerasupport142@gmail.com"
SUPPORT_PHONE = "09018479293"

VOTE_PRICE = 200
OPAY_ACCOUNT = "9018479293"
OPAY_NAME = "Nexera"

REGISTRATION_START = datetime(2026, 9, 1, 0, 0, 0)
VOTING_START = datetime(2026, 10, 1, 0, 0, 0)
VOTING_END = datetime(2026, 11, 1, 23, 59, 0)

ADMIN_PASSWORD = "RavenNexera2026!"

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "nexera.db"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"
BACKGROUND_PATH = ASSETS_DIR / "background.jpg"

# === PAGE CONFIG ===

st.set_page_config(
    page_title=f"{APP_NAME} — {TAGLINE}",
    page_icon="🖤",
    layout="wide",
    initial_sidebar_state="expanded",
)

# === CSS STYLES ===

def local_css():
    st.markdown(
        f"""
        <style>
        .home-background {{
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background-image: url('{BACKGROUND_PATH.as_posix()}');
            background-size: cover;
            background-position: center;
            filter: brightness(0.5);
            z-index: -1;
        }}
        .home-content {{
            position: relative;
            color: white;
            padding: 5rem 2rem;
            text-align: center;
            max-width: 900px;
            margin: 0 auto;
        }}
        .logo-img {{
            max-width: 180px;
            margin-bottom: 1rem;
        }}
        .hero-title {{
            font-size: 3.5rem;
            font-weight: 900;
            margin-bottom: 0.5rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
        }}
        .hero-tagline {{
            font-size: 1.5rem;
            font-weight: 400;
            margin-bottom: 2rem;
            font-style: italic;
        }}
        .sidebar .streamlit-expanderHeader {{
            font-weight: 700;
            font-size: 1.1rem;
        }}
        .stRadio > div > label {{
            font-weight: 600;
            font-size: 1rem;
        }}
        footer {{
            text-align: center;
            margin-top: 3rem;
            font-size: 0.9rem;
            color: #888;
        }}
        .admin-stats {{
            display: flex;
            gap: 2rem;
            margin-bottom: 2rem;
        }}
        .stat-box {{
            background-color: #f0f2f6;
            padding: 1rem 2rem;
            border-radius: 8px;
            text-align: center;
            flex: 1;
        }}
        .stat-number {{
            font-size: 2rem;
            font-weight: 700;
            color: #333;
        }}
        .stat-label {{
            font-size: 1rem;
            color: #666;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

local_css()

# === DATABASE FUNCTIONS ===

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            talent_category TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            bio TEXT NOT NULL,
            why_money TEXT NOT NULL,
            image_path TEXT,
            votes INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

init_db()

# === HELPERS ===

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")

def generate_code():
    conn = get_connection()
    while True:
        code = str(random.randint(1000, 9999))
        exists = conn.execute("SELECT id FROM candidates WHERE code = ?", (code,)).fetchone()
        if not exists:
            conn.close()
            return code

def unique_slug(name, code):
    base = slugify(name)
    if not base:
        base = "contestant"
    return f"{base}-{code}"

def save_uploaded_image(uploaded_file, code):
    if uploaded_file is None:
        return None
    try:
        image = Image.open(uploaded_file)
        image = image.convert("RGB")
        filename = f"{code}.jpg"
        destination = UPLOAD_DIR / filename
        image.save(destination, "JPEG", quality=92)
        return str(destination)
    except Exception:
        return None

def image_exists(path):
    return bool(path) and Path(path).exists()

def validate_nexera_text(text):
    return "nexera" in text.lower()

def show_logo(width=180):
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=width)
    else:
        st.markdown(f"<h2 style='font-weight:900;'>{APP_NAME}</h2>", unsafe_allow_html=True)

# === STATUS CHECKS ===

def registration_status():
    now = datetime.now()
    if now < REGISTRATION_START:
        return "upcoming"
    if now >= VOTING_START:
        return "closed"
    return "active"

def voting_status():
    now = datetime.now()
    if now < VOTING_START:
        return "upcoming"
    if now > VOTING_END:
        return "ended"
    return "active"

# === PAGES ===

def home_page():
    st.markdown(f'<div class="home-background"></div>', unsafe_allow_html=True)
    st.markdown('<div class="home-content">', unsafe_allow_html=True)
    show_logo()
    st.markdown(f'<h1 class="hero-title">{APP_NAME}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="hero-tagline">{TAGLINE}</p>', unsafe_allow_html=True)
    st.markdown(
        """
        <p>
        NEXERA is a premier youth empowerment platform dedicated to discovering talent, mobilizing communities, and creating economic opportunities for young Nigerians.
        Whether you are an influencer, model, content creator, or entrepreneur, NEXERA provides a platform to showcase your talent, share your story, and gain community support.
        </p>
        """,
        unsafe_allow_html=True,
    )
    status = voting_status()
    if status == "ended":
        st.markdown("<h3>COMPETITION OVER</h3>", unsafe_allow_html=True)
        st.write("Thank you to everyone who participated in NEXERA.")
    elif status == "upcoming":
        st.info("NEXERA voting will open on October 1, 2026.")
    else:
        st.success("NEXERA competition is LIVE. Registration and voting are currently open.")
    st.markdown('<h3>How It Works</h3>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 01 — Register\nSubmit your details, photo, category and your story.")
    with col2:
        st.markdown("### 02 — Mobilize Support\nShare your personal NEXERA contestant link and encourage your community to vote.")
    with col3:
        st.markdown("### 03 — Earn & Be Rewarded\nContestants with the highest verified votes compete for NEXERA rewards.")
    st.markdown('<h3>Prize Fund</h3>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("1st Place", "₦120,000")
    with c2:
        st.metric("2nd Place", "₦50,000")
    with c3:
        st.metric("3rd Place", "₦30,000")
    st.info("Additional cash prizes, grants and empowerment rewards may also be awarded.")
    st.markdown('</div>', unsafe_allow_html=True)

def contestants_page():
    st.markdown('<h2>NEXERA Contestants</h2>', unsafe_allow_html=True)
    conn = get_connection()
    search = st.text_input("Search contestant", placeholder="Name, code or category...")
    if search:
        like = f"%{search}%"
        candidates = conn.execute(
            """
            SELECT * FROM candidates
            WHERE status = 'approved' AND
            (full_name LIKE ? OR code LIKE ? OR talent_category LIKE ?)
            ORDER BY votes DESC, created_at ASC
            """,
            (like, like, like),
        ).fetchall()
    else:
        candidates = conn.execute(
            """
            SELECT * FROM candidates
            WHERE status = 'approved'
            ORDER BY votes DESC, created_at ASC
            """
        ).fetchall()
    conn.close()
    if not candidates:
        st.info("No approved contestants found.")
        return
    voting_active = voting_status() == "active"
    for index in range(0, len(candidates), 2):
        cols = st.columns(2)
        for position, col in enumerate(cols):
            candidate_index = index + position
            if candidate_index >= len(candidates):
                continue
            candidate = candidates[candidate_index]
            with col:
                rank = candidate_index + 1
                st.markdown(f"<div style='font-weight:bold; font-size:1.1rem; margin-bottom:0.3rem;'>#{rank} — NEXERA {candidate['code']}</div>", unsafe_allow_html=True)
                if image_exists(candidate["image_path"]):
                    st.image(candidate["image_path"], use_container_width=True)
                else:
                    st.info("Contestant photo unavailable.")
                st.subheader(candidate["full_name"])
                st.write(f"**Category:** {candidate['talent_category']}")
                st.markdown(f"<div style='font-size:1.2rem; font-weight:700; margin-top:0.5rem;'>{candidate['votes']:,} VERIFIED VOTES</div>", unsafe_allow_html=True)
                st.markdown(f"**Why they need the money:** {candidate['why_money']}")
                if voting_active:
                    st.markdown(f"**Voting is active.** Send ₦{VOTE_PRICE} per vote to the account below to support your favorite contestant.")
                    st.markdown(f"**OPay Account:** {OPAY_ACCOUNT} ({OPAY_NAME})")

def registration_page():
    st.markdown('<h2>Register for NEXERA</h2>', unsafe_allow_html=True)
    status = registration_status()
    if status != "active":
        if status == "upcoming":
            st.warning("Registration has not opened yet.")
        else:
            st.info("Registration is closed.")
        return
    st.write("Tell us about yourself, what you're into and why you need the opportunity.")
    st.info("Important: Your 'Why do you need the money?' write-up must contain the word NEXERA. If it does not, your submission will automatically be flagged as INVALID.")
    with st.form("registration_form"):
        full_name = st.text_input("Full Name *", placeholder="Enter your full name")
        phone = st.text_input("Phone Number *", placeholder="08012345678")
        email = st.text_input("Email Address *", placeholder="you@example.com")
        category = st.selectbox("What category do you fall into? *", ["Influencer", "Modeling", "Content Creator", "Small & Medium Scale Business"])
        photo = st.file_uploader("Upload a clear photo of yourself *", type=["jpg", "jpeg", "png"])
        bio = st.text_area("What are you into? *", placeholder="Tell us what you do, your passion, your work, your business or what you are building...", height=160)
        why_money = st.text_area("Why do you need the money? *", placeholder="Explain why you need the money and what you intend to use it for. Remember to include NEXERA in your write-up.", height=220)
        submitted = st.form_submit_button("SUBMIT NEXERA APPLICATION", use_container_width=True)
    if submitted:
        errors = []
        if not full_name.strip():
            errors.append("Please enter your full name.")
        if not phone.strip():
            errors.append("Please enter your phone number.")
        if not email.strip():
            errors.append("Please enter your email address.")
        if not photo:
            errors.append("Please upload your photo.")
        if not bio.strip():
            errors.append("Please tell us what you are into.")
        if not why_money.strip():
            errors.append("Please explain why you need the money.")
        if not validate_nexera_text(why_money):
            errors.append("INVALID SUBMISSION: Your 'Why do you need the money?' write-up must contain the word NEXERA.")
        if errors:
            for error in errors:
                st.error(error)
            return
        code = generate_code()
        slug = unique_slug(full_name, code)
        image_path = save_uploaded_image(photo, code)
        conn = get_connection()
        conn.execute(
            """
            INSERT INTO candidates (
                code, slug, full_name, talent_category, phone, email,
                bio, why_money, image_path, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                code,
                slug,
                full_name.strip(),
                category,
                phone.strip(),
                email.strip(),
                bio.strip(),
                why_money.strip(),
                image_path,
                datetime.now().isoformat(),
            ),
        )
        conn.commit()
        conn.close()
        st.success(f"Thank you for registering, {full_name}! Your application has been submitted.")

def admin_page():
    st.markdown('<h2>Admin Panel</h2>', unsafe_allow_html=True)
    password = st.text_input("Enter admin password", type="password")
    if password == ADMIN_PASSWORD and ADMIN_PASSWORD != "":
        st.success("Access granted.")
        conn = get_connection()
        total = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
        approved = conn.execute("SELECT COUNT(*) FROM candidates WHERE status = 'approved'").fetchone()[0]
        pending = conn.execute("SELECT COUNT(*) FROM candidates WHERE status = 'pending'").fetchone()[0]
        total_votes = conn.execute("SELECT SUM(votes) FROM candidates").fetchone()[0] or 0
        st.markdown('<div class="admin-stats">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-box"><div class="stat-number">{total}</div><div class="stat-label">Total Contestants</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-box"><div class="stat-number">{approved}</div><div class="stat-label">Approved</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-box"><div class="stat-number">{pending}</div><div class="stat-label">Pending</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-box"><div class="stat-number">{total_votes}</div><div class="stat-label">Total Votes</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        # Pending contestants list and approve/reject buttons would go here (omitted for brevity)
        conn.close()
    elif password:
        st.error("Incorrect password.")

def contact_support_page():
    st.markdown('<h2>Contact Support</h2>', unsafe_allow_html=True)
    st.write(
        f"""
        For any questions, issues, or assistance, please reach out to our support team:

        - 📧 Email: {SUPPORT_EMAIL}
        - 📱 WhatsApp: {SUPPORT_PHONE}

        We are here to help you with registration, voting, or any other inquiries.
        """
    )

# === SIDEBAR ===

with st.sidebar:
    show_logo(width=140)
    st.markdown("## Navigation")
    menu_options = [
        "Home",
        "Contestants",
        "Register",
        "Admin",
        "Contact Support"
    ]
    page = st.radio("", menu_options)

# === PAGE ROUTING ===

if page == "Home":
    home_page()
elif page == "Contestants":
    contestants_page()
elif page == "Register":
    registration_page()
elif page == "Admin":
    admin_page()
elif page == "Contact Support":
    contact_support_page()
else:
    st.write("Page not found.")
