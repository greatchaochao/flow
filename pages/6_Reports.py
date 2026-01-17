"""
Reports and Analytics Page
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Reports", page_icon="", layout="wide")

# Check authentication
if not st.session_state.get("authenticated", False):
    st.error(" Please log in to access this page")
    st.stop()

st.title(" Reports & Analytics")
st.markdown("Track your payment activity and FX volume")
st.markdown("---")

# Date range selector
col1, col2, col3 = st.columns([2, 2, 3])

with col1:
    date_from = st.date_input("From Date", value=datetime.now() - timedelta(days=30))

with col2:
    date_to = st.date_input("To Date", value=datetime.now())

with col3:
    report_type = st.selectbox(
        "Report Period",
        [
            "Last 7 Days",
            "Last 30 Days",
            "This Month",
            "Last Month",
            "This Quarter",
            "Custom Range",
        ],
    )

st.markdown("---")

# Key metrics
st.subheader(" Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Payments",
        "28",
        "+12 vs last period",
        help="Total number of payments processed",
    )

with col2:
    st.metric("Total Volume", "£456,850", "+15.2%", help="Total payment volume in GBP")

with col3:
    st.metric("Avg Payment Size", "£16,316", "+2.8%", help="Average payment amount")

with col4:
    st.metric(
        "Success Rate",
        "92.9%",
        "+1.2%",
        help="Percentage of successfully completed payments",
    )

with col5:
    st.metric("Total Fees Paid", "£456.85", "+15.2%", help="Total transaction fees")

st.markdown("---")

# Tabs for different reports
tab1, tab2, tab3, tab4 = st.tabs(
    [" Overview", " FX Analysis", " Beneficiary Report", " Export Data"]
)

with tab1:
    st.subheader("Payment Overview")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Payment volume over time
        st.markdown("**Payment Volume Trend**")

        # Mock data
        dates = pd.date_range(start=date_from, end=date_to, freq="D")
        volumes = [15000 + (i * 1000) + (5000 * (i % 3)) for i in range(len(dates))]

        trend_df = pd.DataFrame({"Date": dates, "Volume (GBP)": volumes})

        fig = px.line(
            trend_df,
            x="Date",
            y="Volume (GBP)",
            title="Daily Payment Volume",
            markers=True,
        )
        fig.update_layout(hovermode="x unified", showlegend=False)

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Payment status breakdown
        st.markdown("**Payment Status**")

        status_df = pd.DataFrame(
            {
                "Status": [
                    "Completed",
                    "Processing",
                    "Pending Approval",
                    "Failed",
                    "Rejected",
                ],
                "Count": [18, 3, 3, 2, 2],
            }
        )

        fig = px.pie(
            status_df,
            values="Count",
            names="Status",
            color="Status",
            color_discrete_map={
                "Completed": "#00CC66",
                "Processing": "#3399FF",
                "Pending Approval": "#FFCC00",
                "Failed": "#FF6666",
                "Rejected": "#FF9999",
            },
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(showlegend=False)

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        # Payments by currency
        st.markdown("**Payments by Currency**")

        currency_df = pd.DataFrame(
            {
                "Currency": ["EUR", "USD", "CHF"],
                "Count": [18, 8, 2],
                "Volume": [215000, 180000, 61850],
            }
        )

        fig = px.bar(
            currency_df,
            x="Currency",
            y="Volume",
            text="Count",
            title="Volume by Target Currency",
            labels={"Volume": "Volume (GBP)"},
        )
        fig.update_traces(texttemplate="%{text} payments", textposition="outside")

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Top beneficiaries
        st.markdown("**Top Beneficiaries by Volume**")

        top_ben_df = pd.DataFrame(
            {
                "Beneficiary": [
                    "Supplier GmbH",
                    "Tech Solutions SAS",
                    "Global Trade SpA",
                    "Manufacturing BV",
                    "Export Services Ltd",
                ],
                "Volume": [98500, 85200, 72400, 65100, 58900],
            }
        )

        fig = px.bar(
            top_ben_df,
            y="Beneficiary",
            x="Volume",
            orientation="h",
            title="Top 5 Beneficiaries",
            labels={"Volume": "Volume (GBP)"},
        )

        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("FX Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # FX rate trends
        st.markdown("**FX Rate Trends**")

        dates = pd.date_range(start=date_from, end=date_to, freq="D")
        eur_rates = [1.165 + (0.001 * (i % 10)) for i in range(len(dates))]
        usd_rates = [1.285 + (0.002 * (i % 8)) for i in range(len(dates))]

        fx_trend_df = pd.DataFrame(
            {"Date": dates, "GBP/EUR": eur_rates, "GBP/USD": usd_rates}
        )

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=fx_trend_df["Date"],
                y=fx_trend_df["GBP/EUR"],
                name="GBP/EUR",
                mode="lines+markers",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=fx_trend_df["Date"],
                y=fx_trend_df["GBP/USD"],
                name="GBP/USD",
                mode="lines+markers",
            )
        )

        fig.update_layout(
            title="Exchange Rate Trends",
            xaxis_title="Date",
            yaxis_title="Rate",
            hovermode="x unified",
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # FX savings analysis
        st.markdown("**FX Markup Analysis**")

        st.metric("Average Markup", "0.50%", help="Average markup on FX rates")
        st.metric(
            "Total Markup Revenue", "£2,284", "+15.2%", help="Revenue from FX markup"
        )
        st.metric("Best Rate Achieved", "1.1695", "GBP/EUR", help="Best rate in period")
        st.metric(
            "Worst Rate Achieved", "1.1608", "GBP/EUR", help="Worst rate in period"
        )

        st.markdown("---")

        st.info("""
        ** FX Insights**
        
        - Average rate volatility: **0.15%**
        - Most favorable day: **Monday**
        - Recommended time: **09:00-11:00 GMT**
        - Currency pairs: **3 active**
        """)

    st.markdown("---")

    # FX volume by currency pair
    st.markdown("**Volume by Currency Pair**")

    pair_df = pd.DataFrame(
        {
            "Currency Pair": [
                "GBP → EUR",
                "GBP → USD",
                "GBP → CHF",
                "EUR → GBP",
                "USD → GBP",
            ],
            "Volume (GBP)": [215000, 180000, 61850, 0, 0],
            "Count": [18, 8, 2, 0, 0],
            "Avg Rate": [1.1650, 1.2850, 1.2920, 0, 0],
        }
    )

    st.dataframe(
        pair_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Volume (GBP)": st.column_config.NumberColumn("Volume (GBP)", format="£%d"),
            "Avg Rate": st.column_config.NumberColumn("Avg Rate", format="%.4f"),
        },
    )

with tab3:
    st.subheader("Beneficiary Report")

    # Beneficiary performance
    ben_report_df = pd.DataFrame(
        {
            "Beneficiary": [
                "Supplier GmbH",
                "Tech Solutions SAS",
                "Global Trade SpA",
                "Manufacturing BV",
                "Export Services Ltd",
                "European Partners AG",
                "Digital Consulting",
                "Import Co SARL",
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
            "Total Payments": [15, 8, 12, 5, 9, 7, 3, 11],
            "Total Volume": [
                "£98,500",
                "£85,200",
                "£72,400",
                "£65,100",
                "£58,900",
                "£42,300",
                "£34,200",
                "£86,750",
            ],
            "Avg Payment": [
                "£6,567",
                "£10,650",
                "£6,033",
                "£13,020",
                "£6,544",
                "£6,043",
                "£11,400",
                "£7,886",
            ],
            "Success Rate": [
                "100%",
                "100%",
                "92%",
                "100%",
                "89%",
                "100%",
                "100%",
                "100%",
            ],
            "Last Payment": [
                (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=12)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            ],
        }
    )

    st.dataframe(ben_report_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Payments by country
        st.markdown("**Payments by Country**")

        country_df = pd.DataFrame(
            {
                "Country": [
                    "Germany",
                    "France",
                    "Italy",
                    "Netherlands",
                    "Spain",
                    "Belgium",
                ],
                "Count": [22, 19, 12, 5, 9, 3],
            }
        )

        fig = px.pie(
            country_df, values="Count", names="Country", title="Distribution by Country"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Top Performers**")
        st.metric("Most Frequent", "Supplier GmbH", "15 payments")
        st.metric("Highest Volume", "Supplier GmbH", "£98,500")
        st.metric("Largest Single", "Manufacturing BV", "£13,020")

    with col3:
        st.markdown("**Activity Metrics**")
        st.metric("Active Beneficiaries", "8", "100%")
        st.metric("Inactive (>30 days)", "0", "0%")
        st.metric("New This Month", "2", "+25%")

with tab4:
    st.subheader("Export Data")

    st.markdown("Download your payment data in various formats")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Payment History Export**")

        export_format = st.selectbox(
            "Export Format", ["CSV", "Excel (XLSX)", "PDF Report"]
        )

        include_fields = st.multiselect(
            "Include Fields",
            [
                "Payment ID",
                "Beneficiary",
                "Amount",
                "Currency",
                "FX Rate",
                "Status",
                "Created Date",
                "Created By",
                "Approved By",
                "Execution Date",
            ],
            default=["Payment ID", "Beneficiary", "Amount", "Status", "Created Date"],
        )

        if st.button(" Download Payment History", use_container_width=True):
            st.success(" Export file prepared!")
            st.info("In production, this would trigger a download")

    with col2:
        st.markdown("**Report Options**")

        include_charts = st.checkbox("Include Charts", value=True)
        include_summary = st.checkbox("Include Summary Statistics", value=True)
        include_fx = st.checkbox("Include FX Analysis", value=True)
        include_beneficiaries = st.checkbox("Include Beneficiary Report", value=False)

        st.markdown("---")

        if st.button(" Generate Full Report", use_container_width=True):
            with st.spinner("Generating comprehensive report..."):
                import time

                time.sleep(2)
            st.success(" Report generated successfully!")
            st.info("In production, this would generate a PDF report")

    st.markdown("---")

    st.markdown("**Quick Export**")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("CSV - All Data", use_container_width=True):
            st.info("Downloading all_payments.csv...")

    with col2:
        if st.button("Excel - Summary", use_container_width=True):
            st.info("Downloading summary_report.xlsx...")

    with col3:
        if st.button("PDF - Monthly", use_container_width=True):
            st.info("Downloading monthly_report.pdf...")

    with col4:
        if st.button("JSON - API Export", use_container_width=True):
            st.info("Downloading data_export.json...")

    st.markdown("---")

    st.info("""
    ** Export Notes:**
    
    - All exports respect your date range filter
    - Sensitive data (like full IBANs) may be masked
    - Large exports may take a few moments to prepare
    - Exports are logged for audit purposes
    """)

# Sidebar info
with st.sidebar:
    st.info(f"**Logged in as:** {st.session_state.user_name}")
    st.caption(f"Role: {st.session_state.user_role.title()}")

    st.markdown("---")

    st.markdown("** Quick Stats**")
    st.metric("This Month", "£145,230")
    st.metric("Last Month", "£126,450")
    st.metric("YTD", "£456,850")

    st.markdown("---")

    st.markdown("** Report Tips**")
    st.caption("• Use date filters for specific periods")
    st.caption("• Export data for offline analysis")
    st.caption("• Charts show trends and patterns")
    st.caption("• All times in UTC")
