"""
Mock FX provider integration for sandbox/testing.

In production, this would integrate with real FX providers like:
- CurrencyCloud API
- Wise (TransferWise) API
- XE Currency Data API
- etc.
"""

import random
from datetime import datetime, timedelta
from typing import Optional, Dict
from decimal import Decimal


class MockFXProvider:
    """Mock FX rate provider for PoC demonstration."""

    # Base rates (GBP as base currency)
    BASE_RATES = {
        "GBP": Decimal("1.0000"),
        "EUR": Decimal("1.1650"),
        "USD": Decimal("1.2720"),
        "CHF": Decimal("1.1250"),
        "JPY": Decimal("145.50"),
        "CAD": Decimal("1.6850"),
        "AUD": Decimal("1.8450"),
        "NZD": Decimal("1.9750"),
        "SEK": Decimal("13.25"),
        "NOK": Decimal("13.15"),
        "DKK": Decimal("8.68"),
        "PLN": Decimal("5.05"),
        "CZK": Decimal("28.50"),
    }

    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """
        Initialize FX provider.

        Args:
            api_key: API key for authentication (unused in mock)
            api_url: API endpoint URL (unused in mock)
        """
        self.api_key = api_key
        self.api_url = api_url

    def get_rate(
        self, from_currency: str, to_currency: str, amount: Optional[Decimal] = None
    ) -> Dict:
        """
        Get FX rate for currency pair.

        Args:
            from_currency: Source currency code (e.g., 'GBP')
            to_currency: Target currency code (e.g., 'EUR')
            amount: Optional amount to convert

        Returns:
            Dictionary with rate information

        Raises:
            ValueError: If currency not supported
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        # Validate currencies
        if from_currency not in self.BASE_RATES:
            raise ValueError(f"Unsupported source currency: {from_currency}")
        if to_currency not in self.BASE_RATES:
            raise ValueError(f"Unsupported target currency: {to_currency}")

        # Same currency
        if from_currency == to_currency:
            return {
                "from_currency": from_currency,
                "to_currency": to_currency,
                "rate": Decimal("1.0000"),
                "inverse_rate": Decimal("1.0000"),
                "timestamp": datetime.utcnow().isoformat(),
                "provider": "MockFX",
            }

        # Calculate cross rate with slight random variation
        # This simulates real-time market fluctuations
        base_rate = self.BASE_RATES[to_currency] / self.BASE_RATES[from_currency]

        # Add small random fluctuation (±0.5%)
        fluctuation = Decimal(str(random.uniform(-0.005, 0.005)))
        rate = base_rate * (Decimal("1.0") + fluctuation)

        # Round to appropriate decimal places
        rate = rate.quantize(Decimal("0.0001"))

        result = {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": rate,
            "inverse_rate": (Decimal("1.0") / rate).quantize(Decimal("0.0001")),
            "timestamp": datetime.utcnow().isoformat(),
            "provider": "MockFX",
        }

        # If amount provided, calculate converted amount
        if amount:
            result["source_amount"] = amount
            result["target_amount"] = (amount * rate).quantize(Decimal("0.01"))

        return result

    def get_quote(
        self,
        from_currency: str,
        to_currency: str,
        amount: Decimal,
        quote_validity_seconds: int = 120,
    ) -> Dict:
        """
        Get a fixed FX quote valid for a specific time period.

        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            amount: Amount to convert
            quote_validity_seconds: Quote validity period (default 120 seconds)

        Returns:
            Dictionary with quote information including expiry time
        """
        rate_info = self.get_rate(from_currency, to_currency, amount)

        # Generate mock quote ID
        quote_id = f"MFX-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"

        quote = {
            "quote_id": quote_id,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": rate_info["rate"],
            "source_amount": amount,
            "target_amount": rate_info["target_amount"],
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(seconds=quote_validity_seconds),
            "validity_seconds": quote_validity_seconds,
            "provider": "MockFX",
        }

        return quote

    def validate_currency(self, currency_code: str) -> bool:
        """
        Check if currency is supported.

        Args:
            currency_code: 3-letter currency code

        Returns:
            True if supported, False otherwise
        """
        return currency_code.upper() in self.BASE_RATES

    def get_supported_currencies(self) -> list:
        """
        Get list of supported currencies.

        Returns:
            List of currency codes
        """
        return list(self.BASE_RATES.keys())

    def get_currency_pairs(self) -> list:
        """
        Get list of available currency pairs.

        Returns:
            List of tuples (from_currency, to_currency)
        """
        currencies = self.get_supported_currencies()
        pairs = []
        for from_curr in currencies:
            for to_curr in currencies:
                if from_curr != to_curr:
                    pairs.append((from_curr, to_curr))
        return pairs
