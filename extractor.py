import os
import re
import json
import pdfplumber
import easyocr
import numpy as np

from PIL import Image
from pdf2image import convert_from_path
from dotenv import load_dotenv

from utils import (
    format_invoice_date
)

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

except Exception as e:

    print(
        f"OpenAI Initialization Error: {str(e)}"
    )

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
            f"PDF Extraction Error: {str(e)}"
        )

    return text

# =========================================================
# SCANNED PDF OCR FALLBACK
# =========================================================

def extract_text_from_scanned_pdf(
    pdf_path
):

    text = ""

    try:

        pages = convert_from_path(
            pdf_path
        )

        for page in pages:

            image_np = np.array(page)

            results = reader.readtext(
                image_np,
                detail=0
            )

            text += "\n".join(
                results
            )

    except Exception as e:

        print(
            f"Scanned PDF OCR Error: {str(e)}"
        )

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

        return "\n".join(results)

    except Exception as e:

        print(
            f"Image OCR Error: {str(e)}"
        )

        return ""

# =========================================================
# GST VALIDATION
# =========================================================

def validate_gst_information(
    text
):

    gst_pattern = r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d[Z]{1}[A-Z\d]{1}\b"

    gst_match = re.search(
        gst_pattern,
        text
    )

    if gst_match:

        return (

            True,

            gst_match.group(0),

            "GST compliant invoice detected."
        )

    return (

        False,

        "",

        """
GST number not found.
Possible reimbursement receipt or
non-tax invoice.
Finance review recommended.
        """
    )

# =========================================================
# ENTERPRISE REGEX EXTRACTION
# =========================================================

def enterprise_regex_extraction(
    text
):

    invoice_data = {

        "Vendor Name": "",

        "Invoice Number": "",

        "Invoice Date": "",

        "Total Amount": "",

        "Currency": "INR",

        "GST Status": "",

        "GST Number": "",

        "GST Message": "",

        "Extraction Confidence": 0.0
    }

    # =====================================================
    # VENDOR DETECTION
    # =====================================================

    lines = [

        line.strip()

        for line in text.split("\n")

        if line.strip()
    ]

    for line in lines[:10]:

        if len(line) > 3:

            if not any(

                keyword in line.lower()

                for keyword in [

                    "invoice",
                    "bill",
                    "gst",
                    "tax",
                    "date"
                ]
            ):

                invoice_data[
                    "Vendor Name"
                ] = line[:80]

                break

    # =====================================================
    # INVOICE NUMBER
    # =====================================================

    invoice_patterns = [

        r"Invoice\s*(?:No|Number|#)?[:\s]*([A-Za-z0-9\-\/]+)",

        r"Bill\s*(?:No|Number|#)?[:\s]*([A-Za-z0-9\-\/]+)",

        r"Receipt\s*(?:No|Number|#)?[:\s]*([A-Za-z0-9\-\/]+)",

        r"Ref\s*(?:No|Number|#)?[:\s]*([A-Za-z0-9\-\/]+)"
    ]

    for pattern in invoice_patterns:

        match = re.search(

            pattern,

            text,

            re.IGNORECASE
        )

        if match:

            invoice_data[
                "Invoice Number"
            ] = match.group(1)

            break

    # =====================================================
    # DATE EXTRACTION
    # =====================================================

    date_patterns = [

        r"\d{2}[/-]\d{2}[/-]\d{4}",

        r"\d{4}[/-]\d{2}[/-]\d{2}"
    ]

    for pattern in date_patterns:

        match = re.search(
            pattern,
            text
        )

        if match:

            formatted_date = (
                format_invoice_date(
                    match.group(0)
                )
            )

            invoice_data[
                "Invoice Date"
            ] = formatted_date

            break

    # =====================================================
    # AMOUNT EXTRACTION
    # =====================================================

    amount_patterns = [

        r"(?:Grand Total|Total Amount|Amount Payable|Net Amount|Total)[^\d]*([\d,]+\.\d{2})",

        r"₹\s*([\d,]+\.\d{2})"
    ]

    for pattern in amount_patterns:

        match = re.search(

            pattern,

            text,

            re.IGNORECASE
        )

        if match:

            invoice_data[
                "Total Amount"
            ] = match.group(1)

            break

    # =====================================================
    # GST VALIDATION
    # =====================================================

    gst_found, gst_number, gst_message = (

        validate_gst_information(
            text
        )
    )

    invoice_data[
        "GST Status"
    ] = (

        "GST Available"
        if gst_found
        else "GST Missing"
    )

    invoice_data[
        "GST Number"
    ] = gst_number

    invoice_data[
        "GST Message"
    ] = gst_message

    # =====================================================
    # CONFIDENCE SCORING
    # =====================================================

    confidence = 0

    if invoice_data["Vendor Name"]:

        confidence += 0.25

    if invoice_data["Invoice Number"]:

        confidence += 0.25

    if invoice_data["Invoice Date"]:

        confidence += 0.25

    if invoice_data["Total Amount"]:

        confidence += 0.25

    invoice_data[
        "Extraction Confidence"
    ] = round(
        confidence,
        2
    )

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

        response = (

            client.chat.completions.create(

                model="gpt-3.5-turbo",

                messages=[

                    {

                        "role": "system",

                        "content":
                        """
You are an enterprise invoice extraction engine.

Extract:

- Vendor Name
- Invoice Number
- Invoice Date
- Total Amount
- Currency
- GST Number
- GST Availability

Return ONLY valid JSON.

JSON FORMAT:

{
  "Vendor Name": "",
  "Invoice Number": "",
  "Invoice Date": "",
  "Total Amount": "",
  "Currency": "INR",
  "GST Number": "",
  "GST Status": ""
}
                        """
                    },

                    {

                        "role": "user",

                        "content":
                        text[:12000]
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

        content = content.replace(
            "```json",
            ""
        )

        content = content.replace(
            "```",
            ""
        )

        parsed = json.loads(
            content
        )

        parsed[
            "Invoice Date"
        ] = format_invoice_date(

            parsed.get(
                "Invoice Date",
                ""
            )
        )

        parsed[
            "Extraction Confidence"
        ] = 0.95

        if not parsed.get(
            "GST Status"
        ):

            parsed[
                "GST Status"
            ] = "Unknown"

        return parsed

    except Exception as e:

        print(
            f"AI Extraction Error: {str(e)}"
        )

        return None

# =========================================================
# MAIN EXTRACTION PIPELINE
# =========================================================

def extract_invoice_data(
    file_path
):

    print(
        "Starting Enterprise Extraction"
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

        # OCR fallback for scanned PDF

        if not extracted_text.strip():

            extracted_text = (

                extract_text_from_scanned_pdf(
                    file_path
                )
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
    # NO TEXT FALLBACK
    # =====================================================

    if not extracted_text:

        return {

            "Vendor Name": "",

            "Invoice Number": "",

            "Invoice Date": "",

            "Total Amount": "",

            "Currency": "INR",

            "GST Status": "Unknown",

            "GST Number": "",

            "GST Message":
            "Text extraction failed.",

            "Extraction Confidence": 0.0
        }

    # =====================================================
    # AI EXTRACTION
    # =====================================================

    ai_result = ai_extract_invoice_data(
        extracted_text
    )

    if ai_result:

        return ai_result

    # =====================================================
    # ENTERPRISE REGEX FALLBACK
    # =====================================================

    return enterprise_regex_extraction(
        extracted_text
    )