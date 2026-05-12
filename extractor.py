import os
import re
import pdfplumber
import pandas as pd

from dotenv import load_dotenv

# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()

# =========================================================
# OPTIONAL OPENAI CLIENT
# =========================================================

OPENAI_AVAILABLE = False

try:

    from openai import OpenAI

    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    if api_key:

        client = OpenAI(
            api_key=api_key
        )

        OPENAI_AVAILABLE = True

except:

    OPENAI_AVAILABLE = False

# =========================================================
# EXTRACT TEXT FROM PDF
# =========================================================

def extract_text_from_pdf(
    pdf_path
):

    text = ""

    try:

        with pdfplumber.open(
            pdf_path
        ) as pdf:

            for page in pdf.pages:

                extracted = page.extract_text()

                if extracted:

                    text += extracted + "\n"

    except:

        return ""

    return text

# =========================================================
# BASIC FIELD EXTRACTION
# =========================================================

def extract_basic_fields(
    text
):

    invoice_data = {

        "Vendor Name": "",

        "Invoice Number": "",

        "Invoice Date": "",

        "Total Amount": "",

        "Currency": "INR"
    }

    # ---------------- INVOICE NUMBER ----------------

    invoice_match = re.search(

        r"Invoice[\s#:]*([A-Za-z0-9\-]+)",

        text,

        re.IGNORECASE
    )

    if invoice_match:

        invoice_data[
            "Invoice Number"
        ] = invoice_match.group(1)

    # ---------------- DATE ----------------

    date_match = re.search(

        r"(\d{2}[/-]\d{2}[/-]\d{4})",

        text
    )

    if date_match:

        invoice_data[
            "Invoice Date"
        ] = date_match.group(1)

    # ---------------- AMOUNT ----------------

    amount_match = re.search(

        r"(?:Total|Amount)[^\d]*([\d,]+\.\d{2})",

        text,

        re.IGNORECASE
    )

    if amount_match:

        invoice_data[
            "Total Amount"
        ] = amount_match.group(1)

    # ---------------- VENDOR ----------------

    lines = text.split("\n")

    if lines:

        invoice_data[
            "Vendor Name"
        ] = lines[0][:50]

    return invoice_data

# =========================================================
# AI ENHANCEMENT (OPTIONAL)
# =========================================================

def ai_extract_invoice_data(
    text
):

    if not OPENAI_AVAILABLE:

        return None

    try:

        response = client.chat.completions.create(

            model="gpt-3.5-turbo",

            messages=[

                {
                    "role": "system",

                    "content":
                    "Extract invoice details."
                },

                {
                    "role": "user",

                    "content": text[:4000]
                }
            ]
        )

        return response.choices[0].message.content

    except:

        return None

# =========================================================
# MAIN EXTRACTION FUNCTION
# =========================================================

def extract_invoice_data(
    file_path
):

    text = extract_text_from_pdf(
        file_path
    )

    if not text:

        return {

            "Vendor Name": "",

            "Invoice Number": "",

            "Invoice Date": "",

            "Total Amount": "",

            "Currency": "INR"
        }

    # =====================================================
    # BASIC EXTRACTION
    # =====================================================

    invoice_data = extract_basic_fields(
        text
    )

    # =====================================================
    # OPTIONAL AI ENHANCEMENT
    # =====================================================

    ai_result = ai_extract_invoice_data(
        text
    )

    # Currently optional
    # Future enhancement point

    return invoice_data