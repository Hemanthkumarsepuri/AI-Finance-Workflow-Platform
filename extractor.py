import os
import re
import json
import pdfplumber

from dotenv import load_dotenv

# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()

# =========================================================
# OPENAI INITIALIZATION
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

        print(
            "OpenAI Client Initialized"
        )

    else:

        print(
            "OPENAI_API_KEY Missing"
        )

except Exception as e:

    print(
        "OpenAI Initialization Error:"
    )

    print(str(e))

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

                extracted_text = (
                    page.extract_text()
                )

                if extracted_text:

                    text += (
                        extracted_text
                        + "\n"
                    )

    except Exception as e:

        print(
            "PDF Extraction Error:"
        )

        print(str(e))

        return ""

    return text

# =========================================================
# BASIC REGEX FALLBACK
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

    # -----------------------------------------------------
    # VENDOR
    # -----------------------------------------------------

    lines = text.split("\n")

    if lines:

        invoice_data[
            "Vendor Name"
        ] = lines[0][:50]

    # -----------------------------------------------------
    # INVOICE NUMBER
    # -----------------------------------------------------

    invoice_match = re.search(

        r"Invoice[\s#:]*([A-Za-z0-9\-\/]+)",

        text,

        re.IGNORECASE
    )

    if invoice_match:

        invoice_data[
            "Invoice Number"
        ] = invoice_match.group(1)

    # -----------------------------------------------------
    # DATE
    # -----------------------------------------------------

    date_match = re.search(

        r"(\d{2}[/-]\d{2}[/-]\d{4})",

        text
    )

    if date_match:

        invoice_data[
            "Invoice Date"
        ] = date_match.group(1)

    # -----------------------------------------------------
    # AMOUNT
    # -----------------------------------------------------

    amount_match = re.search(

        r"(?:Total|Amount|Payable)[^\d]*([\d,]+\.\d{2})",

        text,

        re.IGNORECASE
    )

    if amount_match:

        invoice_data[
            "Total Amount"
        ] = amount_match.group(1)

    return invoice_data

# =========================================================
# AI EXTRACTION
# =========================================================

def ai_extract_invoice_data(
    text
):

    if not OPENAI_AVAILABLE:

        print(
            "OpenAI Not Available"
        )

        return None

    try:

        print(
            "AI Extraction Started"
        )

        response = (
            client.chat.completions.create(

                model="gpt-3.5-turbo",

                messages=[

                    {
                        "role": "system",

                        "content":
                        """
                        Extract invoice details.

                        Return ONLY valid JSON.

                        JSON Format:

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

                        "content":
                        text[:6000]
                    }
                ],

                temperature=0
            )
        )

        content = (

            response
            .choices[0]
            .message
            .content
            .strip()
        )

        print(
            "RAW AI RESPONSE:"
        )

        print(content)

        # -------------------------------------------------
        # CLEAN MARKDOWN JSON
        # -------------------------------------------------

        content = content.replace(
            "```json",
            ""
        )

        content = content.replace(
            "```",
            ""
        )

        content = content.strip()

        parsed = json.loads(
            content
        )

        extracted_data = {

            "Vendor Name":

            parsed.get(
                "Vendor Name",
                ""
            ),

            "Invoice Number":

            parsed.get(
                "Invoice Number",
                ""
            ),

            "Invoice Date":

            parsed.get(
                "Invoice Date",
                ""
            ),

            "Total Amount":

            parsed.get(
                "Total Amount",
                ""
            ),

            "Currency":

            parsed.get(
                "Currency",
                "INR"
            )
        }

        print(
            "AI EXTRACTION SUCCESS"
        )

        return extracted_data

    except Exception as e:

        print(
            "AI Extraction Error:"
        )

        print(str(e))

        return None

# =========================================================
# MAIN EXTRACTION PIPELINE
# =========================================================

def extract_invoice_data(
    file_path
):

    print(
        "Starting Invoice Extraction"
    )

    text = extract_text_from_pdf(
        file_path
    )

    if not text:

        print(
            "No PDF Text Extracted"
        )

        return {

            "Vendor Name": "",

            "Invoice Number": "",

            "Invoice Date": "",

            "Total Amount": "",

            "Currency": "INR"
        }

    print(
        "PDF Text Extraction Success"
    )

    # =====================================================
    # TRY AI EXTRACTION
    # =====================================================

    ai_result = ai_extract_invoice_data(
        text
    )

    if ai_result:

        print(
            "Using AI Extracted Data"
        )

        return ai_result

    # =====================================================
    # FALLBACK REGEX
    # =====================================================

    print(
        "Using Regex Fallback"
    )

    return basic_regex_extraction(
        text
    )