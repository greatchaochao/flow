"""
Company repository for database operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.database.models import Company


class CompanyRepository:
    """Repository for company database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, company_id: int) -> Optional[Company]:
        """
        Get company by ID.

        Args:
            company_id: Company ID

        Returns:
            Company object if found, None otherwise
        """
        return self.db.query(Company).filter(Company.id == company_id).first()

    def get_all(self) -> List[Company]:
        """
        Get all companies.

        Returns:
            List of all companies
        """
        return self.db.query(Company).all()

    def create(self, company_data: dict) -> Company:
        """
        Create a new company.

        Args:
            company_data: Dictionary containing company data

        Returns:
            Created company object
        """
        company = Company(**company_data)
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def update(self, company_id: int, company_data: dict) -> Optional[Company]:
        """
        Update a company.

        Args:
            company_id: Company ID
            company_data: Dictionary containing updated company data

        Returns:
            Updated company object if found, None otherwise
        """
        company = self.get_by_id(company_id)
        if not company:
            return None

        for key, value in company_data.items():
            if hasattr(company, key):
                setattr(company, key, value)

        self.db.commit()
        self.db.refresh(company)
        return company

    def delete(self, company_id: int) -> bool:
        """
        Delete a company.

        Args:
            company_id: Company ID

        Returns:
            True if deleted, False if not found
        """
        company = self.get_by_id(company_id)
        if not company:
            return False

        self.db.delete(company)
        self.db.commit()
        return True

    def search_by_name(self, name: str) -> List[Company]:
        """
        Search companies by name.

        Args:
            name: Company name to search for

        Returns:
            List of matching companies
        """
        return (
            self.db.query(Company).filter(Company.company_name.ilike(f"%{name}%")).all()
        )
