"""
FX provider integrations for sandbox/testing.

Includes:
- MockFXProvider: Simulated rates for testing
- FixerIOProvider: Real delayed rates from Fixer.io API
"""

import random
import requests
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


class FixerIOProvider:
    """
    Fixer.io FX rate provider integration.

    Uses Fixer.io API for real delayed FX rates (~60 min delay on free tier).
    Free tier: 100 requests/month

    API Documentation: https://fixer.io/documentation
    """

    def __init__(self, api_key: str, base_url: str = "http://data.fixer.io/api"):
        """
        Initialize Fixer.io provider.

        Args:
            api_key: Fixer.io API access key
            base_url: Base URL for Fixer.io API (default: http://data.fixer.io/api)
        """
        if not api_key:
            raise ValueError("Fixer.io API key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._cache = {}  # Simple cache to reduce API calls
        self._cache_ttl = (
            1800  # 30 minutes cache for rates (free tier has ~60 min delay anyway)
        )
        self._currencies_cache = None  # Cache for supported currencies
        self._currencies_cache_time = None  # When currencies were cached

        # Common currencies as fallback when API is rate limited
        self._common_currencies = [
            "EUR",
            "USD",
            "GBP",
            "CHF",
            "JPY",
            "CAD",
            "AUD",
            "NZD",
            "SEK",
            "NOK",
            "DKK",
            "PLN",
            "CZK",
            "HUF",
            "RON",
            "BGN",
            "TRY",
            "ILS",
            "CLP",
            "PHP",
            "AED",
            "SAR",
            "MYR",
            "INR",
            "CNY",
            "KRW",
            "SGD",
            "THB",
            "HKD",
            "MXN",
            "BRL",
            "ZAR",
        ]

    def get_rate(self, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """
        Get current exchange rate from Fixer.io.

        Args:
            from_currency: Source currency code (e.g., 'GBP')
            to_currency: Target currency code (e.g., 'EUR')

        Returns:
            Exchange rate as Decimal, or None if unavailable
        """
        # Check cache first
        cache_key = f"{from_currency}_{to_currency}"
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if (datetime.utcnow() - cached_time).total_seconds() < self._cache_ttl:
                return cached_data

        try:
            # Fixer.io free plan only supports EUR as base currency
            # We need to convert from EUR to get other currency pairs
            url = f"{self.base_url}/latest"

            # If from_currency is EUR, we can query directly
            if from_currency == "EUR":
                params = {"access_key": self.api_key, "symbols": to_currency}

                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                if not data.get("success", False):
                    error_info = data.get("error", {})
                    print(f"Fixer.io API error: {error_info}")
                    return None

                rates = data.get("rates", {})
                if to_currency not in rates:
                    print(f"Rate not found for EUR/{to_currency}")
                    return None

                rate = Decimal(str(rates[to_currency]))

            else:
                # For non-EUR base, we need to fetch both currencies and calculate cross-rate
                params = {
                    "access_key": self.api_key,
                    "symbols": f"{from_currency},{to_currency}",
                }

                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                if not data.get("success", False):
                    error_info = data.get("error", {})
                    print(f"Fixer.io API error: {error_info}")
                    return None

                rates = data.get("rates", {})

                if from_currency not in rates or to_currency not in rates:
                    print(f"Rates not found for {from_currency}/{to_currency}")
                    return None

                # Calculate cross rate: (1 EUR = X FROM) and (1 EUR = Y TO)
                # So: 1 FROM = Y/X TO
                from_rate = Decimal(str(rates[from_currency]))
                to_rate = Decimal(str(rates[to_currency]))
                rate = (to_rate / from_rate).quantize(Decimal("0.00000001"))

            # Cache the result
            self._cache[cache_key] = (rate, datetime.utcnow())

            return rate

        except requests.RequestException as e:
            error_msg = str(e)
            if "429" in error_msg:
                print(
                    f"Fixer.io rate limit exceeded. Using cached rates if available or try again later."
                )
            else:
                print(f"Error fetching rate from Fixer.io: {e}")
            return None
        except (ValueError, KeyError, ZeroDivisionError) as e:
            print(f"Error parsing Fixer.io response: {e}")
            return None

    def get_quote(
        self,
        from_currency: str,
        to_currency: str,
        amount: Optional[Decimal] = None,
        validity_seconds: int = 120,
    ) -> Optional[Dict]:
        """
        Get FX quote with validity period.

        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            amount: Optional amount for conversion calculation
            validity_seconds: Quote validity in seconds (default: 120)

        Returns:
            Quote dictionary with rate, timestamp, expiry, etc.
        """
        rate = self.get_rate(from_currency, to_currency)

        if rate is None:
            return None

        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=validity_seconds)

        quote = {
            "quote_id": f"FIXER-{now.strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": rate,
            "timestamp": now,
            "expires_at": expires_at,
            "validity_seconds": validity_seconds,
            "provider": "fixer.io",
        }

        if amount is not None:
            quote["amount"] = amount
            quote["converted_amount"] = amount * rate

        return quote

    def get_supported_currencies(self) -> list:
        """
        Get list of supported currencies from Fixer.io.
        Uses long-term caching and fallback to avoid rate limits.

        Returns:
            List of currency codes
        """
        # Check if we have a cached list (cache for 24 hours)
        if (
            self._currencies_cache is not None
            and self._currencies_cache_time is not None
        ):
            time_since_cache = (
                datetime.utcnow() - self._currencies_cache_time
            ).total_seconds()
            if time_since_cache < 86400:  # 24 hours
                return self._currencies_cache

        try:
            url = f"{self.base_url}/symbols"
            params = {"access_key": self.api_key}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if not data.get("success", False):
                # Return cached or fallback currencies
                return (
                    self._currencies_cache
                    if self._currencies_cache
                    else self._common_currencies
                )

            symbols = data.get("symbols", {})
            currencies = list(symbols.keys())

            # Update cache
            self._currencies_cache = currencies
            self._currencies_cache_time = datetime.utcnow()

            return currencies

        except requests.RequestException as e:
            error_msg = str(e)
            if "429" in error_msg:
                print(
                    f"Fixer.io rate limit for currencies. Using cached/fallback list."
                )
            else:
                print(f"Error fetching currencies from Fixer.io: {e}")

            # Return cached currencies if available, otherwise use common currencies
            return (
                self._currencies_cache
                if self._currencies_cache
                else self._common_currencies
            )
