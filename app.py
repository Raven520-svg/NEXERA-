import streamlit as st
from datetime import datetime
import sqlite3
import re
import random
import pandas as pd
from pathlib import Path
from PIL import Image

# === CONFIGURATION ===
APP_NAME = "NEXERA"
TAGLINE = "Empowering Transparent Elections"
WHATSAPP_CHANNEL = "https://whatsapp.com/channel/0029VbDJzRsGpLHMGlw2at0n"

# BRAND COLORS
NAVY = "#0A1F44"
GOLD = "#D4AF37"
GREEN = "#25D366"
RED = "#DC2626"
BG_GRAY = "#F8FAFC"

SUPPORT_EMAIL = "nexerasupport142@gmail.com"
SUPPORT_PHONE = "09018479293"

VOTE_PRICE = 200
OPAY_ACCOUNT = "9018479293"
OPAY_NAME = "Nexera"

PRIZES = {
    "1st Place": "₦120,000 + Business Grant",
    "2nd Place": "₦50,000 + Mentorship",
    "3rd Place": "₦30,000 + Equipment"
}

REGISTRATION_START = datetime(2026, 9, 1, 0, 0, 0)
VOTING_START = datetime(2026, 10, 1, 0, 0, 0)
VOTING_END = datetime(2026, 11, 1, 23, 59, 0)

ADMIN_PASSWORD = "RavenNexera2026!"

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "nexera.db"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# === SESSION STATE FOR POPUP GATE ===
if "whatsapp_confirmed" not in st.session_state:
    st.session_state.whatsapp_confirmed = False

# === PAGE CONFIG ===
st.set_page_config(
    page_title=f"{APP_NAME} — {TAGLINE}",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# === CSS STYLES ===
def local_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800;900&display=swap');
        html, body, [class*="st-"] {{ font-family: 'Poppins', sans-serif; }}
       .main {{ background-color: {BG_GRAY}; }}

       .whatsapp-banner {{
            background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
            color: white; padding: 1rem; text-align: center; font-weight: 700; font-size: 1.1rem;
            position: sticky; top: 0; z-index: 999; border-radius: 0 0 12px 12px; margin-bottom: 1rem;
        }}
       .whatsapp-banner a {{ color: {NAVY}; text-decoration: none; background: {GOLD}; padding: 0.5rem 1.2rem; border-radius: 8px; margin-left: 1rem; font-weight: 900; }}

       .popup-overlay {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.9); z-index: 10000; display: flex; align-items: center; justify-content: center;
        }}
       .popup-box {{
            background: white; padding: 3rem; border-radius: 20px; max-width: 600px; text-align: center;
            border-top: 8px solid {GREEN};
        }}
       .popup-title {{ font-size: 2rem; font-weight: 900; color: {NAVY}; margin-bottom: 1rem; }}

       .hero {{
            background: linear-gradient(135deg, {NAVY} 0%, #1e3a8a 100%);
            padding: 5rem 2rem; border-radius: 16px; color: white; text-align: center; margin-bottom: 3rem;
        }}
       .hero-title {{ font-size: 3.5rem; font-weight: 900; letter-spacing: 0.05em; color: {GOLD}; margin-bottom: 0.5rem; }}
       .hero-tagline {{ font-size: 1.4rem; font-weight: 400; margin-bottom: 2rem; }}

       .cta-button {{
            background-color: {GOLD}; color: {NAVY}; padding: 1rem 2.5rem; border-radius: 10px;
            font-weight: 800; font-size: 1.1rem; text-decoration: none; display: inline-block; margin: 0.5rem;
        }}

       .section-title {{ color: {NAVY}; font-size: 2.2rem; font-weight: 800; margin-top: 3rem; margin-bottom: 1.5rem; }}

       .stat-box {{
            background-color: white; padding: 2rem; border-radius: 12px; text-align: center;
            border-top: 5px solid {GOLD}; box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        }}
       .stat-number {{ font-size: 2.5rem; font-weight: 900; color: {NAVY}; }}
       .stat-label {{ font-size: 1rem; color: #64748b; font-weight: 600; }}

       .why-card {{
            background: white; padding: 2rem; border-radius: 12px; border-left: 6px solid {GOLD};
            height: 100%; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }}

       .admin-stats {{ display: flex; gap: 1.5rem; margin-bottom: 2rem; flex-wrap: wrap; }}
       .candidate-card {{ background: white; padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; border: 1px solid #e2e8f0; }}

        footer {{ text-align: center; margin-top: 4rem; padding: 2rem; background: {NAVY}; color: white; border-radius: 12px; }}
        </style>
        """,
        unsafe_allow_html=True,
    )
local_css()

# === FORCED POPUP FUNCTION ===
def show_whatsapp_gate():
    if not st.session_state.whatsapp_confirmed:
        st.markdown('<div class="popup-overlay">', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="popup-box">', unsafe_allow_html=True)
            st.markdown('<h2 class="popup-title">📢 MUST FOLLOW FIRST</h2>', unsafe_allow_html=True)
            st.write("To ensure you get all NEXERA updates, results, and announcements, you MUST follow our official WhatsApp Channel.")
            st.markdown(f'<a href="{WHATSAPP_CHANNEL}" target="_blank" style="background:{GREEN}; color:white; padding:1rem 2rem; border-radius:10px; font-weight:800; text-decoration:none; font-size:1.2rem;">Follow NEXERA Channel</a>', unsafe_allow_html=True)
            st.write("")
            if st.button("✅ I HAVE FOLLOWED THE CHANNEL", use_container_width=True, type="primary"):
                st.session_state.whatsapp_confirmed = True
                st.rerun()
            st.caption("You will not be able to register or vote without following.")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Show banner
st.markdown(f'''
<div class="whatsapp-banner">
📢 MUST FOLLOW: Get live updates and results
<a href="{WHATSAPP_CHANNEL}" target="_blank">Follow Channel</a>
</div>
''', unsafe_allow_html=True)

show_whatsapp_gate()

# === DATABASE ===
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""CREATE TABLE IF NOT EXISTS voters (id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT NOT NULL, phone TEXT UNIQUE NOT NULL, email TEXT, state TEXT, lga TEXT, status TEXT DEFAULT 'active', created_at TEXT NOT NULL)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS candidates (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE NOT NULL, slug TEXT UNIQUE NOT NULL, full_name TEXT NOT NULL, talent_category TEXT NOT NULL, phone TEXT NOT NULL, email TEXT NOT NULL, state TEXT, lga TEXT, bio TEXT NOT NULL, why_money TEXT NOT NULL, image_path TEXT, votes INTEGER DEFAULT 0, status TEXT DEFAULT 'pending', rejection_reason TEXT, created_at TEXT NOT NULL)""")
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
        exists = conn.execute("SELECT id FROM candidates WHERE code =?", (code,)).fetchone()
        if not exists:
            conn.close()
            return code

def unique_slug(name, code):
    base = slugify(name)
    if not base: base = "contestant"
    return f"{base}-{code}"

def save_uploaded_image(uploaded_file, code):
    if uploaded_file is None: return None
    try:
        image = Image.open(uploaded_file).convert("RGB")
        image = image.resize((800, 800))
        filename = f"{code}.jpg"
        destination = UPLOAD_DIR / filename
        image.save(destination, "JPEG", quality=90)
        return str(destination)
    except Exception: return None

def image_exists(path): return bool(path) and Path(path).exists()
def validate_nexera_text(text): return "nexera" in text.lower()

def registration_status():
    now = datetime.now()
    if now < REGISTRATION_START: return "upcoming"
    if now >= VOTING_START: return "closed"
    return "active"

def voting_status():
    now = datetime.now()
    if now < VOTING_START: return "upcoming"
    if now > VOTING_END: return "ended"
    return "active"

def export_csv(query, filename):
    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    st.download_button("Download CSV", df.to_csv(index=False).encode('utf-8'), filename, "text/csv")

# === PAGES ===
def home_page():
    st.markdown(f'<div class="hero"><h1 class="hero-title">{APP_NAME}</h1><p class="hero-tagline">{TAGLINE}</p>', unsafe_allow_html=True)
    st.markdown(f'<a href="{WHATSAPP_CHANNEL}" target="_blank" class="cta-button">📢 Follow WhatsApp Channel</a>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.markdown('<a href="#register" class="cta-button">Register to Vote</a>', unsafe_allow_html=True)
    with c2: st.markdown('<a href="#contestants" class="cta-button">View Candidates</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    conn = get_connection()
    total_voters = conn.execute("SELECT COUNT(*) FROM voters").fetchone()[0]
    approved = conn.execute("SELECT COUNT(*) FROM candidates WHERE status = 'approved'").fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM candidates WHERE status = 'pending'").fetchone()[0]
    total_votes = conn.execute("SELECT SUM(votes) FROM candidates").fetchone()[0] or 0
    conn.close()

    st.markdown('<div class="admin-stats">', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-box"><div class="stat-number">{total_voters}</div><div class="stat-label">Registered Voters</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-box"><div class="stat-number">{approved}</div><div class="stat-label">Approved Candidates</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-box"><div class="stat-number">{total_votes}</div><div class="stat-label">Total Votes Cast</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-box"><div class="stat-number">{pending}</div><div class="stat-label">Pending Applications</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<h2 class="section-title">About NEXERA</h2>', unsafe_allow_html=True)
    st.write("NEXERA is a next-generation civic platform built to strengthen democracy through technology and transparency. We provide a secure, accessible system for voter registration, candidate management, and election monitoring. Our mission is to give every citizen a voice while ensuring institutions have the tools to run fair, credible, and accountable elections.")

    st.markdown('<h2 class="section-title">What’s At Stake</h2>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="why-card"><h4>🗳️ Your Voice</h4><p>Decide leadership, policies, and the future of your community. Every vote counts.</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="why-card"><h4>📈 Real Impact</h4><p>Elect leaders who deliver on jobs, security, education, health, and infrastructure.</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="why-card"><h4>🔍 Full Transparency</h4><p>Track registrations and results live. No more doubts, no more fraud.</p></div>', unsafe_allow_html=True)

    st.markdown('<h2 class="section-title">Prize Fund & Rewards</h2>', unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3)
    p1.metric("1st Place", PRIZES["1st Place"])
    p2.metric("2nd Place", PRIZES["2nd Place"])
    p3.metric("3rd Place", PRIZES["3rd Place"])

def voter_registration_page():
    if not st.session_state.whatsapp_confirmed:
        st.warning("⚠️ Please follow the WhatsApp channel first to continue.")
        return

    st.markdown('<h2 class="section-title">Voter Registration</h2>', unsafe_allow_html=True)
    status = registration_status()
    if status!= "active":
        st.warning("Voter registration is currently closed.") if status=="closed" else st.info("Voter registration opens Sept 1, 2026.")
        return

    with st.form("voter_form"):
        full_name = st.text_input("Full Name *")
        phone = st.text_input("Phone Number *")
        email = st.text_input("Email Address")
        state = st.text_input("State *")
        lga = st.text_input("LGA *")
        submitted = st.form_submit_button("REGISTER AS VOTER", use_container_width=True)

    if submitted:
        if not all([full_name, phone, state, lga]):
            st.error("Please fill all required fields.")
            return
        try:
            conn = get_connection()
            conn.execute("INSERT INTO voters (full_name, phone, email, state, lga, created_at) VALUES (?,?,?,?,?,?)",
                         (full_name, phone, email, state, lga, datetime.now().isoformat()))
            conn.commit(); conn.close()
            st.success(f"✅ Registration successful! Welcome {full_name}. You can now vote when it opens.")
        except sqlite3.IntegrityError:
            st.error("This phone number is already registered.")

def contestants_page():
    if not st.session_state.whatsapp_confirmed:
        st.warning("⚠️ Please follow the WhatsApp channel first to view contestants.")
        return

    st.markdown('<h2 class="section-title">NEXERA Contestants</h2>', unsafe_allow_html=True)
    conn = get_connection()
    search = st.text_input("Search contestant", placeholder="Name, code or category...")
    query = "SELECT * FROM candidates WHERE status = 'approved'"
    params = []
    if search:
        like = f"%{search}%"
        query += " AND (full_name LIKE? OR code LIKE? OR talent_category LIKE?)"
        params = [like, like, like]
    query += " ORDER BY votes DESC, created_at ASC"
    candidates = conn.execute(query, params).fetchall()
    conn.close()

    voting_active = voting_status() == "active"
    if not candidates: st.info("No approved contestants yet.")

    for i in range(0, len(candidates), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i+j >= len(candidates): continue
            c = candidates[i+j]
            with col:
                st.markdown(f'<div class="candidate-card">', unsafe_allow_html=True)
                st.markdown(f"### #{i+j+1} — NEXERA {c['code']}")
                if image_exists(c["image_path"]): st.image(c["image_path"], use_container_width=True)
                st.subheader(c["full_name"])
                st.write(f"**Category:** {c['talent_category']} | **Location:** {c['state']}")
                st.markdown(f"### {c['votes']:,} VERIFIED VOTES")
                st.write(f"**Bio:** {c['bio']}")
                st.write(f"**Why they need support:** {c['why_money']}")
                if voting_active:
                    st.success(f"Support with ₦{VOTE_PRICE}/vote → {OPAY_ACCOUNT} ({OPAY_NAME})")
                st.markdown('</div>', unsafe_allow_html=True)

def candidate_registration_page():
    if not st.session_state.whatsapp_confirmed:
        st.warning("⚠️ Please follow the WhatsApp channel first to continue.")
        return

    st.markdown('<h2 class="section-title">Apply as Candidate</h2>', unsafe_allow_html=True)
    status = registration_status()
    if status!= "active":
        st.warning("Candidate registration is currently closed.") if status=="closed" else st.info("Registration opens Sept 1, 2026.")
        return

    with st.form("candidate_form"):
        full_name = st.text_input("Full Name *")
        phone = st.text_input("Phone Number *")
        email = st.text_input("Email Address *")
        category = st.selectbox("Category *", ["Influencer", "Modeling", "Content Creator", "SME", "Tech", "Art"])
        state = st.text_input("State *")
        lga = st.text_input("LGA *")
        photo = st.file_uploader("Upload Clear Photo *", type=["jpg", "jpeg", "png"])
        bio = st.text_area("Tell us what you do *", height=120)
        why_money = st.text_area("Why do you need the money? * Must include 'NEXERA'", height=150)
        submitted = st.form_submit_button("SUBMIT APPLICATION", use_container_width=True)

    if submitted:
        errors = []
        if not all([full_name, phone, email, category, state, lga, photo, bio, why_money]): errors.append("Please fill all required fields.")
        if not validate_nexera_text(why_money): errors.append("INVALID: Your write-up must contain the word NEXERA.")
        if errors: [st.error(e) for e in errors]
        else:
            code = generate_code(); slug = unique_slug(full_name, code); image_path = save_uploaded_image(photo, code)
            conn = get_connection()
            conn.execute("INSERT INTO candidates (code, slug, full_name, talent_category, phone, email, state, lga, bio, why_money, image_path, created_at) VALUES (?,?,?,?,?,?,?,?)",
                         (code, slug, full_name, category, phone, email, state, lga, bio, why_money, image_path, datetime.now().isoformat()))
            conn.commit(); conn.close()
            st.success(f"Application submitted! Your code: NEXERA {code}. Awaiting admin approval.")

def admin_page():
    st.markdown('<h2 class="section-title">Admin Dashboard</h2>', unsafe_allow_html=True)
    password = st.text_input("Enter admin password", type="password")
    if password!= ADMIN_PASSWORD:
        if password: st.error("Incorrect password.")
        return

    st.success("Access granted.")
    conn = get_connection()
    total_voters = conn.execute("SELECT COUNT(*) FROM voters").fetchone()[0]
    total = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
    approved = conn.execute("SELECT COUNT(*) FROM candidates WHERE status = 'approved'").fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM candidates WHERE status = 'pending'").fetchone()[0]
    rejected = conn.execute("SELECT COUNT(*) FROM candidates WHERE status = 'rejected'").fetchone()[0]
    total_votes = conn.execute("SELECT SUM(votes) FROM candidates").fetchone()[0] or 0

    st.markdown('<div class="admin-stats">', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-box"><div class="stat-number">{total_voters}</div><div class="stat-label">Total Voters</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-box"><div class="stat-number">{total}</div><div class="stat-label">Total Candidates</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-box"><div class="stat-number">{approved}</div><div class="stat-label">Approved</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-box"><div class="stat-number">{pending}</div><div class="stat-label">Pending</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-box"><div class="stat-number">{total_votes}</div><div class="stat-label">Total Votes</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["Candidate Management", "Voter Management", "Analytics", "Exports"])

    with tab1:
        st.subheader("All Candidates")
        candidates = conn.execute("SELECT * FROM candidates ORDER BY created_at DESC").fetchall()
        for c in candidates:
            with st.expander(f"{c['full_name']} - NEXERA {c['code']} - Status: {c['status'].upper()}"):
                st.write(f"**Category:** {c['talent_category']} | **Votes:** {c['votes']} | **Location:** {c['state']}, {c['lga']}")
                st.write(f"**Bio:** {c['bio']}")
                st.write(f"**Why:** {c['why_money']}")
                if image_exists(c["image_path"]): st.image(c["image_path"], width=200)
                if c['status'] == 'pending':
                    colA, colB = st.columns(2)
                    if colA.button("✅ Accept", key=f"a{c['id']}"):
                        conn.execute("UPDATE candidates SET status='approved' WHERE id=?", (c['id'],)); conn.commit(); st.rerun()
                    reason = st.text_input("Rejection reason", key=f"reason{c['id']}")
                    if colB.button("❌ Reject", key=f"r{c['id']}"):
                        conn.execute("UPDATE candidates SET status='rejected', rejection_reason=? WHERE id=?", (reason, c['id'])); conn.commit(); st.rerun()
    
    with tab2:
        st.subheader("Voter Management")
        voters = conn.execute("SELECT * FROM voters ORDER BY created_at DESC").fetchall()
        st.write(f"Total Voters: {len(voters)}")
        for v in voters:
            st.write(f"{v['full_name']} | {v['phone']} | {v['state']} | {v['lga']} | {v['status']}")

    with tab3:
        st.subheader("Analytics")
        df_state = pd.read_sql_query("SELECT state, COUNT(*) as count FROM voters GROUP BY state", conn)
        df_category = pd.read_sql_query("SELECT talent_category, COUNT(*) as count FROM candidates GROUP BY talent_category", conn)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Voters by State**")
            if not df_state.empty: st.bar_chart(df_state.set_index('state'))
            else: st.info("No voter data yet")
        with col2:
            st.markdown("**Candidates by Category**")
            if not df_category.empty: st.bar_chart(df_category.set_index('talent_category'))
            else: st.info("No candidate data yet")

    with tab4:
        st.subheader("Export Data")
        st.write("Download all data as CSV")
        export_csv("SELECT * FROM voters", "nexera_voters.csv")
        export_csv("SELECT * FROM candidates", "nexera_candidates.csv")
        export_csv("SELECT * FROM votes", "nexera_votes.csv")
    conn.close()

def contact_support_page():
    st.markdown('<h2 class="section-title">Contact Support</h2>', unsafe_allow_html=True)
    st.write("Need help with registration, voting, or your application?")
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"📧 Email: {SUPPORT_EMAIL}")
        st.info(f"📱 WhatsApp: {SUPPORT_PHONE}")
        st.markdown(f"### 📢 Official Channel\n[Follow NEXERA on WhatsApp]({WHATSAPP_CHANNEL})")
    with c2:
        with st.form("support_form"):
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            message = st.text_area("Message")
            if st.form_submit_button("Send Message"):
                st.success("Message received. We will respond within 24 hours.")

    st.markdown("### FAQ")
    with st.expander("How do I vote?"): st.write(f"Send ₦{VOTE_PRICE} per vote to {OPAY_ACCOUNT} ({OPAY_NAME}) and send proof to support.")
    with st.expander("When does voting start?"): st.write("October 1, 2026")
    with st.expander("When does registration end?"): st.write("September 30, 2026")
    with st.expander("How are winners decided?"): st.write("By highest number of verified votes at the end of voting period.")

# === SIDEBAR ===
with st.sidebar:
    st.markdown(f"<h1 style='color:{NAVY}; font-weight:900;'>{APP_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{GOLD}; font-weight:600;'>{TAGLINE}</p>", unsafe_allow_html=True)
    if st.session_state.whatsapp_confirmed:
        st.success("✅ WhatsApp Channel Followed")
    else:
        st.error("❌ Follow Channel to Unlock")
    st.markdown(f"<a href='{WHATSAPP_CHANNEL}' target='_blank' style='background:{GREEN}; color:white; padding:0.7rem; border-radius:8px; text-decoration:none; font-weight:700; display:block; text-align:center;'>📢 Follow Channel</a>", unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("Navigation", ["Home", "Voter Registration", "Contestants", "Apply as Candidate", "Admin", "Contact Support"])

# === ROUTING ===
if page == "Home": home_page()
elif page == "Voter Registration": voter_registration_page()
elif page == "Contestants": contestants_page()
elif page == "Apply as Candidate": candidate_registration_page()
elif page == "Admin": admin_page()
elif page == "Contact Support": contact_support_page()

st.markdown(f"<footer>© 2026 {APP_NAME}. All Rights Reserved. | <a href='{WHATSAPP_CHANNEL}' style='color:{GOLD};'>Follow us on WhatsApp</a></footer>", unsafe_allow_html=True)
