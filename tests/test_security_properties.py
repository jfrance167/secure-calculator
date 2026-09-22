import re
from decimal import Decimal

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from secure_calculator import Calculator
from secure_calculator.errors import ArithmeticDomainError, ValidationError
from secure_calculator.validation import (
    MAX_INPUT_LENGTH,
    MAX_SIGNIFICANT_DIGITS,
    parse_decimal,
)

ASCII_DECIMAL = re.compile(
    r"^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$"
)


@given(st.text(min_size=0, max_size=256))
@settings(max_examples=1_000, deadline=200)
def test_arbitrary_strings_never_escape_as_unexpected_exceptions(raw: str) -> None:
    try:
        result = parse_decimal(raw, "value")
    except ValidationError:
        return

    assert ASCII_DECIMAL.fullmatch(raw.strip())
    assert result.is_finite()


@given(st.floats(allow_nan=True, allow_infinity=True, width=64))
def test_binary_floats_are_always_rejected(value: float) -> None:
    with pytest.raises(ValidationError):
        parse_decimal(value, "value")


@pytest.mark.parametrize("raw", ["١", "１２", "௧", "𝟡"])
def test_unicode_numerals_are_rejected(raw: str) -> None:
    with pytest.raises(ValidationError):
        parse_decimal(raw, "value")


def test_large_whitespace_payload_is_rejected() -> None:
    raw = " " * (MAX_INPUT_LENGTH + 1)

    with pytest.raises(ValidationError):
        parse_decimal(raw, "value")


def test_significant_digit_boundary() -> None:
    accepted = "9" * MAX_SIGNIFICANT_DIGITS
    rejected = "9" * (MAX_SIGNIFICANT_DIGITS + 1)

    assert parse_decimal(accepted, "value") == Decimal(accepted)
    with pytest.raises(ValidationError):
        parse_decimal(rejected, "value")


def test_maximum_operand_multiplication_is_exact() -> None:
    operand = "9" * MAX_SIGNIFICANT_DIGITS
    expected = Decimal(str(int(operand) ** 2))

    result = Calculator().calculate(
        {"operation": "multiply", "left": operand, "right": operand}
    )

    assert result == expected


def test_extreme_power_request_is_rejected_by_policy() -> None:
    with pytest.raises(ArithmeticDomainError):
        Calculator().calculate(
            {
                "operation": "power",
                "left": "999999999",
                "right": "999999999",
            }
        )


def test_large_integer_is_rejected_before_string_conversion() -> None:
    with pytest.raises(ValidationError):
        parse_decimal(10**10_000, "value")

