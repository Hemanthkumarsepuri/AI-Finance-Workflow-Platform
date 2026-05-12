import pandas as pd
import streamlit as st

from modules.filters import (
    apply_invoice_filters
)

def render_audit_trail(
    session,
    AuditLog
):

    st.subheader(
        "Audit Trail"
    )

    logs = session.query(
        AuditLog
    ).all()

    # =====================================================
    # PREPARE DATA
    # =====================================================

    if logs:

        audit_data = []

        for log in logs:

            audit_data.append({

                "Timestamp":
                log.timestamp,

                "User":
                log.username,

                "Role":
                log.role,

                "Invoice":
                log.invoice_number,

                "Action":
                log.action,

                "Status":
                log.action
            })

        audit_df = pd.DataFrame(
            audit_data
        )

        # =================================================
        # APPLY FILTERS
        # =================================================

        filtered_df = apply_invoice_filters(
            audit_df
        )

        # =================================================
        # DISPLAY
        # =================================================

        st.dataframe(

            filtered_df,

            use_container_width=True
        )

        # =================================================
        # EXPORT
        # =================================================

        csv = filtered_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(

            label="Download Audit CSV",

            data=csv,

            file_name="audit_trail.csv",

            mime="text/csv"
        )

    else:

        st.info(
            "No audit logs available."
        )