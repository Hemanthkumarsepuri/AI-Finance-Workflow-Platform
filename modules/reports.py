import pandas as pd
import streamlit as st

from utils import (
    amount_to_float
)

def render_reports(
    all_invoices
):

    st.subheader(
        "Reports"
    )

    report_data = []

    # =====================================================
    # PREPARE REPORT DATA
    # =====================================================

    for inv in all_invoices:

        report_data.append({

            "Vendor":
            inv.vendor_name,

            "Invoice":
            inv.invoice_number,

            "Invoice Date":
            inv.invoice_date,

            "Amount":
            amount_to_float(
                inv.total_amount
            ),

            "Currency":
            inv.currency,

            "Status":
            inv.approval_status
        })

    # =====================================================
    # DATAFRAME
    # =====================================================

    if report_data:

        report_df = pd.DataFrame(
            report_data
        )

        st.dataframe(

            report_df,

            use_container_width=True
        )

        # =================================================
        # CSV EXPORT
        # =================================================

        csv = report_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(

            label="Download Reports CSV",

            data=csv,

            file_name="invoice_reports.csv",

            mime="text/csv"
        )

    else:

        st.info(
            "No reports available."
        )