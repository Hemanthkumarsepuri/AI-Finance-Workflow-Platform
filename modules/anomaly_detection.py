import pandas as pd
import streamlit as st

from config import (

    ANOMALY_THRESHOLD_MULTIPLIER,

    MIN_VENDOR_HISTORY
)

from utils import (
    amount_to_float
)

def render_anomaly_detection(
    all_invoices
):

    st.subheader(
        "AI Anomaly Detection"
    )

    anomalies = []

    vendor_amounts = {}

    # =====================================================
    # GROUP VENDOR AMOUNTS
    # =====================================================

    for inv in all_invoices:

        amount = amount_to_float(
            inv.total_amount
        )

        vendor = inv.vendor_name

        if vendor not in vendor_amounts:

            vendor_amounts[vendor] = []

        vendor_amounts[vendor].append(
            amount
        )

    # =====================================================
    # DETECT ANOMALIES
    # =====================================================

    for vendor, amounts in vendor_amounts.items():

        if len(amounts) >= MIN_VENDOR_HISTORY:

            average = (
                sum(amounts)
                / len(amounts)
            )

            for amount in amounts:

                if (
                    amount >
                    average *
                    ANOMALY_THRESHOLD_MULTIPLIER
                ):

                    anomalies.append({

                        "Vendor": vendor,

                        "Anomaly":
                        "Abnormally High Invoice",

                        "Severity": "High",

                        "Average Spend":
                        round(average, 2),

                        "Detected Amount":
                        amount
                    })

                    break

    # =====================================================
    # DISPLAY
    # =====================================================

    if anomalies:

        st.dataframe(

            pd.DataFrame(anomalies),

            use_container_width=True
        )

    else:

        st.success(
            "No anomalies detected."
        )