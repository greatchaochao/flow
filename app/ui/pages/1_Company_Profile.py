"""
Company Profile Management Page
"""

import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Company Profile", page_icon="", layout="wide")

# Check authentication
if not st.session_state.get("authenticated", False):
    st.error(" Please log in to access this page")
    st.stop()

st.title(" Company Profile")
st.markdown("---")

# Tabs for different sections
tab1, tab2 = st.tabs([" Company Details", " User Management"])

with tab1:
    st.subheader("Company Information")

    col1, col2 = st.columns(2)

    with col1:
        company_name = st.text_input(
            "Company Name *",
            value="UK SMB Trading Ltd",
            disabled=(st.session_state.user_role != "admin"),
        )

        registered_country = st.selectbox(
            "Registered Country *",
            options=[
                "GB - United Kingdom",
                "DE - Germany",
                "FR - France",
                "ES - Spain",
                "IT - Italy",
            ],
            disabled=(st.session_state.user_role != "admin"),
        )

        industry_sector = st.selectbox(
            "Industry Sector",
            options=[
                "Import/Export",
                "Manufacturing",
                "Technology",
                "Consulting",
                "Retail",
                "Wholesale",
                "Other",
            ],
            disabled=(st.session_state.user_role != "admin"),
        )

    with col2:
        fx_volume_band = st.selectbox(
            "Expected FX Volume Band",
            options=[
                "Small (< £100k/month)",
                "Medium (£100k - £500k/month)",
                "Large (> £500k/month)",
            ],
            index=1,
            disabled=(st.session_state.user_role != "admin"),
        )

        company_reg_number = st.text_input(
            "Company Registration Number",
            value="12345678",
            disabled=(st.session_state.user_role != "admin"),
        )

        vat_number = st.text_input(
            "VAT Number",
            value="GB123456789",
            disabled=(st.session_state.user_role != "admin"),
        )

    st.markdown("---")

    st.subheader("Contact Information")

    col1, col2 = st.columns(2)

    with col1:
        contact_name = st.text_input(
            "Primary Contact Name",
            value="John Smith",
            disabled=(st.session_state.user_role != "admin"),
        )

        contact_email = st.text_input(
            "Contact Email",
            value="contact@uksmb.com",
            disabled=(st.session_state.user_role != "admin"),
        )

    with col2:
        contact_phone = st.text_input(
            "Contact Phone",
            value="+44 20 1234 5678",
            disabled=(st.session_state.user_role != "admin"),
        )

        website = st.text_input(
            "Website",
            value="https://www.uksmb.com",
            disabled=(st.session_state.user_role != "admin"),
        )

    st.markdown("---")

    st.subheader("Business Address")

    col1, col2 = st.columns(2)

    with col1:
        address_line1 = st.text_input(
            "Address Line 1",
            value="123 Business Street",
            disabled=(st.session_state.user_role != "admin"),
        )

        address_line2 = st.text_input(
            "Address Line 2",
            value="Suite 456",
            disabled=(st.session_state.user_role != "admin"),
        )

        city = st.text_input(
            "City", value="London", disabled=(st.session_state.user_role != "admin")
        )

    with col2:
        postcode = st.text_input(
            "Postcode",
            value="EC1A 1BB",
            disabled=(st.session_state.user_role != "admin"),
        )

        country = st.selectbox(
            "Country",
            options=["United Kingdom", "Germany", "France", "Spain", "Italy"],
            disabled=(st.session_state.user_role != "admin"),
        )

    st.markdown("---")

    if st.session_state.user_role == "admin":
        col1, col2, col3 = st.columns([1, 1, 4])

        with col1:
            if st.button(" Save Changes", use_container_width=True):
                st.success(" Company profile updated successfully!")

        with col2:
            if st.button(" Reset", use_container_width=True):
                st.info("Form reset to saved values")
    else:
        st.info("ℹ Only Admin users can edit company profile")

with tab2:
    st.subheader("User Management")

    if st.session_state.user_role == "admin":
        col1, col2 = st.columns([3, 1])

        with col2:
            if st.button(" Add New User", use_container_width=True):
                st.info("Add user dialog would open here")

        st.markdown("---")

        # User list
        import pandas as pd

        users_data = pd.DataFrame(
            {
                "Full Name": [
                    "Admin User",
                    "Maker User",
                    "Approver User",
                    "Finance Manager",
                ],
                "Email": [
                    "admin@uksmb.com",
                    "maker@uksmb.com",
                    "approver@uksmb.com",
                    "finance@uksmb.com",
                ],
                "Role": ["Admin", "Maker", "Approver", "Maker"],
                "Status": ["Active", "Active", "Active", "Active"],
                "Last Login": [
                    "2026-01-11 09:30",
                    "2026-01-11 10:15",
                    "2026-01-10 16:45",
                    "2026-01-09 14:20",
                ],
            }
        )

        st.dataframe(users_data, use_container_width=True, hide_index=True)

        st.markdown("---")

        st.subheader("Role Permissions")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.info("** Admin**")
            st.markdown("""
            - Manage company profile
            - Add/edit users
            - View all reports
            - Full system access
            """)

        with col2:
            st.info("** Maker**")
            st.markdown("""
            - Create payments
            - Manage beneficiaries
            - Request FX quotes
            - Cannot approve payments
            """)

        with col3:
            st.info("** Approver**")
            st.markdown("""
            - Approve/reject payments
            - View payment details
            - Add comments
            - Cannot create payments
            """)

    else:
        st.warning(" Only Admin users can manage users")
        st.info("Contact your administrator to add or modify user accounts")

# Sidebar info
with st.sidebar:
    st.info(f"**Logged in as:** {st.session_state.user_name}")
    st.caption(f"Role: {st.session_state.user_role.title()}")
    st.caption(f"Company: UK SMB Trading Ltd")
