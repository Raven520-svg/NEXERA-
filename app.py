import streamlit as st
import sqlite3
import os
import io
import uuid
from datetime import datetime, timedelta

import pandas as pd
from PIL import Image, ImageOps

# Optional HEIC / HEIF support
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except Exception:
    pass


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NEXERA — Your Next Era",
    page_icon="logo.png" if os.path.exists("logo.png") else "N",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# NEXERA SETTINGS
# ============================================================

DB_NAME = "nexera.db"

UPLOAD_DIR = "uploads"
PROOF_DIR = "proofs"

# Your real logo
LOGO_PATH = "logo.png"

CHANNEL_LINK = "https://whatsapp.com/channel/0029VbDJzRsGpLHMGlw2at0n"

VOTING_ACCOUNT = {
    "Bank": "OPAY",
    "Account Name": "NEXERA SUPPORT",
    "Account No": "9018479293"
}

VOTE_PRICE = 200

ADMIN_PASSWORD = "nexera2026"

SUPPORT_EMAIL = "nexerasupport142@gmail.com"

SUPPORT_WHATSAPP = "09018479293"

PRIZES = {
    1: 120000,
    2: 70000,
    3: 30000
}

# Large images are accepted, then optimized for the website.
MAX_IMAGE_DIMENSION = 2500
IMAGE_QUALITY = 88


# ============================================================
# CREATE FOLDERS
# ============================================================

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROOF_DIR, exist_ok=True)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    conn = sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_db():

    conn = get_connection()
    c = conn.cursor()

    c.execute(
        """
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
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contestant_id INTEGER,
            voter_name TEXT,
            voter_phone TEXT,
            proof TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )

    defaults = [
        ("voting_active", "0"),
        ("voting_start", ""),
        ("voting_end", "")
    ]

    for key, value in defaults:

        c.execute(
            """
            INSERT OR IGNORE INTO settings
            (key, value)
            VALUES (?, ?)
            """,
            (key, value)
        )

    conn.commit()
    conn.close()


init_db()


# ============================================================
# SETTINGS HELPERS
# ============================================================

def get_setting(key):

    conn = get_connection()
    c = conn.cursor()

    c.execute(
        """
        SELECT value
        FROM settings
        WHERE key = ?
        """,
        (key,)
    )

    row = c.fetchone()

    conn.close()

    if row:
        return row["value"]

    return ""


def set_setting(key, value):

    conn = get_connection()
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO settings
        (key, value)
        VALUES (?, ?)
        ON CONFLICT(key)
        DO UPDATE SET value = excluded.value
        """,
        (key, str(value))
    )

    conn.commit()
    conn.close()


# ============================================================
# CONTESTANT DATA
# ============================================================

def get_contestants(status=None):

    conn = get_connection()

    if status:

        df = pd.read_sql_query(
            """
            SELECT *
            FROM submissions
            WHERE status = ?
            ORDER BY votes DESC, id ASC
            """,
            conn,
            params=(status,)
        )

    else:

        df = pd.read_sql_query(
            """
            SELECT *
            FROM submissions
            ORDER BY id DESC
            """,
            conn
        )

    conn.close()

    return df


# ============================================================
# IMAGE PROCESSING
# ============================================================

def save_uploaded_image(
    uploaded_file,
    output_folder,
    prefix="image"
):

    if uploaded_file is None:
        return None

    try:

        image_bytes = uploaded_file.getvalue()

        if not image_bytes:
            raise ValueError(
                "The uploaded image is empty."
            )

        # Open image
        image = Image.open(
            io.BytesIO(image_bytes)
        )

        # Fix phone-camera orientation
        image = ImageOps.exif_transpose(image)

        # Convert image to RGB
        if image.mode in (
            "RGBA",
            "LA",
            "P"
        ):

            if image.mode == "P":
                image = image.convert("RGBA")

            if image.mode in (
                "RGBA",
                "LA"
            ):

                background = Image.new(
                    "RGB",
                    image.size,
                    "white"
                )

                background.paste(
                    image,
                    mask=image.getchannel("A")
                )

                image = background

            else:

                image = image.convert("RGB")

        else:

            image = image.convert("RGB")

        # Resize extremely large images
        width, height = image.size

        if max(
            width,
            height
        ) > MAX_IMAGE_DIMENSION:

            scale = (
                MAX_IMAGE_DIMENSION /
                max(width, height)
            )

            new_width = max(
                1,
                int(width * scale)
            )

            new_height = max(
                1,
                int(height * scale)
            )

            image = image.resize(
                (
                    new_width,
                    new_height
                ),
                Image.Resampling.LANCZOS
            )

        # Generate unique filename
        filename = (
            f"{prefix}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
            f"{uuid.uuid4().hex[:12]}.jpg"
        )

        filepath = os.path.join(
            output_folder,
            filename
        )

        # Save optimized JPEG
        image.save(
            filepath,
            "JPEG",
            quality=IMAGE_QUALITY,
            optimize=True
        )

        return filepath

    except Exception as e:

        st.error(
            "The image could not be processed. "
            f"Please try another image.\n\nError: {e}"
        )

        return None


# ============================================================
# VOTING STATUS
# ============================================================

def voting_is_active():

    active = get_setting(
        "voting_active"
    )

    if active != "1":
        return False

    end_value = get_setting(
        "voting_end"
    )

    if end_value:

        try:

            end_time = datetime.fromisoformat(
                end_value
            )

            if datetime.now() >= end_time:

                set_setting(
                    "voting_active",
                    "0"
                )

                return False

        except Exception:
            pass

    return True


# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #ffffff;
    }

    .nexera-title {
        font-size: 55px;
        font-weight: 900;
        text-align: center;
        letter-spacing: 5px;
        margin-bottom: 0;
    }

    .nexera-subtitle {
        text-align: center;
        font-size: 20px;
        color: #666666;
        margin-bottom: 30px;
    }

    .hero-box {
        padding: 35px;
        border-radius: 20px;
        background: linear-gradient(
            135deg,
            #111111,
            #292929
        );
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }

    .hero-box h1 {
        font-size: 48px;
        margin-bottom: 10px;
    }

    .hero-box p {
        font-size: 20px;
    }

    .contestant-card {
        padding: 15px;
        border-radius: 18px;
        border: 1px solid #dddddd;
        margin-bottom: 20px;
        background: white;
    }

    .vote-count {
        font-size: 24px;
        font-weight: 800;
    }

    .rank-number {
        font-size: 30px;
        font-weight: 900;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR LOGO
# ============================================================

if os.path.exists(LOGO_PATH):

    st.sidebar.image(
        LOGO_PATH,
        use_container_width=True
    )

else:

    st.sidebar.markdown(
        "# NEXERA"
    )


st.sidebar.markdown(
    "**Your Next Era**"
)

st.sidebar.markdown("---")


# ============================================================
# NAVIGATION
# ============================================================

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Register",
        "Vote",
        "Support",
        "Admin"
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    "Registration is open. "
    "Voting can be activated by the NEXERA admin."
)


# ============================================================
# HOME PAGE
# ============================================================

if page == "Home":

    # Real logo
    if os.path.exists(LOGO_PATH):

        col1, col2, col3 = st.columns(
            [1, 2, 1]
        )

        with col2:

            st.image(
                LOGO_PATH,
                use_container_width=True
            )

    st.markdown(
        """
        <div class="hero-box">

            <h1>NEXERA</h1>

            <p>
                Your Next Era
            </p>

            <p>
                Discover talents.
                Support dreams.
                Change someone's next chapter.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "🥇 1st Prize",
            "₦120,000"
        )

    with col2:

        st.metric(
            "🥈 2nd Prize",
            "₦70,000"
        )

    with col3:

        st.metric(
            "🥉 3rd Prize",
            "₦30,000"
        )

    st.markdown("---")

    if voting_is_active():

        st.success(
            "🟢 VOTING IS CURRENTLY OPEN"
        )

    else:

        st.warning(
            "🔴 Voting is currently closed."
        )

    st.markdown(
        "## Featured Contestants"
    )

    contestants = get_contestants(
        "approved"
    )

    if contestants.empty:

        st.info(
            "No contestants have been approved yet."
        )

    else:

        contestants = contestants.head(6)

        cols = st.columns(3)

        for index, (_, row) in enumerate(
            contestants.iterrows()
        ):

            with cols[index % 3]:

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

                st.markdown(
                    f"### {row['name']}"
                )

                st.write(
                    f"**Talent:** {row['talent']}"
                )

                st.write(
                    f"**Location:** "
                    f"{row['location']}, "
                    f"{row['state']}"
                )

                st.write(
                    f"**Votes:** {int(row['votes'])}"
                )

                st.write(
                    row["reason"]
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

    st.markdown("---")

    st.subheader(
        "Join NEXERA"
    )

    st.write(
        "Do you have a talent, business idea, "
        "creative skill, or dream that deserves "
        "support?"
    )

    if st.button(
        "Register Now",
        use_container_width=True
    ):

        st.info(
            "Select **Register** from the navigation menu."
        )

    st.markdown("---")

    st.markdown(
        f"""
        ### Join our WhatsApp Channel

        Stay updated with NEXERA announcements,
        contestants and voting information.

        [Join NEXERA WhatsApp Channel]({CHANNEL_LINK})
        """
    )


# ============================================================
# REGISTRATION PAGE
# ============================================================

elif page == "Register":

    st.title(
        "NEXERA Registration"
    )

    st.write(
        "Registration is open."
    )

    st.info(
        "Applications are reviewed before "
        "contestants appear publicly."
    )

    with st.form(
        "registration_form"
    ):

        name = st.text_input(
            "Full Name *"
        )

        phone = st.text_input(
            "Phone Number *"
        )

        talent = st.text_input(
            "Talent / Business / Skill *"
        )

        bank = st.text_input(
            "Bank Account / Bank Name *"
        )

        state = st.text_input(
            "State *"
        )

        location = st.text_input(
            "Location / City *"
        )

        reason = st.text_area(
            "Why should NEXERA support you? *",
            height=150
        )

        st.markdown(
            "### Upload Your Photo"
        )

        photo = st.file_uploader(
            "Upload Clear Photo *",
            type=[
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
            ],
            help=(
                "Large images are accepted. "
                "Please wait until the upload "
                "finishes before submitting."
            )
        )

        submitted = st.form_submit_button(
            "Submit Registration",
            use_container_width=True
        )

        if submitted:

            if not name.strip():

                st.error(
                    "Please enter your full name."
                )

            elif not phone.strip():

                st.error(
                    "Please enter your phone number."
                )

            elif not talent.strip():

                st.error(
                    "Please enter your talent or business."
                )

            elif not bank.strip():

                st.error(
                    "Please enter your bank information."
                )

            elif not state.strip():

                st.error(
                    "Please enter your state."
                )

            elif not location.strip():

                st.error(
                    "Please enter your location."
                )

            elif not reason.strip():

                st.error(
                    "Please explain why you should be supported."
                )

            elif photo is None:

                st.error(
                    "Please upload your photo."
                )

            else:

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
                        "✅ Registration submitted successfully!"
                    )

                    st.info(
                        "Your application is now awaiting approval."
                    )

                    st.balloons()


# ============================================================
# VOTING PAGE
# ============================================================

elif page == "Vote":

    st.title(
        "NEXERA Voting"
    )

    if not voting_is_active():

        st.warning(
            "Voting is currently closed."
        )

        start = get_setting(
            "voting_start"
        )

        end = get_setting(
            "voting_end"
        )

        if start:

            st.write(
                f"Voting starts: **{start}**"
            )

        if end:

            st.write(
                f"Voting ends: **{end}**"
            )

        st.stop()

    st.success(
        f"🟢 Voting is OPEN — "
        f"Each vote costs ₦{VOTE_PRICE}"
    )

    st.markdown(
        f"""
        ### Voting Payment Details

        **Bank:** {VOTING_ACCOUNT['Bank']}

        **Account Name:** {VOTING_ACCOUNT['Account Name']}

        **Account Number:** {VOTING_ACCOUNT['Account No']}

        **Cost per vote:** ₦{VOTE_PRICE}
        """
    )

    st.markdown("---")

    contestants = get_contestants(
        "approved"
    )

    if contestants.empty:

        st.info(
            "No approved contestants are available."
        )

    else:

        for _, row in contestants.iterrows():

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
                        use_container_width=True
                    )

            with col2:

                st.subheader(
                    row["name"]
                )

                st.write(
                    f"**Talent:** {row['talent']}"
                )

                st.write(
                    f"**Location:** "
                    f"{row['location']}, "
                    f"{row['state']}"
                )

                st.markdown(
                    f"""
                    <div class="vote-count">
                    Votes: {int(row['votes'])}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.write(
                    row["reason"]
                )

                with st.expander(
                    f"Vote for {row['name']}"
                ):

                    with st.form(
                        f"vote_form_{row['id']}"
                    ):

                        voter_name = st.text_input(
                            "Your Name"
                        )

                        voter_phone = st.text_input(
                            "Your Phone Number"
                        )

                        st.write(
                            f"Send ₦{VOTE_PRICE} to:"
                        )

                        st.code(
                            VOTING_ACCOUNT["Account No"]
                        )

                        st.write(
                            VOTING_ACCOUNT["Bank"]
                        )

                        st.write(
                            VOTING_ACCOUNT["Account Name"]
                        )

                        proof = st.file_uploader(
                            "Upload Payment Screenshot *",
                            type=[
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
                            ],
                            key=f"proof_{row['id']}"
                        )

                        vote_submit = st.form_submit_button(
                            "Submit Vote",
                            use_container_width=True
                        )

                        if vote_submit:

                            if not voter_name.strip():

                                st.error(
                                    "Enter your name."
                                )

                            elif not voter_phone.strip():

                                st.error(
                                    "Enter your phone number."
                                )

                            elif proof is None:

                                st.error(
                                    "Upload your payment proof."
                                )

                            else:

                                with st.spinner(
                                    "Processing payment proof..."
                                ):

                                    proofpath = save_uploaded_image(
                                        proof,
                                        PROOF_DIR,
                                        "proof"
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
                                            int(row["id"]),
                                            voter_name.strip(),
                                            voter_phone.strip(),
                                            proofpath,
                                            "pending",
                                            datetime.now().isoformat()
                                        )
                                    )

                                    conn.commit()
                                    conn.close()

                                    st.success(
                                        "✅ Vote submitted successfully!"
                                    )

                                    st.info(
                                        "Your payment proof is awaiting "
                                        "verification by NEXERA."
                                    )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )


# ============================================================
# SUPPORT PAGE
# ============================================================

elif page == "Support":

    if os.path.exists(LOGO_PATH):

        col1, col2, col3 = st.columns(
            [1, 2, 1]
        )

        with col2:

            st.image(
                LOGO_PATH,
                use_container_width=True
            )

    st.title(
        "NEXERA Support"
    )

    st.write(
        "Need help with registration, voting "
        "or your application?"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "Email Support"
        )

        st.write(
            SUPPORT_EMAIL
        )

        st.markdown(
            f"[Send us an email](mailto:{SUPPORT_EMAIL})"
        )

    with col2:

        st.subheader(
            "WhatsApp Support"
        )

        st.write(
            SUPPORT_WHATSAPP
        )

        st.markdown(
            f"[Chat with NEXERA Support]"
            f"(https://wa.me/234{SUPPORT_WHATSAPP[1:]})"
        )

    st.markdown("---")

    st.subheader(
        "Voting Payment Details"
    )

    st.write(
        f"**Bank:** {VOTING_ACCOUNT['Bank']}"
    )

    st.write(
        f"**Account Name:** "
        f"{VOTING_ACCOUNT['Account Name']}"
    )

    st.write(
        f"**Account Number:** "
        f"{VOTING_ACCOUNT['Account No']}"
    )

    st.write(
        f"**Cost:** ₦{VOTE_PRICE} per vote"
    )


# ============================================================
# ADMIN PAGE
# ============================================================

elif page == "Admin":

    # Logo
    if os.path.exists(LOGO_PATH):

        st.image(
            LOGO_PATH,
            width=180
        )

    st.title(
        "NEXERA Admin Panel"
    )

    password = st.text_input(
        "Admin Password",
        type="password"
    )

    if password != ADMIN_PASSWORD:

        st.info(
            "Enter the admin password to continue."
        )

        st.stop()

    st.success(
        "Admin access granted."
    )

    admin_menu = st.radio(
        "Admin Section",
        [
            "Dashboard",
            "Contestants",
            "Payment Proofs",
            "Voting Controls"
        ]
    )


    # ========================================================
    # ADMIN DASHBOARD
    # ========================================================

    if admin_menu == "Dashboard":

        all_contestants = get_contestants()

        pending_count = len(
            all_contestants[
                all_contestants["status"]
                == "pending"
            ]
        )

        approved_count = len(
            all_contestants[
                all_contestants["status"]
                == "approved"
            ]
        )

        conn = get_connection()

        votes_df = pd.read_sql_query(
            "SELECT * FROM votes",
            conn
        )

        conn.close()

        if votes_df.empty:

            pending_votes = 0
            approved_votes = 0

        else:

            pending_votes = len(
                votes_df[
                    votes_df["status"]
                    == "pending"
                ]
            )

            approved_votes = len(
                votes_df[
                    votes_df["status"]
                    == "approved"
                ]
            )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Total Contestants",
                len(all_contestants)
            )

        with col2:

            st.metric(
                "Pending Contestants",
                pending_count
            )

        with col3:

            st.metric(
                "Approved Contestants",
                approved_count
            )

        with col4:

            st.metric(
                "Pending Payments",
                pending_votes
            )

        st.markdown("---")

        st.subheader(
            "Voting Status"
        )

        if voting_is_active():

            st.success(
                "🟢 Voting is ACTIVE"
            )

        else:

            st.error(
                "🔴 Voting is CLOSED"
            )

        if not votes_df.empty:

            st.subheader(
                "Vote Summary"
            )

            st.write(
                f"Approved payments: "
                f"{approved_votes}"
            )

            st.write(
                f"Pending payments: "
                f"{pending_votes}"
            )


    # ========================================================
    # ADMIN CONTESTANTS
    # ========================================================

    elif admin_menu == "Contestants":

        st.subheader(
            "Contestant Management"
        )

        contestants = get_contestants()

        if contestants.empty:

            st.info(
                "No contestants found."
            )

        else:

            for _, row in contestants.iterrows():

                with st.expander(
                    f"{row['name']} — "
                    f"{row['status'].upper()}"
                ):

                    col1, col2 = st.columns(
                        [1, 2]
                    )

                    with col1:

                        if (
                            row["photo"]
                            and os.path.exists(
                                row["photo"]
                            )
                        ):

                            st.image(
                                row["photo"],
                                width=220
                            )

                    with col2:

                        st.write(
                            f"**Name:** {row['name']}"
                        )

                        st.write(
                            f"**Phone:** {row['phone']}"
                        )

                        st.write(
                            f"**Talent:** {row['talent']}"
                        )

                        st.write(
                            f"**Bank:** {row['bank']}"
                        )

                        st.write(
                            f"**Location:** "
                            f"{row['location']}, "
                            f"{row['state']}"
                        )

                        st.write(
                            f"**Reason:** "
                            f"{row['reason']}"
                        )

                        st.write(
                            f"**Current Votes:** "
                            f"{row['votes']}"
                        )

                    st.markdown("---")

                    col_a, col_b, col_c = st.columns(3)

                    with col_a:

                        if row["status"] == "pending":

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
                                    "Contestant approved."
                                )

                                st.rerun()

                    with col_b:

                        if row["status"] == "pending":

                            if st.button(
                                "Reject",
                                key=f"reject_{row['id']}"
                            ):

                                conn = get_connection()
                                c = conn.cursor()

                                c.execute(
                                    """
                                    UPDATE submissions
                                    SET status = 'rejected'
                                    WHERE id = ?
                                    """,
                                    (int(row["id"]),)
                                )

                                conn.commit()
                                conn.close()

                                st.warning(
                                    "Contestant rejected."
                                )

                                st.rerun()

                    with col_c:

                        if st.button(
                            "Remove Contestant",
                            key=f"remove_{row['id']}"
                        ):

                            conn = get_connection()
                            c = conn.cursor()

                            # Delete associated votes
                            c.execute(
                                """
                                DELETE FROM votes
                                WHERE contestant_id = ?
                                """,
                                (int(row["id"]),)
                            )

                            # Delete contestant
                            c.execute(
                                """
                                DELETE FROM submissions
                                WHERE id = ?
                                """,
                                (int(row["id"]),)
                            )

                            conn.commit()
                            conn.close()

                            # Delete photo
                            try:

                                if (
                                    row["photo"]
                                    and os.path.exists(
                                        row["photo"]
                                    )
                                ):

                                    os.remove(
                                        row["photo"]
                                    )

                            except Exception:
                                pass

                            st.success(
                                "Contestant removed."
                            )

                            st.rerun()

                    st.markdown("---")

                    st.write(
                        "### Manually Update Vote Score"
                    )

                    new_score = st.number_input(
                        "Update Vote Score",
                        min_value=0,
                        value=int(row["votes"]),
                        step=1,
                        key=f"score_{row['id']}"
                    )

                    if st.button(
                        "Save Vote Score",
                        key=f"save_score_{row['id']}"
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
                            "Vote score updated."
                        )

                        st.rerun()


    # ========================================================
    # ADMIN PAYMENT PROOFS
    # ========================================================

    elif admin_menu == "Payment Proofs":

        st.subheader(
            "Payment Proof Verification"
        )

        conn = get_connection()

        votes_df = pd.read_sql_query(
            """
            SELECT
                votes.*,
                submissions.name AS contestant_name
            FROM votes
            LEFT JOIN submissions
            ON votes.contestant_id = submissions.id
            ORDER BY votes.id DESC
            """,
            conn
        )

        conn.close()

        if votes_df.empty:

            st.info(
                "No payment proofs submitted."
            )

        else:

            for _, vote in votes_df.iterrows():

                with st.expander(
                    f"Vote #{vote['id']} — "
                    f"{vote['contestant_name']}"
                ):

                    st.write(
                        f"**Voter:** "
                        f"{vote['voter_name']}"
                    )

                    st.write(
                        f"**Voter Phone:** "
                        f"{vote['voter_phone']}"
                    )

                    st.write(
                        f"**Contestant:** "
                        f"{vote['contestant_name']}"
                    )

                    st.write(
                        f"**Status:** "
                        f"{vote['status']}"
                    )

                    if (
                        vote["proof"]
                        and os.path.exists(
                            vote["proof"]
                        )
                    ):

                        st.image(
                            vote["proof"],
                            width=300
                        )

                    st.markdown("---")

                    col1, col2 = st.columns(2)

                    with col1:

                        if vote["status"] == "pending":

                            if st.button(
                                "Approve Payment",
                                key=f"approve_vote_{vote['id']}"
                            ):

                                conn = get_connection()
                                c = conn.cursor()

                                c.execute(
                                    """
                                    SELECT id, status
                                    FROM submissions
                                    WHERE id = ?
                                    """,
                                    (
                                        int(
                                            vote[
                                                "contestant_id"
                                            ]
                                        ),
                                    )
                                )

                                contestant = c.fetchone()

                                if contestant:

                                    c.execute(
                                        """
                                        UPDATE votes
                                        SET status = 'approved'
                                        WHERE id = ?
                                        """,
                                        (
                                            int(
                                                vote["id"]
                                            ),
                                        )
                                    )

                                    c.execute(
                                        """
                                        UPDATE submissions
                                        SET votes = votes + 1
                                        WHERE id = ?
                                        """,
                                        (
                                            int(
                                                vote[
                                                    "contestant_id"
                                                ]
                                            ),
                                        )
                                    )

                                    conn.commit()

                                    st.success(
                                        "Payment approved "
                                        "and vote added."
                                    )

                                else:

                                    st.error(
                                        "Contestant no longer exists."
                                    )

                                conn.close()

                                st.rerun()

                    with col2:

                        if vote["status"] == "pending":

                            if st.button(
                                "Reject Payment",
                                key=f"reject_vote_{vote['id']}"
                            ):

                                conn = get_connection()
                                c = conn.cursor()

                                c.execute(
                                    """
                                    UPDATE votes
                                    SET status = 'rejected'
                                    WHERE id = ?
                                    """,
                                    (
                                        int(
                                            vote["id"]
                                        ),
                                    )
                                )

                                conn.commit()
                                conn.close()

                                st.warning(
                                    "Payment rejected."
                                )

                                st.rerun()


    # ========================================================
    # ADMIN VOTING CONTROLS
    # ========================================================

    elif admin_menu == "Voting Controls":

        st.subheader(
            "Voting Controls"
        )

        if voting_is_active():

            st.success(
                "🟢 Voting is currently ACTIVE"
            )

        else:

            st.warning(
                "🔴 Voting is currently CLOSED"
            )

        st.markdown("---")

        st.write(
            "Start a new 7-day voting period."
        )

        if st.button(
            "START VOTING",
            use_container_width=True
        ):

            start_time = datetime.now()

            end_time = (
                start_time +
                timedelta(days=7)
            )

            set_setting(
                "voting_active",
                "1"
            )

            set_setting(
                "voting_start",
                start_time.isoformat()
            )

            set_setting(
                "voting_end",
                end_time.isoformat()
            )

            st.success(
                "🟢 Voting has started!"
            )

            st.write(
                f"Start: {start_time}"
            )

            st.write(
                f"End: {end_time}"
            )

            st.rerun()

        st.markdown("---")

        if st.button(
            "STOP VOTING",
            use_container_width=True
        ):

            set_setting(
                "voting_active",
                "0"
            )

            st.warning(
                "🔴 Voting has been stopped."
            )

            st.rerun()

        st.markdown("---")

        start = get_setting(
            "voting_start"
        )

        end = get_setting(
            "voting_end"
        )

        if start:

            st.write(
                f"**Voting Started:** {start}"
            )

        if end:

            st.write(
                f"**Voting Ends:** {end}"
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

if os.path.exists(LOGO_PATH):

    st.image(
        LOGO_PATH,
        width=90
    )

st.caption(
    "© 2026 NEXERA — Your Next Era"
)








































































































































































