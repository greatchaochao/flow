"""
Main Streamlit application entry point.
"""

import streamlit as st
from app.config import config
from app.database.connection import SessionLocal
from app.services.auth_service import AuthService
from app.services.audit_service import AuditService

# Page configuration
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="",
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
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

# Main page
st.title(" Flow Payment Platform")
st.subheader("Cross-Border FX Digital Payment Automation (PoC)")

if not st.session_state.authenticated:
    st.info(" Please log in using the sidebar to access the platform")

    # Display demo credentials
    st.markdown("---")
    st.subheader(" Demo Credentials")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("**Admin User**")
        st.code("admin@uksmb.com")
        st.code("admin123")

    with col2:
        st.info("**Maker User**")
        st.code("maker@uksmb.com")
        st.code("maker123")

    with col3:
        st.info("**Approver User**")
        st.code("approver@uksmb.com")
        st.code("approver123")

    st.markdown("---")

    # Feature overview
    st.subheader(" Platform Features")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ** Company Management**
        - Company profile setup
        - User role management (Admin, Maker, Approver)
        
        ** Beneficiary Management**
        - Add and manage beneficiaries
        - Bank account validation (IBAN/SWIFT)
        - Multi-currency support
        
        ** FX Quote Engine**
        - Real-time FX quotes
        - Transparent pricing with markup
        - Quote expiry handling (60-120s)
        """)

    with col2:
        st.markdown("""
        ** Payment Processing**
        - Create payment instructions
        - Automatic FX calculation
        - Fee transparency
        
        ** Maker-Checker Approval**
        - Submit payments for approval
        - Approval workflow with comments
        - Full audit trail
        
        ** Reporting & Analytics**
        - Payment history and status
        - FX volume tracking
        - Basic dashboard metrics
        """)

    with st.sidebar:
        st.header(" Login")

        with st.form("login_form"):
            email = st.text_input("Email", placeholder="user@example.com")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)

            if submit:
                if email and password:
                    # Real database authentication
                    db = SessionLocal()
                    try:
                        auth_service = AuthService(db)
                        user = auth_service.authenticate(email, password)

                        if user:
                            # Set session state
                            st.session_state.authenticated = True
                            st.session_state.user_id = user.id
                            st.session_state.user_role = user.role
                            st.session_state.company_id = user.company_id
                            st.session_state.user_name = user.full_name
                            st.session_state.user_email = user.email

                            # Log the login
                            audit_service = AuditService(db)
                            audit_service.log_login(user.id)

                            st.success(f"Logged in as {user.role.title()}")
                            st.rerun()
                        else:
                            st.error("Invalid email or password")
                    except Exception as e:
                        st.error(f"Login error: {str(e)}")
                    finally:
                        db.close()
                else:
                    st.error("Please enter both email and password")
else:
    # Dashboard for authenticated users
    st.success(
        f"Welcome back, {st.session_state.user_name}! (Role: {st.session_state.user_role.title()})"
    )

    st.markdown("---")

    # Key metrics
    st.subheader(" Dashboard Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Active Beneficiaries", value="12", delta="2 this month")

    with col2:
        st.metric(label="Pending Approvals", value="3", delta="-1")

    with col3:
        st.metric(label="Total FX Volume (MTD)", value="£145,230", delta="+15%")

    with col4:
        st.metric(label="Completed Payments", value="28", delta="+8")

    st.markdown("---")

    # Recent activity
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(" Recent Payments")

        # Mock payment data
        import pandas as pd
        from datetime import datetime, timedelta

        payments_data = pd.DataFrame(
            {
                "ID": ["PAY-001", "PAY-002", "PAY-003", "PAY-004", "PAY-005"],
                "Beneficiary": [
                    "Supplier GmbH",
                    "Tech Corp Ltd",
                    "Global Trade Inc",
                    "Export Co",
                    "Import Services",
                ],
                "Amount": [
                    "£10,500.00",
                    "£25,000.00",
                    "£5,750.00",
                    "£18,200.00",
                    "£12,900.00",
                ],
                "Currency": ["EUR", "USD", "GBP", "EUR", "USD"],
                "Status": [
                    "Pending Approval",
                    "Completed",
                    "Completed",
                    "Draft",
                    "Processing",
                ],
                "Date": [
                    (datetime.now() - timedelta(days=0)).strftime("%Y-%m-%d"),
                    (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                    (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                    (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
                    (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),
                ],
            }
        )

        st.dataframe(payments_data, use_container_width=True, hide_index=True)

    with col2:
        st.subheader(" Quick Actions")

        if st.button(" Request FX Quote", use_container_width=True):
            st.switch_page("pages/3_FX_Quotes.py")

        if st.button(" Create Payment", use_container_width=True):
            st.switch_page("pages/4_Payments.py")

        if st.button(" Add Beneficiary", use_container_width=True):
            st.switch_page("pages/2_Beneficiaries.py")

        if st.button(" View Reports", use_container_width=True):
            st.switch_page("pages/6_Reports.py")

    st.markdown("---")

    # Role-specific content
    if st.session_state.user_role == "approver":
        st.subheader(" Pending Your Approval")
        st.info(
            "You have 3 payments waiting for approval. Visit the Approvals page to review."
        )
    elif st.session_state.user_role == "maker":
        st.subheader(" Your Draft Payments")
        st.info("You have 2 draft payments. Complete and submit them for approval.")

    # Logout button in sidebar
    if st.sidebar.button(" Logout", use_container_width=True):
        # Log the logout
        if st.session_state.user_id:
            db = SessionLocal()
            try:
                audit_service = AuditService(db)
                audit_service.log_logout(st.session_state.user_id)
            finally:
                db.close()

        # Clear session state
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.user_role = None
        st.session_state.company_id = None
        st.session_state.user_name = None
        st.session_state.user_email = None
        st.rerun()

# Sidebar info
with st.sidebar:
    if st.session_state.authenticated:
        st.divider()
        st.info(f"**{st.session_state.user_name}**")
        st.caption(f"Role: {st.session_state.user_role.title()}")
        st.caption(f"Email: {st.session_state.user_email}")

        st.divider()

        # Role-specific navigation hints
        if st.session_state.user_role == "admin":
            st.markdown("**Admin Access:**")
            st.markdown("- Company Profile")
            st.markdown("- All Reports")
            st.markdown("- User Management")
        elif st.session_state.user_role == "maker":
            st.markdown("**Maker Access:**")
            st.markdown("- Create Payments")
            st.markdown("- Manage Beneficiaries")
            st.markdown("- Request FX Quotes")
        elif st.session_state.user_role == "approver":
            st.markdown("**Approver Access:**")
            st.markdown("- Review Payments")
            st.markdown("- Approve/Reject")
            st.markdown("- View History")

    st.divider()
    st.caption(f"Environment: {config.ENVIRONMENT}")
    st.caption(f"Version: 0.1.0")
