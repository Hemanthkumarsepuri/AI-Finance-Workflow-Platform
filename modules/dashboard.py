import pandas as pd
import streamlit as st
import plotly.express as px

from config import (

    STATUS_APPROVED,

    STATUS_REJECTED,

    STATUS_MANAGER_APPROVAL,

    STATUS_FINANCE_REVIEW
)

from utils import (
    amount_to_float
)

def render_dashboard(

    all_invoices,

    total_invoices,

    pending_approvals,

    approved_invoices,

    rejected_invoices
):

    st.subheader(
        "Executive Dashboard"
    )

    # =====================================================
    # KPI CARDS
    # =====================================================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Invoices",
        total_invoices
    )

    col2.metric(
        "Pending",
        pending_approvals
    )

    col3.metric(
        "Approved",
        approved_invoices
    )

    col4.metric(
        "Rejected",
        rejected_invoices
    )

    st.markdown("---")

    # =====================================================
    # DATAFRAME
    # =====================================================

    dashboard_data = []

    for inv in all_invoices:

        dashboard_data.append({

            "Vendor":
            inv.vendor_name,

            "Invoice":
            inv.invoice_number,

            "Amount":
            amount_to_float(
                inv.total_amount
            ),

            "Status":
            inv.approval_status,

            "Date":
            inv.invoice_date
        })

    df = pd.DataFrame(
        dashboard_data
    )

    if not df.empty:

        # =================================================
        # TOP VENDORS
        # =================================================

        st.subheader(
            "Top Vendor Spend"
        )

        vendor_summary = (

            df.groupby("Vendor")["Amount"]

            .sum()

            .reset_index()

            .sort_values(
                by="Amount",
                ascending=False
            )

            .head(10)
        )

        vendor_fig = px.bar(

            vendor_summary,

            x="Vendor",

            y="Amount",

            title="Top Vendor Spend"
        )

        st.plotly_chart(

            vendor_fig,

            use_container_width=True
        )

        # =================================================
        # STATUS DISTRIBUTION
        # =================================================

        st.subheader(
            "Workflow Status Distribution"
        )

        status_summary = (

            df.groupby("Status")

            .size()

            .reset_index(
                name="Count"
            )
        )

        status_fig = px.pie(

            status_summary,

            names="Status",

            values="Count",

            title="Approval Workflow Status"
        )

        st.plotly_chart(

            status_fig,

            use_container_width=True
        )

        # =================================================
        # APPROVAL BOTTLENECKS
        # =================================================

        st.subheader(
            "Approval Bottlenecks"
        )

        pending_df = df[

            df["Status"].isin([

                STATUS_MANAGER_APPROVAL,

                STATUS_FINANCE_REVIEW
            ])
        ]

        st.dataframe(

            pending_df,

            use_container_width=True
        )

        # =================================================
        # REJECTION ANALYSIS
        # =================================================

        st.subheader(
            "Rejected Invoice Analysis"
        )

        rejected_df = df[
            df["Status"]
            == STATUS_REJECTED
        ]

        if not rejected_df.empty:

            rejection_summary = (

                rejected_df.groupby("Vendor")

                .size()

                .reset_index(
                    name="Rejected Count"
                )
            )

            rejection_fig = px.bar(

                rejection_summary,

                x="Vendor",

                y="Rejected Count",

                title="Vendor Rejection Trend"
            )

            st.plotly_chart(

                rejection_fig,

                use_container_width=True
            )

        else:

            st.success(
                "No rejected invoices detected."
            )

        # =================================================
        # TOTAL SPEND
        # =================================================

        total_spend = (
            df["Amount"].sum()
        )

        st.metric(
            "Total Spend Processed",
            f"₹ {round(total_spend, 2)}"
        )

    else:

        st.info(
            "No dashboard data available."
        )