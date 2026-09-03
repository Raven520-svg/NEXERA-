```python
import streamlit as st

# Step 1: Basic Streamlit app with default layout and sidebar navigation

st.set_page_config(
    page_title="NEXERA — Step Into Your Next Era",
    page_icon="🖤",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar navigation menu
with st.sidebar:
    st.title("NEXERA")
    page = st.radio("Navigation", ["Home", "About", "Register", "Contestants", "Admin"])

# Header
st.title("NEXERA")
st.subheader("Step Into Your Next Era")

# Page routing based on sidebar selection
if page == "Home":
    st.write("Welcome to NEXERA! This is the home page.")
elif page == "About":
    st.write("About NEXERA: Nigeria's premier youth empowerment platform.")
elif page == "Register":
    st.write("Registration page coming soon.")
elif page == "Contestants":
    st.write("Contestants page coming soon.")
elif page == "Admin":
    st.write("Admin panel coming soon.")
  
