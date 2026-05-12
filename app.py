import streamlit as st

from datetime import datetime

# ---------------- UI ----------------

from modules.ui import (
    setup_ui,
    render_header
)

# ---------------- AUTH ----------------

from modules.auth import (
    initialize_session,
    login_screen,
    sidebar_logout
)

# ---------------- DASHBOARD ----------------

from modules.dashboard import (
    render_dashboard
)

# ---------------- UPLOAD ----------------

from modules.upload import (
    render_upload_page
)

# ---------------- APPROVALS ----------------

from modules.approvals import (
    render_approval_queue
)

# ---------------- ANALYTICS ----------------

from modules.analytics import (
    render_analytics
)

# ---------------- SLA ----------------

from modules.sla import (
    render_sla
)

# ---------------- VENDOR ----------------

from modules.vendor_intelligence import (
    render_vendor_intelligence
)

# ---------------- ANOMALY ----------------

from modules.anomaly_detection import (
    render_anomaly_detection
)

# ---------------- REPORTS ----------------

from modules.reports import (
    render_reports
)

# ---------------- AUDIT ----------------

from modules.audit import (
    render_audit_trail
)

# ---------------- DATABASE ----------------

from database import (
    Session,
    Invoice,
    AuditLog
)

# =========================================================
# UI SETUP
# =========================================================

setup_ui()

render_header()

# =========================================================
# SESSION
# =========================================================

initialize_session()

# =========================================================
# LOGIN
# =========================================================

if not st.session_state.logged_in:

    login_screen()

    st.stop()

# =========================================================
# ROLE PAGES
# =========================================================

ROLE_PAGES = {

    "Employee": [
        "Dashboard",
        "Upload Invoice",
        "Reports"
    ],

    "Manager": [
        "Dashboard",
        "Upload Invoice",
        "Approval Queue",
        "Analytics",
        "Reports",
        "SLA Monitoring",
        "Vendor Intelligence",
        "AI Anomaly Detection"
    ],

    "Finance Admin": [
        "Dashboard",
        "Upload Invoice",
        "Approval Queue",
        "Analytics",
        "Reports",
        "Audit Trail",
        "SLA Monitoring",
        "Vendor Intelligence",
        "AI Anomaly Detection"
    ]
}

# =========================================================
# SIDEBAR
# =========================================================

sidebar_logout()

page = st.sidebar.radio(
    "Navigation",
    ROLE_PAGES[st.session_state.role]
)

# =========================================================
# DATABASE
# =========================================================

session = Session()

all_invoices = session.query(
    Invoice
).all()

# =========================================================
# AUDIT FUNCTION
# =========================================================

def add_audit_log(invoice_number, action):

    log = AuditLog(

        timestamp=datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        username=st.session_state.username,

        role=st.session_state.role,

        invoice_number=invoice_number,

        action=action
    )

    session.add(log)

    session.commit()

# =========================================================
# KPI CALCULATIONS
# =========================================================

total_invoices = len(all_invoices)

pending_approvals = len([
    inv for inv in all_invoices
    if inv.approval_status in [
        "Manager Approval",
        "Finance Review"
    ]
])

approved_invoices = len([
    inv for inv in all_invoices
    if inv.approval_status == "Approved"
])

rejected_invoices = len([
    inv for inv in all_invoices
    if inv.approval_status == "Rejected"
])

# =========================================================
# ROUTING
# =========================================================

# ---------------- DASHBOARD ----------------

if page == "Dashboard":

    render_dashboard(

    all_invoices,

    total_invoices,

    pending_approvals,

    approved_invoices,

    rejected_invoices
)

# ---------------- UPLOAD ----------------

elif page == "Upload Invoice":

    render_upload_page(

        session,

        Invoice,

        add_audit_log
    )

# ---------------- APPROVALS ----------------

elif page == "Approval Queue":

    render_approval_queue(

        session,

        Invoice,

        AuditLog,

        add_audit_log
    )

# ---------------- ANALYTICS ----------------

elif page == "Analytics":

    render_analytics(
        all_invoices
    )

# ---------------- SLA ----------------

elif page == "SLA Monitoring":

    render_sla(
        session,
        Invoice
    )

# ---------------- VENDOR ----------------

elif page == "Vendor Intelligence":

    render_vendor_intelligence(
        all_invoices
    )

# ---------------- ANOMALY ----------------

elif page == "AI Anomaly Detection":

    render_anomaly_detection(
        all_invoices
    )

# ---------------- REPORTS ----------------

elif page == "Reports":

    render_reports(
        all_invoices
    )

# ---------------- AUDIT ----------------

elif page == "Audit Trail":

    render_audit_trail(
        session,
        AuditLog
    )