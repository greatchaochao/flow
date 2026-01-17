"""
Beneficiary service for business logic.
"""

from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.repositories.beneficiary_repository import (
    BeneficiaryRepository,
    BeneficiaryBankAccountRepository,
)
from app.repositories.audit_repository import AuditRepository
from app.database.models import Beneficiary, BeneficiaryBankAccount
from app.utils.validators import (
    validate_iban,
    validate_swift_bic,
    validate_currency_code,
    validate_account_holder_name,
    format_iban,
)


class BeneficiaryService:
    """Service for beneficiary business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.beneficiary_repo = BeneficiaryRepository(db)
        self.bank_account_repo = BeneficiaryBankAccountRepository(db)
        self.audit_repo = AuditRepository(db)

    def get_beneficiary(self, beneficiary_id: int) -> Optional[Beneficiary]:
        """
        Get beneficiary by ID.

        Args:
            beneficiary_id: Beneficiary ID

        Returns:
            Beneficiary object if found, None otherwise
        """
        return self.beneficiary_repo.get_by_id(beneficiary_id)

    def get_company_beneficiaries(
        self, company_id: int, include_inactive: bool = False
    ) -> List[Beneficiary]:
        """
        Get all beneficiaries for a company.

        Args:
            company_id: Company ID
            include_inactive: Whether to include inactive beneficiaries

        Returns:
            List of beneficiaries
        """
        return self.beneficiary_repo.get_by_company(company_id, include_inactive)

    def create_beneficiary(self, beneficiary_data: dict, user_id: int) -> Beneficiary:
        """
        Create a new beneficiary with audit logging.

        Args:
            beneficiary_data: Dictionary containing beneficiary data
            user_id: ID of user creating the beneficiary

        Returns:
            Created beneficiary object
        """
        # Create beneficiary
        beneficiary = self.beneficiary_repo.create(beneficiary_data)

        # Log the creation
        self.audit_repo.create(
            {
                "user_id": user_id,
                "entity_type": "beneficiary",
                "entity_id": beneficiary.id,
                "action": "created",
                "new_values": {
                    "beneficiary_name": beneficiary.beneficiary_name,
                    "beneficiary_type": beneficiary.beneficiary_type,
                    "country": beneficiary.country,
                },
            }
        )

        return beneficiary

    def update_beneficiary(
        self, beneficiary_id: int, beneficiary_data: dict, user_id: int
    ) -> Optional[Beneficiary]:
        """
        Update a beneficiary with audit logging.

        Args:
            beneficiary_id: Beneficiary ID
            beneficiary_data: Dictionary containing updated beneficiary data
            user_id: ID of user updating the beneficiary

        Returns:
            Updated beneficiary object if found, None otherwise
        """
        # Get old values for audit
        old_beneficiary = self.beneficiary_repo.get_by_id(beneficiary_id)
        if not old_beneficiary:
            return None

        old_values = {
            "beneficiary_name": old_beneficiary.beneficiary_name,
            "beneficiary_type": old_beneficiary.beneficiary_type,
            "country": old_beneficiary.country,
        }

        # Update beneficiary
        beneficiary = self.beneficiary_repo.update(beneficiary_id, beneficiary_data)

        if beneficiary:
            # Log the update
            self.audit_repo.create(
                {
                    "user_id": user_id,
                    "entity_type": "beneficiary",
                    "entity_id": beneficiary.id,
                    "action": "updated",
                    "old_values": old_values,
                    "new_values": {
                        "beneficiary_name": beneficiary.beneficiary_name,
                        "beneficiary_type": beneficiary.beneficiary_type,
                        "country": beneficiary.country,
                    },
                }
            )

        return beneficiary

    def disable_beneficiary(self, beneficiary_id: int, user_id: int) -> bool:
        """
        Disable a beneficiary with audit logging.

        Args:
            beneficiary_id: Beneficiary ID
            user_id: ID of user disabling the beneficiary

        Returns:
            True if disabled, False if not found
        """
        success = self.beneficiary_repo.delete(beneficiary_id)

        if success:
            # Log the disable
            self.audit_repo.create(
                {
                    "user_id": user_id,
                    "entity_type": "beneficiary",
                    "entity_id": beneficiary_id,
                    "action": "disabled",
                }
            )

        return success

    def enable_beneficiary(self, beneficiary_id: int, user_id: int) -> bool:
        """
        Enable a disabled beneficiary with audit logging.

        Args:
            beneficiary_id: Beneficiary ID
            user_id: ID of user enabling the beneficiary

        Returns:
            True if enabled, False if not found
        """
        success = self.beneficiary_repo.restore(beneficiary_id)

        if success:
            # Log the enable
            self.audit_repo.create(
                {
                    "user_id": user_id,
                    "entity_type": "beneficiary",
                    "entity_id": beneficiary_id,
                    "action": "enabled",
                }
            )

        return success

    def search_beneficiaries(
        self, company_id: int, search_term: str
    ) -> List[Beneficiary]:
        """
        Search beneficiaries by name or country.

        Args:
            company_id: Company ID
            search_term: Search term

        Returns:
            List of matching beneficiaries
        """
        return self.beneficiary_repo.search(company_id, search_term)

    def add_bank_account(
        self, beneficiary_id: int, account_data: dict, user_id: int
    ) -> tuple[Optional[BeneficiaryBankAccount], Optional[str]]:
        """
        Add a bank account to a beneficiary with validation.

        Args:
            beneficiary_id: Beneficiary ID
            account_data: Dictionary containing bank account data
            user_id: ID of user adding the account

        Returns:
            Tuple of (bank_account, error_message)
        """
        # Validate account holder name
        is_valid, error = validate_account_holder_name(
            account_data.get("account_holder_name", "")
        )
        if not is_valid:
            return None, error

        # Validate IBAN if provided
        if account_data.get("iban"):
            is_valid, error = validate_iban(account_data["iban"])
            if not is_valid:
                return None, error
            # Format IBAN
            account_data["iban"] = format_iban(account_data["iban"])

        # Validate SWIFT/BIC if provided
        if account_data.get("swift_bic"):
            is_valid, error = validate_swift_bic(account_data["swift_bic"])
            if not is_valid:
                return None, error
            account_data["swift_bic"] = (
                account_data["swift_bic"].replace(" ", "").upper()
            )

        # Validate currency
        is_valid, error = validate_currency_code(account_data.get("currency", ""))
        if not is_valid:
            return None, error
        account_data["currency"] = account_data["currency"].upper()

        # Ensure beneficiary_id is set
        account_data["beneficiary_id"] = beneficiary_id

        # Create bank account
        account = self.bank_account_repo.create(account_data)

        # Log the creation
        self.audit_repo.create(
            {
                "user_id": user_id,
                "entity_type": "bank_account",
                "entity_id": account.id,
                "action": "created",
                "new_values": {
                    "beneficiary_id": beneficiary_id,
                    "currency": account.currency,
                    "iban": account.iban[:10] + "****" if account.iban else None,
                },
            }
        )

        return account, None

    def get_beneficiary_accounts(
        self, beneficiary_id: int
    ) -> List[BeneficiaryBankAccount]:
        """
        Get all bank accounts for a beneficiary.

        Args:
            beneficiary_id: Beneficiary ID

        Returns:
            List of bank accounts
        """
        return self.bank_account_repo.get_by_beneficiary(beneficiary_id)

    def delete_bank_account(self, account_id: int, user_id: int) -> bool:
        """
        Delete a bank account with audit logging.

        Args:
            account_id: Bank account ID
            user_id: ID of user deleting the account

        Returns:
            True if deleted, False if not found
        """
        success = self.bank_account_repo.delete(account_id)

        if success:
            # Log the deletion
            self.audit_repo.create(
                {
                    "user_id": user_id,
                    "entity_type": "bank_account",
                    "entity_id": account_id,
                    "action": "deleted",
                }
            )

        return success

    def set_default_account(
        self, account_id: int, user_id: int
    ) -> Optional[BeneficiaryBankAccount]:
        """
        Set a bank account as default.

        Args:
            account_id: Bank account ID
            user_id: ID of user setting the default

        Returns:
            Updated bank account object if found, None otherwise
        """
        account = self.bank_account_repo.set_default(account_id)

        if account:
            # Log the update
            self.audit_repo.create(
                {
                    "user_id": user_id,
                    "entity_type": "bank_account",
                    "entity_id": account_id,
                    "action": "set_default",
                }
            )

        return account
