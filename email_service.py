import smtplib
import os

from email.mime.text import MIMEText
from dotenv import load_dotenv

# =========================================================
# LOAD ENV VARIABLES
# =========================================================

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# =========================================================
# GENERIC EMAIL SENDER
# =========================================================

def send_email(

    recipient_email,
    subject,
    body
):

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient_email

    try:

        with smtplib.SMTP(
            "smtp.gmail.com",
            587
        ) as server:

            server.starttls()

            server.login(
                EMAIL_ADDRESS,
                EMAIL_PASSWORD
            )

            server.send_message(msg)

        return True

    except Exception as e:

        print(
            f"Email Error: {e}"
        )

        return False

# =========================================================
# REVIEW REQUEST EMAIL
# =========================================================

def send_review_email(

    recipient_email,
    vendor_name,
    invoice_number,
    amount,
    approval_status
):

    subject = (
        f"Invoice Requires Review - {invoice_number}"
    )

    body = f"""
Invoice requires workflow review.

Vendor: {vendor_name}

Invoice Number: {invoice_number}

Amount: ₹ {amount}

Workflow Status: {approval_status}

Please review the invoice in the AI Finance Workflow Platform.
"""

    return send_email(

        recipient_email,
        subject,
        body
    )

# =========================================================
# APPROVED EMAIL
# =========================================================

def send_approved_email(

    recipient_email,
    vendor_name,
    invoice_number,
    amount
):

    subject = (
        f"Invoice Approved - {invoice_number}"
    )

    body = f"""
Invoice has been APPROVED successfully.

Vendor: {vendor_name}

Invoice Number: {invoice_number}

Amount: ₹ {amount}

Final Status: Approved

AI Finance Workflow Platform
"""

    return send_email(

        recipient_email,
        subject,
        body
    )

# =========================================================
# REJECTED EMAIL
# =========================================================

def send_rejected_email(

    recipient_email,
    vendor_name,
    invoice_number,
    amount,
    rejection_reason=None
):

    subject = (
        f"Invoice Rejected - {invoice_number}"
    )

    body = f"""
Invoice has been REJECTED.

Vendor: {vendor_name}

Invoice Number: {invoice_number}

Amount: ₹ {amount}

Final Status: Rejected
"""

    if rejection_reason:

        body += f"""

Rejection Reason:
{rejection_reason}
"""

    body += """

Please review and re-submit if required.

AI Finance Workflow Platform
"""

    return send_email(

        recipient_email,
        subject,
        body
    )

# =========================================================
# FORWARD APPROVAL EMAIL
# =========================================================

def send_forward_email(

    recipient_email,
    vendor_name,
    invoice_number,
    amount,
    forwarded_by,
    comments=None
):

    subject = (
        f"Invoice Approval Forwarded - {invoice_number}"
    )

    body = f"""
Invoice approval has been forwarded.

Vendor: {vendor_name}

Invoice Number: {invoice_number}

Amount: ₹ {amount}

Forwarded By:
{forwarded_by}
"""

    if comments:

        body += f"""

Workflow Comments:
{comments}
"""

    body += """

Please review the invoice in the AI Finance Workflow Platform.
"""

    return send_email(

        recipient_email,
        subject,
        body
    )

# =========================================================
# SLA ESCALATION EMAIL
# =========================================================

def send_sla_alert_email(

    recipient_email,
    invoice_number,
    vendor_name,
    sla_status
):

    subject = (
        f"SLA Alert - {invoice_number}"
    )

    body = f"""
Invoice workflow SLA alert detected.

Invoice Number: {invoice_number}

Vendor: {vendor_name}

SLA Status: {sla_status}

Immediate workflow action required.

AI Finance Workflow Platform
"""

    return send_email(

        recipient_email,
        subject,
        body
    )

# =========================================================
# AI SUMMARY EMAIL
# =========================================================

def send_ai_summary_email(

    recipient_email,
    invoice_number,
    vendor_name,
    amount,
    ai_recommendation,
    confidence_score,
    duplicate_risk,
    anomaly_score
):

    subject = (
        f"AI Invoice Intelligence Summary - {invoice_number}"
    )

    body = f"""
AI Invoice Intelligence Summary

Vendor: {vendor_name}

Invoice Number: {invoice_number}

Amount: ₹ {amount}

AI Recommendation:
{ai_recommendation}

Extraction Confidence:
{confidence_score}

Duplicate Risk Score:
{duplicate_risk}

Anomaly Risk Score:
{anomaly_score}

Generated By:
AI Finance Workflow Platform
"""

    return send_email(

        recipient_email,
        subject,
        body
    )