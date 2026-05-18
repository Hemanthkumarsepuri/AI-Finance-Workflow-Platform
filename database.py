from sqlalchemy import create_engine

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Boolean
from sqlalchemy import Text

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# =========================================================
# DATABASE ENGINE
# =========================================================

engine = create_engine(
    "sqlite:///invoices.db"
)

Base = declarative_base()

# =========================================================
# USER TABLE
# =========================================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True
    )

    employee_id = Column(String)

    employee_name = Column(String)

    email = Column(String)

    role = Column(String)

    department = Column(String)

    project_name = Column(String)

    manager_employee_id = Column(String)

    delivery_manager_employee_id = Column(String)

# =========================================================
# INVOICE TABLE
# =========================================================

class Invoice(Base):

    __tablename__ = "invoices"

    id = Column(
        Integer,
        primary_key=True
    )

    employee_id = Column(String)

    employee_name = Column(String)

    project_name = Column(String)

    vendor_name = Column(String)

    normalized_vendor_name = Column(String)

    invoice_number = Column(String)

    invoice_date = Column(String)

    total_amount = Column(Float)

    currency = Column(String)

    bill_category = Column(String)

    file_path = Column(String)

    extracted_text = Column(Text)

    extraction_confidence = Column(Float)

    duplicate_risk_score = Column(Float)

    anomaly_risk_score = Column(Float)

    ai_recommendation = Column(String)

    ai_reasoning = Column(Text)

    approval_status = Column(String)

    workflow_stage = Column(String)

    current_approver = Column(String)

    forwarded_to = Column(String)

    rejection_reason = Column(Text)

    parent_invoice_id = Column(Integer)

    version_number = Column(Integer)

    resubmitted_flag = Column(Boolean)

    sla_status = Column(String)

    sla_due_date = Column(String)

# =========================================================
# APPROVAL HISTORY
# =========================================================

class ApprovalHistory(Base):

    __tablename__ = "approval_history"

    id = Column(
        Integer,
        primary_key=True
    )

    invoice_id = Column(Integer)

    action = Column(String)

    from_user = Column(String)

    to_user = Column(String)

    comments = Column(Text)

# =========================================================
# AUDIT LOG TABLE
# =========================================================

class AuditLog(Base):

    __tablename__ = "audit_logs"

    id = Column(
        Integer,
        primary_key=True
    )

    timestamp = Column(String)

    username = Column(String)

    role = Column(String)

    invoice_number = Column(String)

    action = Column(String)

    details = Column(Text)

# =========================================================
# CREATE TABLES
# =========================================================

Base.metadata.create_all(engine)

# =========================================================
# SESSION
# =========================================================

Session = sessionmaker(
    bind=engine
)