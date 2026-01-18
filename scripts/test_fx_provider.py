"""
Test script to verify Fixer.io integration.

This script tests:
1. Mock provider (fallback)
2. Fixer.io provider (if API key configured)
"""

from decimal import Decimal
from app.integrations.fx_provider import MockFXProvider, FixerIOProvider
from app.config import config


def test_mock_provider():
    """Test the mock FX provider."""
    print("\n" + "=" * 60)
    print("Testing Mock FX Provider")
    print("=" * 60)

    provider = MockFXProvider(api_key="", api_url="")

    # Test get_rate
    rate = provider.get_rate("GBP", "EUR")
    print(f"\n✓ GBP/EUR rate: {rate}")

    # Test get_quote
    quote = provider.get_quote("GBP", "USD", amount=Decimal("1000"))
    print(f"\n✓ Quote generated:")
    print(f"  - Quote ID: {quote['quote_id']}")
    print(f"  - Rate: {quote['rate']}")
    print(
        f"  - Amount: {quote.get('source_amount', quote.get('amount', 'N/A'))} {quote['from_currency']}"
    )
    print(
        f"  - Converted: {float(quote.get('target_amount', quote.get('converted_amount', 0))):.2f} {quote['to_currency']}"
    )
    print(f"  - Expires at: {quote['expires_at']}")

    # Test supported currencies
    currencies = provider.get_supported_currencies()
    print(f"\n✓ Supported currencies ({len(currencies)}): {', '.join(currencies)}")


def test_fixer_io_provider():
    """Test the Fixer.io provider (requires API key)."""
    print("\n" + "=" * 60)
    print("Testing Fixer.io Provider")
    print("=" * 60)

    if not config.FX_PROVIDER_API_KEY:
        print("\n⚠️  No API key configured. Skipping Fixer.io test.")
        print("   To test: Set FX_PROVIDER_API_KEY in .env file")
        return

    try:
        provider = FixerIOProvider(
            api_key=config.FX_PROVIDER_API_KEY,
            base_url=config.FX_PROVIDER_API_URL or "http://data.fixer.io/api",
        )

        print(
            f"\n✓ Provider initialized with API key: {config.FX_PROVIDER_API_KEY[:8]}..."
        )

        # Test get_rate
        print("\n📊 Fetching GBP/EUR rate from Fixer.io...")
        rate = provider.get_rate("GBP", "EUR")

        if rate:
            print(f"✓ GBP/EUR rate: {rate}")
        else:
            print("✗ Failed to fetch rate")
            return

        # Test get_quote
        print("\n📊 Generating quote for 1000 GBP to USD...")
        quote = provider.get_quote("GBP", "USD", amount=Decimal("1000"))

        if quote:
            print(f"✓ Quote generated:")
            print(f"  - Quote ID: {quote['quote_id']}")
            print(f"  - Rate: {quote['rate']}")
            print(
                f"  - Amount: {quote.get('amount', quote.get('source_amount', 'N/A'))} {quote['from_currency']}"
            )
            print(
                f"  - Converted: {float(quote.get('converted_amount', quote.get('target_amount', 0))):.2f} {quote['to_currency']}"
            )
            print(f"  - Provider: {quote['provider']}")
            print(f"  - Expires at: {quote['expires_at']}")
        else:
            print("✗ Failed to generate quote")
            return

        # Test supported currencies
        print("\n📊 Fetching supported currencies...")
        currencies = provider.get_supported_currencies()
        print(
            f"✓ Supported currencies ({len(currencies)}): {', '.join(currencies[:10])}..."
        )

        print("\n✅ All Fixer.io tests passed!")

    except ValueError as e:
        print(f"\n✗ Error: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("FX Provider Integration Test")
    print("=" * 60)

    # Test mock provider
    test_mock_provider()

    # Test Fixer.io provider
    test_fixer_io_provider()

    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
