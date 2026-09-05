import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
from datetime import datetime

# ===== CONFIG =====
DB_NAME = "nexera.db"
UPLOAD_FOLDER = "uploads"
ADMIN_PASSWORD = "nexera2026" # CHANGE THIS
CHANNEL_LINK = "https://www.instagram.com/nexera.ng" # CHANGE THIS
VOTE_PRICE = 200
PRIZE_POOL = 200000

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
st.set_page_config(page_title="NEXERA - Step Into Your Next Era", layout="wide", initial_sidebar_state="expanded")

# BLACK THEME + STANDARD NAV
st.markdown("""
<style>
   .stApp { background-color: #000; color: #FFFFFF; }
    h1, h2, h3, h4, h5, h6 { color: #FFD700!important; }
   .stButton>button { background-color: #FFD700; color: #000; font-weight: 700; border-radius: 8px; }
   .stMetric { background-color: #1a1a1a; padding: 15px; border-radius: 10px; }
    [data-testid="stSidebar"] {background-color: #111;}
</style>
""", unsafe_allow_html=True)

# ===== DATABASE =====
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY, voting_enabled INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS candidates
             (id INTEGER PRIMARY KEY, code TEXT UNIQUE, name TEXT, photo TEXT, reason TEXT,
              location TEXT, votes INTEGER, status TEXT, created_at TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS submissions
             (id INTEGER PRIMARY KEY, name TEXT, talent TEXT, phone TEXT, bank TEXT,
              photo TEXT, reason TEXT, location TEXT, status TEXT, created_at TEXT)''')

if c.execute("SELECT * FROM settings").fetchone() is None:
    c.execute("INSERT INTO settings (voting_enabled) VALUES (1)")
    conn.commit()

# ===== FUNCTIONS =====
def get_settings(): return c.execute("SELECT * FROM settings WHERE id=1").fetchone()
def toggle_voting():
    current = get_settings()[1]
    c.execute("UPDATE settings SET voting_enabled=? WHERE id=1", (0 if current else 1,)); conn.commit()
def get_candidates(status='approved'): return pd.read_sql_query(f"SELECT * FROM candidates WHERE status='{status}' ORDER BY votes DESC", conn)
def get_all_candidates(): return pd.read_sql_query("SELECT * FROM candidates ORDER BY created_at DESC", conn)
def get_submissions(): return pd.read_sql_query("SELECT * FROM submissions WHERE status='pending' ORDER BY created_at DESC", conn)

# ===== SIDEBAR NAV =====
st.sidebar.image("https://placehold.co/200x60/FFD700/000?text=NEXERA", use_column_width=True) # Replace with logo
page = st.sidebar.radio("Navigation", ["🏠 Home", "📝 Submit", "ℹ️ About", "🔒 Admin"])
st.sidebar.markdown("---")
st.sidebar.info("Every ₦200 vote goes directly to contestants")

# ===== PAGE: HOME =====
if page == "🏠 Home":
    st.title("STEP INTO YOUR NEXT ERA")
    settings = get_settings()
    voting_enabled = settings[1] == 1
    candidates = get_candidates()

    # STATS BAR + GRAPH DATA
    total_votes = candidates['votes'].sum() if not candidates.empty else 0
    total_raised = total_votes * VOTE_PRICE
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Candidates", len(candidates))
    col2.metric("Total Votes", f"{total_votes:,}")
    col3.metric("Total Raised", f"₦{total_raised:,}")
    col4.metric("Prize Pool", f"₦{PRIZE_POOL:,}")

    if not voting_enabled: st.error("⚠️ Voting is currently OFF")
    st.divider()

    # CANDIDATE CARDS - AUTO UPLOAD WHEN APPROVED
    if candidates.empty:
        st.warning("No candidates yet. Admin needs to approve submissions.")
    else:
        for i in range(0, len(candidates), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i+j < len(candidates):
                    cand = candidates.iloc[i+j]
                    with col:
                        with st.container(border=True):
                            st.image(cand['photo'], use_column_width=True)
                            st.markdown(f"### #{i+j+1} | CODE: `{cand['code']}`")
                            st.markdown(f"#### {cand['name']}")
                            st.markdown(f"**Why I need capital:** {cand['reason']}")
                            st.markdown(f"**Location:** {cand['location']}")
                            st.markdown(f"**Verified Votes:** {cand['votes']}")

                            if voting_enabled:
                                if st.button(f"VOTE ₦{VOTE_PRICE}", key=f"vote{cand['id']}", use_container_width=True):
                                    # CHANNEL POPUP FROM YESTERDAY
                                    with st.dialog(f"Vote for {cand['name']}"):
                                        st.write("To verify your vote:")
                                        st.write(f"1. Pay ₦{VOTE_PRICE}")
                                        st.write(f"2. [Follow our channel here]({CHANNEL_LINK})")
                                        st.write("3. Click confirm below")
                                        if st.button("I have paid & followed. Count my vote", key=f"confirm{cand['id']}"):
                                            c.execute("UPDATE candidates SET votes=votes+1 WHERE id=?", (cand['id'],))
                                            conn.commit()
                                            st.success("Vote counted! Thank you for supporting.")
                                            st.rerun()

# ===== PAGE: SUBMIT =====
elif page == "📝 Submit":
    st.title("Submit Your Talent")
    st.write("Tell us your story and why you need capital.")
    with st.form("submission_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("Full Name *")
        talent = col2.text_input("Talent/Category *")
        phone = col1.text_input("Phone Number *")
        bank = col2.text_input("Bank Account Details *")
        location = st.text_input("City/Location where we can accept you *")
        reason = st.text_area("Why do you need this capital? What will you use it for? *", height=150)
        photo = st.file_uploader("Upload Clear Photo *", type=['png','jpg','jpeg'])
        submitted = st.form_submit_button("Submit Application", use_container_width=True)

        if submitted:
            if not all([name, talent, phone, bank, location, reason, photo]):
                st.error("Please fill all required fields")
            else:
                filepath = os.path.join(UPLOAD_FOLDER, f"{datetime.now().timestamp()}_{photo.name}")
                with open(filepath, "wb") as f: f.write(photo.getbuffer())
                c.execute("""INSERT INTO submissions
                            (name, talent, phone, bank, photo, reason, location, status, created_at)
                            VALUES (?,?,?,?,?)""",
                          (name, talent, phone, bank, filepath, reason, location, 'pending', datetime.now()))
                conn.commit()
                st.success("✅ Submission received! We will review it within 48hrs.")

# ===== PAGE: ABOUT =====
elif page == "ℹ️ About":
    st.title("About NEXERA")
    st.markdown("""
    ### Step Into Your Next Era

    NEXERA is a youth empowerment competition.
    Our mission is simple: **find raw talent and give it the capital to grow.**

    Across Nigeria, there are singers with no studio time, dancers with no costumes, artists with no materials, and creators with no equipment. The talent is there. The opportunity isn’t.

    NEXERA changes that.

    #### How We Help
    1. **Discover**: Talented people from all fields register and tell us their story. Not just their name, but *why* they need capital and what they’ll do with it.
    2. **Support**: The public votes by supporting directly. Every vote is ₦200, and 100% of it goes straight to the contestant’s account. No deductions.
    3. **Win Big**: After voting ends, the 3 contestants with the most verified votes receive cash prizes from our ₦200,000 pool to invest in their talent.

    #### Why It’s Different
    It’s a fair stage. Verified votes. Real receipts. Real impact.
    When you vote on NEXERA, you’re not just clicking a button. You’re funding someone’s dream.

    From music to dance, comedy to fashion, art to content creation — if you have talent and a plan, NEXERA is your stage.

    Join us. Discover talent. Support creators. Win together.
    **#YourNextEra #NexeraCompetition**
    """)

# ===== PAGE: ADMIN =====
elif page == "🔒 Admin":
    st.title("Admin Portal")
    password = st.text_input("Enter Admin Password", type="password")

    if password == ADMIN_PASSWORD:
        st.success("Logged in")
        settings = get_settings()

        # 1. VOTING TOGGLE
        st.subheader("1. Control Panel")
        col1, col2 = st.columns(2)
        col1.metric("Voting Status", "ON" if settings[1] else "OFF")
        if col2.button("Toggle Voting On/Off", use_container_width=True): toggle_voting(); st.rerun()

        # 2. DASHBOARD + GRAPH
        st.subheader("2. Dashboard & Analytics")
        candidates = get_all_candidates()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Candidates", len(candidates))
        col2.metric("Total Votes", candidates['votes'].sum())
        col3.metric("Total ₦ Raised", f"₦{candidates['votes'].sum() * VOTE_PRICE:,}")

        if not candidates.empty:
            fig = px.bar(candidates, x='name', y='votes', title='Votes per Candidate', color='votes')
            st.plotly_chart(fig, use_container_width=True)

        # 3. PENDING SUBMISSIONS - APPROVE = INSTANT FRONT PAGE
        st.subheader("3. Pending Submissions")
        submissions = get_submissions()
        if submissions.empty: st.info("No pending submissions")
        for _, sub in submissions.iterrows():
            with st.expander(f"{sub['name']} - {sub['talent']} | {sub['location']}"):
                col1, col2 = st.columns([1,2])
                col1.image(sub['photo'], width=150)
                col2.write(f"**Phone:** {sub['phone']}")
                col2.write(f"**Bank:** {sub['bank']}")
                col2.write(f"**Reason:** {sub['reason']}")
                if st.button("✅ Approve & Publish to Front Page", key=f"app{sub['id']}"):
                    new_code = f"NEX{sub['id']:03d}"
                    c.execute("""INSERT INTO candidates
                                (code, name, photo, reason, location, votes, status, created_at)
                                VALUES (?,?,?,?,?,?,?,?)""",
                              (new_code, sub['name'], sub['photo'], sub['reason'],
                               sub['location'], 0, 'approved', datetime.now()))
                    c.execute("UPDATE submissions SET status='approved' WHERE id=?", (sub['id'],))
                    conn.commit(); st.success(f"{sub['name']} is now LIVE"); st.rerun()

        # 4. EDIT/DELETE CANDIDATES - NO GITHUB NEEDED
        st.subheader("4. Manage Live Candidates")
        for _, cand in candidates.iterrows():
            with st.expander(f"{cand['name']} | {cand['code']} | Votes: {cand['votes']}"):
                new_name = st.text_input("Name", cand['name'], key=f"n{cand['id']}")
                new_reason = st.text_area("Reason", cand['reason'], key=f"r{cand['id']}")
                new_loc = st.text_input("Location", cand['location'], key=f"l{cand['id']}")
                col1, col2 = st.columns(2)
                if col1.button("💾 Save Changes", key=f"s{cand['id']}"):
                    c.execute("UPDATE candidates SET name=?, reason=?, location=? WHERE id=?",
                              (new_name, new_reason, new_loc, cand['id'])); conn.commit(); st.success("Updated")
                if col2.button("🗑️ Delete Candidate", key=f"d{cand['id']}"):
                    c.execute("DELETE FROM candidates WHERE id=?", (cand['id'],)); conn.commit(); st.rerun()
    elif password: st.error("Incorrect password")

conn.close()




























































































































