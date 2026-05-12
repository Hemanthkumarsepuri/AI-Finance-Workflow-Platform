import pandas as pd
import streamlit as st

# =========================================================
# GLOBAL FILTER ENGINE
# =========================================================

def apply_invoice_filters(
    dataframe
):

    st.subheader(
        "Search & Filters"
    )

    # =====================================================
    # SEARCH
    # =====================================================

    search_text = st.text_input(
        "Search Invoice / Vendor"
    )

    # =====================================================
    # STATUS FILTER
    # =====================================================

    status_options = ["All"]

    if "Status" in dataframe.columns:

        unique_status = sorted(

            dataframe["Status"]
            .dropna()
            .unique()
        )

        status_options.extend(
            unique_status
        )

    selected_status = st.selectbox(

        "Filter By Status",

        status_options
    )

    # =====================================================
    # FILTER LOGIC
    # =====================================================

    filtered_df = dataframe.copy()

    # ---------------- SEARCH ----------------

    if search_text:

        search_text = (
            search_text.lower()
        )

        filtered_df = filtered_df[

            filtered_df.apply(

                lambda row:

                search_text in str(row)
                .lower(),

                axis=1
            )
        ]

    # ---------------- STATUS ----------------

    if (

        selected_status != "All"

        and "Status" in filtered_df.columns
    ):

        filtered_df = filtered_df[

            filtered_df["Status"]
            == selected_status
        ]

    # =====================================================
    # RESULT
    # =====================================================

    st.markdown(
        f"### Filtered Results: {len(filtered_df)}"
    )

    return filtered_df