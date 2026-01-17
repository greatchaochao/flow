"""
Beneficiary Management Page
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from app.database.connection import SessionLocal
from app.services.beneficiary_service import BeneficiaryService

st.set_page_config(page_title="Beneficiaries", page_icon="", layout="wide")

# Check authentication
if not st.session_state.get("authenticated", False):
    st.error(" Please log in to access this page")
    st.stop()

st.title(" Beneficiary Management")
st.markdown("---")

# Only Makers and Admins can add/edit beneficiaries
can_edit = st.session_state.user_role in ["admin", "maker"]

# Initialize session state for forms
if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False

# Get database session
db = SessionLocal()

try:
    beneficiary_service = BeneficiaryService(db)

    # Action buttons
    col1, col2, col3 = st.columns([2, 1, 1])

    with col2:
        search_input = st.text_input(
            " Search", placeholder="Name or country...", key="search_input"
        )

    with col3:
        if can_edit:
            if st.button(" Add New Beneficiary", use_container_width=True):
                st.session_state.show_add_form = True
                st.rerun()

    st.markdown("---")

    # Show add form
    if st.session_state.show_add_form:
        with st.form("beneficiary_form"):
            st.subheader("Beneficiary Details")

            col1, col2 = st.columns(2)

            with col1:
                ben_name = st.text_input(
                    "Beneficiary Name *", placeholder="Company or Individual Name"
                )
                ben_type = st.selectbox(
                    "Beneficiary Type *", ["business", "individual"]
                )

                # Country mapping
                country_options = {
                    "DE": "DE - Germany",
                    "FR": "FR - France",
                    "ES": "ES - Spain",
                    "IT": "IT - Italy",
                    "NL": "NL - Netherlands",
                    "BE": "BE - Belgium",
                    "GB": "GB - United Kingdom",
                    "CH": "CH - Switzerland",
                }
                country_display = st.selectbox(
                    "Country *",
                    options=list(country_options.values()),
                )
                country_code = [
                    k for k, v in country_options.items() if v == country_display
                ][0]

            with col2:
                st.text("")  # Spacer
                st.caption("Required fields marked with *")

            st.markdown("---")
            st.subheader("Bank Account Details")

            col1, col2 = st.columns(2)

            with col1:
                account_holder = st.text_input("Account Holder Name *")
                iban = st.text_input("IBAN *", placeholder="DE89370400440532013000")

            with col2:
                swift_bic = st.text_input("SWIFT/BIC *", placeholder="DEUTDEFF")
                bank_name = st.text_input("Bank Name", placeholder="Deutsche Bank")

            currency_options = ["EUR", "GBP", "USD", "CHF", "JPY", "CAD", "AUD"]
            currency = st.selectbox("Account Currency *", options=currency_options)

            st.markdown("---")

            col1, col2, col3 = st.columns([1, 1, 4])

            with col1:
                submitted = st.form_submit_button(
                    " Save Beneficiary", use_container_width=True
                )

            with col2:
                if st.form_submit_button(" Cancel", use_container_width=True):
                    st.session_state.show_add_form = False
                    st.rerun()

            if submitted:
                # Validate required fields
                if not all(
                    [
                        ben_name,
                        ben_type,
                        country_code,
                        account_holder,
                        iban,
                        swift_bic,
                        currency,
                    ]
                ):
                    st.error("Please fill in all required fields")
                else:
                    try:
                        # Create beneficiary
                        beneficiary_data = {
                            "company_id": st.session_state.company_id,
                            "beneficiary_name": ben_name,
                            "beneficiary_type": ben_type,
                            "country": country_code,
                        }

                        beneficiary = beneficiary_service.create_beneficiary(
                            beneficiary_data, st.session_state.user_id
                        )

                        # Add bank account
                        account_data = {
                            "account_holder_name": account_holder,
                            "iban": iban,
                            "swift_bic": swift_bic,
                            "bank_name": bank_name,
                            "currency": currency,
                            "is_default": True,
                        }

                        account, error = beneficiary_service.add_bank_account(
                            beneficiary.id, account_data, st.session_state.user_id
                        )

                        if error:
                            st.error(f"Validation error: {error}")
                        else:
                            st.success(f" Beneficiary '{ben_name}' added successfully!")
                            st.session_state.show_add_form = False
                            st.rerun()

                    except Exception as e:
                        st.error(f"Error creating beneficiary: {str(e)}")

    # Get beneficiaries
    if search_input:
        beneficiaries = beneficiary_service.search_beneficiaries(
            st.session_state.company_id, search_input
        )
    else:
        beneficiaries = beneficiary_service.get_company_beneficiaries(
            st.session_state.company_id, include_inactive=True
        )

    # Display beneficiaries
    st.subheader(f" Your Beneficiaries ({len(beneficiaries)})")

    if beneficiaries:
        # Create DataFrame
        beneficiary_list = []
        for ben in beneficiaries:
            # Get bank accounts
            accounts = beneficiary_service.get_beneficiary_accounts(ben.id)
            default_account = next(
                (acc for acc in accounts if acc.is_default),
                accounts[0] if accounts else None,
            )

            beneficiary_list.append(
                {
                    "ID": ben.id,
                    "Name": ben.beneficiary_name,
                    "Type": ben.beneficiary_type.title(),
                    "Country": ben.country,
                    "Currency": default_account.currency if default_account else "N/A",
                    "IBAN": default_account.iban[:10] + "****"
                    if default_account and default_account.iban
                    else "N/A",
                    "Status": "Active" if ben.is_active else "Inactive",
                    "Created": ben.created_at.strftime("%Y-%m-%d"),
                }
            )

        df = pd.DataFrame(beneficiary_list)

        # Display dataframe
        st.dataframe(
            df.drop(columns=["ID"]),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Status": st.column_config.TextColumn(
                    "Status", help="Beneficiary status"
                ),
                "Created": st.column_config.DateColumn("Created", help="Date created"),
            },
        )

        st.markdown("---")

        # Beneficiary details
        selected_ben_name = st.selectbox(
            "View Details",
            options=[b.beneficiary_name for b in beneficiaries],
            key="selected_beneficiary",
        )

        selected_ben = next(
            (b for b in beneficiaries if b.beneficiary_name == selected_ben_name), None
        )

        if selected_ben:
            with st.expander(
                f" Details: {selected_ben.beneficiary_name}", expanded=True
            ):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Basic Information**")
                    st.text(f"Name: {selected_ben.beneficiary_name}")
                    st.text(f"Type: {selected_ben.beneficiary_type.title()}")
                    st.text(f"Country: {selected_ben.country}")
                    st.text(
                        f"Status: {'Active' if selected_ben.is_active else 'Inactive'}"
                    )
                    st.text(
                        f"Created: {selected_ben.created_at.strftime('%Y-%m-%d %H:%M')}"
                    )

                with col2:
                    st.markdown("**Bank Accounts**")
                    accounts = beneficiary_service.get_beneficiary_accounts(
                        selected_ben.id
                    )

                    if accounts:
                        for account in accounts:
                            st.text(f"Currency: {account.currency}")
                            st.text(f"IBAN: {account.iban}")
                            st.text(f"SWIFT: {account.swift_bic}")
                            st.text(f"Bank: {account.bank_name or 'N/A'}")
                            st.text(f"Default: {'Yes' if account.is_default else 'No'}")
                            st.markdown("---")
                    else:
                        st.info("No bank accounts found")

                if can_edit:
                    col1, col2, col3 = st.columns([1, 1, 4])

                    with col1:
                        if selected_ben.is_active:
                            if st.button(
                                " Disable", use_container_width=True, key="disable_btn"
                            ):
                                try:
                                    beneficiary_service.disable_beneficiary(
                                        selected_ben.id, st.session_state.user_id
                                    )
                                    st.success("Beneficiary disabled")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                        else:
                            if st.button(
                                " Enable", use_container_width=True, key="enable_btn"
                            ):
                                try:
                                    beneficiary_service.enable_beneficiary(
                                        selected_ben.id, st.session_state.user_id
                                    )
                                    st.success("Beneficiary enabled")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")

    else:
        st.info("No beneficiaries found. Add your first beneficiary to get started!")

    # Statistics
    if beneficiaries:
        st.markdown("---")
        st.subheader(" Statistics")

        active_count = sum(1 for b in beneficiaries if b.is_active)
        total_count = len(beneficiaries)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Beneficiaries", total_count)

        with col2:
            st.metric(
                "Active", active_count, f"{(active_count / total_count * 100):.0f}%"
            )

        with col3:
            # Most common currency
            currencies = []
            for ben in beneficiaries:
                accounts = beneficiary_service.get_beneficiary_accounts(ben.id)
                currencies.extend([acc.currency for acc in accounts])
            most_common = (
                max(set(currencies), key=currencies.count) if currencies else "N/A"
            )
            st.metric("Most Used Currency", most_common)

        with col4:
            # Count countries
            countries = set(b.country for b in beneficiaries)
            st.metric("Countries", len(countries))

    if not can_edit:
        st.info("ℹ Only Makers and Admins can add or edit beneficiaries")

finally:
    db.close()

# Sidebar info
with st.sidebar:
    st.info(f"**Logged in as:** {st.session_state.user_name}")
    st.caption(f"Role: {st.session_state.user_role.title()}")

    st.markdown("---")

    st.markdown("** Tips**")
    st.caption("• Verify IBAN and SWIFT codes before saving")
    st.caption("• Keep beneficiary information up to date")
    st.caption("• Inactive beneficiaries cannot receive payments")
