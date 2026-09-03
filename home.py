import streamlit as st
from utils.helpers import show_logo

def show():
    st.markdown(f'<div class="home-background"></div>', unsafe_allow_html=True)
    st.markdown('<div class="home-content">', unsafe_allow_html=True)
    show_logo()
    st.markdown(f'<h1 class="hero-title">NEXERA</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="hero-tagline">Step Into Your Next Era</p>', unsafe_allow_html=True)
    st.markdown(
        """
        <p>
        NEXERA is a premier youth empowerment platform dedicated to discovering talent, mobilizing communities, and creating economic opportunities for young Nigerians.
        Whether you are an influencer, model, content creator, or entrepreneur, NEXERA provides a platform to showcase your talent, share your story, and gain community support.
        </p>
        """,
        unsafe_allow_html=True,
    )
    from utils.db import get_connection
    from datetime import datetime
    from utils.helpers import VOTING_START, VOTING_END

    now = datetime.now()
    if now > VOTING_END:
        st.markdown("<h3>COMPETITION OVER</h3>", unsafe_allow_html=True)
        st.write("Thank you to everyone who participated in NEXERA.")
    elif now < VOTING_START:
        st.info(f"NEXERA voting will open on {VOTING_START.strftime('%B %d, %Y')}.")
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
