import pandas as pd
import streamlit as st
import plotly.express as px

from utils import (
    amount_to_float
)

from modules.filters import (
    apply_invoice_filters
)

def render_analytics(
    all_invoices
):

    st.subheader(
        "Analytics"
    )

    analytics_data = []

    # =====================================================
    # PREPARE DATA
    # =====================================================

    for inv in all_invoices:

        analytics_data.append({

            "Vendor":
            inv.vendor_name,

            "Amount":
            amount_to_float(
                inv.total_amount
            ),

            "Status":
            inv.approval_status,

            "Invoice":
            inv.invoice_number
        })

    # =====================================================
    # DATAFRAME
    # =====================================================

    df = pd.DataFrame(
        analytics_data
    )

    if not df.empty:

        # =================================================
        # APPLY FILTERS
        # =================================================

        filtered_df = apply_invoice_filters(
            df
        )

        # =================================================
        # VENDOR SPEND
        # =================================================

        vendor_summary = (

            filtered_df.groupby("Vendor")["Amount"]

            .sum()

            .reset_index()
        )

        fig = px.bar(

            vendor_summary,

            x="Vendor",

            y="Amount",

            title="Vendor Spend Analytics"
        )

        st.plotly_chart(

            fig,

            use_container_width=True
        )

        # =================================================
        # STATUS DISTRIBUTION
        # =================================================

        status_summary = (

            filtered_df.groupby("Status")

            .size()

            .reset_index(
                name="Count"
            )
        )

        status_fig = px.pie(

            status_summary,

            names="Status",

            values="Count",

            title="Invoice Status Distribution"
        )

        st.plotly_chart(

            status_fig,

            use_container_width=True
        )

        # =================================================
        # DISPLAY TABLE
        # =================================================

        st.dataframe(

            filtered_df,

            use_container_width=True
        )

    else:

        st.info(
            "No analytics data available."
        )