import pandas as pd
import streamlit as st

from config import (

    HIGH_SPEND_RISK_LIMIT,

    HIGH_REJECTION_LIMIT,

    STATUS_REJECTED
)

from utils import (
    amount_to_float
)

def render_vendor_intelligence(
    all_invoices
):

    st.subheader(
        "Vendor Intelligence"
    )

    risks = []

    vendor_groups = {}

    # =====================================================
    # GROUP VENDORS
    # =====================================================

    for inv in all_invoices:

        vendor = inv.vendor_name

        if vendor not in vendor_groups:

            vendor_groups[vendor] = []

        vendor_groups[vendor].append(
            inv
        )

    # =====================================================
    # ANALYZE VENDORS
    # =====================================================

    for vendor, invoices in vendor_groups.items():

        rejected_count = 0

        total_spend = 0

        for inv in invoices:

            amount = amount_to_float(
                inv.total_amount
            )

            total_spend += amount

            if (
                inv.approval_status
                == STATUS_REJECTED
            ):

                rejected_count += 1

        # ---------------- HIGH REJECTIONS ----------------

        if rejected_count >= HIGH_REJECTION_LIMIT:

            risks.append({

                "Vendor": vendor,

                "Risk":
                "High Rejection Rate",

                "Severity":
                "Medium",

                "Rejected Count":
                rejected_count,

                "Total Spend":
                round(total_spend, 2)
            })

        # ---------------- HIGH SPEND ----------------

        if total_spend >= HIGH_SPEND_RISK_LIMIT:

            risks.append({

                "Vendor": vendor,

                "Risk":
                "High Spend Vendor",

                "Severity":
                "High",

                "Rejected Count":
                rejected_count,

                "Total Spend":
                round(total_spend, 2)
            })

    # =====================================================
    # DISPLAY
    # =====================================================

    if risks:

        st.dataframe(

            pd.DataFrame(risks),

            use_container_width=True
        )

    else:

        st.success(
            "No vendor risks detected."
        )