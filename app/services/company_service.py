"""
Company service for business logic.
"""

from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.repositories.company_repository import CompanyRepository
from app.repositories.audit_repository import AuditRepository
from app.database.models import Company


class CompanyService:
    """Service for company business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.company_repo = CompanyRepository(db)
        self.audit_repo = AuditRepository(db)

    def get_company(self, company_id: int) -> Optional[Company]:
        """
        Get company by ID.

        Args:
            company_id: Company ID

        Returns:
            Company object if found, None otherwise
        """
        return self.company_repo.get_by_id(company_id)

    def create_company(self, company_data: dict, user_id: int) -> Company:
        """
        Create a new company with audit logging.

        Args:
            company_data: Dictionary containing company data
            user_id: ID of user creating the company

        Returns:
            Created company object
        """
        # Create company
        company = self.company_repo.create(company_data)

        # Log the creation
        self.audit_repo.create(
            {
                "user_id": user_id,
                "entity_type": "company",
                "entity_id": company.id,
                "action": "created",
                "new_values": {
                    "company_name": company.company_name,
                    "registered_country": company.registered_country,
                    "industry_sector": company.industry_sector,
                    "fx_volume_band": company.fx_volume_band,
                },
            }
        )

        return company

    def update_company(
        self, company_id: int, company_data: dict, user_id: int
    ) -> Optional[Company]:
        """
        Update a company with audit logging.

        Args:
            company_id: Company ID
            company_data: Dictionary containing updated company data
            user_id: ID of user updating the company

        Returns:
            Updated company object if found, None otherwise
        """
        # Get old values for audit
        old_company = self.company_repo.get_by_id(company_id)
        if not old_company:
            return None

        old_values = {
            "company_name": old_company.company_name,
            "registered_country": old_company.registered_country,
            "industry_sector": old_company.industry_sector,
            "fx_volume_band": old_company.fx_volume_band,
        }

        # Update company
        company = self.company_repo.update(company_id, company_data)

        if company:
            # Log the update
            self.audit_repo.create(
                {
                    "user_id": user_id,
                    "entity_type": "company",
                    "entity_id": company.id,
                    "action": "updated",
                    "old_values": old_values,
                    "new_values": {
                        "company_name": company.company_name,
                        "registered_country": company.registered_country,
                        "industry_sector": company.industry_sector,
                        "fx_volume_band": company.fx_volume_band,
                    },
                }
            )

        return company

    def get_company_summary(self, company_id: int) -> Optional[Dict]:
        """
        Get company summary with additional statistics.

        Args:
            company_id: Company ID

        Returns:
            Dictionary with company details and stats
        """
        company = self.company_repo.get_by_id(company_id)
        if not company:
            return None

        return {
            "id": company.id,
            "company_name": company.company_name,
            "registered_country": company.registered_country,
            "industry_sector": company.industry_sector,
            "fx_volume_band": company.fx_volume_band,
            "created_at": company.created_at,
            "updated_at": company.updated_at,
            "user_count": len(company.users),
            "beneficiary_count": len(company.beneficiaries),
        }
