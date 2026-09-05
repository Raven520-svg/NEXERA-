import streamlit as st
import pandas as pd
import sqlite3
import os
import matplotlib.pyplot as plt
import io
from datetime import datetime

# ===== CONFIG =====
DB_NAME = "nexera.db"
UPLOAD_FOLDER = "uploads"
ADMIN_PASSWORD = "NEXERAAdmin2026"
CHANNEL_LINK = "https://whatsapp.com/channel/0029VbDJzRsGpLHMGlw2at0n"
VOTE_PRICE = 200
PRIZE_POOL = 200000
PAYMENT_ACCOUNT = "9018479293"
BANK_NAME = "Opay"
SUPPORT_EMAIL = "nexerasupport142@gmail.com"
SUPPORT_WHATSAPP = "09018479293"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
st.set_page_config(page_title="NEXERA - Step Into Your Next Era", layout="wide", initial_sidebar_state="expanded")

# BLACK + GOLD THEME
st.markdown("""
<style>
.stApp { background-color: #000; color: #FFFFFF; }
    h1, h2, h3, h4, h5, h6 { color: #FFD700!important; }
.stButton>button { background-color: #FFD700; color: #000; font-weight: 700; border-radius: 8px; }
.stMetric { background-color: #1a1a1a; padding: 15px; border-radius: 10px; border: 1px solid #FFD700; }
    [data-testid="stSidebar"] {background-color: #111;}
.account-box {background-color: #1a1a1a; padding: 15px; border-radius: 10px; border: 2px dashed #FFD700; text-align: center;}
.support-box {background-color: #111; padding: 10px; border-radius: 8px; margin-top: 10px;}
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
c.execute('''CREATE TABLE IF NOT EXISTS votes
             (id INTEGER PRIMARY KEY, candidate_id INTEGER, candidate_name TEXT, proof_path TEXT, status TEXT, created_at TEXT)''')

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
def get_pending_votes(): return pd.read_sql_query("SELECT * FROM votes WHERE status='pending' ORDER BY created_at DESC", conn)

# ===== SIDEBAR NAV =====
try: st.sidebar.image("logo.png", use_column_width=True)
except: st.sidebar.image("https://placehold.co/200x60/FFD700/000?text=NEXERA", use_column_width=True)

page = st.sidebar.radio("Navigation", ["🏠 Home", "📝 Submit", "ℹ️ About", "🏆 Prizes", "📞 Support", "🔒 Admin"])
st.sidebar.markdown("---")
st.sidebar.link_button("📢 Follow NEXERA WhatsApp Channel", CHANNEL_LINK)
st.sidebar.markdown(f"<div class='support-box'><b>NEXERA Support:</b><br>Email: {SUPPORT_EMAIL}<br>WhatsApp: {SUPPORT_WHATSAPP}</div>", unsafe_allow_html=True)

# ===== PAGE: HOME =====
if page == "🏠 Home":
    st.title("STEP INTO YOUR NEXT ERA")
    settings = get_settings()
    voting_enabled = settings[1] == 1
    candidates = get_candidates()

    # STATS BAR
    total_votes = candidates['votes'].sum() if not candidates.empty else 0
    total_raised = total_votes * VOTE_PRICE
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("NEXERA Candidates", len(candidates))
    col2.metric("Total Votes", f"{total_votes:,}")
    col3.metric("Total Raised", f"₦{total_raised:,}")
    col4.metric("NEXERA Prize Pool", f"₦{PRIZE_POOL:,}")

    if not voting_enabled:
        st.error("⚠️ NEXERA Voting is currently OFF")
    else:
        st.success("✅ NEXERA Voting is ON")
        st.markdown(f"""
        <div class="account-box">
            <h4>To Vote on NEXERA: Pay ₦{VOTE_PRICE} to</h4>
            <h2>{PAYMENT_ACCOUNT}</h2>
            <h3>{BANK_NAME}</h3>
        </div>
        """, unsafe_allow_html=True)
    st.divider()

    # CANDIDATE CARDS
    if candidates.empty:
        st.warning("No NEXERA candidates yet. Admin needs to approve submissions.")
    else:
        # TOP 3 LEADERBOARD
        st.subheader("🏆 NEXERA Top 3 Leaderboard")
        top3 = candidates.head(3)
        cols = st.columns(3)
        for i, col in enumerate(cols):
            if i < len(top3):
                cand = top3.iloc[i]
                with col:
                    st.metric(f"#{i+1} {cand['name']}", f"{cand['votes']} Votes", f"₦{cand['votes']*VOTE_PRICE:,} Earned")
        st.divider()

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
                            st.markdown(f"**Why I need NEXERA capital:** {cand['reason']}")
                            st.markdown(f"**Location:** {cand['location']}")
                            st.markdown(f"**Verified Votes:** {cand['votes']}")
                            st.markdown(f"**Total Earned:** ₦{cand['votes']*VOTE_PRICE:,}")

                            if voting_enabled:
                                if st.button(f"VOTE ₦{VOTE_PRICE} for {cand['name']}", key=f"vote{cand['id']}", use_container_width=True):
                                    with st.dialog(f"🗳️ Vote for {cand['name']} on NEXERA"):
                                        st.markdown("### Verify Your NEXERA Vote in 4 Steps")
                                        st.warning(f"**Step 1:** Transfer ₦{VOTE_PRICE} to")
                                        st.code(f"Account: {PAYMENT_ACCOUNT}\nBank: {BANK_NAME}", language="text")
                                        st.info(f"**Step 2:** Join NEXERA WhatsApp Channel")
                                        st.link_button("Join NEXERA Channel Now", CHANNEL_LINK, use_container_width=True)
                                        st.write(f"**Step 3:** Upload proof of payment below")
                                        proof = st.file_uploader("Upload Payment Screenshot", type=['png','jpg','jpeg'], key=f"proof{cand['id']}")

                                        st.success("**Step 4:** Submit for verification")
                                        if st.button("Submit Vote for Verification", key=f"submitvote{cand['id']}", use_container_width=True):
                                            if proof is None:
                                                st.error("Please upload proof of payment")
                                            else:
                                                filepath = os.path.join(UPLOAD_FOLDER, f"vote_{datetime.now().timestamp()}_{proof.name}")
                                                with open(filepath, "wb") as f: f.write(proof.getbuffer())
                                                c.execute("""INSERT INTO votes
                                                            (candidate_id, candidate_name, proof_path, status, created_at)
                                                            VALUES (?,?,?,?,?)""",
                                                          (cand['id'], cand['name'], filepath, 'pending', datetime.now()))
                                                conn.commit()
                                                st.success(f"✅ Awaiting Verification... Your vote for {cand['name']} will be counted once NEXERA admin verifies payment.")
                                                st.rerun()

# ===== PAGE: SUBMIT =====
elif page == "📝 Submit":
    st.title("Submit Your Talent to NEXERA")
    with st.form("submission_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("Full Name *")
        talent = col2.text_input("Talent/Category *")
        phone = col1.text_input("Phone Number *")
        bank = col2.text_input("Bank Account Details *")
        location = st.text_input("City/Location where NEXERA can accept you *")
        reason = st.text_area("Why do you need NEXERA capital? What will you use it for? *", height=150)
        photo = st.file_uploader("Upload Clear Photo *", type=['png','jpg','jpeg'])
        submitted = st.form_submit_button("Submit Application to NEXERA", use_container_width=True)

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
                st.success("✅ NEXERA Submission received! Your application is pending review. We will contact you within 48hrs.")

# ===== PAGE: ABOUT =====
elif page == "ℹ️ About":
    st.title("About NEXERA")
    st.markdown(f"""
    ### Step Into Your Next Era with NEXERA

    **NEXERA** is a youth empowerment competition. Our mission: **find raw talent and give it the capital to grow.**

    Across Nigeria, NEXERA believes there are singers with no studio time, dancers with no costumes, artists with no materials. The talent is there. The opportunity isn’t.

    NEXERA changes that.

    #### How NEXERA Helps
    1. **Discover**: Talented people register for NEXERA and tell us *why* they need capital.
    2. **Support**: The public votes on NEXERA by supporting directly. Every vote is ₦{VOTE_PRICE}, and 100% goes to the contestant.
    3. **Win Big**: Top 3 NEXERA contestants with most verified votes receive cash prizes from our ₦{PRIZE_POOL:,} pool.

    Join NEXERA. Discover talent. Support creators. Win together.
    **#YourNextEra #NexeraCompetition**
    """)

# ===== PAGE: PRIZES =====
elif page == "🏆 Prizes":
    st.title("🏆 NEXERA Prize Breakdown")
    st.markdown(f"### Total NEXERA Prize Pool: ₦{PRIZE_POOL:,}")
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🥇 1st Place NEXERA Winner", "₦100,000")
        st.write("Highest votes on NEXERA")
    with col2:
        st.metric("🥈 2nd Place NEXERA Winner", "₦70,000")
        st.write("Runner up on NEXERA")
    with col3:
        st.metric("🥉 3rd Place NEXERA Winner", "₦30,000")
        st.write("Second Runner up on NEXERA")
    st.info(f"Note: On NEXERA, 100% of all vote money goes directly to contestants. Every ₦{VOTE_PRICE} vote = direct support.")

# ===== PAGE: SUPPORT =====
elif page == "📞 Support":
    st.title("NEXERA Support")
    st.markdown(f"""
    ### Need Help with NEXERA?
    Our NEXERA support team is here for you.

    **Email:** {SUPPORT_EMAIL}
    **WhatsApp:** {SUPPORT_WHATSAPP}
    **Channel:** [NEXERA WhatsApp Channel]({CHANNEL_LINK})

    For issues with payment, verification, or submissions, contact NEXERA support and we’ll respond within 24hrs.
    """)

# ===== PAGE: ADMIN =====
elif page == "🔒 Admin":
    st.title("NEXERA Admin Portal")
    password = st.text_input("Enter NEXERA Admin Password", type="password")

    if password == ADMIN_PASSWORD:
        st.success("Logged into NEXERA Admin")
        settings = get_settings()
        candidates = get_all_candidates()
        if not candidates.empty:
            candidates['Total Earned'] = candidates['votes'] * VOTE_PRICE

        st.subheader("1. Control Panel")
        col1, col2 = st.columns(2)
        col1.metric("NEXERA Voting Status", "ON" if settings[1] else "OFF")
        if col2.button("Toggle NEXERA Voting On/Off", use_container_width=True): toggle_voting(); st.rerun()

        st.subheader("2. Dashboard & Analysis")
        total_votes = candidates['votes'].sum() if not candidates.empty else 0
        total_raised = total_votes * VOTE_PRICE

        col1, col2, col3 = st.columns(3)
        col1.metric("Total NEXERA Candidates", len(candidates))
        col2.metric("Total Votes", f"{total_votes:,}")
        col3.metric("Total ₦ Raised", f"₦{total_raised:,}")

        if not candidates.empty:
            st.markdown("### 💰 Earnings Breakdown Per Candidate")
            st.dataframe(candidates[['code', 'name', 'votes', 'Total Earned', 'location']].sort_values('Total Earned', ascending=False), use_container_width=True)

            fig, ax = plt.subplots()
            ax.bar(candidates['name'], candidates['votes'], color='#FFD700')
            ax.set_title('NEXERA Votes per Candidate', color='white')
            ax.tick_params(axis='x', rotation=45, colors='white')
            ax.tick_params(axis='y', colors='white')
            ax.set_facecolor('#111')
            fig.patch.set_facecolor('#000')
            st.pyplot(fig)

        st.subheader("3. Download NEXERA Reports")
        if st.button("📥 Generate Full Excel Report", use_container_width=True):
            submissions = pd.read_sql_query("SELECT * FROM submissions", conn)
            votes = pd.read_sql_query("SELECT * FROM votes", conn)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                if not candidates.empty: candidates.to_excel(writer, sheet_name='Candidates', index=False)
                if not submissions.empty: submissions.to_excel(writer, sheet_name='Submissions', index=False)
                if not votes.empty: votes.to_excel(writer, sheet_name='Votes', index=False)

            st.download_button(
                label="Click to Download Excel",
                data=output.getvalue(),
                file_name=f"NEXERA_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        st.subheader("4. Pending Vote Verifications")
        pending_votes = get_pending_votes()
        if pending_votes.empty: st.info("No pending vote verifications")
        for _, vote in pending_votes.iterrows():
            with st.expander(f"Vote for {vote['candidate_name']} | {vote['created_at']}"):
                st.image(vote['proof_path'], width=300)
                col1, col2 = st.columns(2)
                if col1.button("✅ Approve Vote", key=f"approve{vote['id']}"):
                    c.execute("UPDATE candidates SET votes=votes+1 WHERE id=?", (vote['candidate_id'],))
                    c.execute("UPDATE votes SET status='approved' WHERE id=?", (vote['id'],))
                    conn.commit(); st.success("Vote Approved and Counted"); st.rerun()
                if col2.button("❌ Reject Vote", key=f"reject{vote['id']}"):
                    c.execute("UPDATE votes SET status='rejected' WHERE id=?", (vote['id'],))
                    conn.commit(); st.error("Vote Rejected"); st.rerun()

        st.subheader("5. Pending NEXERA Submissions")
        submissions = get_submissions()
        if submissions.empty: st.info("No pending submissions")
        for _, sub in submissions.iterrows():
            with st.expander(f"{sub['name']} - {sub['talent']} | {sub['location']}"):
                col1, col2 = st.columns([1,2])
                col1.image(sub['photo'], width=150)
                col2.write(f"**Phone:** {sub['phone']}")
                col2.write(f"**Bank:** {sub['bank']}")
                col2.write(f"**Reason:** {sub['reason']}")
                if st.button("✅ Approve & Publish to NEXERA", key=f"app{sub['id']}"):
                    new_code = f"NEX{sub['id']:03d}"
                    c.execute("""INSERT INTO candidates
                                (code, name, photo, reason, location, votes, status, created_at)
                                VALUES (?,?,?,?,?,?,?,?)""",
                              (new_code, sub['name'], sub['photo'], sub['reason'],
                               sub['location'], 0, 'approved', datetime.now()))
                    c.execute("UPDATE submissions SET status='approved' WHERE id=?", (sub['id'],))
                    conn.commit(); st.success(f"{sub['name']} is now LIVE on NEXERA"); st.rerun()

        st.subheader("6. Manage Live NEXERA Candidates")
        for _, cand in candidates.iterrows():
            with st.expander(f"{cand['name']} | {cand['code']} | Votes: {cand['votes']} | Earned: ₦{cand['votes']*VOTE_PRICE:,}"):
                new_name = st.text_input("Name", cand['name'], key=f"n{cand['id']}")
                new_reason = st.text_area("Reason", cand['reason'], key=f"r{cand['id']}")
                new_loc = st.text_input("Location", cand['location'], key=f"l{cand['id']}")
                col1, col2 = st.columns(2)
                if col1.button("💾 Save Changes", key=f"s{cand['id']}"):
                    c.execute("UPDATE candidates SET name=?, reason=?, location=? WHERE id=?",
                              (new_name, new_reason, new_loc, cand['id'])); conn.commit(); st.success("Updated")
                if col2.button("🗑️ Delete Candidate", key=f"d{cand['id']}"):
                    c.execute("DELETE FROM candidates WHERE id=?", (cand['id'],)); conn.commit(); st.rerun()
    elif password: st.error("Incorrect NEXERA Admin password")

conn.close()






















































































































































































































































































































































































































