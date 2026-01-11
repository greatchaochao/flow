"""
Beneficiary Management Page
"""

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Beneficiaries", page_icon="", layout="wide")

# Check authentication
if not st.session_state.get("authenticated", False):
    st.error(" Please log in to access this page")
    st.stop()

st.title(" Beneficiary Management")
st.markdown("---")

# Only Makers and Admins can add/edit beneficiaries
can_edit = st.session_state.user_role in ["admin", "maker"]

# Action buttons
col1, col2, col3 = st.columns([2, 1, 1])

with col2:
    search_term = st.text_input(
        " Search beneficiaries", placeholder="Name or country..."
    )

with col3:
    if can_edit:
        if st.button(" Add New Beneficiary", use_container_width=True):
            st.session_state.show_add_form = True

st.markdown("---")

# Show add/edit form if requested
if st.session_state.get("show_add_form", False):
    with st.expander(" Add New Beneficiary", expanded=True):
        st.subheader("Beneficiary Details")

        col1, col2 = st.columns(2)

        with col1:
            ben_name = st.text_input(
                "Beneficiary Name *", placeholder="Company or Individual Name"
            )
            ben_type = st.selectbox("Beneficiary Type *", ["Business", "Individual"])
            country = st.selectbox(
                "Country *",
                [
                    "DE - Germany",
                    "FR - France",
                    "ES - Spain",
                    "IT - Italy",
                    "NL - Netherlands",
                    "BE - Belgium",
                ],
            )

        with col2:
            reference = st.text_input(
                "Internal Reference", placeholder="Optional reference ID"
            )
            relationship = st.selectbox(
                "Relationship", ["Supplier", "Vendor", "Partner", "Employee", "Other"]
            )
            notes = st.text_area("Notes", placeholder="Additional information...")

        st.markdown("---")
        st.subheader("Bank Account Details")

        col1, col2 = st.columns(2)

        with col1:
            account_holder = st.text_input("Account Holder Name *")
            iban = st.text_input("IBAN *", placeholder="DE89370400440532013000")

            # IBAN validation hint
            if iban:
                if len(iban) >= 15:
                    st.success(" IBAN format looks valid")
                else:
                    st.warning(" IBAN seems too short")

        with col2:
            swift_bic = st.text_input("SWIFT/BIC *", placeholder="DEUTDEFF")

            # SWIFT validation hint
            if swift_bic:
                if len(swift_bic) in [8, 11]:
                    st.success(" SWIFT/BIC format looks valid")
                else:
                    st.warning(" SWIFT/BIC should be 8 or 11 characters")

            bank_name = st.text_input("Bank Name", placeholder="Deutsche Bank")
            currency = st.selectbox(
                "Account Currency *",
                [
                    "EUR - Euro",
                    "GBP - British Pound",
                    "USD - US Dollar",
                    "CHF - Swiss Franc",
                ],
            )

        st.markdown("---")

        col1, col2, col3 = st.columns([1, 1, 4])

        with col1:
            if st.button(" Save Beneficiary", use_container_width=True):
                st.success(" Beneficiary added successfully!")
                st.session_state.show_add_form = False
                st.rerun()

        with col2:
            if st.button(" Cancel", use_container_width=True):
                st.session_state.show_add_form = False
                st.rerun()

# Beneficiary list
st.subheader(" Your Beneficiaries")

# Filter options
col1, col2, col3, col4 = st.columns(4)

with col1:
    filter_status = st.selectbox("Status", ["All", "Active", "Inactive"])

with col2:
    filter_country = st.selectbox(
        "Country", ["All", "Germany", "France", "Spain", "Italy", "Netherlands"]
    )

with col3:
    filter_type = st.selectbox("Type", ["All", "Business", "Individual"])

with col4:
    filter_currency = st.selectbox("Currency", ["All", "EUR", "GBP", "USD", "CHF"])

st.markdown("---")

# Mock beneficiary data
beneficiaries_data = pd.DataFrame(
    {
        "Name": [
            "Supplier GmbH",
            "Tech Solutions SAS",
            "Global Trade SpA",
            "Manufacturing BV",
            "Export Services Ltd",
            "European Partners AG",
            "Digital Consulting",
            "Import Co SARL",
        ],
        "Type": [
            "Business",
            "Business",
            "Business",
            "Business",
            "Business",
            "Business",
            "Business",
            "Business",
        ],
        "Country": [
            "Germany",
            "France",
            "Italy",
            "Netherlands",
            "Spain",
            "Germany",
            "Belgium",
            "France",
        ],
        "Currency": ["EUR", "EUR", "EUR", "EUR", "EUR", "EUR", "EUR", "EUR"],
        "IBAN": [
            "DE89370400440532013000",
            "FR1420041010050500013M02606",
            "IT60X0542811101000000123456",
            "NL91ABNA0417164300",
            "ES9121000418450200051332",
            "DE89370400440532013001",
            "BE68539007547034",
            "FR1420041010050500013M02607",
        ],
        "Status": [
            "Active",
            "Active",
            "Active",
            "Active",
            "Inactive",
            "Active",
            "Active",
            "Active",
        ],
        "Payments": [15, 8, 23, 5, 12, 9, 3, 18],
        "Last Used": [
            "2026-01-10",
            "2026-01-08",
            "2026-01-11",
            "2026-01-05",
            "2025-12-20",
            "2026-01-09",
            "2026-01-06",
            "2026-01-11",
        ],
    }
)

# Display as interactive dataframe
st.dataframe(
    beneficiaries_data,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Status": st.column_config.TextColumn("Status", help="Beneficiary status"),
        "Payments": st.column_config.NumberColumn(
            "# Payments", help="Total number of payments made"
        ),
        "Last Used": st.column_config.DateColumn(
            "Last Used", help="Date of last payment"
        ),
    },
)

st.markdown("---")

# Beneficiary details expander
with st.expander("ℹ View Beneficiary Details"):
    selected_ben = st.selectbox(
        "Select Beneficiary", beneficiaries_data["Name"].tolist()
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Basic Information**")
        st.text(f"Name: {selected_ben}")
        st.text("Type: Business")
        st.text("Country: Germany")
        st.text("Relationship: Supplier")
        st.text("Status: Active")

    with col2:
        st.markdown("**Bank Details**")
        st.text("IBAN: DE89370400440532013000")
        st.text("SWIFT/BIC: DEUTDEFF")
        st.text("Bank: Deutsche Bank")
        st.text("Currency: EUR")
        st.text("Account Holder: Supplier GmbH")

    st.markdown("---")

    if can_edit:
        col1, col2, col3 = st.columns([1, 1, 4])

        with col1:
            if st.button(" Edit", use_container_width=True):
                st.info("Edit form would open here")

        with col2:
            if st.button(" Deactivate", use_container_width=True):
                st.warning("This will deactivate the beneficiary")

# Statistics
st.markdown("---")
st.subheader(" Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Beneficiaries", "8", "+2 this month")

with col2:
    st.metric("Active", "7", "87.5%")

with col3:
    st.metric("Most Used Currency", "EUR", "100%")

with col4:
    st.metric("Total Payments", "93", "+12")

if not can_edit:
    st.info("ℹ Only Makers and Admins can add or edit beneficiaries")

# Sidebar info
with st.sidebar:
    st.info(f"**Logged in as:** {st.session_state.user_name}")
    st.caption(f"Role: {st.session_state.user_role.title()}")

    st.markdown("---")

    st.markdown("** Tips**")
    st.caption("• Verify IBAN and SWIFT codes before saving")
    st.caption("• Keep beneficiary information up to date")
    st.caption("• Inactive beneficiaries cannot receive payments")
