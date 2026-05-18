import os
import uuid
import streamlit as st
import pandas as pd

from datetime import datetime, timedelta

from config import (

    AUTO_APPROVAL_LIMIT,

    FINANCE_REVIEW_LIMIT,

    STATUS_APPROVED,

    STATUS_MANAGER_APPROVAL,

    STATUS_FINANCE_REVIEW,

    PROCESSED_FOLDER
)

from extractor import (
    extract_invoice_data
)

from email_service import (

    send_review_email,

    send_ai_summary_email
)

from utils import (

    amount_to_float,

    clean_amount
)

# =========================================================
# VENDOR NORMALIZATION
# =========================================================

def normalize_vendor_name(
    vendor_name
):

    if not vendor_name:

        return ""

    vendor_name = vendor_name.lower()

    remove_words = [

        "services",
        "service",
        "limited",
        "ltd",
        "private",
        "pvt",
        "solutions",
        "technologies",
        "technology",
        "telecom",
        "communications",
        "communication",
        "india",
        "infocomm",
        "corporation"
    ]

    for word in remove_words:

        vendor_name = vendor_name.replace(
            word,
            ""
        )

    vendor_name = (
        vendor_name
        .replace("-", " ")
        .replace("_", " ")
        .strip()
    )

    vendor_name = " ".join(
        vendor_name.split()
    )

    return vendor_name

# =========================================================
# BILL CATEGORY ENGINE
# =========================================================

def detect_bill_category(
    vendor_name,
    extracted_text
):

    text = f"""
{vendor_name}
{extracted_text}
""".lower()

    category_mapping = {

        "Travel": [

            "uber",
            "ola",
            "flight",
            "airlines",
            "irctc",
            "railway",
            "travel",
            "cab"
        ],

        "Food": [

            "swiggy",
            "zomato",
            "restaurant",
            "food",
            "cafe",
            "hotel"
        ],

        "Broadband": [

            "jio",
            "airtel",
            "broadband",
            "fiber",
            "wifi",
            "internet"
        ],

        "Accommodation": [

            "oyo",
            "marriott",
            "hotel",
            "stay"
        ],

        "Office Expense": [

            "printer",
            "stationery",
            "office",
            "supplies"
        ]
    }

    for category, keywords in category_mapping.items():

        for keyword in keywords:

            if keyword in text:

                return category

    return "Miscellaneous"

# =========================================================
# AI RECOMMENDATION ENGINE
# =========================================================

def generate_ai_recommendation(

    amount,
    duplicate_risk,
    category
):

    if duplicate_risk > 0.7:

        return (

            "Review",

            """
Possible duplicate invoice detected.
Finance review recommended.
            """
        )

    if amount > FINANCE_REVIEW_LIMIT:

        return (

            "Finance Review",

            """
High invoice amount detected.
Finance governance review recommended.
            """
        )

    if category == "Travel" and amount > 10000:

        return (

            "Review",

            """
High-value travel invoice detected.
Manager review recommended.
            """
        )

    return (

        "Approve",

        """
Invoice pattern appears normal.
Low anomaly risk detected.
        """
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
# DUPLICATE DETECTION ENGINE
# =========================================================

def calculate_duplicate_risk(

    session,
    Invoice,
    normalized_vendor_name,
    invoice_number,
    amount
):

    existing_invoices = session.query(
        Invoice
    ).all()

    for inv in existing_invoices:

        existing_vendor = normalize_vendor_name(
            inv.vendor_name
        )

        existing_invoice_number = (
            inv.invoice_number or ""
        ).strip().lower()

        current_invoice_number = (
            invoice_number or ""
        ).strip().lower()

        try:

            existing_amount = float(
                inv.total_amount
            )

        except:

            existing_amount = 0

        if (

            existing_vendor
            == normalized_vendor_name

            and

            existing_invoice_number
            == current_invoice_number
        ):

            return 0.95

        if (

            existing_vendor
            == normalized_vendor_name

            and

            abs(existing_amount - amount)
            < 5
        ):

            return 0.75

    return 0.10

# =========================================================
# SLA INITIALIZATION
# =========================================================

def initialize_sla_status():

    return (

        "On Time",

        str(
            datetime.now()
            + timedelta(days=2)
        )
    )

# =========================================================
# APPROVER ROUTING ENGINE
# =========================================================

def determine_workflow_and_approver(

    session,
    User,
    employee_id,
    amount,
    bill_category
):

    employee = session.query(
        User
    ).filter_by(
        employee_id=employee_id
    ).first()

    if not employee:

        return (

            STATUS_MANAGER_APPROVAL,

            "Manager Review",

            "Finance Admin"
        )

    manager_id = (
        employee.manager_employee_id
    )

    delivery_manager_id = (
        employee.delivery_manager_employee_id
    )

    manager = session.query(
        User
    ).filter_by(
        employee_id=manager_id
    ).first()

    delivery_manager = session.query(
        User
    ).filter_by(
        employee_id=delivery_manager_id
    ).first()

    # =====================================================
    # CATEGORY BASED GOVERNANCE
    # =====================================================

    if bill_category == "Broadband":

        workflow_stage = (
            "Manager Review"
        )

        approval_status = (
            STATUS_MANAGER_APPROVAL
        )

        approver = (

            manager.employee_name
            if manager
            else "Finance Admin"
        )

    elif amount > FINANCE_REVIEW_LIMIT:

        workflow_stage = (
            "Delivery Manager Review"
        )

        approval_status = (
            STATUS_FINANCE_REVIEW
        )

        approver = (

            delivery_manager.employee_name
            if delivery_manager
            else "Finance Admin"
        )

    elif amount > AUTO_APPROVAL_LIMIT:

        workflow_stage = (
            "Manager Review"
        )

        approval_status = (
            STATUS_MANAGER_APPROVAL
        )

        approver = (

            manager.employee_name
            if manager
            else "Finance Admin"
        )

    else:

        workflow_stage = (
            "Auto Approved"
        )

        approval_status = (
            STATUS_APPROVED
        )

        approver = "System"

    return (

        approval_status,

        workflow_stage,

        approver
    )

# =========================================================
# MAIN PAGE
# =========================================================

def render_upload_page(

    session,

    Invoice,

    User,

    ApprovalHistory,

    add_audit_log
):

    st.subheader(
        "Enterprise Invoice Upload"
    )

    # =====================================================
    # EMPLOYEE SELECTION
    # =====================================================

    employees = session.query(
        User
    ).filter_by(
        role="employee"
    ).all()

    employee_options = {

        f"{emp.employee_name} ({emp.employee_id})":

        emp.employee_id

        for emp in employees
    }

    selected_employee = st.selectbox(

        "Select Employee",

        list(employee_options.keys())
    )

    employee_id = employee_options[
        selected_employee
    ]

    employee = session.query(
        User
    ).filter_by(
        employee_id=employee_id
    ).first()

    # =====================================================
    # FILE UPLOAD
    # =====================================================

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

        unique_filename = f"""
{uuid.uuid4()}_{uploaded_file.name}
"""

        save_path = os.path.join(

            PROCESSED_FOLDER,

            unique_filename
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

        extracted_text = str(result)

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
        # NORMALIZATION
        # =================================================

        normalized_vendor_name = (
            normalize_vendor_name(
                vendor_name
            )
        )

        # =================================================
        # CATEGORY DETECTION
        # =================================================

        bill_category = detect_bill_category(

            vendor_name,

            extracted_text
        )

        st.info(
            f"Detected Bill Category: {bill_category}"
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

            # =================================================
            # DUPLICATE INTELLIGENCE
            # =================================================

            duplicate_risk_score = (
                calculate_duplicate_risk(

                    session,

                    Invoice,

                    normalized_vendor_name,

                    invoice_number,

                    amount_value
                )
            )

            if duplicate_risk_score >= 0.90:

                st.error(
                    """
High duplicate probability detected.
Invoice blocked for governance review.
                    """
                )

                st.stop()

            # =================================================
            # AI RECOMMENDATION
            # =================================================

            ai_recommendation, ai_reasoning = (

                generate_ai_recommendation(

                    amount_value,

                    duplicate_risk_score,

                    bill_category
                )
            )

            # =================================================
            # WORKFLOW ROUTING
            # =================================================

            approval_status, workflow_stage, current_approver = (

                determine_workflow_and_approver(

                    session,

                    User,

                    employee_id,

                    amount_value,

                    bill_category
                )
            )

            # =================================================
            # SLA INITIALIZATION
            # =================================================

            sla_status, sla_due_date = (

                initialize_sla_status()
            )

            # =================================================
            # REUPLOAD DETECTION
            # =================================================

            previous_rejected_invoice = (

                session.query(Invoice)

                .filter(

                    Invoice.invoice_number
                    == invoice_number,

                    Invoice.approval_status
                    == "Rejected"
                )

                .first()
            )

            parent_invoice_id = None
            version_number = 1
            resubmitted_flag = False

            if previous_rejected_invoice:

                parent_invoice_id = (
                    previous_rejected_invoice.id
                )

                version_number = (
                    previous_rejected_invoice.version_number
                    + 1
                )

                resubmitted_flag = True

            # =================================================
            # CREATE INVOICE
            # =================================================

            invoice = Invoice(

                employee_id=employee.employee_id,

                employee_name=employee.employee_name,

                project_name=employee.project_name,

                vendor_name=vendor_name,

                normalized_vendor_name=normalized_vendor_name,

                invoice_number=invoice_number,

                invoice_date=invoice_date,

                total_amount=amount_value,

                currency=currency,

                bill_category=bill_category,

                file_path=save_path,

                extracted_text=extracted_text,

                extraction_confidence=0.95,

                duplicate_risk_score=duplicate_risk_score,

                anomaly_risk_score=0.10,

                ai_recommendation=ai_recommendation,

                ai_reasoning=ai_reasoning,

                approval_status=approval_status,

                workflow_stage=workflow_stage,

                current_approver=current_approver,

                forwarded_to=None,

                rejection_reason=None,

                parent_invoice_id=parent_invoice_id,

                version_number=version_number,

                resubmitted_flag=resubmitted_flag,

                sla_status=sla_status,

                sla_due_date=sla_due_date
            )

            session.add(invoice)

            session.commit()

            # =================================================
            # APPROVAL HISTORY
            # =================================================

            history = ApprovalHistory(

                invoice_id=invoice.id,

                action="Invoice Uploaded",

                from_user=employee.employee_name,

                to_user=current_approver,

                comments="""
Invoice uploaded into enterprise workflow engine.
                """
            )

            session.add(history)

            session.commit()

            # =================================================
            # AUDIT LOG
            # =================================================

            add_audit_log(

                invoice_number,

                f"""
Invoice Saved
({approval_status})
                """
            )

            # =================================================
            # EMAIL NOTIFICATION
            # =================================================

            if approval_status != STATUS_APPROVED:

                send_review_email(

                    recipient_email="finance@company.com",

                    vendor_name=vendor_name,

                    invoice_number=invoice_number,

                    amount=amount_value,

                    approval_status=approval_status
                )

            # =================================================
            # AI SUMMARY EMAIL
            # =================================================

            send_ai_summary_email(

                recipient_email="finance@company.com",

                invoice_number=invoice_number,

                vendor_name=vendor_name,

                amount=amount_value,

                ai_recommendation=ai_recommendation,

                confidence_score=0.95,

                duplicate_risk=duplicate_risk_score,

                anomaly_score=0.10
            )

            # =================================================
            # SUCCESS MESSAGE
            # =================================================

            st.success(
                f"""
Invoice successfully onboarded into
enterprise workflow orchestration.
                """
            )

            st.info(
                f"""
Current Approver:
{current_approver}

Workflow Stage:
{workflow_stage}

AI Recommendation:
{ai_recommendation}
                """
            )

            st.session_state.uploader_key += 1

            st.rerun()