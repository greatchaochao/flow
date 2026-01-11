"""
Main Streamlit application entry point.
"""

import streamlit as st
from app.config import config

# Page configuration
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="💱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "company_id" not in st.session_state:
    st.session_state.company_id = None

# Main page
st.title("💱 Flow Payment Platform")
st.subheader("Cross-Border FX Digital Payment Automation (PoC)")

if not st.session_state.authenticated:
    st.info("👈 Please log in using the sidebar")

    with st.sidebar:
        st.header("🔐 Login")

        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                # TODO: Implement authentication
                st.warning("Authentication not yet implemented")
else:
    st.success(f"Welcome! You are logged in as {st.session_state.user_role}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Active Beneficiaries", "0")

    with col2:
        st.metric("Pending Payments", "0")

    with col3:
        st.metric("Total FX Volume", "£0.00")

    st.info("🚧 Dashboard under construction - Navigate using the sidebar")

    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.user_role = None
        st.session_state.company_id = None
        st.rerun()

# Sidebar info
with st.sidebar:
    st.divider()
    st.caption(f"Environment: {config.ENVIRONMENT}")
    st.caption(f"Version: 0.1.0")
