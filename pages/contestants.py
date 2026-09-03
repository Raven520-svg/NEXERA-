import streamlit as st
from utils.db import get_approved_candidates
from utils.helpers import image_exists, candidate_link, VOTE_PRICE, OPAY_ACCOUNT, OPAY_NAME
from datetime import datetime

def show():
    st.markdown('<h2>NEXERA Contestants</h2>', unsafe_allow_html=True)
    now = datetime.now()
    voting_active = now >= datetime(2026, 10, 1) and now <= datetime(2026, 11, 1, 23, 59, 59)
    if now > datetime(2026, 11, 1, 23, 59, 59):
        st.markdown("<h3>COMPETITION OVER</h3>", unsafe_allow_html=True)
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
                    <div style="font-weight:bold; font-size:1.1rem; margin-bottom:0.3rem;">
                        #{rank} — NEXERA {candidate['code']}
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
                    <div style="font-size:1.2rem; font-weight:700; margin-top:0.5rem;">
                        {candidate['votes']:,} VERIFIED VOTES
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(f"**Why they need the money:** {candidate['why_money']}")
                profile_url = candidate_link(candidate["slug"])
                st.markdown(f"[View contestant profile]({profile_url})")
                if voting_active:
                    st.markdown(f"**Voting is active.** Send ₦{VOTE_PRICE} per vote to the account below to support your favorite contestant.")
                    st.markdown(f"**OPay Account:** {OPAY_ACCOUNT} ({OPAY_NAME})")
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
