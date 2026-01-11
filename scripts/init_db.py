"""
Initialize database schema.
"""

from app.database.connection import engine, Base
from app.database.models import (
    User,
    Company,
    Beneficiary,
    BeneficiaryBankAccount,
    FXQuote,
    Payment,
    PaymentApproval,
    AuditLog,
)


def init_database():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully!")


if __name__ == "__main__":
    init_database()
