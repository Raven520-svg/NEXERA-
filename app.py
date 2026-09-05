import streamlit as st
import sqlite3
import os
from datetime import datetime, timedelta
import pandas as pd

# ========== SETTINGS ==========
DB_NAME = "nexera.db"
UPLOAD_DIR = "uploads"
PROOF_DIR = "proofs"
CHANNEL_LINK = "https://whatsapp.com/channel/0029VbDJzRsGpLHMGlw2at0n"
VOTING_ACCOUNT = {"Bank": "OPAY", "Account Name": "NEXERA SUPPORT", "Account No": "9123456789"} # CHANGE THIS
VOTE_PRICE = 200
ADMIN_PASSWORD = "nexera2026" # CHANGE THIS
SUPPORT_EMAIL = "nexerasupport142@gmail.com"
SUPPORT_WHATSAPP = "09018479293"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROOF_DIR, exist_ok=True)

# ========== PAGE CONFIG + CSS ==========
st.set_page_config(page_title="NEXERA - Your Next Era", page_icon="✨", layout="wide")
st.markdown("""
<style>
.main {background-color: #000; color: white;}
.stButton>button {background-color: #B91C1C; color: white; border-radius: 8px; width: 100%; border: none; font-weight: bold; padding: 10px;}
.stButton>button:hover {background-color: #991B1B;}
.contestant-card {border: 1px solid #333; border-radius: 10px; padding: 15px; background-color: #111; margin-bottom: 15px;}
.prize-box {text-align: center; border: 2px solid #FFD700; border-radius: 10px; padding: 15px; background-color: #1a1a1a;}
.channel-banner {background-color: #25D366; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 20px;}
.channel-banner a {color: white; font-weight: bold; text-decoration: none; font-size: 17px;}
.account-box {border: 2px dashed #FFD700; padding: 15px; border-radius: 10px; background-color: #1a1a1a; margin-bottom: 15px;}
h1, h2, h3, h4 {color: white;}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""<div class="channel-banner">📢 <a href="{CHANNEL_LINK}" target="_blank">JOIN NEXERA WHATSAPP CHANNEL FOR UPDATES</a></div>""", unsafe_allow_html=True)

# ========== DATABASE ==========
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS submissions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, talent TEXT, bank TEXT, photo TEXT,
                  reason TEXT, state TEXT, location TEXT, status TEXT DEFAULT 'pending', created_at TEXT, votes INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS votes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, contestant_id INTEGER, voter_name TEXT, voter_phone TEXT,
                  proof TEXT, status TEXT DEFAULT 'pending', created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
    defaults = [('voting_active', '0'), ('voting_start', ''), ('voting_end', '')]
    for key, value in defaults:
        c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)", (key, value))
    conn.commit()
    conn.close()

def get_setting(key):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key =?", (key,)); res = c.fetchone()
    conn.close(); return res[0] if res else ""

def set_setting(key, value):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("UPDATE settings SET value =? WHERE key =?", (value, key))
    conn.commit(); conn.close()

init_db()

NIGERIA_STATES = ["Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno", "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "FCT Abuja", "Gombe", "Imo", "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara"]
CATEGORIES = ["Music", "Dance", "Comedy", "Content Creator", "Fashion Design", "Food & Catering", "Beauty & Makeup", "Barbing", "Tech & App Development", "Art & Painting", "Crafts", "Farming", "Sports", "Other"]

st.title("✨ NEXERA")
st.subheader("STEP INTO YOUR NEXT ERA")
st.write("**Community Support: Every ₦200 vote goes DIRECTLY to contestants** 💛")
menu = st.tabs(["🏠 Home", "🗳️ Vote", "📝 Submit", "ℹ️ About", "⚙️ Admin"])

def show_countdown():
    end = get_setting('voting_end')
    if end:
        try:
            end_time = datetime.fromisoformat(end)
            now = datetime.now()
            if now < end_time:
                remaining = end_time - now
                days, seconds = remaining.days, remaining.seconds
                hours = seconds // 3600; minutes = (seconds % 3600) // 60
                st.info(f"⏰ Voting Ends In: {days}d {hours}h {minutes}m")
            else: st.error("Voting has ended")
        except: pass

with menu[0]:
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown('<div class="prize-box">', unsafe_allow_html=True); st.metric("🥇 1st Place", "₦120,000"); st.markdown('</div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="prize-box">', unsafe_allow_html=True); st.metric("🥈 2nd Place", "₦70,000"); st.markdown('</div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="prize-box">', unsafe_allow_html=True); st.metric("🥉 3rd Place", "₦30,000"); st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("🔥 Top Contestants")
    conn = sqlite3.connect(DB_NAME); df = pd.read_sql("SELECT * FROM submissions WHERE status='approved' ORDER BY votes DESC LIMIT 6", conn); conn.close()
    if not df.empty:
        cols = st.columns(2)
        for i, row in df.iterrows():
            with cols[i % 2]:
                st.markdown('<div class="contestant-card">', unsafe_allow_html=True)
                if row['photo'] and os.path.exists(row['photo']): st.image(row['photo'], use_column_width=True)
                st.write(f"### {row['name']}"); st.write(f"**Category:** {row['talent']} | **State:** {row['state']}")
                st.write(f"**Reason for Capital:** {row['reason']}"); st.write(f"**VERIFIED VOTES:** {row['votes']}")
                st.markdown('</div>', unsafe_allow_html=True)
    else: st.info("No contestants yet. Be the first to submit!")

with menu[1]:
    show_countdown(); voting_active = get_setting('voting_active') == '1'
    if not voting_active: st.error("🚫 Voting is currently CLOSED. Please check back later.")
    else:
        st.subheader("Vote for Your Favorite"); st.warning(f"Each vote is ₦{VOTE_PRICE}. 100% goes to the contestant")
        conn = sqlite3.connect(DB_NAME); df = pd.read_sql("SELECT * FROM submissions WHERE status='approved' ORDER BY votes DESC", conn); conn.close()
        if not df.empty:
            for i in range(0, len(df), 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < len(df):
                        row = df.iloc[i + j]
                        with cols[j]:
                            st.markdown('<div class="contestant-card">', unsafe_allow_html=True)
                            if row['photo'] and os.path.exists(row['photo']): st.image(row['photo'], use_column_width=True)
                            st.write(f"### {row['name']}"); st.write(f"**{row['talent']} - {row['state']}**")
                            st.write(f"**Reason:** {row['reason']}"); st.write(f"**VERIFIED VOTES:** {row['votes']}")
                            if st.button("VOTE NOW", key=f"vote_btn_{row['id']}"): st.session_state['voting_for'] = row['id']; st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
            if 'voting_for' in st.session_state:
                contestant = df[df['id'] == st.session_state['voting_for']].iloc[0]
                with st.form("vote_form"):
                    st.subheader(f"Vote for {contestant['name']}")
                    st.markdown(f"""<div class="account-box"><h4>Step 1: Pay ₦{VOTE_PRICE} to:</h4><p><b>Bank:</b> {VOTING_ACCOUNT['Bank']}<br><b>Account Name:</b> {VOTING_ACCOUNT['Account Name']}<br><b>Account No:</b> {VOTING_ACCOUNT['Account No']}</p></div>""", unsafe_allow_html=True)
                    st.write("**Step 2: Upload Proof Below**")
                    voter_name = st.text_input("Your Full Name *"); voter_phone = st.text_input("Your Phone Number *")
                    proof = st.file_uploader("Upload Proof of Payment *", type=['png', 'jpg', 'jpeg'])
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("SUBMIT VOTE"):
                            if voter_name and voter_phone and proof:
                                proofpath = os.path.join(PROOF_DIR, f"{datetime.now().timestamp()}_{proof.name}")
                                with open(proofpath, "wb") as f: f.write(proof.getbuffer())
                                conn = sqlite3.connect(DB_NAME); c = conn.cursor()
                                c.execute("INSERT INTO votes (contestant_id, voter_name, voter_phone, proof, status, created_at) VALUES (?,?,?,?,?,?)",
                                          (contestant['id'], voter_name, voter_phone, proofpath, 'pending', datetime.now().isoformat()))
                                conn.commit(); conn.close(); del st.session_state['voting_for']
                                st.success("✅ Vote submitted! Awaiting admin approval."); st.rerun()
                            else: st.error("Please fill all fields and upload proof")
                    with col2:
                        if st.form_submit_button("CANCEL"): del st.session_state['voting_for']; st.rerun()
        else: st.warning("No approved contestants to vote for yet.")

# ========== SUBMIT TAB ========== FIXED FOR REAL THIS TIME
with menu[2]:
    st.subheader("Submit Your Talent to NEXERA")
    with st.form("submission_form", clear_on_submit=True):
        name = st.text_input("Full Name *"); phone = st.text_input("Phone Number *")
        talent = st.selectbox("Talent/Category *", ["Select..."] + CATEGORIES)
        state = st.selectbox("State *", ["Select..."] + NIGERIA_STATES)
        location = st.text_input("City/Location where NEXERA can accept you *")
        bank = st.text_input("Bank Account Details *")
        reason = st.text_area("Why do you need NEXERA capital? What will you use it for? *", height=150)
        photo = st.file_uploader("Upload Clear Photo *", type=['png', 'jpg', 'jpeg'])
        if st.form_submit_button("SUBMIT NOW"):
            if name and phone and talent!= "Select..." and state!= "Select..." and location and bank and reason and photo:
                filepath = os.path.join(UPLOAD_DIR, f"{datetime.now().timestamp()}_{photo.name}")
                with open(filepath, "wb") as f: f.write(photo.getbuffer())
                conn = sqlite3.connect(DB_NAME); c = conn.cursor()
                # FIXED: 10 COLUMNS = 10 QUESTION MARKS
                c.execute("INSERT INTO submissions (name, phone, talent, bank, photo, reason, state, location, status, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                          (name, phone, talent, bank, filepath, reason, state, location, 'pending', datetime.now().isoformat()))
                conn.commit(); conn.close()
                st.success("✅ Submission received! Awaiting admin approval.")
            else: st.error("❌ Please fill all * fields and select State + Category")

with menu[3]:
    st.subheader("About NEXERA")
    st.write("**NEXERA is a community-driven talent and SME funding platform.**")
    st.write("We believe every Nigerian with talent or a small business deserves a chance to grow.")
    st.write(f"**How it works:** Talented people submit. The community votes with ₦{VOTE_PRICE}. 100% of vote money goes directly to contestants. Top 3 winners get ₦120k, ₦70k, ₦30k.")
    st.write("**Our mission:** To fund 1000 SMEs and Talents by 2027.")
    st.markdown(f"**Join our community:** {CHANNEL_LINK}")

with menu[4]:
    password = st.text_input("Enter Admin Password", type="password")
    if password == ADMIN_PASSWORD:
        st.subheader("Admin Dashboard")
        conn = sqlite3.connect(DB_NAME)
        total_submissions = pd.read_sql("SELECT COUNT(*) as c FROM submissions", conn).iloc[0]['c']
        total_approved = pd.read_sql("SELECT COUNT(*) as c FROM submissions WHERE status='approved'", conn).iloc[0]['c']
        total_votes = pd.read_sql("SELECT COUNT(*) as c FROM votes WHERE status='approved'", conn).iloc[0]['c']
        funds_raised = total_votes * VOTE_PRICE; conn.close()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Submissions", total_submissions); col2.metric("Approved Contestants", total_approved)
        col3.metric("Total Voters", total_votes); col4.metric("Funds Raised", f"₦{funds_raised:,}")
        st.markdown("---")
        st.subheader("Voting Controls")
        voting_active = get_setting('voting_active') == '1'
        if st.button("TURN ON VOTING" if not voting_active else "TURN OFF VOTING"):
            new_status = '0' if voting_active else '1'; set_setting('voting_active', new_status)
            if new_status == '1': set_setting('voting_start', datetime.now().isoformat()); set_setting('voting_end', (datetime.now() + timedelta(days=7)).isoformat())
            st.rerun()
        st.write(f"Status: {'🟢 ACTIVE' if voting_active else '🔴 INACTIVE'}")
        st.markdown("---")
        st.subheader("Approve Contestants")
        conn = sqlite3.connect(DB_NAME); df_sub = pd.read_sql("SELECT * FROM submissions WHERE status='pending'", conn); conn.close()
        if not df_sub.empty:
            for i, row in df_sub.iterrows():
                col1, col2 = st.columns([4,1])
                with col1: st.write(f"**{row['name']}** - {row['talent']} - {row['state']}")
                with col2:
                    if st.button("Approve", key=f"approve_{row['id']}"):
                        conn = sqlite3.connect(DB_NAME); c = conn.cursor(); c.execute("UPDATE submissions SET status='approved' WHERE id =?", (row['id'],)); conn.commit(); conn.close(); st.rerun()
        else: st.info("No pending submissions")
        st.markdown("---")
        st.subheader("Approve Votes / Proof of Payment")
        conn = sqlite3.connect(DB_NAME); df_votes = pd.read_sql("SELECT v.*, s.name as contestant_name FROM votes v JOIN submissions s ON v.contestant_id=s.id WHERE v.status='pending'", conn); conn.close()
        if not df_votes.empty:
            for i, row in df_votes.iterrows():
                st.write(f"**{row['voter_name']}** voted for **{row['contestant_name']}** - {row['voter_phone']}")
                if row['proof'] and os.path.exists(row['proof']): st.image(row['proof'], width=300)
                if st.button(f"Approve Vote", key=f"approve_vote_{row['id']}"):
                    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
                    c.execute("UPDATE votes SET status='approved' WHERE id =?", (row['id'],))
                    c.execute("UPDATE submissions SET votes = votes + 1 WHERE id =?", (row['contestant_id'],))
                    conn.commit(); conn.close(); st.success("Vote Approved!"); st.rerun()
        else: st.info("No pending votes")
    elif password: st.error("Wrong password")

st.markdown("---")
st.write("### NEXERA Support")
col1, col2 = st.columns(2)
with col1: st.write(f"**Email:** {SUPPORT_EMAIL}")
with col2: st.write(f"**WhatsApp:** {SUPPORT_WHATSAPP}")
st.write(f"**Channel:** {CHANNEL_LINK}")
st.write("© 2026 NEXERA. Your Next Era Starts Now.")
