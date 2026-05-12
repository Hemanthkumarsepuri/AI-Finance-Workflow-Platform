import os
import json
import re
import pdfplumber

from dotenv import load_dotenv

# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()

# =========================================================
# OPENAI SETUP
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
# PDF TEXT EXTRACTION
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

                page_text = page.extract_text()

                if page_text:

                    text += page_text + "\n"

    except:

        return ""

    return text

# =========================================================
# REGEX FALLBACK
# =========================================================

def basic_regex_extraction(
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

        r"(?:Total|Amount|Payable)[^\d]*([\d,]+\.\d{2})",

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
# AI EXTRACTION
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
                    """
                    Extract invoice details and return ONLY valid JSON.

                    Required JSON format:

                    {
                      "Vendor Name": "",
                      "Invoice Number": "",
                      "Invoice Date": "",
                      "Total Amount": "",
                      "Currency": ""
                    }
                    """
                },

                {
                    "role": "user",

                    "content": text[:6000]
                }
            ],

            temperature=0
        )

        content = (
            response
            .choices[0]
            .message
            .content
        )

        return json.loads(content)

    except:

        return None

# =========================================================
# MAIN EXTRACTION
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
    # TRY AI EXTRACTION
    # =====================================================

    ai_data = ai_extract_invoice_data(
        text
    )

    if ai_data:

        return ai_data

    # =====================================================
    # FALLBACK EXTRACTION
    # =====================================================

    return basic_regex_extraction(
        text
    )