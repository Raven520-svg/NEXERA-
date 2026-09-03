import streamlit as st
from pages import home, contestants, register, admin, about, rules_faq, contact_support
from utils.helpers import local_css, show_logo

st.set_page_config(page_title="NEXERA", page_icon="🖤", layout="wide")

local_css()

with st.sidebar:
    show_logo(width=140)
    st.markdown("## Navigation")
    menu_options = [
        "Home",
        "Contestants",
        "Register",
        "About",
        "Rules & FAQ",
        "Admin",
        "Contact Support"
    ]
    page = st.radio("", menu_options)

if page == "Home":
    home.show()
elif page == "Contestants":
    contestants.show()
elif page == "Register":
    register.show()
elif page == "About":
    about.show()
elif page == "Rules & FAQ":
    rules_faq.show()
elif page == "Admin":
    admin.show()
elif page == "Contact Support":
    contact_support.show()
else:
    st.write("Page not found.")
```

