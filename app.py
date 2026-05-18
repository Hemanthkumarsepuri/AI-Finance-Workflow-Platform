import streamlit as st

from datetime import datetime

# =========================================================
# UI
# =========================================================

from modules.ui import (

    setup_ui,

    render_header
)

# =========================================================
# AUTH
# =========================================================

from modules.auth import (

    initialize_session,

    login_screen,

    sidebar_logout,

    seed_demo_users
)

# =========================================================
# DASHBOARD
# =========================================================

from modules.dashboard import (
    render_dashboard
)

# =========================================================
# UPLOAD
# =========================================================

from modules.upload import (
    render_upload_page
)

# =========================================================
# APPROVALS
# =========================================================

from modules.approvals import (
    render_approval_queue
)

# =========================================================
# ANALYTICS
# =========================================================

from modules.analytics import (
    render_analytics
)

# =========================================================
# SLA
# =========================================================

from modules.sla import (
    render_sla
)

# =========================================================
# VENDOR INTELLIGENCE
# =========================================================

from modules.vendor_intelligence import (
    render_vendor_intelligence
)

# =========================================================
# ANOMALY DETECTION
# =========================================================

from modules.anomaly_detection import (
    render_anomaly_detection
)

# =========================================================
# REPORTS
# =========================================================

from modules.reports import (
    render_reports
)

# =========================================================
# AUDIT
# =========================================================

from modules.audit import (
    render_audit_trail
)

# =========================================================
# DATABASE
# =========================================================

from database import (

    Session,

    Invoice,

    AuditLog,

    User,

    ApprovalHistory
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(

    page_title=
    "AI Finance Workflow Platform",

    page_icon="💰",

    layout="wide"
)

# =========================================================
# UI SETUP
# =========================================================

setup_ui()

render_header()

# =========================================================
# SESSION INITIALIZATION
# =========================================================

initialize_session()

# =========================================================
# DATABASE SESSION
# =========================================================

session = Session()

# =========================================================
# DEMO USER SEEDING
# =========================================================

seed_demo_users(

    session,

    User
)

# =========================================================
# LOGIN
# =========================================================

if not st.session_state.logged_in:

    login_screen(

        session,

        User
    )

    st.stop()

# =========================================================
# SIDEBAR
# =========================================================

sidebar_logout()

# =========================================================
# ENTERPRISE SIDEBAR INFO
# =========================================================

st.sidebar.markdown("---")

st.sidebar.caption(

    f"""
Employee ID:
{st.session_state.employee_id}
    """
)

st.sidebar.caption(

    f"""
Department:
{st.session_state.department}
    """
)

st.sidebar.caption(

    f"""
Project:
{st.session_state.project_name}
    """
)

# =========================================================
# ROLE-BASED PAGES
# =========================================================

ROLE_PAGES = {

    "employee": [

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

    "Delivery Manager": [

        "Dashboard",

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
# PAGE NAVIGATION
# =========================================================

user_role = (
    st.session_state.role
)

allowed_pages = ROLE_PAGES.get(

    user_role,

    ["Dashboard"]
)

page = st.sidebar.radio(

    "Navigation",

    allowed_pages
)

# =========================================================
# FETCH INVOICES
# =========================================================

all_invoices = session.query(
    Invoice
).all()

# =========================================================
# ENTERPRISE AUDIT LOGGER
# =========================================================

def add_audit_log(

    invoice_number,

    action
):

    log = AuditLog(

        timestamp=datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        username=(
            st.session_state.employee_name
        ),

        role=(
            st.session_state.role
        ),

        invoice_number=invoice_number,

        action=action,

        details=f"""
Action performed by:
{st.session_state.employee_name}

Role:
{st.session_state.role}

Project:
{st.session_state.project_name}
        """
    )

    session.add(log)

    session.commit()

# =========================================================
# KPI CALCULATIONS
# =========================================================

total_invoices = len(
    all_invoices
)

pending_approvals = len([

    inv for inv in all_invoices

    if inv.approval_status in [

        "Manager Approval",

        "Finance Review",

        "Forwarded"
    ]
])

approved_invoices = len([

    inv for inv in all_invoices

    if inv.approval_status
    == "Approved"
])

rejected_invoices = len([

    inv for inv in all_invoices

    if inv.approval_status
    == "Rejected"
])

high_risk_invoices = len([

    inv for inv in all_invoices

    if (

        inv.duplicate_risk_score
        and
        inv.duplicate_risk_score >= 0.80
    )
])

sla_breaches = len([

    inv for inv in all_invoices

    if inv.sla_status
    == "Breached"
])

# =========================================================
# ENTERPRISE HEADER METRICS
# =========================================================

st.markdown("---")

metric_col1, metric_col2, metric_col3, metric_col4, metric_col5, metric_col6 = (

    st.columns(6)
)

with metric_col1:

    st.metric(

        "Total Invoices",

        total_invoices
    )

with metric_col2:

    st.metric(

        "Pending",

        pending_approvals
    )

with metric_col3:

    st.metric(

        "Approved",

        approved_invoices
    )

with metric_col4:

    st.metric(

        "Rejected",

        rejected_invoices
    )

with metric_col5:

    st.metric(

        "High Risk",

        high_risk_invoices
    )

with metric_col6:

    st.metric(

        "SLA Breaches",

        sla_breaches
    )

st.markdown("---")

# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    render_dashboard(

        all_invoices,

        total_invoices,

        pending_approvals,

        approved_invoices,

        rejected_invoices
    )

# =========================================================
# UPLOAD
# =========================================================

elif page == "Upload Invoice":

    render_upload_page(

        session,

        Invoice,

        User,

        ApprovalHistory,

        add_audit_log
    )

# =========================================================
# APPROVAL QUEUE
# =========================================================

elif page == "Approval Queue":

    render_approval_queue(

        session,

        Invoice,

        AuditLog,

        ApprovalHistory,

        User,

        add_audit_log
    )

# =========================================================
# ANALYTICS
# =========================================================

elif page == "Analytics":

    render_analytics(
        all_invoices
    )

# =========================================================
# SLA MONITORING
# =========================================================

elif page == "SLA Monitoring":

    render_sla(

        session,

        Invoice
    )

# =========================================================
# VENDOR INTELLIGENCE
# =========================================================

elif page == "Vendor Intelligence":

    render_vendor_intelligence(
        all_invoices
    )

# =========================================================
# AI ANOMALY DETECTION
# =========================================================

elif page == "AI Anomaly Detection":

    render_anomaly_detection(
        all_invoices
    )

# =========================================================
# REPORTS
# =========================================================

elif page == "Reports":

    render_reports(
        all_invoices
    )

# =========================================================
# AUDIT TRAIL
# =========================================================

elif page == "Audit Trail":

    render_audit_trail(

        session,

        AuditLog
    )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(

    """
AI Finance Workflow Platform
Enterprise Workflow Governance Engine
    """
)