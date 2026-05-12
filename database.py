from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Database Engine
engine = create_engine(
    "sqlite:///invoices.db"
)

Base = declarative_base()

# ---------------- INVOICE TABLE ----------------

class Invoice(Base):

    __tablename__ = "invoices"

    id = Column(
        Integer,
        primary_key=True
    )

    vendor_name = Column(String)

    invoice_number = Column(String)

    invoice_date = Column(String)

    total_amount = Column(String)

    currency = Column(String)

    approval_status = Column(String)

    file_path = Column(String)

# ---------------- AUDIT LOG TABLE ----------------

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

# ---------------- CREATE TABLES ----------------

Base.metadata.create_all(engine)

# ---------------- SESSION ----------------

Session = sessionmaker(bind=engine)