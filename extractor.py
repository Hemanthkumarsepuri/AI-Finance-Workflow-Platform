import pdfplumber
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
import base64
import json
import os

# Load environment variables
load_dotenv()

# OpenAI Client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Function to convert image to base64
def encode_image(image_path):

    with open(image_path, "rb") as image_file:

        return base64.b64encode(
            image_file.read()
        ).decode("utf-8")

# Main Extraction Function
def extract_invoice_data(file_path):

    file_extension = os.path.splitext(
        file_path
    )[1].lower()

    text = ""

    # PDF Processing
    if file_extension == ".pdf":

        with pdfplumber.open(file_path) as pdf:

            for page in pdf.pages:

                extracted = page.extract_text()

                if extracted:

                    text += extracted

        prompt = f"""
        Extract these invoice details:

        - Vendor Name
        - Invoice Number
        - Invoice Date
        - Total Amount
        - Currency

        Return ONLY valid JSON.

        Invoice Text:
        {text}
        """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

    # Image Processing
    else:

        base64_image = encode_image(file_path)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """
                            Extract these invoice details:

                            - Vendor Name
                            - Invoice Number
                            - Invoice Date
                            - Total Amount
                            - Currency

                            Return ONLY valid JSON.
                            """
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        )

    # Clean Response
    result = response.choices[0].message.content

    result = result.replace(
        "```json",
        ""
    )

    result = result.replace(
        "```",
        ""
    )

    result = result.strip()

    parsed_json = json.loads(result)

    return parsed_json