import os
import re
import json
import pdfplumber
import easyocr
import numpy as np

from PIL import Image
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

except Exception as e:

    print(
        "OpenAI Initialization Error:"
    )

    print(str(e))

# =========================================================
# OCR INITIALIZATION
# =========================================================

reader = easyocr.Reader(
    ['en'],
    gpu=False
)

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

                extracted = (
                    page.extract_text()
                )

                if extracted:

                    text += (
                        extracted
                        + "\n"
                    )

    except Exception as e:

        print(
            "PDF Extraction Error:"
        )

        print(str(e))

    return text

# =========================================================
# IMAGE OCR EXTRACTION
# =========================================================

def extract_text_from_image(
    image_path
):

    try:

        image = Image.open(
            image_path
        )

        image_np = np.array(
            image
        )

        results = reader.readtext(
            image_np,
            detail=0
        )

        extracted_text = "\n".join(
            results
        )

        return extracted_text

    except Exception as e:

        print(
            "Image OCR Error:"
        )

        print(str(e))

        return ""

# =========================================================
# BASIC FALLBACK EXTRACTION
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

                        JSON format:

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

        # -------------------------------------------------
        # CLEAN JSON BLOCKS
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

        return {

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
        "Starting Extraction"
    )

    extension = (
        file_path
        .split(".")[-1]
        .lower()
    )

    extracted_text = ""

    # =====================================================
    # PDF EXTRACTION
    # =====================================================

    if extension == "pdf":

        extracted_text = (
            extract_text_from_pdf(
                file_path
            )
        )

        # OCR fallback for scanned PDFs

        if not extracted_text.strip():

            print(
                "PDF text empty"
            )

    # =====================================================
    # IMAGE OCR
    # =====================================================

    elif extension in [

        "png",
        "jpg",
        "jpeg"
    ]:

        extracted_text = (
            extract_text_from_image(
                file_path
            )
        )

    # =====================================================
    # VALIDATION
    # =====================================================

    if not extracted_text:

        print(
            "No text extracted"
        )

        return {

            "Vendor Name": "",

            "Invoice Number": "",

            "Invoice Date": "",

            "Total Amount": "",

            "Currency": "INR"
        }

    print(
        "TEXT EXTRACTION SUCCESS"
    )

    # =====================================================
    # AI EXTRACTION
    # =====================================================

    ai_result = ai_extract_invoice_data(
        extracted_text
    )

    if ai_result:

        print(
            "AI EXTRACTION SUCCESS"
        )

        return ai_result

    # =====================================================
    # FALLBACK REGEX
    # =====================================================

    print(
        "Using Regex Fallback"
    )

    return basic_regex_extraction(
        extracted_text
    )