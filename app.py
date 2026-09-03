```python
import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import streamlit as st
from PIL import Image

# ============================================================
# NEXERA CONFIGURATION
# ============================================================

APP_NAME = "NEXERA"
TAGLINE = "Step Into Your Next Era"

SUPPORT_EMAIL = "nexerasupport142@gmail.com"
SUPPORT_PHONE = "09018479293"

VOTE_PRICE = 200
OPAY_ACCOUNT = "9018479293"
OPAY_NAME = "Nexera"

# Registration and voting dates
REGISTRATION_START = datetime(2026, 9, 1, 0, 0, 0)  # Registration opens now (example)
VOTING_START = datetime(2026, 10, 1, 0, 0, 0)
VOTING_END = datetime(2026, 11, 1, 23, 59, 0)

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "nexera.db"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"

ADMIN_PASSWORD = "RavenNexera2026!"

APP_BASE_URL = ""  # Leave empty or set your app base URL here if needed

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="NEXERA — Step Into Your Next Era",
    page_icon="🖤",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# DATABASE
# ============================================================

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

    columns = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(candidates)").fetchall()
    }

    if "why_money" not in columns:
        conn.execute(
            "ALTER TABLE candidates ADD COLUMN why_money TEXT DEFAULT ''"
        )

    conn.commit()
    conn.close()

init_db()

# ============================================================
# STATUS CHECKS
# ============================================================

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

REGISTRATION_STATUS = registration_status()
VOTING_STATUS = voting_status()

# ============================================================
# HELPERS
# ============================================================

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")

def unique_slug(name, code):
    base = slugify(name)
    if not base:
        base = "contestant"
    return f"{base}-{code}"

def generate_code():
    conn = get_connection()
    while True:
        import random
        code = str(random.randint(1000, 9999))
        exists = conn.execute(
            "SELECT id FROM candidates WHERE code = ?", (code,)
        ).fetchone()
        if not exists:
            conn.close()
            return code

def candidate_link(slug):
    if APP_BASE_URL:
        return f"{APP_BASE_URL.rstrip('/')}?candidate={quote(slug)}"
    return f"?candidate={quote(slug)}"

def get_candidate_by_slug(slug):
    conn = get_connection()
    candidate = conn.execute(
        "SELECT * FROM candidates WHERE slug = ?", (slug,)
    ).fetchone()
    conn.close()
    return candidate

def get_approved_candidates(search=""):
    conn = get_connection()
    if search:
        like = f"%{search}%"
        rows = conn.execute(
            """
            SELECT *
            FROM candidates
            WHERE status = 'approved'
            AND (
                full_name LIKE ?
                OR code LIKE ?
                OR talent_category LIKE ?
            )
            ORDER BY votes DESC, created_at ASC
            """,
            (like, like, like),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT *
            FROM candidates
            WHERE status = 'approved'
            ORDER BY votes DESC, created_at ASC
            """
        ).fetchall()
    conn.close()
    return rows

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

# ============================================================
# LOGO DISPLAY FUNCTION
# ============================================================

def show_logo():
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=180)
    else:
        st.markdown("<h2 style='font-weight:900;'>NEXERA</h2>", unsafe_allow_html=True)

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:
    show_logo()
    st.markdown("## NEXERA")
    menu_options = [
        "Home",
        "Contestants",
        "Register",
        "About",
        "Rules & FAQ",
        "Admin",
    ]
    page = st.radio("Navigation", menu_options)
    st.markdown("---")
    st.markdown(
        f"""
**Competition**

🗓️ Registration Opens: **{REGISTRATION_START.strftime('%B %d, %Y')}**

🗓️ Voting Starts: **{VOTING_START.strftime('%B %d, %Y')}**

⏰ Voting Ends: **{VOTING_END.strftime('%B %d, %Y — %I:%M %p')}**

💰 Vote: **₦{VOTE_PRICE:,}**

OPay: **{OPAY_ACCOUNT}**

Account: **{OPAY_NAME}**
"""
    )

# ============================================================
# PAGES
# ============================================================

def home_page():
    st.markdown(
        f"""
        <div class="hero">
            <h1>NEXERA</h1>
            <p>{TAGLINE}</p>
            <p style="color:white;font-size:16px;">
                Nigeria's premier youth empowerment platform.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="section-title">About NEXERA</div>
        <p>
        NEXERA is built to discover talent, mobilize communities, and create economic opportunities for young Nigerians.
        Whether you're an influencer, model, content creator, or building a small or medium-scale business, NEXERA gives you an opportunity to tell your story and receive community support.
        </p>
        """,
        unsafe_allow_html=True,
    )
    if VOTING_STATUS == "ended":
        st.markdown("<div class='over'>COMPETITION OVER</div>", unsafe_allow_html=True)
        st.write("Thank you to everyone who participated in NEXERA.")
    elif VOTING_STATUS == "upcoming":
        st.info("NEXERA voting will open on October 1, 2026.")
    else:
        st.success("NEXERA competition is LIVE. Registration and voting are currently open.")
    st.markdown("<div class='section-title'>How It Works</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 01 — Register\nSubmit your details, photo, category and your story.")
    with col2:
        st.markdown("### 02 — Mobilize Support\nShare your personal NEXERA contestant link and encourage your community to vote.")
    with col3:
        st.markdown("### 03 — Earn & Be Rewarded\nContestants with the highest verified votes compete for NEXERA rewards.")
    st.markdown('<div class="section-title">Prize Fund</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("1st Place", "₦120,000")
    with c2:
        st.metric("2nd Place", "₦50,000")
    with c3:
        st.metric("3rd Place", "₦30,000")
    st.info("Additional cash prizes, grants and empowerment rewards may also be awarded.")

def contestants_page():
    st.markdown('<div class="section-title">NEXERA Contestants</div>', unsafe_allow_html=True)
    if VOTING_STATUS == "ended":
        st.markdown("<div class='over'>COMPETITION OVER</div>", unsafe_allow_html=True)
    search = st.text_input("Search contestant", placeholder="Name, code or category...")
    candidates = get_approved_candidates(search)
    if not candidates:
        st.info("No approved contestants found.")
        return
    for index in range(0, len(candidates), 2):
        cols = st.columns(2)
        for position, col in enumerate(cols):
            candidate_index = index + position
            if candidate_index >= len(candidates):
                continue
            candidate = candidates[candidate_index]
            with col:
                rank = candidate_index + 1
                st.markdown(
                    f"""
                    <div class="card">
                        <span class="rank">{rank}</span>
                        &nbsp;
                        <span class="code">NEXERA {candidate['code']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if image_exists(candidate["image_path"]):
                    st.image(candidate["image_path"], use_container_width=True)
                else:
                    st.info("Contestant photo unavailable.")
                st.subheader(candidate["full_name"])
                st.write(f"**Category:** {candidate['talent_category']}")
                st.markdown(
                    f"""
                    <div class="vote-count">{candidate['votes']:,}</div>
                    <div class="verified">VERIFIED VOTES</div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(f"**Why they need the money:** {candidate['why_money']}")
                profile_url = candidate_link(candidate["slug"])
                st.markdown(f"[View contestant profile]({profile_url})")
                if VOTING_STATUS == "active":
                    if st.button(f"VOTE FOR {candidate['full_name']}", key=f"vote_{candidate['id']}", use_container_width=True):
                        st.session_state[f"show_vote_{candidate['id']}"] = True
                    if st.session_state.get(f"show_vote_{candidate['id']}", False):
                        st.markdown(
                            """
                            ### How to Vote

                            1. Send **₦200 per vote** to:

                            **OPay:** 9018479293  
                            **Account Name:** Nexera

                            2. Send your payment screenshot to:

                            **WhatsApp: 09018479293**

                            Or ensure the contestant's name is included
                            in the payment narration.

                            Your vote will be verified before it is added.
                            """
                        )

def registration_page():
    st.markdown('<div class="section-title">Register for NEXERA</div>', unsafe_allow_html=True)
    if REGISTRATION_STATUS != "active":
        if REGISTRATION_STATUS == "upcoming":
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
        st.markdown("### Upload Your Photo")
        photo = st.file_uploader("Upload a clear photo of yourself *", type=["jpg", "jpeg", "png"])
        st.markdown("### Tell Us About Yourself")
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

def about_page():
    st.markdown('<div class="section-title">About NEXERA</div>', unsafe_allow_html=True)
    st.write(
        """
        NEXERA is Nigeria's premier youth empowerment platform designed to discover talent, mobilize communities, and create economic opportunities for young Nigerians.
        
        Whether you are an influencer, model, content creator, or entrepreneur, NEXERA provides a platform to showcase your talent, share your story, and gain community support.
        
        Our mission is to empower the youth by providing opportunities for growth, recognition, and financial rewards.
        """
    )

def rules_faq_page():
    st.markdown('<div class="section-title">Rules & FAQ</div>', unsafe_allow_html=True)
    st.write(
        """
        **Rules:**
        - All contestants must be Nigerian youths.
        - Submissions must be original and truthful.
        - Voting costs ₦200 per vote.
        - Votes must be verified before counting.
        
        **FAQ:**
        - *When does registration open?* September 1, 2026.
        - *When does voting start?* October 1, 2026.
        - *How do I vote?* Send ₦200 per vote to the OPay account and submit proof.
        - *Who can participate?* Anyone fitting the talent categories listed.
        """
    )

def admin_page():
    st.markdown('<div class="section-title">Admin Panel</div>', unsafe_allow_html=True)
    password = st.text_input("Enter admin password", type="password")
    if password == ADMIN_PASSWORD and ADMIN_PASSWORD != "":
        st.success("Access granted.")
        # Add admin functionalities here
    elif password:
        st.error("Incorrect password.")

# ============================================================
# PAGE ROUTING
# ============================================================

if __name__ == "__main__":
    with st.sidebar:
        show_logo()
    if 'page' not in st.session_state:
        st.session_state.page = "Home"

    page = st.sidebar.radio("Navigation", ["Home", "Contestants", "Register", "About", "Rules & FAQ", "Admin"])

    if page == "Home":
        home_page()
    elif page == "Contestants":
        contestants_page()
    elif page == "Register":
        registration_page()
    elif page == "About":
        about_page()
    elif page == "Rules & FAQ":
        rules_faq_page()
    elif page == "Admin":
        admin_page()
    else:
        st.write("Page not found.")
```
