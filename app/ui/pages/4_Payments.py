"""
Payment Management Page
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Payments", page_icon="", layout="wide")

# Check authentication
if not st.session_state.get("authenticated", False):
    st.error(" Please log in to access this page")
    st.stop()

st.title(" Payment Management")
st.markdown("---")

# Only Makers and Admins can create payments
can_create = st.session_state.user_role in ["admin", "maker"]

# Tabs for different views
tab1, tab2, tab3 = st.tabs(
    [" All Payments", " Create Payment", " Payment Details"]
)

with tab1:
    st.subheader("Payment List")

    # Filters
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        filter_status = st.selectbox(
            "Status",
            [
                "All",
                "Draft",
                "Pending Approval",
                "Approved",
                "Processing",
                "Completed",
                "Failed",
                "Rejected",
            ],
        )

    with col2:
        filter_currency = st.selectbox("Currency", ["All", "GBP", "EUR", "USD", "CHF"])

    with col3:
        filter_date_from = st.date_input(
            "From Date", datetime.now() - timedelta(days=30)
        )

    with col4:
        filter_date_to = st.date_input("To Date", datetime.now())

    with col5:
        if can_create:
            if st.button(" New Payment", use_container_width=True):
                st.session_state.active_tab = 1
                st.rerun()

    st.markdown("---")

    # Mock payment data
    payments_data = pd.DataFrame(
        {
            "Payment ID": [
                "PAY-001",
                "PAY-002",
                "PAY-003",
                "PAY-004",
                "PAY-005",
                "PAY-006",
                "PAY-007",
                "PAY-008",
                "PAY-009",
                "PAY-010",
            ],
            "Beneficiary": [
                "Supplier GmbH",
                "Tech Solutions SAS",
                "Global Trade SpA",
                "Manufacturing BV",
                "Export Services Ltd",
                "European Partners AG",
                "Digital Consulting",
                "Import Co SARL",
                "Supplier GmbH",
                "Tech Solutions SAS",
            ],
            "Source": [
                "GBP 10,500.00",
                "GBP 25,000.00",
                "GBP 5,750.00",
                "GBP 18,200.00",
                "GBP 12,900.00",
                "GBP 8,450.00",
                "GBP 15,600.00",
                "GBP 22,100.00",
                "GBP 9,800.00",
                "GBP 31,200.00",
            ],
            "Target": [
                "EUR 12,208.50",
                "USD 32,125.00",
                "EUR 6,686.25",
                "EUR 21,163.00",
                "USD 16,576.50",
                "EUR 9,823.75",
                "EUR 18,144.00",
                "EUR 25,706.50",
                "EUR 11,397.00",
                "USD 40,092.00",
            ],
            "FX Rate": [
                "1.1627",
                "1.2850",
                "1.1627",
                "1.1627",
                "1.2850",
                "1.1627",
                "1.1627",
                "1.1627",
                "1.1627",
                "1.2850",
            ],
            "Status": [
                "Pending Approval",
                "Completed",
                "Completed",
                "Draft",
                "Processing",
                "Approved",
                "Rejected",
                "Failed",
                "Pending Approval",
                "Completed",
            ],
            "Created By": [
                "Maker User",
                "Maker User",
                "Maker User",
                "Maker User",
                "Maker User",
                "Maker User",
                "Maker User",
                "Finance Manager",
                "Maker User",
                "Finance Manager",
            ],
            "Created Date": [
                (datetime.now() - timedelta(days=0)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=9)).strftime("%Y-%m-%d"),
            ],
        }
    )

    # Display payments
    st.dataframe(
        payments_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.TextColumn("Status", help="Payment status"),
            "Payment ID": st.column_config.TextColumn(
                "Payment ID", help="Unique payment identifier"
            ),
        },
    )

    # Summary statistics
    st.markdown("---")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Payments", "10")

    with col2:
        st.metric("Pending Approval", "2", "+1")

    with col3:
        st.metric("Completed", "3", "30%")

    with col4:
        st.metric("Total Value", "£159,500")

    with col5:
        st.metric("Failed/Rejected", "2", "-1")

with tab2:
    st.subheader("Create New Payment")

    if not can_create:
        st.warning(" Only Makers and Admins can create payments")
        st.info("Please contact a Maker or Admin to create payments")
    else:
        with st.form("payment_form"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Beneficiary Selection**")

                beneficiary = st.selectbox(
                    "Select Beneficiary *",
                    [
                        "Supplier GmbH (Germany, EUR)",
                        "Tech Solutions SAS (France, EUR)",
                        "Global Trade SpA (Italy, EUR)",
                        "Manufacturing BV (Netherlands, EUR)",
                    ],
                )

                bank_account = st.selectbox(
                    "Bank Account *", ["DE89370400440532013000 - Deutsche Bank (EUR)"]
                )

                st.markdown("---")
                st.markdown("**Payment Details**")

                source_currency = st.selectbox(
                    "Source Currency *",
                    ["GBP - British Pound", "EUR - Euro", "USD - US Dollar"],
                )

                target_currency = st.selectbox(
                    "Target Currency *",
                    ["EUR - Euro", "USD - US Dollar", "GBP - British Pound"],
                    disabled=True,
                    help="Based on beneficiary's bank account",
                )

            with col2:
                st.markdown("**Amount**")

                amount_type = st.radio(
                    "Amount Type",
                    ["Fixed Source Amount", "Fixed Target Amount"],
                    help="Choose whether to fix the send or receive amount",
                )

                if amount_type == "Fixed Source Amount":
                    source_amount = st.number_input(
                        "Amount to Send (GBP) *",
                        min_value=100.0,
                        max_value=1000000.0,
                        value=10000.0,
                        step=100.0,
                        format="%.2f",
                    )

                    # Mock calculation
                    fx_rate = 1.1650
                    target_amount = source_amount * fx_rate

                    st.info(f"They will receive: **EUR {target_amount:,.2f}**")
                else:
                    target_amount = st.number_input(
                        "Amount to Receive (EUR) *",
                        min_value=100.0,
                        max_value=1000000.0,
                        value=11650.0,
                        step=100.0,
                        format="%.2f",
                    )

                    # Mock calculation
                    fx_rate = 1.1650
                    source_amount = target_amount / fx_rate

                    st.info(f"You will send: **GBP {source_amount:,.2f}**")

                st.markdown("---")
                st.markdown("**Additional Information**")

                execution_date = st.date_input(
                    "Execution Date *",
                    value=datetime.now(),
                    min_value=datetime.now(),
                    max_value=datetime.now() + timedelta(days=30),
                )

                payment_reference = st.text_input(
                    "Payment Reference",
                    placeholder="Invoice INV-2026-001",
                    help="Internal reference for this payment",
                )

            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**FX Quote**")

                use_existing_quote = st.checkbox("Use existing FX quote")

                if use_existing_quote:
                    quote_id = st.selectbox(
                        "Select Quote",
                        [
                            "QT-20260111103045 (Rate: 1.1707, Expires: 1m 45s)",
                            "Request new quote",
                        ],
                    )
                else:
                    st.info("A new quote will be requested upon payment creation")

            with col2:
                st.markdown("**Cost Breakdown**")

                # Mock calculation
                fee = source_amount * 0.001
                total_debit = source_amount + fee

                breakdown_df = pd.DataFrame(
                    {
                        "Item": [
                            "Source Amount",
                            "FX Rate",
                            "Target Amount",
                            "Fee (0.1%)",
                            "Total Debit",
                        ],
                        "Value": [
                            f"GBP {source_amount:,.2f}",
                            f"{fx_rate:.6f}",
                            f"EUR {target_amount:,.2f}",
                            f"GBP {fee:,.2f}",
                            f"GBP {total_debit:,.2f}",
                        ],
                    }
                )

                st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

            st.markdown("---")

            purpose = st.text_area(
                "Payment Purpose *",
                placeholder="Describe the purpose of this payment",
                help="Required for compliance and record-keeping",
            )

            st.markdown("---")

            col1, col2, col3 = st.columns([1, 1, 2])

            with col1:
                save_draft = st.form_submit_button(
                    " Save as Draft", use_container_width=True
                )
                if save_draft:
                    st.success(" Payment saved as draft!")

            with col2:
                submit_approval = st.form_submit_button(
                    " Submit for Approval", use_container_width=True
                )
                if submit_approval:
                    st.success(" Payment submitted for approval!")
                    st.balloons()

with tab3:
    st.subheader("Payment Details")

    payment_id = st.selectbox(
        "Select Payment to View",
        ["PAY-001", "PAY-002", "PAY-003", "PAY-004", "PAY-005"],
    )

    st.markdown("---")

    # Mock payment details
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Payment Information**")
        st.text(f"Payment ID: {payment_id}")
        st.text("Status: Pending Approval")
        st.text("Created: 2026-01-11 10:30:45")
        st.text("Created By: Maker User")
        st.text("Execution Date: 2026-01-12")

        st.markdown("---")

        st.markdown("**Beneficiary**")
        st.text("Name: Supplier GmbH")
        st.text("Country: Germany")
        st.text("Bank: Deutsche Bank")
        st.text("IBAN: DE89370400440532013000")
        st.text("SWIFT: DEUTDEFF")

    with col2:
        st.markdown("**Amount Details**")
        st.text("Source Amount: GBP 10,000.00")
        st.text("Target Amount: EUR 11,650.00")
        st.text("FX Rate: 1.165000")
        st.text("Fee: GBP 10.00")
        st.text("Total Debit: GBP 10,010.00")

        st.markdown("---")

        st.markdown("**FX Quote**")
        st.text("Quote ID: QT-20260111103045")
        st.text("Base Rate: 1.165000")
        st.text("Markup: 0.50%")
        st.text("Quote Created: 2026-01-11 10:30:00")

    st.markdown("---")

    st.markdown("**Payment Purpose**")
    st.info("Payment for invoice INV-2026-001 - Raw materials supply for Q1 2026")

    st.markdown("---")

    st.markdown("**Approval History**")

    approval_data = pd.DataFrame(
        {
            "Timestamp": ["2026-01-11 10:35:22"],
            "User": ["Maker User"],
            "Action": ["Submitted for Approval"],
            "Comments": ["Urgent payment - please review ASAP"],
        }
    )

    st.dataframe(approval_data, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Action buttons based on status and role
    if st.session_state.user_role == "maker":
        col1, col2 = st.columns(2)

        with col1:
            if st.button(" Edit Payment", use_container_width=True):
                st.info("Only draft payments can be edited")

        with col2:
            if st.button(" Cancel Payment", use_container_width=True):
                st.warning("This will cancel the payment and notification will be sent")

# Sidebar info
with st.sidebar:
    st.info(f"**Logged in as:** {st.session_state.user_name}")
    st.caption(f"Role: {st.session_state.user_role.title()}")

    st.markdown("---")

    st.markdown("** Payment Tips**")
    st.caption("• Lock FX rate by using recent quote")
    st.caption("• Save as draft to complete later")
    st.caption("• Review all details before submitting")
    st.caption("• Makers cannot approve own payments")

    st.markdown("---")

    st.markdown("** Your Activity**")
    if can_create:
        st.metric("Drafts", "2")
        st.metric("Pending", "3")
        st.metric("This Month", "12")
