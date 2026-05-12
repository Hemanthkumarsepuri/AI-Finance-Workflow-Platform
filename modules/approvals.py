import os
import pandas as pd
import streamlit as st

from config import (

    AUTO_APPROVAL_LIMIT,

    FINANCE_REVIEW_LIMIT,

    STATUS_APPROVED,

    STATUS_REJECTED,

    STATUS_MANAGER_APPROVAL,

    STATUS_FINANCE_REVIEW
)

from modules.filters import (
    apply_invoice_filters
)

from utils import (
    amount_to_float
)

from email_service import (

    send_review_email,

    send_approved_email,

    send_rejected_email
)

def render_approval_queue(

    session,

    Invoice,

    AuditLog,

    add_audit_log
):

    st.subheader(
        "Approval Queue"
    )

    # =====================================================
    # FETCH PENDING
    # =====================================================

    if st.session_state.role == "Manager":

        pending_invoices = session.query(
            Invoice
        ).filter(
            Invoice.approval_status
            == STATUS_MANAGER_APPROVAL
        ).all()

    elif st.session_state.role == "Finance Admin":

        pending_invoices = session.query(
            Invoice
        ).filter(
            Invoice.approval_status
            == STATUS_FINANCE_REVIEW
        ).all()

    else:

        pending_invoices = []

    # =====================================================
    # FILTER TABLE
    # =====================================================

    filter_data = []

    for inv in pending_invoices:

        filter_data.append({

            "Vendor":
            inv.vendor_name,

            "Invoice":
            inv.invoice_number,

            "Amount":
            amount_to_float(
                inv.total_amount
            ),

            "Status":
            inv.approval_status
        })

    if filter_data:

        filter_df = pd.DataFrame(
            filter_data
        )

        filtered_df = apply_invoice_filters(
            filter_df
        )

        allowed_invoices = filtered_df[
            "Invoice"
        ].tolist()

    else:

        allowed_invoices = []

    # =====================================================
    # DISPLAY
    # =====================================================

    if pending_invoices:

        for inv in pending_invoices:

            if (
                inv.invoice_number
                not in allowed_invoices
            ):

                continue

            st.markdown("---")

            st.write(
                f"### {inv.vendor_name}"
            )

            st.write(
                f"Invoice: {inv.invoice_number}"
            )

            st.write(
                f"Amount: ₹ {inv.total_amount}"
            )

            st.write(
                f"Status: {inv.approval_status}"
            )

            # =================================================
            # DOCUMENT VIEWER
            # =================================================

            if os.path.exists(inv.file_path):

                extension = (
                    inv.file_path
                    .split(".")[-1]
                    .lower()
                )

                if extension == "pdf":

                    with open(
                        inv.file_path,
                        "rb"
                    ) as pdf_file:

                        st.download_button(

                            "Download Invoice PDF",

                            data=pdf_file,

                            file_name=os.path.basename(
                                inv.file_path
                            ),

                            mime="application/pdf"
                        )

                else:

                    st.image(

                        inv.file_path,

                        use_container_width=True
                    )

            # =================================================
            # ACTIVITY HISTORY
            # =================================================

            with st.expander(
                "Invoice Activity History"
            ):

                logs = session.query(
                    AuditLog
                ).filter_by(
                    invoice_number=inv.invoice_number
                ).all()

                if logs:

                    activity = []

                    for log in logs:

                        activity.append({

                            "Timestamp":
                            log.timestamp,

                            "User":
                            log.username,

                            "Role":
                            log.role,

                            "Action":
                            log.action
                        })

                    st.dataframe(

                        pd.DataFrame(activity),

                        use_container_width=True
                    )

            # =================================================
            # APPROVAL LOGIC
            # =================================================

            amount_value = amount_to_float(
                inv.total_amount
            )

            approval_allowed = True

            if amount_value > AUTO_APPROVAL_LIMIT:

                approval_allowed = st.checkbox(

                    "Confirm Approval",

                    key=f"confirm_{inv.id}"
                )

            col1, col2 = st.columns(2)

            # ---------------- MANAGER ----------------

            if (

                st.session_state.role == "Manager"

                and inv.approval_status
                == STATUS_MANAGER_APPROVAL
            ):

                if approval_allowed:

                    if col1.button(

                        "Approve / Continue Workflow",

                        key=f"mgr_{inv.id}"
                    ):

                        if amount_value <= FINANCE_REVIEW_LIMIT:

                            inv.approval_status = (
                                STATUS_APPROVED
                            )

                            session.commit()

                            add_audit_log(

                                inv.invoice_number,

                                "Manager Final Approved"
                            )

                            send_approved_email(

                                inv.vendor_name,

                                inv.invoice_number,

                                inv.total_amount
                            )

                            st.success(
                                "Invoice Approved"
                            )

                        else:

                            inv.approval_status = (
                                STATUS_FINANCE_REVIEW
                            )

                            session.commit()

                            add_audit_log(

                                inv.invoice_number,

                                "Manager Approved → Finance Review"
                            )

                            send_review_email(

                                inv.vendor_name,

                                inv.invoice_number,

                                inv.total_amount,

                                STATUS_FINANCE_REVIEW
                            )

                            st.success(
                                "Sent To Finance Review"
                            )

                        st.rerun()

            # ---------------- FINANCE ----------------

            elif (

                st.session_state.role
                == "Finance Admin"

                and inv.approval_status
                == STATUS_FINANCE_REVIEW
            ):

                if approval_allowed:

                    if col1.button(

                        "Final Approve",

                        key=f"fin_{inv.id}"
                    ):

                        inv.approval_status = (
                            STATUS_APPROVED
                        )

                        session.commit()

                        add_audit_log(

                            inv.invoice_number,

                            "Finance Final Approved"
                        )

                        send_approved_email(

                            inv.vendor_name,

                            inv.invoice_number,

                            inv.total_amount
                        )

                        st.success(
                            "Invoice Approved"
                        )

                        st.rerun()

            # ---------------- REJECT ----------------

            if col2.button(

                "Reject Invoice",

                key=f"reject_{inv.id}"
            ):

                inv.approval_status = (
                    STATUS_REJECTED
                )

                session.commit()

                add_audit_log(

                    inv.invoice_number,

                    "Invoice Rejected"
                )

                send_rejected_email(

                    inv.vendor_name,

                    inv.invoice_number,

                    inv.total_amount
                )

                st.warning(
                    "Invoice Rejected"
                )

                st.rerun()

    else:

        st.info(
            "No Pending Approvals"
        )