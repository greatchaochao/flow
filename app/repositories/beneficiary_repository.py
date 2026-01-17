"""
Beneficiary repository for database operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.models import Beneficiary, BeneficiaryBankAccount


class BeneficiaryRepository:
    """Repository for beneficiary database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, beneficiary_id: int) -> Optional[Beneficiary]:
        """
        Get beneficiary by ID.

        Args:
            beneficiary_id: Beneficiary ID

        Returns:
            Beneficiary object if found, None otherwise
        """
        return (
            self.db.query(Beneficiary).filter(Beneficiary.id == beneficiary_id).first()
        )

    def get_by_company(
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
        query = self.db.query(Beneficiary).filter(Beneficiary.company_id == company_id)

        if not include_inactive:
            query = query.filter(Beneficiary.is_active == True)

        return query.all()

    def create(self, beneficiary_data: dict) -> Beneficiary:
        """
        Create a new beneficiary.

        Args:
            beneficiary_data: Dictionary containing beneficiary data

        Returns:
            Created beneficiary object
        """
        beneficiary = Beneficiary(**beneficiary_data)
        self.db.add(beneficiary)
        self.db.commit()
        self.db.refresh(beneficiary)
        return beneficiary

    def update(
        self, beneficiary_id: int, beneficiary_data: dict
    ) -> Optional[Beneficiary]:
        """
        Update a beneficiary.

        Args:
            beneficiary_id: Beneficiary ID
            beneficiary_data: Dictionary containing updated beneficiary data

        Returns:
            Updated beneficiary object if found, None otherwise
        """
        beneficiary = self.get_by_id(beneficiary_id)
        if not beneficiary:
            return None

        for key, value in beneficiary_data.items():
            if hasattr(beneficiary, key):
                setattr(beneficiary, key, value)

        self.db.commit()
        self.db.refresh(beneficiary)
        return beneficiary

    def delete(self, beneficiary_id: int) -> bool:
        """
        Delete a beneficiary (soft delete by setting is_active to False).

        Args:
            beneficiary_id: Beneficiary ID

        Returns:
            True if deleted, False if not found
        """
        beneficiary = self.get_by_id(beneficiary_id)
        if not beneficiary:
            return False

        beneficiary.is_active = False
        self.db.commit()
        return True

    def restore(self, beneficiary_id: int) -> bool:
        """
        Restore a deleted beneficiary.

        Args:
            beneficiary_id: Beneficiary ID

        Returns:
            True if restored, False if not found
        """
        beneficiary = self.get_by_id(beneficiary_id)
        if not beneficiary:
            return False

        beneficiary.is_active = True
        self.db.commit()
        return True

    def search(self, company_id: int, search_term: str) -> List[Beneficiary]:
        """
        Search beneficiaries by name or country.

        Args:
            company_id: Company ID
            search_term: Search term

        Returns:
            List of matching beneficiaries
        """
        search_pattern = f"%{search_term}%"
        return (
            self.db.query(Beneficiary)
            .filter(
                Beneficiary.company_id == company_id,
                Beneficiary.is_active == True,
                or_(
                    Beneficiary.beneficiary_name.ilike(search_pattern),
                    Beneficiary.country.ilike(search_pattern),
                ),
            )
            .all()
        )


class BeneficiaryBankAccountRepository:
    """Repository for beneficiary bank account database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, account_id: int) -> Optional[BeneficiaryBankAccount]:
        """
        Get bank account by ID.

        Args:
            account_id: Bank account ID

        Returns:
            Bank account object if found, None otherwise
        """
        return (
            self.db.query(BeneficiaryBankAccount)
            .filter(BeneficiaryBankAccount.id == account_id)
            .first()
        )

    def get_by_beneficiary(self, beneficiary_id: int) -> List[BeneficiaryBankAccount]:
        """
        Get all bank accounts for a beneficiary.

        Args:
            beneficiary_id: Beneficiary ID

        Returns:
            List of bank accounts
        """
        return (
            self.db.query(BeneficiaryBankAccount)
            .filter(BeneficiaryBankAccount.beneficiary_id == beneficiary_id)
            .all()
        )

    def create(self, account_data: dict) -> BeneficiaryBankAccount:
        """
        Create a new bank account.

        Args:
            account_data: Dictionary containing bank account data

        Returns:
            Created bank account object
        """
        # If this is set as default, unset other defaults for this beneficiary
        if account_data.get("is_default", False):
            self._unset_default_accounts(account_data["beneficiary_id"])

        account = BeneficiaryBankAccount(**account_data)
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def update(
        self, account_id: int, account_data: dict
    ) -> Optional[BeneficiaryBankAccount]:
        """
        Update a bank account.

        Args:
            account_id: Bank account ID
            account_data: Dictionary containing updated bank account data

        Returns:
            Updated bank account object if found, None otherwise
        """
        account = self.get_by_id(account_id)
        if not account:
            return None

        # If setting as default, unset other defaults
        if account_data.get("is_default", False):
            self._unset_default_accounts(account.beneficiary_id)

        for key, value in account_data.items():
            if hasattr(account, key):
                setattr(account, key, value)

        self.db.commit()
        self.db.refresh(account)
        return account

    def delete(self, account_id: int) -> bool:
        """
        Delete a bank account.

        Args:
            account_id: Bank account ID

        Returns:
            True if deleted, False if not found
        """
        account = self.get_by_id(account_id)
        if not account:
            return False

        self.db.delete(account)
        self.db.commit()
        return True

    def set_default(self, account_id: int) -> Optional[BeneficiaryBankAccount]:
        """
        Set a bank account as default for its beneficiary.

        Args:
            account_id: Bank account ID

        Returns:
            Updated bank account object if found, None otherwise
        """
        account = self.get_by_id(account_id)
        if not account:
            return None

        # Unset other defaults
        self._unset_default_accounts(account.beneficiary_id)

        # Set this as default
        account.is_default = True
        self.db.commit()
        self.db.refresh(account)
        return account

    def _unset_default_accounts(self, beneficiary_id: int) -> None:
        """
        Unset all default accounts for a beneficiary.

        Args:
            beneficiary_id: Beneficiary ID
        """
        self.db.query(BeneficiaryBankAccount).filter(
            BeneficiaryBankAccount.beneficiary_id == beneficiary_id,
            BeneficiaryBankAccount.is_default == True,
        ).update({"is_default": False})
        self.db.commit()
