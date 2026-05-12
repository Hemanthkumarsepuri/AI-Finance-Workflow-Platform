import smtplib
import os

from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Generic Email Sender
def send_email(
    subject,
    body
):

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS

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

        print(e)

        return False

# Review Request Email
def send_review_email(
    vendor_name,
    invoice_number,
    amount,
    approval_status
):

    subject = (
        f"Invoice Requires Review - {invoice_number}"
    )

    body = f"""
Invoice requires approval review.

Vendor: {vendor_name}

Invoice Number: {invoice_number}

Amount: ₹ {amount}

Current Status: {approval_status}
"""

    return send_email(
        subject,
        body
    )

# Approved Email
def send_approved_email(
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
"""

    return send_email(
        subject,
        body
    )

# Rejected Email
def send_rejected_email(
    vendor_name,
    invoice_number,
    amount
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

    return send_email(
        subject,
        body
    )