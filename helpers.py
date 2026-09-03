import re
import random
from pathlib import Path
import streamlit as st
from PIL import Image

BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"
BACKGROUND_PATH = ASSETS_DIR / "background.jpg"

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
    conn = None
    from utils.db import get_connection
    conn = get_connection()
    while True:
        code = str(random.randint(1000, 9999))
        exists = conn.execute("SELECT id FROM candidates WHERE code = ?", (code,)).fetchone()
        if not exists:
            conn.close()
            return code

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
        st.markdown(f"<h2 style='font-weight:900;'>NEXERA</h2>", unsafe_allow_html=True)

def local_css():
    st.markdown(
        f"""
        <style>
        .home-background {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
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
        /* Admin dashboard styles */
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
