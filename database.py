# Enhanced Enterprise Database Model — AI Finance Workflow Platform

```python
from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import Boolean
from sqlalchemy import Float
from sqlalchemy import Text

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

from datetime import datetime

# =========================================================
# DATABASE ENGINE
# =========================================================

engine = create_engine(
    "sqlite:///invoices.db",
    echo=False
)

Base = declarative_base()

# =========================================================
# USERS TABLE
# =========================================================
# Stores:
# - Employees
# - Managers
# - Delivery Managers
# - Finance Users
# - Admin Users
#
# This supports enterprise hierarchy-based approvals.
# =========================================================

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    employee_id = Column(String, unique=True)

    employee_name = Column(String)

    email = Column(String, unique=True)

    role = Column(String)
    # Roles:
    # employee
    # manager
    # delivery_manager
    # finance
    # admin

    department = Column(String)

    project_name = Column(String)

    manager_employee_id = Column(String)

    delivery_manager_employee_id = Column(String)

    is_active = Column(Boolean, default=True)

    created_at = Column(String, default=lambda: str(datetime.now()))

# =========================================================
# INVOICE TABLE
# =========================================================
# Core invoice workflow table.
#
# Enhanced with:
# - Workflow tracking
# - Re-upload handling
# - Versioning
# - SLA tracking
# - Approval routing
# - AI governance
# =========================================================

class Invoice(Base):

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)

    # -----------------------------------------------------
    # EMPLOYEE DETAILS
    # -----------------------------------------------------

    employee_id = Column(String)

    employee_name = Column(String)

    project_name = Column(String)

    # -----------------------------------------------------
    # INVOICE DETAILS
    # -----------------------------------------------------

    vendor_name = Column(String)

    invoice_number = Column(String)

    invoice_date = Column(String)

    total_amount = Column(Float)

    currency = Column(String)

    bill_category = Column(String)
    # Example:
    # Food
    # Travel
    # Broadband
    # Miscellaneous
    # Cab
    # Accommodation

    file_path = Column(String)

    extracted_text = Column(Text)

    # -----------------------------------------------------
    # AI GOVERNANCE FIELDS
    # -----------------------------------------------------

    extraction_confidence = Column(Float)

    duplicate_risk_score = Column(Float)

    anomaly_risk_score = Column(Float)

    ai_recommendation = Column(String)
    # Approve / Review / Reject

    ai_reasoning = Column(Text)

    # -----------------------------------------------------
    # APPROVAL WORKFLOW
    # -----------------------------------------------------

    approval_status = Column(String)
    # Pending
    # Approved
    # Rejected
    # Forwarded
    # Finance Review
    # Auto Approved

    workflow_stage = Column(String)
    # Employee Upload
    # Manager Review
    # Delivery Manager Review
    # Finance Review
    # Completed

    current_approver = Column(String)

    forwarded_to = Column(String)

    rejection_reason = Column(Text)

    # -----------------------------------------------------
    # VERSIONING / REUPLOAD TRACKING
    # -----------------------------------------------------

    parent_invoice_id = Column(Integer)

    version_number = Column(Integer, default=1)

    resubmitted_flag = Column(Boolean, default=False)

    # -----------------------------------------------------
    # SLA TRACKING
    # -----------------------------------------------------

    sla_status = Column(String)
    # On Time
    # Near Breach
    # Breached

    sla_due_date = Column(String)

    # -----------------------------------------------------
    # TIMESTAMPS
    # -----------------------------------------------------

    created_at = Column(String, default=lambda: str(datetime.now()))

    updated_at = Column(String, default=lambda: str(datetime.now()))

# =========================================================
# APPROVAL HISTORY TABLE
# =========================================================
# Tracks every workflow action.
#
# Enables:
# - Workflow timeline
# - Audit transparency
# - Forward tracking
# - Escalation history
# =========================================================

class ApprovalHistory(Base):

    __tablename__ = "approval_history"

    id = Column(Integer, primary_key=True)

    invoice_id = Column(Integer)

    action = Column(String)
    # Approved
    # Rejected
    # Forwarded
    # Escalated
    # Clarification Requested

    from_user = Column(String)

    to_user = Column(String)

    comments = Column(Text)

    action_timestamp = Column(
        String,
        default=lambda: str(datetime.now())
    )

# =========================================================
# AUDIT LOG TABLE
# =========================================================
# Enterprise audit governance.
# =========================================================

class AuditLog(Base):

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)

    timestamp = Column(
        String,
        default=lambda: str(datetime.now())
    )

    username = Column(String)

    role = Column(String)

    invoice_number = Column(String)

    action = Column(String)

    details = Column(Text)

# =========================================================
# VENDOR INTELLIGENCE TABLE
# =========================================================
# Tracks vendor-level analytics and governance.
# =========================================================

class VendorProfile(Base):

    __tablename__ = "vendor_profiles"

    id = Column(Integer, primary_key=True)

    vendor_name = Column(String, unique=True)

    total_invoice_count = Column(Integer, default=0)

    total_spend = Column(Float, default=0.0)

    duplicate_invoice_attempts = Column(Integer, default=0)

    rejection_count = Column(Integer, default=0)

    anomaly_count = Column(Integer, default=0)

    vendor_risk_score = Column(Float, default=0.0)

    last_invoice_date = Column(String)

# =========================================================
# NOTIFICATION TRACKING TABLE
# =========================================================
# Supports:
# - Email triggers
# - Escalation tracking
# - SLA reminder tracking
# =========================================================

class NotificationLog(Base):

    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True)

    invoice_id = Column(Integer)

    recipient_email = Column(String)

    notification_type = Column(String)
    # Approval Request
    # SLA Reminder
    # Rejection
    # Escalation
    # Forwarded Approval

    status = Column(String)

    sent_timestamp = Column(
        String,
        default=lambda: str(datetime.now())
    )

# =========================================================
# CREATE TABLES
# =========================================================

Base.metadata.create_all(engine)

# =========================================================
# SESSION
# =========================================================

Session = sessionmaker(bind=engine)
```

# What This Enhancement Solves

## Lead Feedback Coverage

### 1. Mail Triggers

Handled using:

* NotificationLog table
* workflow notification tracking
* escalation support

---

### 2. Employee → Manager → Delivery Manager Mapping

Handled using:

* User table
* hierarchy fields
* project mapping

---

### 3. Forward Approval Workflow

Handled using:

* ApprovalHistory table
* forwarded_to field
* current_approver field

---

### 4. Bill Category & Sorting

Handled using:

* bill_category field

Supports:

* food
* travel
* broadband
* miscellaneous
* cab
* accommodation

---

### 5. Rejected Invoice Re-upload Tracking

Handled using:

* parent_invoice_id
* version_number
* resubmitted_flag
* rejection_reason

---

# Enterprise Improvements Added

## AI Governance

* extraction confidence
* anomaly score
* duplicate risk score
* AI recommendation
* AI reasoning

---

## Workflow Intelligence

* workflow stage tracking
* current approver tracking
* forwarding support
* escalation support

---

## SLA Governance

* SLA due date
* SLA breach tracking
* SLA status

---

## Vendor Intelligence

* vendor risk score
* rejection trends
* anomaly tracking
* duplicate attempt tracking

---

# Recommended Next File

Next enhancement should be:

```text
approvals.py
```

Because now the workflow engine must support:

* hierarchy-based approvals
* forwarding
* escalation
* AI recommenda
