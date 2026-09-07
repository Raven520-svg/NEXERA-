import streamlit as st
import sqlite3
import os
import io
from datetime import datetime, timedelta
import pandas as pd

from PIL import Image, ImageOps

# Optional HEIC / HEIF support
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except Exception:
    pass


# ========== SETTINGS ==========
DB_NAME = "nexera.db"
UPLOAD_DIR = "uploads"
PROOF_DIR = "proofs"
CHANNEL_LINK = "https://whatsapp.com/channel/0029VbDJzRsGpLHMGlw2at0n"

# VOTING PAYMENT ACCOUNT
VOTING_ACCOUNT = {
    "Bank": "OPAY",
    "Account Name": "NEXERA SUPPORT",
    "Account No": "9018479293"
}

VOTE_PRICE = 200
ADMIN_PASSWORD = "nexera2026"
SUPPORT_EMAIL = "nexerasupport142@gmail.com"
SUPPORT_WHATSAPP = "09018479293"

# IMAGE SETTINGS
MAX_IMAGE_DIMENSION = 3000
IMAGE_QUALITY = 88

ALLOWED_IMAGE_TYPES = [
    "png",
    "jpg",
    "jpeg",
    "webp",
    "gif",
    "bmp",
    "tif",
    "tiff",
    "heic",
    "heif"
]

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROOF_DIR, exist_ok=True)


# ========== PAGE CONFIG + CSS ==========
st.set_page_config(
    page_title="NEXERA - Your Next Era",
    page_icon="✨",
    layout="wide"
)

st.markdown("""
<style>
.main {
    background-color: #000;
    color: white;
}

.stButton>button {
    background-color: #B91C1C;
    color: white;
    border-radius: 8px;
    width: 100%;
    border: none;
    font-weight: bold;
    padding: 10px;
}

.stButton>button:hover {
    background-color: #991B1B;
}

.contestant-card {
    border: 1px solid #333;
    border-radius: 10px;
    padding: 15px;
    background-color: #111;
    margin-bottom: 15px;
}

.prize-box {
    text-align: center;
    border: 2px solid #FFD700;
    border-radius: 10px;
    padding: 15px;
    background-color: #1a1a1a;
}

.channel-banner {
    background-color: #25D366;
    padding: 12px;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 20px;
}

.channel-banner a {
    color: white;
    font-weight: bold;
    text-decoration: none;
    font-size: 17px;
}

.account-box {
    border: 2px dashed #FFD700;
    padding: 15px;
    border-radius: 10px;
    background-color: #1a1a1a;
    margin-bottom: 15px;
}

h1, h2, h3, h4 {
    color: white;
}
</style>
""", unsafe_allow_html=True)


st.markdown(
    f"""
    <div class="channel-banner">
        📢 <a href="{CHANNEL_LINK}" target="_blank">
        JOIN NEXERA WHATSAPP CHANNEL FOR UPDATES
        </a>
    </div>
    """,
    unsafe_allow_html=True
)


# ========== DATABASE ==========
def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            talent TEXT,
            bank TEXT,
            photo TEXT,
            reason TEXT,
            state TEXT,
            location TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT,
            votes INTEGER DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contestant_id INTEGER,
            voter_name TEXT,
            voter_phone TEXT,
            proof TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    defaults = [
        ("voting_active", "0"),
        ("voting_start", ""),
        ("voting_end", "")
    ]

    for key, value in defaults:
        c.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )

    conn.commit()
    conn.close()


def get_setting(key):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "SELECT value FROM settings WHERE key = ?",
        (key,)
    )

    result = c.fetchone()
    conn.close()

    return result[0] if result else ""


def set_setting(key, value):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "UPDATE settings SET value = ? WHERE key = ?",
        (value, key)
    )

    conn.commit()
    conn.close()


init_db()


# ============================================================
# IMAGE HANDLING
# ============================================================

def save_uploaded_image(uploaded_file, folder, prefix="image"):
    """
    Accepts common image formats, including HEIC/HEIF when
    pillow-heif is installed.

    The image is:
    - Opened safely
    - EXIF orientation corrected
    - Converted to RGB
    - Resized if extremely large
    - Saved as optimized JPEG
    """

    if uploaded_file is None:
        return None

    try:
        # Read uploaded bytes
        image_bytes = uploaded_file.getvalue()

        if not image_bytes:
            raise ValueError("The uploaded file is empty.")

        # Open image from memory
        image = Image.open(io.BytesIO(image_bytes))

        # Correct phone-camera rotation
        image = ImageOps.exif_transpose(image)

        # Convert everything to RGB
        if image.mode != "RGB":
            if image.mode in ("RGBA", "LA"):
                background = Image.new(
                    "RGB",
                    image.size,
                    "white"
                )

                alpha = image.getchannel("A")

                background.paste(
                    image.convert("RGBA"),
                    mask=alpha
                )

                image = background

            else:
                image = image.convert("RGB")

        # Resize very large images
        width, height = image.size

        largest_dimension = max(width, height)

        if largest_dimension > MAX_IMAGE_DIMENSION:

            scale = (
                MAX_IMAGE_DIMENSION
                / float(largest_dimension)
            )

            new_width = int(width * scale)
            new_height = int(height * scale)

            image = image.resize(
                (new_width, new_height),
                Image.LANCZOS
            )

        # Unique filename
        timestamp = datetime.now().strftime(
            "%Y%m%d%H%M%S%f"
        )

        safe_name = os.path.basename(
            uploaded_file.name
        )

        original_name = os.path.splitext(
            safe_name
        )[0]

        # Remove problematic characters
        clean_name = "".join(
            char if char.isalnum() or char in "_-"
            else "_"
            for char in original_name
        )

        filename = (
            f"{prefix}_{timestamp}_"
            f"{clean_name}.jpg"
        )

        filepath = os.path.join(
            folder,
            filename
        )

        # Save optimized image
        image.save(
            filepath,
            format="JPEG",
            quality=IMAGE_QUALITY,
            optimize=True
        )

        return filepath

    except Exception as e:
        st.error(
            f"❌ Could not process this image: {e}"
        )
        return None


# ========== CONSTANTS ==========
NIGERIA_STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi",
    "Bayelsa", "Benue", "Borno", "Cross River", "Delta",
    "Ebonyi", "Edo", "Ekiti", "Enugu", "FCT Abuja",
    "Gombe", "Imo", "Jigawa", "Kaduna", "Kano",
    "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos",
    "Nasarawa", "Niger", "Ogun", "Ondo", "Osun",
    "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba",
    "Yobe", "Zamfara"
]

CATEGORIES = [
    "Music",
    "Dance",
    "Comedy",
    "Content Creator",
    "Fashion Design",
    "Food & Catering",
    "Beauty & Makeup",
    "Barbing",
    "Tech & App Development",
    "Art & Painting",
    "Crafts",
    "Farming",
    "Sports",
    "Other"
]


# ========== HEADER ==========
st.title("✨ NEXERA")
st.subheader("STEP INTO YOUR NEXT ERA")
st.write(
    "**Community Support: Every ₦200 vote goes DIRECTLY to contestants** 💛"
)

menu = st.tabs([
    "🏠 Home",
    "🗳️ Vote",
    "📝 Submit",
    "ℹ️ About",
    "⚙️ Admin"
])


# ========== COUNTDOWN ==========
def show_countdown():

    end = get_setting("voting_end")

    if end:

        try:

            end_time = datetime.fromisoformat(end)
            now = datetime.now()

            if now < end_time:

                remaining = end_time - now

                days = remaining.days
                seconds = remaining.seconds

                hours = seconds // 3600
                minutes = (seconds % 3600) // 60

                st.info(
                    f"⏰ Voting Ends In: "
                    f"{days}d {hours}h {minutes}m"
                )

            else:

                st.error("Voting has ended")

        except Exception:
            pass


# ============================================================
# HOME
# ============================================================
with menu[0]:

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            '<div class="prize-box">',
            unsafe_allow_html=True
        )

        st.metric(
            "🥇 1st Place",
            "₦120,000"
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            '<div class="prize-box">',
            unsafe_allow_html=True
        )

        st.metric(
            "🥈 2nd Place",
            "₦70,000"
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            '<div class="prize-box">',
            unsafe_allow_html=True
        )

        st.metric(
            "🥉 3rd Place",
            "₦30,000"
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.subheader("🔥 Top Contestants")

    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT *
        FROM submissions
        WHERE status = 'approved'
        ORDER BY votes DESC
        LIMIT 6
        """,
        conn
    )

    conn.close()

    if not df.empty:

        cols = st.columns(2)

        for i, row in df.iterrows():

            with cols[i % 2]:

                st.markdown(
                    '<div class="contestant-card">',
                    unsafe_allow_html=True
                )

                if (
                    row["photo"]
                    and os.path.exists(row["photo"])
                ):

                    st.image(
                        row["photo"],
                        use_container_width=True
                    )

                st.write(
                    f"### {row['name']}"
                )

                st.write(
                    f"**Category:** {row['talent']} | "
                    f"**State:** {row['state']}"
                )

                st.write(
                    f"**Reason for Capital:** "
                    f"{row['reason']}"
                )

                st.write(
                    f"**VERIFIED VOTES:** "
                    f"{int(row['votes'])}"
                )

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

    else:

        st.info(
            "No contestants yet. Be the first to submit!"
        )


# ============================================================
# VOTE
# ============================================================
with menu[1]:

    show_countdown()

    voting_active = (
        get_setting("voting_active") == "1"
    )

    if not voting_active:

        st.error(
            "🚫 Voting is currently CLOSED. "
            "Please check back later."
        )

    else:

        st.subheader(
            "Vote for Your Favorite"
        )

        st.warning(
            f"Each vote is ₦{VOTE_PRICE}. "
            "100% goes to the contestant"
        )

        conn = get_connection()

        df = pd.read_sql(
            """
            SELECT *
            FROM submissions
            WHERE status = 'approved'
            ORDER BY votes DESC
            """,
            conn
        )

        conn.close()

        if not df.empty:

            for i in range(0, len(df), 2):

                cols = st.columns(2)

                for j in range(2):

                    if i + j < len(df):

                        row = df.iloc[i + j]

                        with cols[j]:

                            st.markdown(
                                '<div class="contestant-card">',
                                unsafe_allow_html=True
                            )

                            if (
                                row["photo"]
                                and os.path.exists(row["photo"])
                            ):

                                st.image(
                                    row["photo"],
                                    use_container_width=True
                                )

                            st.write(
                                f"### {row['name']}"
                            )

                            st.write(
                                f"**{row['talent']} - "
                                f"{row['state']}**"
                            )

                            st.write(
                                f"**Reason:** "
                                f"{row['reason']}"
                            )

                            st.write(
                                f"**VERIFIED VOTES:** "
                                f"{int(row['votes'])}"
                            )

                            if st.button(
                                "VOTE NOW",
                                key=f"vote_btn_{row['id']}"
                            ):

                                st.session_state[
                                    "voting_for"
                                ] = int(row["id"])

                                st.rerun()

                            st.markdown(
                                '</div>',
                                unsafe_allow_html=True
                            )

            # ==================================================
            # VOTE FORM
            # ==================================================

            if "voting_for" in st.session_state:

                contestant_id = (
                    st.session_state["voting_for"]
                )

                conn = get_connection()

                contestant_df = pd.read_sql(
                    """
                    SELECT *
                    FROM submissions
                    WHERE id = ?
                    AND status = 'approved'
                    """,
                    conn,
                    params=(contestant_id,)
                )

                conn.close()

                if not contestant_df.empty:

                    contestant = contestant_df.iloc[0]

                    with st.form("vote_form"):

                        st.subheader(
                            f"Vote for {contestant['name']}"
                        )

                        st.markdown(
                            f"""
                            <div class="account-box">
                                <h4>Step 1: Pay ₦{VOTE_PRICE} to:</h4>
                                <p>
                                <b>Bank:</b>
                                {VOTING_ACCOUNT['Bank']}<br>

                                <b>Account Name:</b>
                                {VOTING_ACCOUNT['Account Name']}<br>

                                <b>Account No:</b>
                                {VOTING_ACCOUNT['Account No']}
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        st.write(
                            "**Step 2: Upload Proof Below**"
                        )

                        voter_name = st.text_input(
                            "Your Full Name *"
                        )

                        voter_phone = st.text_input(
                            "Your Phone Number *"
                        )

                        proof = st.file_uploader(
                            "Upload Proof of Payment *",
                            type=ALLOWED_IMAGE_TYPES,
                            key="vote_proof_upload"
                        )

                        col1, col2 = st.columns(2)

                        with col1:

                            submit_vote = (
                                st.form_submit_button(
                                    "SUBMIT VOTE"
                                )
                            )

                        with col2:

                            cancel_vote = (
                                st.form_submit_button(
                                    "CANCEL"
                                )
                            )

                        if submit_vote:

                            if (
                                voter_name
                                and voter_phone
                                and proof
                            ):

                                with st.spinner(
                                    "Processing your payment proof..."
                                ):

                                    proofpath = (
                                        save_uploaded_image(
                                            proof,
                                            PROOF_DIR,
                                            "proof"
                                        )
                                    )

                                if proofpath:

                                    conn = get_connection()
                                    c = conn.cursor()

                                    c.execute(
                                        """
                                        INSERT INTO votes
                                        (
                                            contestant_id,
                                            voter_name,
                                            voter_phone,
                                            proof,
                                            status,
                                            created_at
                                        )
                                        VALUES (?, ?, ?, ?, ?, ?)
                                        """,
                                        (
                                            int(
                                                contestant["id"]
                                            ),
                                            voter_name.strip(),
                                            voter_phone.strip(),
                                            proofpath,
                                            "pending",
                                            datetime.now().isoformat()
                                        )
                                    )

                                    conn.commit()
                                    conn.close()

                                    del st.session_state[
                                        "voting_for"
                                    ]

                                    st.success(
                                        "✅ Vote submitted! "
                                        "Awaiting admin approval."
                                    )

                                    st.rerun()

                            else:

                                st.error(
                                    "Please fill all fields "
                                    "and upload proof"
                                )

                        if cancel_vote:

                            del st.session_state[
                                "voting_for"
                            ]

                            st.rerun()

                else:

                    del st.session_state[
                        "voting_for"
                    ]

                    st.warning(
                        "This contestant is no longer available."
                    )

        else:

            st.warning(
                "No approved contestants to vote for yet."
            )


# ============================================================
# SUBMIT
# ============================================================
with menu[2]:

    st.subheader(
        "Submit Your Talent to NEXERA"
    )

    with st.form(
        "submission_form",
        clear_on_submit=True
    ):

        name = st.text_input(
            "Full Name *"
        )

        phone = st.text_input(
            "Phone Number *"
        )

        talent = st.selectbox(
            "Talent/Category *",
            ["Select..."] + CATEGORIES
        )

        state = st.selectbox(
            "State *",
            ["Select..."] + NIGERIA_STATES
        )

        location = st.text_input(
            "City/Location where NEXERA can accept you *"
        )

        bank = st.text_input(
            "Bank Account Details *"
        )

        reason = st.text_area(
            "Why do you need NEXERA capital? "
            "What will you use it for? *",
            height=150
        )

        photo = st.file_uploader(
            "Upload Clear Photo *",
            type=ALLOWED_IMAGE_TYPES,
            key="contestant_photo_upload"
        )

        submit = st.form_submit_button(
            "SUBMIT NOW"
        )

        if submit:

            if (
                name
                and phone
                and talent != "Select..."
                and state != "Select..."
                and location
                and bank
                and reason
                and photo
            ):

                with st.spinner(
                    "Processing your photo..."
                ):

                    filepath = save_uploaded_image(
                        photo,
                        UPLOAD_DIR,
                        "contestant"
                    )

                if filepath:

                    conn = get_connection()
                    c = conn.cursor()

                    c.execute(
                        """
                        INSERT INTO submissions
                        (
                            name,
                            phone,
                            talent,
                            bank,
                            photo,
                            reason,
                            state,
                            location,
                            status,
                            created_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            name.strip(),
                            phone.strip(),
                            talent.strip(),
                            bank.strip(),
                            filepath,
                            reason.strip(),
                            state.strip(),
                            location.strip(),
                            "pending",
                            datetime.now().isoformat()
                        )
                    )

                    conn.commit()
                    conn.close()

                    st.success(
                        "✅ Submission received! "
                        "Awaiting admin approval."
                    )

            else:

                st.error(
                    "❌ Please fill all * fields "
                    "and select State + Category"
                )


# ============================================================
# ABOUT
# ============================================================
with menu[3]:

    st.subheader(
        "About NEXERA"
    )

    st.write(
        "**NEXERA is a community-driven talent "
        "and SME funding platform.**"
    )

    st.write(
        "We believe every Nigerian with talent "
        "or a small business deserves a chance to grow."
    )

    st.write(
        f"**How it works:** Talented people submit. "
        f"The community votes with ₦{VOTE_PRICE}. "
        "100% of vote money goes directly to contestants. "
        "Top 3 winners get ₦120k, ₦70k, ₦30k."
    )

    st.write(
        "**Our mission:** To fund 1000 SMEs and "
        "Talents by 2027."
    )

    st.markdown(
        f"**Join our community:** {CHANNEL_LINK}"
    )


# ============================================================
# ADMIN
# ============================================================
with menu[4]:

    password = st.text_input(
        "Enter Admin Password",
        type="password"
    )

    if password == ADMIN_PASSWORD:

        st.subheader(
            "Admin Dashboard"
        )

        # ====================================================
        # DASHBOARD STATISTICS
        # ====================================================

        conn = get_connection()

        total_submissions = pd.read_sql(
            """
            SELECT COUNT(*) AS c
            FROM submissions
            """,
            conn
        ).iloc[0]["c"]

        total_approved = pd.read_sql(
            """
            SELECT COUNT(*) AS c
            FROM submissions
            WHERE status = 'approved'
            """,
            conn
        ).iloc[0]["c"]

        total_votes = pd.read_sql(
            """
            SELECT COUNT(*) AS c
            FROM votes
            WHERE status = 'approved'
            """,
            conn
        ).iloc[0]["c"]

        funds_raised = (
            total_votes * VOTE_PRICE
        )

        conn.close()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Submissions",
            int(total_submissions)
        )

        col2.metric(
            "Approved Contestants",
            int(total_approved)
        )

        col3.metric(
            "Total Voters",
            int(total_votes)
        )

        col4.metric(
            "Funds Raised",
            f"₦{int(funds_raised):,}"
        )


        # ====================================================
        # VOTING CONTROLS
        # ====================================================

        st.markdown("---")

        st.subheader(
            "Voting Controls"
        )

        voting_active = (
            get_setting("voting_active") == "1"
        )

        if st.button(
            "TURN ON VOTING"
            if not voting_active
            else "TURN OFF VOTING"
        ):

            new_status = (
                "0"
                if voting_active
                else "1"
            )

            set_setting(
                "voting_active",
                new_status
            )

            if new_status == "1":

                set_setting(
                    "voting_start",
                    datetime.now().isoformat()
                )

                set_setting(
                    "voting_end",
                    (
                        datetime.now()
                        + timedelta(days=7)
                    ).isoformat()
                )

            st.rerun()

        st.write(
            f"Status: "
            f"{'🟢 ACTIVE' if voting_active else '🔴 INACTIVE'}"
        )


        # ====================================================
        # APPROVE CONTESTANTS
        # ====================================================

        st.markdown("---")

        st.subheader(
            "Approve Contestants"
        )

        conn = get_connection()

        df_sub = pd.read_sql(
            """
            SELECT *
            FROM submissions
            WHERE status = 'pending'
            ORDER BY id DESC
            """,
            conn
        )

        conn.close()

        if not df_sub.empty:

            for i, row in df_sub.iterrows():

                st.markdown(
                    '<div class="contestant-card">',
                    unsafe_allow_html=True
                )

                if (
                    row["photo"]
                    and os.path.exists(row["photo"])
                ):

                    st.image(
                        row["photo"],
                        width=200
                    )

                st.write(
                    f"**{row['name']}** - "
                    f"{row['talent']} - "
                    f"{row['state']}"
                )

                st.write(
                    f"**Phone:** {row['phone']} | "
                    f"**Bank:** {row['bank']}"
                )

                st.write(
                    f"**Location:** {row['location']}"
                )

                st.write(
                    f"**Reason:** {row['reason']}"
                )

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "Approve",
                        key=f"approve_{row['id']}"
                    ):

                        conn = get_connection()
                        c = conn.cursor()

                        c.execute(
                            """
                            UPDATE submissions
                            SET status = 'approved'
                            WHERE id = ?
                            """,
                            (int(row["id"]),)
                        )

                        conn.commit()
                        conn.close()

                        st.success(
                            f"{row['name']} approved!"
                        )

                        st.rerun()

                with col2:

                    if st.button(
                        "Remove",
                        key=f"remove_pending_{row['id']}"
                    ):

                        conn = get_connection()
                        c = conn.cursor()

                        c.execute(
                            """
                            DELETE FROM votes
                            WHERE contestant_id = ?
                            """,
                            (int(row["id"]),)
                        )

                        c.execute(
                            """
                            DELETE FROM submissions
                            WHERE id = ?
                            """,
                            (int(row["id"]),)
                        )

                        conn.commit()
                        conn.close()

                        try:

                            if (
                                row["photo"]
                                and os.path.exists(row["photo"])
                            ):

                                os.remove(
                                    row["photo"]
                                )

                        except Exception:
                            pass

                        st.success(
                            f"{row['name']} removed."
                        )

                        st.rerun()

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

        else:

            st.info(
                "No pending submissions"
            )


        # ====================================================
        # MANAGE APPROVED CONTESTANTS
        # ====================================================

        st.markdown("---")

        st.subheader(
            "👥 Manage Approved Contestants"
        )

        st.write(
            "Admins can manually update a contestant's "
            "vote score or remove a contestant."
        )

        conn = get_connection()

        approved_df = pd.read_sql(
            """
            SELECT *
            FROM submissions
            WHERE status = 'approved'
            ORDER BY votes DESC, id ASC
            """,
            conn
        )

        conn.close()

        if not approved_df.empty:

            for i, row in approved_df.iterrows():

                st.markdown(
                    '<div class="contestant-card">',
                    unsafe_allow_html=True
                )

                col1, col2 = st.columns(
                    [1, 2]
                )

                with col1:

                    if (
                        row["photo"]
                        and os.path.exists(row["photo"])
                    ):

                        st.image(
                            row["photo"],
                            width=220
                        )

                with col2:

                    st.write(
                        f"### {row['name']}"
                    )

                    st.write(
                        f"**Category:** {row['talent']}"
                    )

                    st.write(
                        f"**State:** {row['state']}"
                    )

                    st.write(
                        f"**Location:** {row['location']}"
                    )

                    st.write(
                        f"**Reason:** {row['reason']}"
                    )

                    st.write(
                        f"**Current Verified Votes:** "
                        f"{int(row['votes'])}"
                    )

                    new_score = st.number_input(
                        "Update Vote Score",
                        min_value=0,
                        value=int(row["votes"]),
                        step=1,
                        key=f"score_{row['id']}"
                    )

                    col_a, col_b = st.columns(2)

                    with col_a:

                        if st.button(
                            "💾 UPDATE SCORE",
                            key=f"update_score_{row['id']}"
                        ):

                            conn = get_connection()
                            c = conn.cursor()

                            c.execute(
                                """
                                UPDATE submissions
                                SET votes = ?
                                WHERE id = ?
                                """,
                                (
                                    int(new_score),
                                    int(row["id"])
                                )
                            )

                            conn.commit()
                            conn.close()

                            st.success(
                                f"Score for {row['name']} "
                                f"updated to {int(new_score)}."
                            )

                            st.rerun()

                    with col_b:

                        if st.button(
                            "🗑️ REMOVE CONTESTANT",
                            key=f"remove_approved_{row['id']}"
                        ):

                            conn = get_connection()
                            c = conn.cursor()

                            c.execute(
                                """
                                SELECT proof
                                FROM votes
                                WHERE contestant_id = ?
                                """,
                                (int(row["id"]),)
                            )

                            proof_files = c.fetchall()

                            c.execute(
                                """
                                DELETE FROM votes
                                WHERE contestant_id = ?
                                """,
                                (int(row["id"]),)
                            )

                            c.execute(
                                """
                                DELETE FROM submissions
                                WHERE id = ?
                                """,
                                (int(row["id"]),)
                            )

                            conn.commit()
                            conn.close()

                            try:

                                if (
                                    row["photo"]
                                    and os.path.exists(row["photo"])
                                ):

                                    os.remove(
                                        row["photo"]
                                    )

                            except Exception:
                                pass

                            for proof_row in proof_files:

                                proof_file = proof_row[0]

                                try:

                                    if (
                                        proof_file
                                        and os.path.exists(
                                            proof_file
                                        )
                                    ):

                                        os.remove(
                                            proof_file
                                        )

                                except Exception:
                                    pass

                            if (
                                "voting_for"
                                in st.session_state
                                and st.session_state[
                                    "voting_for"
                                ] == int(row["id"])
                            ):

                                del st.session_state[
                                    "voting_for"
                                ]

                            st.success(
                                f"{row['name']} has been removed."
                            )

                            st.rerun()

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

        else:

            st.info(
                "No approved contestants yet."
            )


        # ====================================================
        # APPROVE VOTES
        # ====================================================

        st.markdown("---")

        st.subheader(
            "Approve Votes / Proof of Payment"
        )

        conn = get_connection()

        df_votes = pd.read_sql(
            """
            SELECT
                v.*,
                s.name AS contestant_name
            FROM votes v
            JOIN submissions s
                ON v.contestant_id = s.id
            WHERE v.status = 'pending'
            ORDER BY v.id DESC
            """,
            conn
        )

        conn.close()

        if not df_votes.empty:

            for i, row in df_votes.iterrows():

                st.markdown(
                    '<div class="contestant-card">',
                    unsafe_allow_html=True
                )

                st.write(
                    f"**{row['voter_name']}** "
                    f"voted for "
                    f"**{row['contestant_name']}**"
                )

                st.write(
                    f"**Phone:** {row['voter_phone']}"
                )

                st.write(
                    f"**Submitted:** {row['created_at']}"
                )

                if (
                    row["proof"]
                    and os.path.exists(row["proof"])
                ):

                    st.image(
                        row["proof"],
                        width=300
                    )

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "✅ Approve Vote",
                        key=f"approve_vote_{row['id']}"
                    ):

                        conn = get_connection()
                        c = conn.cursor()

                        c.execute(
                            """
                            SELECT status
                            FROM votes
                            WHERE id = ?
                            """,
                            (int(row["id"]),)
                        )

                        current_vote = c.fetchone()

                        if (
                            current_vote
                            and current_vote[0] == "pending"
                        ):

                            c.execute(
                                """
                                SELECT id
                                FROM submissions
                                WHERE id = ?
                                AND status = 'approved'
                                """,
                                (int(row["contestant_id"]),)
                            )

                            contestant_exists = c.fetchone()

                            if contestant_exists:

                                c.execute(
                                    """
                                    UPDATE votes
                                    SET status = 'approved'
                                    WHERE id = ?
                                    """,
                                    (int(row["id"]),)
                                )

                                c.execute(
                                    """
                                    UPDATE submissions
                                    SET votes = votes + 1
                                    WHERE id = ?
                                    """,
                                    (
                                        int(
                                            row["contestant_id"]
                                        ),
                                    )
                                )

                                conn.commit()

                                st.success(
                                    "Vote Approved!"
                                )

                            else:

                                c.execute(
                                    """
                                    DELETE FROM votes
                                    WHERE id = ?
                                    """,
                                    (int(row["id"]),)
                                )

                                conn.commit()

                                st.warning(
                                    "The contestant no longer "
                                    "exists. The pending vote "
                                    "was removed."
                                )

                        conn.close()

                        st.rerun()

                with col2:

                    if st.button(
                        "❌ Reject Vote",
                        key=f"reject_vote_{row['id']}"
                    ):

                        conn = get_connection()
                        c = conn.cursor()

                        c.execute(
                            """
                            UPDATE votes
                            SET status = 'rejected'
                            WHERE id = ?
                            """,
                            (int(row["id"]),)
                        )

                        conn.commit()
                        conn.close()

                        st.success(
                            "Vote rejected."
                        )

                        st.rerun()

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

        else:

            st.info(
                "No pending votes"
            )

    elif password:

        st.error(
            "Wrong password"
        )


# ============================================================
# SUPPORT
# ============================================================
st.markdown("---")

st.write(
    "### NEXERA Support"
)

col1, col2 = st.columns(2)

with col1:

    st.write(
        f"**Email:** {SUPPORT_EMAIL}"
    )

with col2:

    st.write(
        f"**WhatsApp:** {SUPPORT_WHATSAPP}"
    )

st.write(
    f"**Channel:** {CHANNEL_LINK}"
)

st.write(
    "© 2026 NEXERA. Your Next Era Starts Now."
)
