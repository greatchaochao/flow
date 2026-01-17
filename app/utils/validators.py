"""
Validation utilities for financial data formats.
"""

import re
from typing import Optional, Tuple


def validate_iban(iban: str) -> Tuple[bool, Optional[str]]:
    """
    Validate IBAN (International Bank Account Number).

    Args:
        iban: IBAN string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not iban:
        return False, "IBAN is required"

    # Remove spaces and convert to uppercase
    iban = iban.replace(" ", "").upper()

    # Check length (15-34 characters)
    if len(iban) < 15 or len(iban) > 34:
        return False, "IBAN must be between 15 and 34 characters"

    # Check format: 2 letters + 2 digits + alphanumeric
    if not re.match(r"^[A-Z]{2}[0-9]{2}[A-Z0-9]+$", iban):
        return False, "IBAN format invalid (should start with 2 letters and 2 digits)"

    # Move first 4 characters to end
    rearranged = iban[4:] + iban[:4]

    # Replace letters with numbers (A=10, B=11, ..., Z=35)
    numeric_string = ""
    for char in rearranged:
        if char.isdigit():
            numeric_string += char
        else:
            numeric_string += str(ord(char) - ord("A") + 10)

    # Check modulo 97
    if int(numeric_string) % 97 != 1:
        return False, "IBAN checksum validation failed"

    return True, None


def validate_swift_bic(swift: str) -> Tuple[bool, Optional[str]]:
    """
    Validate SWIFT/BIC code.

    Args:
        swift: SWIFT/BIC code to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not swift:
        return False, "SWIFT/BIC code is required"

    # Remove spaces and convert to uppercase
    swift = swift.replace(" ", "").upper()

    # SWIFT code format: 8 or 11 characters
    # Format: AAAABBCCDDD
    # AAAA - Bank code (4 letters)
    # BB - Country code (2 letters)
    # CC - Location code (2 letters or digits)
    # DDD - Branch code (3 letters or digits, optional)

    if len(swift) not in [8, 11]:
        return False, "SWIFT/BIC code must be 8 or 11 characters"

    # Check format
    if not re.match(r"^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$", swift):
        return False, "Invalid SWIFT/BIC format"

    return True, None


def format_iban(iban: str) -> str:
    """
    Format IBAN with spaces for readability.

    Args:
        iban: IBAN string

    Returns:
        Formatted IBAN with spaces every 4 characters
    """
    iban = iban.replace(" ", "").upper()
    return " ".join([iban[i : i + 4] for i in range(0, len(iban), 4)])


def validate_currency_code(currency: str) -> Tuple[bool, Optional[str]]:
    """
    Validate ISO 4217 currency code.

    Args:
        currency: 3-letter currency code

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not currency:
        return False, "Currency code is required"

    currency = currency.upper()

    if len(currency) != 3:
        return False, "Currency code must be 3 characters"

    if not currency.isalpha():
        return False, "Currency code must contain only letters"

    # Common currency codes (expand as needed)
    valid_currencies = {
        "GBP",
        "EUR",
        "USD",
        "CHF",
        "JPY",
        "AUD",
        "CAD",
        "NZD",
        "SEK",
        "NOK",
        "DKK",
        "PLN",
        "CZK",
        "HUF",
        "RON",
        "BGN",
        "HRK",
        "RSD",
        "TRY",
        "ILS",
        "ZAR",
        "INR",
        "CNY",
        "HKD",
        "SGD",
        "THB",
        "MYR",
        "IDR",
        "PHP",
        "KRW",
        "TWD",
        "BRL",
        "MXN",
        "ARS",
        "CLP",
        "COP",
        "PEN",
        "AED",
        "SAR",
        "EGP",
    }

    if currency not in valid_currencies:
        return False, f"Currency code '{currency}' is not supported"

    return True, None


def validate_account_holder_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate account holder name.

    Args:
        name: Account holder name

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Account holder name is required"

    name = name.strip()

    if len(name) < 2:
        return False, "Account holder name must be at least 2 characters"

    if len(name) > 255:
        return False, "Account holder name must not exceed 255 characters"

    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-Z\s\-\'\.]+$", name):
        return False, "Account holder name contains invalid characters"

    return True, None
