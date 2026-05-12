import pandas as pd
import streamlit as st
import plotly.express as px

from datetime import datetime

from config import (

    STATUS_MANAGER_APPROVAL,

    STATUS_FINANCE_REVIEW,

    SLA_HEALTHY_DAYS,

    SLA_WARNING_DAYS
)

from utils import (
    safe_date
)

def render_sla(
    session,
    Invoice
):

    st.subheader(
        "SLA Monitoring"
    )

    sla_data = []

    today = datetime.today()

    # =====================================================
    # FETCH PENDING INVOICES
    # =====================================================

    pending_invoices = session.query(
        Invoice
    ).filter(
        Invoice.approval_status.in_([

            STATUS_MANAGER_APPROVAL,

            STATUS_FINANCE_REVIEW
        ])
    ).all()

    # =====================================================
    # PROCESS SLA
    # =====================================================

    for inv in pending_invoices:

        try:

            invoice_date = safe_date(
                inv.invoice_date
            )

            # ---------------- INVALID DATE ----------------

            if pd.isnull(invoice_date):

                pending_days = 0

            else:

                pending_days = (
                    today - invoice_date
                ).days

            # ---------------- SLA STATUS ----------------

            if pending_days <= SLA_HEALTHY_DAYS:

                sla_status = "Healthy"

            elif pending_days <= SLA_WARNING_DAYS:

                sla_status = "Warning"

            else:

                sla_status = "Critical"

            sla_data.append({

                "Invoice":
                inv.invoice_number,

                "Vendor":
                inv.vendor_name,

                "Current Status":
                inv.approval_status,

                "Pending Days":
                pending_days,

                "SLA Status":
                sla_status
            })

        except:

            sla_data.append({

                "Invoice":
                inv.invoice_number,

                "Vendor":
                inv.vendor_name,

                "Current Status":
                inv.approval_status,

                "Pending Days":
                "Error",

                "SLA Status":
                "Date Issue"
            })

    # =====================================================
    # DISPLAY TABLE
    # =====================================================

    if sla_data:

        sla_df = pd.DataFrame(
            sla_data
        )

        st.dataframe(

            sla_df,

            use_container_width=True
        )

        # =================================================
        # SUMMARY CHART
        # =================================================

        summary = (

            sla_df.groupby(
                "SLA Status"
            )

            .size()

            .reset_index(
                name="Count"
            )
        )

        fig = px.bar(

            summary,

            x="SLA Status",

            y="Count",

            title="SLA Status Distribution"
        )

        st.plotly_chart(

            fig,

            use_container_width=True
        )

    else:

        st.info(
            "No invoices currently pending for SLA monitoring."
        )