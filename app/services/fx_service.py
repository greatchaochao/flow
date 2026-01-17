"""
FX Quote service for business logic.
"""

from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.repositories.fx_repository import FXQuoteRepository
from app.repositories.audit_repository import AuditRepository
from app.integrations.fx_provider import MockFXProvider
from app.database.models import FXQuote
from app.config import config


class FXService:
    """Service for FX quote business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.fx_repo = FXQuoteRepository(db)
        self.audit_repo = AuditRepository(db)
        self.fx_provider = MockFXProvider(
            api_key=config.FX_PROVIDER_API_KEY, api_url=config.FX_PROVIDER_API_URL
        )
        self.markup_percentage = Decimal(str(config.FX_MARKUP_PERCENTAGE))

    def get_live_rate(
        self, from_currency: str, to_currency: str, amount: Optional[Decimal] = None
    ) -> Dict:
        """
        Get live FX rate from provider.

        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            amount: Optional amount to convert

        Returns:
            Dictionary with rate information
        """
        return self.fx_provider.get_rate(from_currency, to_currency, amount)

    def request_quote(
        self,
        company_id: int,
        from_currency: str,
        to_currency: str,
        amount: Decimal,
        user_id: int,
        validity_seconds: int = 120,
    ) -> tuple[Optional[FXQuote], Optional[str]]:
        """
        Request a fixed FX quote with markup.

        Args:
            company_id: Company ID
            from_currency: Source currency code
            to_currency: Target currency code
            amount: Amount to convert
            user_id: ID of user requesting quote
            validity_seconds: Quote validity period (default 120 seconds)

        Returns:
            Tuple of (FXQuote, error_message)
        """
        try:
            # Get quote from provider
            provider_quote = self.fx_provider.get_quote(
                from_currency, to_currency, amount, validity_seconds
            )

            # Calculate rate with markup
            base_rate = provider_quote["rate"]
            markup_rate = base_rate * (Decimal("1.0") + self.markup_percentage)
            final_rate = markup_rate.quantize(Decimal("0.0001"))

            # Calculate target amount with markup
            target_amount = (amount * final_rate).quantize(Decimal("0.01"))

            # Create quote in database
            quote_data = {
                "company_id": company_id,
                "quote_id": provider_quote["quote_id"],
                "source_currency": from_currency.upper(),
                "target_currency": to_currency.upper(),
                "rate": base_rate,
                "markup_percentage": self.markup_percentage,
                "final_rate": final_rate,
                "quote_expires_at": provider_quote["expires_at"],
                "is_expired": False,
            }

            quote = self.fx_repo.create(quote_data)

            # Log the quote request
            self.audit_repo.create(
                {
                    "user_id": user_id,
                    "entity_type": "fx_quote",
                    "entity_id": quote.id,
                    "action": "requested",
                    "new_values": {
                        "quote_id": quote.quote_id,
                        "currency_pair": f"{from_currency}/{to_currency}",
                        "rate": str(final_rate),
                        "amount": str(amount),
                    },
                }
            )

            return quote, None

        except Exception as e:
            return None, str(e)

    def get_quote(self, quote_id: int) -> Optional[FXQuote]:
        """
        Get quote by ID.

        Args:
            quote_id: Quote ID

        Returns:
            FXQuote object if found, None otherwise
        """
        return self.fx_repo.get_by_id(quote_id)

    def get_company_quotes(
        self, company_id: int, include_expired: bool = False
    ) -> List[FXQuote]:
        """
        Get all quotes for a company.

        Args:
            company_id: Company ID
            include_expired: Whether to include expired quotes

        Returns:
            List of FX quotes
        """
        return self.fx_repo.get_by_company(company_id, include_expired)

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
        return self.fx_repo.get_active_quotes(company_id, currency_pair)

    def is_quote_valid(self, quote: FXQuote) -> bool:
        """
        Check if a quote is still valid.

        Args:
            quote: FXQuote object

        Returns:
            True if valid, False if expired
        """
        if quote.is_expired:
            return False

        if quote.quote_expires_at < datetime.utcnow():
            # Mark as expired in database
            self.fx_repo.mark_expired(quote.id)
            return False

        return True

    def get_quote_time_remaining(self, quote: FXQuote) -> int:
        """
        Get seconds remaining before quote expires.

        Args:
            quote: FXQuote object

        Returns:
            Seconds remaining (0 if expired)
        """
        if not self.is_quote_valid(quote):
            return 0

        delta = quote.quote_expires_at - datetime.utcnow()
        return max(0, int(delta.total_seconds()))

    def calculate_amount(
        self, quote: FXQuote, source_amount: Decimal
    ) -> Dict[str, Decimal]:
        """
        Calculate converted amount using quote rate.

        Args:
            quote: FXQuote object
            source_amount: Amount in source currency

        Returns:
            Dictionary with calculated amounts and fees
        """
        target_amount = (source_amount * quote.final_rate).quantize(Decimal("0.01"))

        # Calculate markup fee (difference between base and final rate)
        base_target_amount = (source_amount * quote.rate).quantize(Decimal("0.01"))
        markup_fee = target_amount - base_target_amount

        return {
            "source_amount": source_amount,
            "target_amount": target_amount,
            "exchange_rate": quote.final_rate,
            "base_rate": quote.rate,
            "markup_fee": markup_fee,
            "markup_percentage": quote.markup_percentage
            * Decimal("100"),  # Convert to %
        }

    def get_supported_currencies(self) -> List[str]:
        """
        Get list of supported currencies.

        Returns:
            List of currency codes
        """
        return self.fx_provider.get_supported_currencies()

    def get_currency_pairs(self) -> List[tuple]:
        """
        Get list of available currency pairs.

        Returns:
            List of tuples (from_currency, to_currency)
        """
        return self.fx_provider.get_currency_pairs()

    def get_quote_statistics(self, company_id: int, days: int = 30) -> Dict:
        """
        Get quote statistics for a company.

        Args:
            company_id: Company ID
            days: Number of days to analyze

        Returns:
            Dictionary with statistics
        """
        return self.fx_repo.get_quote_statistics(company_id, days)

    def expire_old_quotes(self) -> int:
        """
        Mark all expired quotes in database.

        Returns:
            Number of quotes expired
        """
        return self.fx_repo.expire_old_quotes()

    def get_rate_breakdown(self, quote: FXQuote) -> Dict:
        """
        Get detailed breakdown of FX rate components.

        Args:
            quote: FXQuote object

        Returns:
            Dictionary with rate breakdown
        """
        return {
            "base_rate": quote.rate,
            "markup_percentage": (quote.markup_percentage * Decimal("100")).quantize(
                Decimal("0.01")
            ),
            "markup_amount": (quote.rate * quote.markup_percentage).quantize(
                Decimal("0.0001")
            ),
            "final_rate": quote.final_rate,
            "currency_pair": f"{quote.source_currency}/{quote.target_currency}",
            "inverse_rate": (Decimal("1.0") / quote.final_rate).quantize(
                Decimal("0.0001")
            ),
        }
