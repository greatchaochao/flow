"""
FX Quote Request Page
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="FX Quotes", page_icon="", layout="wide")

# Check authentication
if not st.session_state.get("authenticated", False):
    st.error(" Please log in to access this page")
    st.stop()

st.title(" FX Quote Engine")
st.markdown("Get real-time foreign exchange quotes with transparent pricing")
st.markdown("---")

# Initialize session state for quote data
if "current_quote" not in st.session_state:
    st.session_state.current_quote = None
if "quote_expiry" not in st.session_state:
    st.session_state.quote_expiry = None

# Two column layout
col1, col2 = st.columns([2, 3])

with col1:
    st.subheader(" Request FX Quote")

    with st.form("fx_quote_form"):
        source_currency = st.selectbox(
            "From Currency *",
            ["GBP - British Pound", "EUR - Euro", "USD - US Dollar"],
            index=0,
        )

        target_currency = st.selectbox(
            "To Currency *",
            [
                "EUR - Euro",
                "USD - US Dollar",
                "GBP - British Pound",
                "CHF - Swiss Franc",
            ],
            index=0,
        )

        amount = st.number_input(
            "Amount *",
            min_value=100.0,
            max_value=1000000.0,
            value=10000.0,
            step=100.0,
            format="%.2f",
        )

        quote_type = st.radio(
            "Quote Type",
            ["I want to send this amount", "I want them to receive this amount"],
            horizontal=False,
        )

        purpose = st.selectbox(
            "Payment Purpose",
            [
                "Trade Payment",
                "Invoice Settlement",
                "Salary Payment",
                "Service Fee",
                "Other",
            ],
        )

        submit = st.form_submit_button(" Get Quote", use_container_width=True)

        if submit:
            # Simulate getting a quote
            with st.spinner("Fetching live FX rate..."):
                time.sleep(1)  # Simulate API call

                # Mock quote data
                base_rate = 1.1650 if "EUR" in target_currency else 1.2850
                markup = 0.005  # 0.5%
                final_rate = base_rate * (1 + markup)

                source_curr = source_currency.split(" - ")[0]
                target_curr = target_currency.split(" - ")[0]

                if quote_type == "I want to send this amount":
                    source_amount = amount
                    target_amount = amount * final_rate
                else:
                    target_amount = amount
                    source_amount = amount / final_rate

                fee = source_amount * 0.001  # 0.1% fee
                total_debit = source_amount + fee

                st.session_state.current_quote = {
                    "quote_id": f"QT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "source_currency": source_curr,
                    "target_currency": target_curr,
                    "source_amount": source_amount,
                    "target_amount": target_amount,
                    "base_rate": base_rate,
                    "markup": markup,
                    "final_rate": final_rate,
                    "fee": fee,
                    "total_debit": total_debit,
                    "created_at": datetime.now(),
                }
                st.session_state.quote_expiry = datetime.now() + timedelta(seconds=120)

            st.success(" Quote retrieved successfully!")
            st.rerun()

with col2:
    st.subheader(" Current Quote")

    if st.session_state.current_quote:
        quote = st.session_state.current_quote

        # Check if quote is expired
        if datetime.now() > st.session_state.quote_expiry:
            st.error(" This quote has expired. Please request a new quote.")
            st.session_state.current_quote = None
            st.session_state.quote_expiry = None
        else:
            # Calculate remaining time
            remaining_seconds = (
                st.session_state.quote_expiry - datetime.now()
            ).total_seconds()
            remaining_time = (
                f"{int(remaining_seconds // 60)}m {int(remaining_seconds % 60)}s"
            )

            # Quote expiry warning
            if remaining_seconds < 30:
                st.warning(f"⏰ Quote expires in {remaining_time}")
            else:
                st.info(f"⏱ Quote valid for: {remaining_time}")

            # Progress bar for quote expiry
            progress = remaining_seconds / 120
            st.progress(progress)

            st.markdown("---")

            # Quote details
            st.markdown(f"**Quote ID:** `{quote['quote_id']}`")
            st.markdown(
                f"**Created:** {quote['created_at'].strftime('%Y-%m-%d %H:%M:%S')}"
            )

            st.markdown("---")

            # Exchange rate display
            col_a, col_b = st.columns(2)

            with col_a:
                st.metric(
                    label=f"You Send ({quote['source_currency']})",
                    value=f"{quote['source_currency']} {quote['source_amount']:,.2f}",
                )

            with col_b:
                st.metric(
                    label=f"They Receive ({quote['target_currency']})",
                    value=f"{quote['target_currency']} {quote['target_amount']:,.2f}",
                )

            st.markdown("---")

            # Rate breakdown
            st.markdown("** Rate Breakdown**")

            breakdown_df = pd.DataFrame(
                {
                    "Description": [
                        "Base Exchange Rate",
                        "Our Markup (0.5%)",
                        "Final Exchange Rate",
                        "Transaction Fee (0.1%)",
                        "Total Amount to Debit",
                    ],
                    "Value": [
                        f"{quote['base_rate']:.6f}",
                        f"{quote['markup'] * 100:.2f}%",
                        f"{quote['final_rate']:.6f}",
                        f"{quote['source_currency']} {quote['fee']:.2f}",
                        f"{quote['source_currency']} {quote['total_debit']:.2f}",
                    ],
                }
            )

            st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

            st.markdown("---")

            # Action buttons
            col1, col2 = st.columns(2)

            with col1:
                if st.button(" Use This Quote", use_container_width=True):
                    st.success("Quote locked! Redirecting to payment creation...")
                    time.sleep(1)
                    st.info(
                        " In full version, this would create a payment with this quote"
                    )

            with col2:
                if st.button(" Refresh Quote", use_container_width=True):
                    st.session_state.current_quote = None
                    st.session_state.quote_expiry = None
                    st.rerun()

            # Transparency message
            st.markdown("---")
            st.success("""
             **Transparent Pricing**
            
            We show you exactly how we calculate your rate:
            - Base rate from live market data
            - Our markup clearly displayed (0.5%)
            - All fees shown upfront
            - No hidden charges
            """)

            # Auto-refresh to update countdown
            time.sleep(1)
            st.rerun()

    else:
        st.info(" Request a quote to see live FX rates and pricing breakdown")

        st.markdown("---")

        st.markdown("** How it works:**")
        st.markdown("""
        1. **Select currencies** - Choose source and target currencies
        2. **Enter amount** - Specify how much you want to send or receive
        3. **Get instant quote** - See live rate with full breakdown
        4. **Quote valid for 2 minutes** - Lock in the rate by creating a payment
        5. **Transparent pricing** - All fees and markups clearly shown
        """)

        st.markdown("---")

        st.markdown("** Supported Currencies:**")

        currencies_df = pd.DataFrame(
            {
                "Currency": ["GBP", "EUR", "USD", "CHF"],
                "Name": ["British Pound", "Euro", "US Dollar", "Swiss Franc"],
                "Status": [
                    " Available",
                    " Available",
                    " Available",
                    " Available",
                ],
            }
        )

        st.dataframe(currencies_df, use_container_width=True, hide_index=True)

# Recent quotes section
st.markdown("---")
st.subheader(" Recent Quotes")

recent_quotes_data = pd.DataFrame(
    {
        "Quote ID": [
            "QT-20260111103045",
            "QT-20260111095230",
            "QT-20260111091520",
            "QT-20260110163045",
        ],
        "From": ["GBP", "GBP", "EUR", "GBP"],
        "To": ["EUR", "USD", "GBP", "EUR"],
        "Amount": ["£10,000.00", "£25,000.00", "€5,000.00", "£15,000.00"],
        "Rate": ["1.1707", "1.2916", "0.8565", "1.1695"],
        "Status": ["Used", "Expired", "Used", "Used"],
        "Created": [
            "2026-01-11 10:30",
            "2026-01-11 09:52",
            "2026-01-11 09:15",
            "2026-01-10 16:30",
        ],
    }
)

st.dataframe(
    recent_quotes_data,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Status": st.column_config.TextColumn("Status", help="Quote usage status")
    },
)

# Sidebar info
with st.sidebar:
    st.info(f"**Logged in as:** {st.session_state.user_name}")
    st.caption(f"Role: {st.session_state.user_role.title()}")

    st.markdown("---")

    st.markdown("** FX Quote Tips**")
    st.caption("• Quotes are valid for 2 minutes")
    st.caption("• Lock rate by creating payment immediately")
    st.caption("• Rates update in real-time")
    st.caption("• All fees shown transparently")

    st.markdown("---")

    st.markdown("** Today's Market**")
    st.metric("GBP/EUR", "1.1650", "+0.15%")
    st.metric("GBP/USD", "1.2850", "-0.08%")
    st.metric("EUR/USD", "1.1025", "+0.05%")
