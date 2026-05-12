# =========================================================
# AMOUNT CLEANING
# =========================================================

def clean_amount(amount):

    try:

        cleaned = (
            str(amount)
            .replace(",", "")
            .replace("₹", "")
            .strip()
        )

        return cleaned

    except:

        return "0"

# =========================================================
# AMOUNT TO FLOAT
# =========================================================

def amount_to_float(amount):

    try:

        cleaned = clean_amount(amount)

        return float(cleaned)

    except:

        return 0

# =========================================================
# SAFE DATE PARSING
# =========================================================

import pandas as pd

def safe_date(date_value):

    try:

        parsed = pd.to_datetime(
            date_value,
            errors="coerce"
        )

        return parsed

    except:

        return None