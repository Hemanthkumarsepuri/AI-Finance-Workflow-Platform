import os
import streamlit as st

from config import (
    AUTO_APPROVAL_LIMIT,
    FINANCE_REVIEW_LIMIT,
    STATUS_APPROVED,
    STATUS_MANAGER_APPROVAL,
    PROCESSED_FOLDER
)

from extractor import extract_invoice_data

from email_service import (
    send_review_email
)

def render_upload_page(
    session,
    Invoice,
    add_audit_log
):

    st.subheader("Upload Invoice")

    uploaded_file = st.file_uploader(
        "Upload Invoice",
        type=["pdf", "png", "jpg", "jpeg"],
        key=st.session_state.uploader_key
    )

    if uploaded_file:

        # ---------------- CREATE FOLDER ----------------

        if not os.path.exists(PROCESSED_FOLDER):

            os.makedirs(PROCESSED_FOLDER)

        save_path = os.path.join(
            PROCESSED_FOLDER,
            uploaded_file.name
        )

        # ---------------- SAVE FILE ----------------

        with open(save_path, "wb") as f:

            f.write(
                uploaded_file.getbuffer()
            )

        # ---------------- EXTRACT DATA ----------------

        result = extract_invoice_data(
            save_path
        )

        vendor_name = st.text_input(
            "Vendor",
            result.get("Vendor Name", "")
        )

        invoice_number = st.text_input(
            "Invoice Number",
            result.get("Invoice Number", "")
        )

        invoice_date = st.text_input(
            "Invoice Date",
            result.get("Invoice Date", "")
        )

        total_amount = st.text_input(
            "Total Amount",
            result.get("Total Amount", "")
        )

        currency = st.text_input(
            "Currency",
            result.get("Currency", "")
        )

        # ---------------- SAVE BUTTON ----------------

        if st.button("Save Invoice"):

            cleaned_amount = (
                str(total_amount)
                .replace(",", "")
                .replace("₹", "")
                .strip()
            )

            # ---------------- AMOUNT PARSE ----------------

            try:

                amount_value = float(
                    cleaned_amount
                )

            except:

                amount_value = 0

            # ---------------- WORKFLOW ----------------

            if amount_value <= AUTO_APPROVAL_LIMIT:

                approval_status = STATUS_APPROVED

            elif amount_value <= FINANCE_REVIEW_LIMIT:

                approval_status = STATUS_MANAGER_APPROVAL

            else:

                approval_status = STATUS_MANAGER_APPROVAL

            # ---------------- DUPLICATE CHECK ----------------

            existing_invoice = (
                session.query(Invoice)
                .filter_by(
                    invoice_number=invoice_number,
                    vendor_name=vendor_name
                )
                .first()
            )

            if existing_invoice:

                st.warning(
                    "Duplicate Invoice Detected"
                )

            else:

                # ---------------- SAVE DATABASE ----------------

                invoice = Invoice(

                    vendor_name=vendor_name,

                    invoice_number=invoice_number,

                    invoice_date=invoice_date,

                    total_amount=cleaned_amount,

                    currency=currency,

                    approval_status=approval_status,

                    file_path=save_path
                )

                session.add(invoice)

                session.commit()

                # ---------------- AUDIT ----------------

                add_audit_log(

                    invoice_number,

                    f"Invoice Saved ({approval_status})"
                )

                # ---------------- EMAIL ----------------

                if approval_status == STATUS_MANAGER_APPROVAL:

                    send_review_email(

                        vendor_name,

                        invoice_number,

                        cleaned_amount,

                        approval_status
                    )

                # ---------------- SUCCESS ----------------

                st.success(
                    f"Invoice Saved ({approval_status})"
                )

                # ---------------- RESET ----------------

                st.session_state.uploader_key += 1

                st.rerun()