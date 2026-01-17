"""
FX Quotes Page
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from decimal import Decimal
import time
from app.database.connection import SessionLocal
from app.services.fx_service import FXService

st.set_page_config(page_title="FX Quotes", page_icon="", layout="wide")

# Check authentication
if not st.session_state.get("authenticated", False):
    st.error(" Please log in to access this page")
    st.stop()

st.title(" FX Quotes")
st.markdown("---")

# Get database session
db = SessionLocal()

try:
    fx_service = FXService(db)

    # Get supported currencies
    currencies = fx_service.get_supported_currencies()

    # Request new quote section
    st.subheader(" Request FX Quote")

    with st.form("quote_request_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            from_currency = st.selectbox(
                "From Currency *",
                options=currencies,
                index=currencies.index("GBP") if "GBP" in currencies else 0,
            )

        with col2:
            to_currency = st.selectbox(
                "To Currency *",
                options=currencies,
                index=currencies.index("EUR") if "EUR" in currencies else 1,
            )

        with col3:
            amount = st.number_input(
                "Amount *", min_value=0.01, value=1000.00, step=100.00, format="%.2f"
            )

        st.caption(
            f"Quote will be valid for {120} seconds. Markup: {fx_service.markup_percentage * 100:.2f}%"
        )

        submitted = st.form_submit_button(" Get Quote", use_container_width=True)

        if submitted:
            if from_currency == to_currency:
                st.error("Source and target currencies must be different")
            else:
                with st.spinner("Fetching live FX rate..."):
                    quote, error = fx_service.request_quote(
                        company_id=st.session_state.company_id,
                        from_currency=from_currency,
                        to_currency=to_currency,
                        amount=Decimal(str(amount)),
                        user_id=st.session_state.user_id,
                    )

                    if error:
                        st.error(f"Error requesting quote: {error}")
                    else:
                        st.success(f" Quote received! Valid for 120 seconds")
                        st.rerun()

    st.markdown("---")

    # Display active quotes
    st.subheader(" Active Quotes")

    active_quotes = fx_service.get_active_quotes(st.session_state.company_id)

    if active_quotes:
        for quote in active_quotes:
            # Check if still valid
            time_remaining = fx_service.get_quote_time_remaining(quote)
            is_valid = time_remaining > 0

            # Create expander for each quote
            status_icon = "✓" if is_valid else "⏱"
            expander_label = f"{status_icon} {quote.source_currency} → {quote.target_currency} | Rate: {quote.final_rate} | Expires in: {time_remaining}s"

            with st.expander(expander_label, expanded=is_valid):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("**Quote Details**")
                    st.text(f"Quote ID: {quote.quote_id}")
                    st.text(f"From: {quote.source_currency}")
                    st.text(f"To: {quote.target_currency}")
                    st.text(f"Created: {quote.created_at.strftime('%H:%M:%S')}")

                with col2:
                    st.markdown("**Rate Breakdown**")
                    breakdown = fx_service.get_rate_breakdown(quote)
                    st.text(f"Base Rate: {breakdown['base_rate']}")
                    st.text(f"Markup: {breakdown['markup_percentage']}%")
                    st.text(f"Final Rate: {breakdown['final_rate']}")
                    st.text(f"Inverse: {breakdown['inverse_rate']}")

                with col3:
                    st.markdown("**Example Conversion**")
                    example_amount = Decimal("1000.00")
                    calc = fx_service.calculate_amount(quote, example_amount)
                    st.text(f"Amount: {calc['source_amount']} {quote.source_currency}")
                    st.text(
                        f"Converts to: {calc['target_amount']} {quote.target_currency}"
                    )
                    st.text(f"Markup Fee: {calc['markup_fee']} {quote.target_currency}")

                # Expiry status
                if is_valid:
                    progress_value = time_remaining / 120.0
                    st.progress(
                        progress_value, text=f"Valid for {time_remaining} more seconds"
                    )
                else:
                    st.error(" Quote expired")

                # Auto-refresh countdown
                if is_valid and time_remaining > 0:
                    # Use empty placeholder for countdown
                    st.caption("Page will auto-refresh to update countdown")

    else:
        st.info("No active quotes. Request a quote above to get started.")

    # Add auto-refresh for active quotes
    if active_quotes and any(
        fx_service.get_quote_time_remaining(q) > 0 for q in active_quotes
    ):
        time.sleep(5)  # Refresh every 5 seconds
        st.rerun()

    st.markdown("---")

    # Recent quotes history
    st.subheader(" Recent Quotes (Last 7 Days)")

    recent_quotes = fx_service.get_company_quotes(
        st.session_state.company_id, include_expired=True
    )[:20]

    if recent_quotes:
        quote_list = []
        for quote in recent_quotes:
            is_valid = fx_service.is_quote_valid(quote)
            quote_list.append(
                {
                    "Quote ID": quote.quote_id[:20] + "...",
                    "Currency Pair": f"{quote.source_currency}/{quote.target_currency}",
                    "Rate": f"{quote.final_rate}",
                    "Markup": f"{quote.markup_percentage * 100:.2f}%",
                    "Status": "Active" if is_valid else "Expired",
                    "Created": quote.created_at.strftime("%Y-%m-%d %H:%M"),
                    "Expires": quote.quote_expires_at.strftime("%H:%M:%S"),
                }
            )

        df = pd.DataFrame(quote_list)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No recent quotes found.")

    # Statistics
    st.markdown("---")
    st.subheader(" Statistics (Last 30 Days)")

    stats = fx_service.get_quote_statistics(st.session_state.company_id, days=30)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Quotes", stats["total_quotes"])

    with col2:
        st.metric("Active Quotes", stats["active_quotes"])

    with col3:
        st.metric("Expired Quotes", stats["expired_quotes"])

    with col4:
        st.metric("Currency Pairs", len(stats["currency_pairs"]))

    if stats["currency_pairs"]:
        st.markdown("**Popular Currency Pairs:**")
        st.write(", ".join(stats["currency_pairs"]))

finally:
    db.close()

# Sidebar info
with st.sidebar:
    st.info(f"**Logged in as:** {st.session_state.user_name}")
    st.caption(f"Role: {st.session_state.user_role.title()}")

    st.markdown("---")

    st.markdown("** FX Quote Info**")
    st.caption("• Quotes are valid for 120 seconds")
    st.caption(f"• Markup applied: {fx_service.markup_percentage * 100:.2f}%")
    st.caption("• Rates update in real-time")
    st.caption("• Page auto-refreshes for active quotes")

    st.markdown("---")

    st.markdown("** Supported Currencies**")
    currencies_display = ", ".join(sorted(fx_service.get_supported_currencies()))
    st.caption(currencies_display)
