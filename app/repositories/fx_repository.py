"""
FX Quote repository for database operations.
"""

from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.database.models import FXQuote


class FXQuoteRepository:
    """Repository for FX quote database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, quote_id: int) -> Optional[FXQuote]:
        """
        Get FX quote by ID.

        Args:
            quote_id: Quote ID

        Returns:
            FXQuote object if found, None otherwise
        """
        return self.db.query(FXQuote).filter(FXQuote.id == quote_id).first()

    def get_by_quote_id(self, quote_id: str) -> Optional[FXQuote]:
        """
        Get FX quote by external quote ID.

        Args:
            quote_id: External provider quote ID

        Returns:
            FXQuote object if found, None otherwise
        """
        return self.db.query(FXQuote).filter(FXQuote.quote_id == quote_id).first()

    def get_by_company(
        self, company_id: int, include_expired: bool = False
    ) -> List[FXQuote]:
        """
        Get all FX quotes for a company.

        Args:
            company_id: Company ID
            include_expired: Whether to include expired quotes

        Returns:
            List of FX quotes
        """
        query = self.db.query(FXQuote).filter(FXQuote.company_id == company_id)

        if not include_expired:
            query = query.filter(
                or_(
                    FXQuote.is_expired == False,
                    and_(
                        FXQuote.is_expired == False,
                        FXQuote.quote_expires_at > datetime.utcnow(),
                    ),
                )
            )

        return query.order_by(FXQuote.created_at.desc()).all()

    def create(self, quote_data: dict) -> FXQuote:
        """
        Create a new FX quote.

        Args:
            quote_data: Dictionary containing quote data

        Returns:
            Created FXQuote object
        """
        quote = FXQuote(**quote_data)
        self.db.add(quote)
        self.db.commit()
        self.db.refresh(quote)
        return quote

    def update(self, quote_id: int, quote_data: dict) -> Optional[FXQuote]:
        """
        Update an FX quote.

        Args:
            quote_id: Quote ID
            quote_data: Dictionary containing updated quote data

        Returns:
            Updated FXQuote object if found, None otherwise
        """
        quote = self.get_by_id(quote_id)
        if not quote:
            return None

        for key, value in quote_data.items():
            if hasattr(quote, key):
                setattr(quote, key, value)

        self.db.commit()
        self.db.refresh(quote)
        return quote

    def mark_expired(self, quote_id: int) -> bool:
        """
        Mark a quote as expired.

        Args:
            quote_id: Quote ID

        Returns:
            True if updated, False if not found
        """
        quote = self.get_by_id(quote_id)
        if not quote:
            return False

        quote.is_expired = True
        self.db.commit()
        return True

    def get_active_quotes(
        self, company_id: int, currency_pair: Optional[tuple] = None
    ) -> List[FXQuote]:
        """
        Get active (non-expired) quotes for a company.

        Args:
            company_id: Company ID
            currency_pair: Optional tuple of (source_currency, target_currency)

        Returns:
            List of active FX quotes
        """
        query = self.db.query(FXQuote).filter(
            FXQuote.company_id == company_id,
            FXQuote.is_expired == False,
            FXQuote.quote_expires_at > datetime.utcnow(),
        )

        if currency_pair:
            source_currency, target_currency = currency_pair
            query = query.filter(
                FXQuote.source_currency == source_currency,
                FXQuote.target_currency == target_currency,
            )

        return query.order_by(FXQuote.created_at.desc()).all()

    def expire_old_quotes(self) -> int:
        """
        Mark all expired quotes in database.

        Returns:
            Number of quotes marked as expired
        """
        result = (
            self.db.query(FXQuote)
            .filter(
                FXQuote.is_expired == False,
                FXQuote.quote_expires_at < datetime.utcnow(),
            )
            .update({"is_expired": True})
        )
        self.db.commit()
        return result

    def get_recent_quotes(
        self, company_id: int, days: int = 7, limit: int = 50
    ) -> List[FXQuote]:
        """
        Get recent quotes for a company.

        Args:
            company_id: Company ID
            days: Number of days to look back
            limit: Maximum number of quotes to return

        Returns:
            List of recent FX quotes
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return (
            self.db.query(FXQuote)
            .filter(FXQuote.company_id == company_id, FXQuote.created_at >= cutoff_date)
            .order_by(FXQuote.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_quote_statistics(self, company_id: int, days: int = 30) -> dict:
        """
        Get quote statistics for a company.

        Args:
            company_id: Company ID
            days: Number of days to analyze

        Returns:
            Dictionary with statistics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        quotes = (
            self.db.query(FXQuote)
            .filter(FXQuote.company_id == company_id, FXQuote.created_at >= cutoff_date)
            .all()
        )

        if not quotes:
            return {
                "total_quotes": 0,
                "expired_quotes": 0,
                "active_quotes": 0,
                "currency_pairs": [],
            }

        currency_pairs = set()
        for quote in quotes:
            currency_pairs.add(f"{quote.source_currency}/{quote.target_currency}")

        return {
            "total_quotes": len(quotes),
            "expired_quotes": sum(1 for q in quotes if q.is_expired),
            "active_quotes": sum(1 for q in quotes if not q.is_expired),
            "currency_pairs": list(currency_pairs),
        }
