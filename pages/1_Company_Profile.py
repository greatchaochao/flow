"""
Company Profile Management Page
"""

import streamlit as st
from datetime import datetime
from app.database.connection import SessionLocal
from app.services.company_service import CompanyService
from app.repositories.user_repository import UserRepository

st.set_page_config(page_title="Company Profile", page_icon="", layout="wide")

# Check authentication
if not st.session_state.get("authenticated", False):
    st.error(" Please log in to access this page")
    st.stop()

st.title(" Company Profile")
st.markdown("---")

# Get database session
db = SessionLocal()

try:
    # Get company data
    company_service = CompanyService(db)
    company = company_service.get_company(st.session_state.company_id)

    if not company:
        st.error("Company profile not found")
        st.stop()

    # Tabs for different sections
    tab1, tab2 = st.tabs([" Company Details", " User Management"])

    with tab1:
        st.subheader("Company Information")

        col1, col2 = st.columns(2)

        # Country mapping
        country_map = {
            "GB": "GB - United Kingdom",
            "DE": "DE - Germany",
            "FR": "FR - France",
            "ES": "ES - Spain",
            "IT": "IT - Italy",
        }

        country_reverse_map = {v: k for k, v in country_map.items()}

        # Industry sector mapping
        industry_options = [
            "Import/Export",
            "Manufacturing",
            "Technology",
            "Consulting",
            "Retail",
            "Wholesale",
            "Other",
        ]

        # FX volume band mapping
        fx_volume_map = {
            "small": "Small (< £100k/month)",
            "medium": "Medium (£100k - £500k/month)",
            "large": "Large (> £500k/month)",
        }

        fx_volume_reverse_map = {v: k for k, v in fx_volume_map.items()}

        with col1:
            company_name = st.text_input(
                "Company Name *",
                value=company.company_name,
                disabled=(st.session_state.user_role != "admin"),
                key="company_name",
            )

            current_country = country_map.get(
                company.registered_country, "GB - United Kingdom"
            )
            registered_country = st.selectbox(
                "Registered Country *",
                options=list(country_map.values()),
                index=list(country_map.values()).index(current_country),
                disabled=(st.session_state.user_role != "admin"),
                key="registered_country",
            )

            current_industry = company.industry_sector or "Import/Export"
            industry_sector = st.selectbox(
                "Industry Sector",
                options=industry_options,
                index=industry_options.index(current_industry)
                if current_industry in industry_options
                else 0,
                disabled=(st.session_state.user_role != "admin"),
                key="industry_sector",
            )

        with col2:
            current_fx_volume = fx_volume_map.get(
                company.fx_volume_band, "Medium (£100k - £500k/month)"
            )
            fx_volume_band = st.selectbox(
                "Expected FX Volume Band",
                options=list(fx_volume_map.values()),
                index=list(fx_volume_map.values()).index(current_fx_volume),
                disabled=(st.session_state.user_role != "admin"),
                key="fx_volume_band",
            )

        st.markdown("---")

        # Display metadata
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"Created: {company.created_at.strftime('%Y-%m-%d %H:%M')}")
        with col2:
            st.caption(f"Last Updated: {company.updated_at.strftime('%Y-%m-%d %H:%M')}")

        st.markdown("---")

        if st.session_state.user_role == "admin":
            col1, col2, col3 = st.columns([1, 1, 4])

            with col1:
                if st.button(
                    " Save Changes", use_container_width=True, key="save_company"
                ):
                    try:
                        # Update company data
                        updated_data = {
                            "company_name": company_name,
                            "registered_country": country_reverse_map[
                                registered_country
                            ],
                            "industry_sector": industry_sector,
                            "fx_volume_band": fx_volume_reverse_map[fx_volume_band],
                        }

                        company_service.update_company(
                            company.id, updated_data, st.session_state.user_id
                        )

                        st.success(" Company profile updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating company: {str(e)}")

            with col2:
                if st.button(
                    " Refresh", use_container_width=True, key="refresh_company"
                ):
                    st.rerun()
        else:
            st.info("ℹ Only Admin users can edit company profile")

    with tab2:
        st.subheader("User Management")

        if st.session_state.user_role == "admin":
            # Get user repository
            user_repo = UserRepository(db)
            users = user_repo.get_by_company(st.session_state.company_id)

            col1, col2 = st.columns([3, 1])

            with col2:
                if st.button(" Add New User", use_container_width=True, key="add_user"):
                    st.info("Add user functionality coming in future phase")

            st.markdown("---")

            # Display users
            if users:
                import pandas as pd

                users_data = pd.DataFrame(
                    [
                        {
                            "Full Name": user.full_name,
                            "Email": user.email,
                            "Role": user.role.title(),
                            "Status": "Active" if user.is_active else "Inactive",
                            "Created": user.created_at.strftime("%Y-%m-%d"),
                        }
                        for user in users
                    ]
                )

                st.dataframe(users_data, use_container_width=True, hide_index=True)
            else:
                st.info("No users found")

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

finally:
    db.close()

# Sidebar info
with st.sidebar:
    st.info(f"**Logged in as:** {st.session_state.user_name}")
    st.caption(f"Role: {st.session_state.user_role.title()}")
    if company:
        st.caption(f"Company: {company.company_name}")
