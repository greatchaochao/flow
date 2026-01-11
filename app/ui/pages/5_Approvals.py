"""
Payment Approval Page
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Approvals", page_icon="", layout="wide")

# Check authentication
if not st.session_state.get("authenticated", False):
    st.error(" Please log in to access this page")
    st.stop()

st.title(" Payment Approvals")
st.markdown("Review and approve payment requests")
st.markdown("---")

# Only Approvers and Admins can approve payments
can_approve = st.session_state.user_role in ["admin", "approver"]

if not can_approve:
    st.warning(" Only Approvers and Admins can access this page")
    st.info(
        "You are logged in as a Maker. Contact an Approver to review pending payments."
    )
    st.stop()

# Tabs
tab1, tab2, tab3 = st.tabs(["⏳ Pending Approvals", " Approved", " Rejected"])

with tab1:
    st.subheader("Payments Awaiting Approval")

    # Filters
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        filter_creator = st.selectbox(
            "Created By", ["All", "Maker User", "Finance Manager"]
        )

    with col2:
        filter_amount = st.selectbox(
            "Amount Range", ["All", "< £10k", "£10k - £50k", "> £50k"]
        )

    with col3:
        filter_urgent = st.checkbox("Urgent Only")

    st.markdown("---")

    # Pending payments
    pending_data = pd.DataFrame(
        {
            "Payment ID": ["PAY-001", "PAY-009", "PAY-012"],
            "Beneficiary": ["Supplier GmbH", "Supplier GmbH", "Tech Solutions SAS"],
            "Source Amount": ["GBP 10,500.00", "GBP 9,800.00", "GBP 15,200.00"],
            "Target Amount": ["EUR 12,208.50", "EUR 11,397.00", "EUR 17,683.00"],
            "Created By": ["Maker User", "Maker User", "Finance Manager"],
            "Submitted": [
                (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
                (datetime.now() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"),
                (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
            ],
            "Priority": [" Urgent", "🟡 Normal", "🟡 Normal"],
        }
    )

    st.dataframe(pending_data, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Detailed review section
    st.subheader("Review Payment")

    selected_payment = st.selectbox(
        "Select Payment to Review",
        [
            "PAY-001 - Supplier GmbH (GBP 10,500.00)",
            "PAY-009 - Supplier GmbH (GBP 9,800.00)",
            "PAY-012 - Tech Solutions SAS (GBP 15,200.00)",
        ],
    )

    st.markdown("---")

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        st.markdown("**Payment Details**")
        st.text("Payment ID: PAY-001")
        st.text("Status: Pending Approval")
        st.text("Created: 2026-01-11 10:30:45")
        st.text("Created By: Maker User")
        st.text("Execution Date: 2026-01-12")
        st.text("Reference: Invoice INV-2026-001")

        st.markdown("---")

        st.markdown("**Amount Breakdown**")
        st.text("Source: GBP 10,000.00")
        st.text("FX Rate: 1.165000")
        st.text("Target: EUR 11,650.00")
        st.text("Fee: GBP 10.00")
        st.text("Total Debit: GBP 10,010.00")

    with col2:
        st.markdown("**Beneficiary Information**")
        st.text("Name: Supplier GmbH")
        st.text("Type: Business")
        st.text("Country: Germany")
        st.text("Bank: Deutsche Bank")
        st.text("IBAN: DE89370400440532013000")
        st.text("SWIFT/BIC: DEUTDEFF")
        st.text("Currency: EUR")

        st.markdown("---")

        st.markdown("**FX Quote Details**")
        st.text("Quote ID: QT-20260111103045")
        st.text("Base Rate: 1.165000")
        st.text("Our Markup: 0.50%")
        st.text("Quote Time: 2026-01-11 10:30")

    with col3:
        st.markdown("**Risk Indicators**")

        st.success(" Known beneficiary")
        st.success(" Within volume limits")
        st.success(" Valid FX quote")
        st.success(" Bank details verified")

        st.markdown("---")

        st.metric("Previous Payments", "14", "To this beneficiary")

    st.markdown("---")

    st.markdown("**Payment Purpose**")
    st.info("Payment for invoice INV-2026-001 - Raw materials supply for Q1 2026")

    st.markdown("---")

    st.markdown("**Maker's Comments**")
    st.text_area(
        "Comments from Maker",
        value="Urgent payment - please review ASAP. Supplier requires payment by end of business today.",
        disabled=True,
        height=80,
    )

    st.markdown("---")

    # Approval/Rejection form
    st.subheader("Your Decision")

    col1, col2 = st.columns(2)

    with col1:
        approver_comments = st.text_area(
            "Add Comments (Optional)",
            placeholder="Add any comments or notes about this decision...",
            help="Your comments will be recorded in the audit trail",
        )

    with col2:
        st.markdown("**Approval Checklist**")

        check1 = st.checkbox(" Beneficiary details verified", value=True)
        check2 = st.checkbox(" Amount and currency correct", value=True)
        check3 = st.checkbox(" FX rate is reasonable", value=True)
        check4 = st.checkbox(" Purpose is clear and valid", value=True)
        check5 = st.checkbox(" No red flags identified", value=True)

        all_checked = check1 and check2 and check3 and check4 and check5

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button(
            " Approve Payment", use_container_width=True, disabled=not all_checked
        ):
            st.success(" Payment PAY-001 approved successfully!")
            st.info("The payment will be submitted to the payment provider.")
            st.balloons()

    with col2:
        if st.button(" Reject Payment", use_container_width=True):
            if approver_comments:
                st.error(" Payment PAY-001 rejected")
                st.info("The maker will be notified of the rejection.")
            else:
                st.warning(
                    " Please add comments explaining why you are rejecting this payment"
                )

    if not all_checked:
        st.warning(" Please complete the approval checklist before approving")

    st.markdown("---")

    # Maker-Checker enforcement
    st.info(
        " **Maker-Checker Control**: You cannot approve payments created by yourself"
    )

with tab2:
    st.subheader("Approved Payments")

    approved_data = pd.DataFrame(
        {
            "Payment ID": ["PAY-002", "PAY-003", "PAY-006", "PAY-010"],
            "Beneficiary": [
                "Tech Solutions SAS",
                "Global Trade SpA",
                "European Partners AG",
                "Tech Solutions SAS",
            ],
            "Amount": [
                "GBP 25,000.00",
                "GBP 5,750.00",
                "GBP 8,450.00",
                "GBP 31,200.00",
            ],
            "Target": [
                "USD 32,125.00",
                "EUR 6,686.25",
                "EUR 9,823.75",
                "USD 40,092.00",
            ],
            "Approved By": [
                "Approver User",
                "Approver User",
                "Admin User",
                "Approver User",
            ],
            "Approved Date": [
                (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
                (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"),
                (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M"),
                (datetime.now() - timedelta(days=9)).strftime("%Y-%m-%d %H:%M"),
            ],
            "Status": ["Completed", "Completed", "Approved", "Completed"],
        }
    )

    st.dataframe(approved_data, use_container_width=True, hide_index=True)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Approved", "4")

    with col2:
        st.metric("Total Value", "£70,400")

    with col3:
        st.metric("Avg Approval Time", "2.5 hours")

with tab3:
    st.subheader("Rejected Payments")

    rejected_data = pd.DataFrame(
        {
            "Payment ID": ["PAY-007", "PAY-013"],
            "Beneficiary": ["Digital Consulting", "Unknown Supplier Ltd"],
            "Amount": ["GBP 15,600.00", "GBP 45,000.00"],
            "Rejected By": ["Approver User", "Admin User"],
            "Rejected Date": [
                (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d %H:%M"),
                (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M"),
            ],
            "Reason": [
                "Beneficiary bank details need verification",
                "Unverified beneficiary - further due diligence required",
            ],
        }
    )

    st.dataframe(rejected_data, use_container_width=True, hide_index=True)

    st.markdown("---")

    st.info("ℹ Rejected payments can be edited and resubmitted by the maker")

# Summary metrics
st.markdown("---")
st.subheader(" Approval Statistics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Pending Review", "3", "+1 today")

with col2:
    st.metric("Approved Today", "0", "0%")

with col3:
    st.metric("Rejected Today", "0", "0%")

with col4:
    st.metric("Approval Rate", "85%", "+5%")

with col5:
    st.metric("Avg Review Time", "3.2 hrs", "-0.8 hrs")

# Sidebar info
with st.sidebar:
    st.info(f"**Logged in as:** {st.session_state.user_name}")
    st.caption(f"Role: {st.session_state.user_role.title()}")

    st.markdown("---")

    st.markdown("** Approver Guidelines**")
    st.caption("• Verify beneficiary details")
    st.caption("• Check FX rates are reasonable")
    st.caption("• Ensure payment purpose is clear")
    st.caption("• Cannot approve own payments")
    st.caption("• Add comments for rejections")

    st.markdown("---")

    st.markdown("** Quick Stats**")
    st.metric("Your Approvals (MTD)", "12")
    st.metric("Pending Your Review", "3")
    st.metric("Your Rejection Rate", "15%")
