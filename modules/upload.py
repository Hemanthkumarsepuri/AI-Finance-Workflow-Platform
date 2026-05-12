import os
import streamlit as st

from config import (

    AUTO_APPROVAL_LIMIT,

    FINANCE_REVIEW_LIMIT,

    STATUS_APPROVED,

    STATUS_MANAGER_APPROVAL,

    PROCESSED_FOLDER
)

from extractor import (
    extract_invoice_data
)

from email_service import (
    send_review_email
)

from utils import (
    amount_to_float,
    clean_amount
)

# =========================================================
# VALIDATION
# =========================================================

def validate_invoice_data(
    vendor_name,
    invoice_number,
    invoice_date,
    total_amount
):

    errors = []

    if not vendor_name.strip():

        errors.append(
            "Vendor Name Missing"
        )

    if not invoice_number.strip():

        errors.append(
            "Invoice Number Missing"
        )

    if not invoice_date.strip():

        errors.append(
            "Invoice Date Missing"
        )

    cleaned_amount = clean_amount(
        total_amount
    )

    try:

        amount_value = float(
            cleaned_amount
        )

        if amount_value <= 0:

            errors.append(
                "Invalid Invoice Amount"
            )

    except:

        errors.append(
            "Amount Extraction Failed"
        )

    return errors

# =========================================================
# MAIN PAGE
# =========================================================

def render_upload_page(

    session,

    Invoice,

    add_audit_log
):

    st.subheader(
        "Upload Invoice"
    )

    uploaded_file = st.file_uploader(

        "Upload Invoice",

        type=[
            "pdf",
            "png",
            "jpg",
            "jpeg"
        ],

        key=st.session_state.uploader_key
    )

    if uploaded_file:

        # =================================================
        # SAVE FILE
        # =================================================

        if not os.path.exists(
            PROCESSED_FOLDER
        ):

            os.makedirs(
                PROCESSED_FOLDER
            )

        save_path = os.path.join(

            PROCESSED_FOLDER,

            uploaded_file.name
        )

        with open(
            save_path,
            "wb"
        ) as f:

            f.write(
                uploaded_file.getbuffer()
            )

        # =================================================
        # EXTRACTION
        # =================================================

        result = extract_invoice_data(
            save_path
        )

        # =================================================
        # FORM
        # =================================================

        vendor_name = st.text_input(

            "Vendor",

            result.get(
                "Vendor Name",
                ""
            )
        )

        invoice_number = st.text_input(

            "Invoice Number",

            result.get(
                "Invoice Number",
                ""
            )
        )

        invoice_date = st.text_input(

            "Invoice Date",

            result.get(
                "Invoice Date",
                ""
            )
        )

        total_amount = st.text_input(

            "Total Amount",

            result.get(
                "Total Amount",
                ""
            )
        )

        currency = st.text_input(

            "Currency",

            result.get(
                "Currency",
                "INR"
            )
        )

        # =================================================
        # VALIDATION
        # =================================================

        validation_errors = validate_invoice_data(

            vendor_name,

            invoice_number,

            invoice_date,

            total_amount
        )

        if validation_errors:

            st.error(
                "Extraction Validation Failed"
            )

            for err in validation_errors:

                st.warning(err)

        # =================================================
        # SAVE
        # =================================================

        if st.button(
            "Save Invoice"
        ):

            # --------------------------------------------
            # BLOCK INVALID SAVE
            # --------------------------------------------

            if validation_errors:

                st.error(
                    "Cannot save invalid invoice."
                )

                st.stop()

            cleaned_amount = clean_amount(
                total_amount
            )

            amount_value = amount_to_float(
                cleaned_amount
            )

            # --------------------------------------------
            # WORKFLOW
            # --------------------------------------------

            if amount_value <= AUTO_APPROVAL_LIMIT:

                approval_status = (
                    STATUS_APPROVED
                )

            elif amount_value <= FINANCE_REVIEW_LIMIT:

                approval_status = (
                    STATUS_MANAGER_APPROVAL
                )

            else:

                approval_status = (
                    STATUS_MANAGER_APPROVAL
                )

            # --------------------------------------------
            # DUPLICATE CHECK
            # --------------------------------------------

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

                add_audit_log(

                    invoice_number,

                    f"Invoice Saved ({approval_status})"
                )

                # ----------------------------------------
                # EMAIL
                # ----------------------------------------

                if approval_status == STATUS_MANAGER_APPROVAL:

                    send_review_email(

                        vendor_name,

                        invoice_number,

                        cleaned_amount,

                        approval_status
                    )

                st.success(
                    f"Invoice Saved ({approval_status})"
                )

                st.session_state.uploader_key += 1

                st.rerun()