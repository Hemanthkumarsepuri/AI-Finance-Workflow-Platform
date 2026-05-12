# =========================================================
# APPLICATION
# =========================================================

APP_TITLE = "AI Vendor Bill & Expense Manager"

APP_LAYOUT = "wide"

# =========================================================
# ROLES
# =========================================================

ROLE_EMPLOYEE = "Employee"

ROLE_MANAGER = "Manager"

ROLE_FINANCE = "Finance Admin"

# =========================================================
# APPROVAL WORKFLOW
# =========================================================

AUTO_APPROVAL_LIMIT = 5000

FINANCE_REVIEW_LIMIT = 20000

STATUS_APPROVED = "Approved"

STATUS_REJECTED = "Rejected"

STATUS_MANAGER_APPROVAL = "Manager Approval"

STATUS_FINANCE_REVIEW = "Finance Review"

# =========================================================
# SLA
# =========================================================

SLA_HEALTHY_DAYS = 3

SLA_WARNING_DAYS = 7

# =========================================================
# FILE STORAGE
# =========================================================

PROCESSED_FOLDER = "processed"

FAILED_FOLDER = "failed"

# =========================================================
# UI COLORS
# =========================================================

PRIMARY_COLOR = "#2563EB"

SECONDARY_COLOR = "#7DD3FC"

BACKGROUND_COLOR = "#0B1220"

SIDEBAR_COLOR = "#111827"

# =========================================================
# AI DETECTION
# =========================================================

ANOMALY_THRESHOLD_MULTIPLIER = 4

MIN_VENDOR_HISTORY = 3

HIGH_SPEND_RISK_LIMIT = 50000

HIGH_REJECTION_LIMIT = 2