"""
SQLAlchemy database models.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Date,
    Numeric,
    Text,
    ForeignKey,
    DECIMAL,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database.connection import Base


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), nullable=False)  # 'admin', 'maker', 'approver'
    company_id = Column(Integer, ForeignKey("companies.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="users")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"


class Company(Base):
    """Company model."""

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    registered_country = Column(String(2), nullable=False)
    industry_sector = Column(String(100))
    fx_volume_band = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="company")
    beneficiaries = relationship("Beneficiary", back_populates="company")

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.company_name}')>"


class Beneficiary(Base):
    """Beneficiary model."""

    __tablename__ = "beneficiaries"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    beneficiary_name = Column(String(255), nullable=False)
    beneficiary_type = Column(String(50))
    country = Column(String(2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="beneficiaries")
    bank_accounts = relationship("BeneficiaryBankAccount", back_populates="beneficiary")

    def __repr__(self):
        return f"<Beneficiary(id={self.id}, name='{self.beneficiary_name}')>"


class BeneficiaryBankAccount(Base):
    """Beneficiary bank account model."""

    __tablename__ = "beneficiary_bank_accounts"

    id = Column(Integer, primary_key=True, index=True)
    beneficiary_id = Column(Integer, ForeignKey("beneficiaries.id"), nullable=False)
    account_holder_name = Column(String(255), nullable=False)
    iban = Column(String(34))
    swift_bic = Column(String(11))
    bank_name = Column(String(255))
    currency = Column(String(3), nullable=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    beneficiary = relationship("Beneficiary", back_populates="bank_accounts")

    def __repr__(self):
        return f"<BeneficiaryBankAccount(id={self.id}, currency='{self.currency}')>"


class FXQuote(Base):
    """FX Quote model."""

    __tablename__ = "fx_quotes"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    quote_id = Column(String(100), unique=True)
    source_currency = Column(String(3), nullable=False)
    target_currency = Column(String(3), nullable=False)
    rate = Column(DECIMAL(18, 8), nullable=False)
    markup_percentage = Column(DECIMAL(5, 4))
    final_rate = Column(DECIMAL(18, 8), nullable=False)
    quote_expires_at = Column(DateTime, nullable=False)
    is_expired = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<FXQuote(id={self.id}, {self.source_currency}/{self.target_currency})>"


class Payment(Base):
    """Payment model."""

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    beneficiary_id = Column(Integer, ForeignKey("beneficiaries.id"), nullable=False)
    beneficiary_bank_account_id = Column(
        Integer, ForeignKey("beneficiary_bank_accounts.id"), nullable=False
    )
    fx_quote_id = Column(Integer, ForeignKey("fx_quotes.id"))

    source_currency = Column(String(3), nullable=False)
    target_currency = Column(String(3), nullable=False)
    source_amount = Column(DECIMAL(18, 2))
    target_amount = Column(DECIMAL(18, 2))
    fx_rate = Column(DECIMAL(18, 8))
    fee_amount = Column(DECIMAL(18, 2))
    total_debit = Column(DECIMAL(18, 2))

    payment_reference = Column(String(255))
    execution_date = Column(Date)

    status = Column(String(50), nullable=False, default="draft")
    external_payment_id = Column(String(100))
    failure_reason = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Payment(id={self.id}, status='{self.status}')>"


class PaymentApproval(Base):
    """Payment approval model."""

    __tablename__ = "payment_approvals"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    approver_user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(50), nullable=False)
    comments = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PaymentApproval(id={self.id}, action='{self.action}')>"


class AuditLog(Base):
    """Audit log model."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}')>"
