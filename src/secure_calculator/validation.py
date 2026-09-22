"""Strict validation that never evaluates or executes user input."""

import re
from collections.abc import Mapping
from decimal import Decimal, InvalidOperation
from typing import Any

from secure_calculator.errors import ValidationError
from secure_calculator.models import CalculationRequest

MAX_INPUT_LENGTH = 128
MAX_SIGNIFICANT_DIGITS = 34
ARITHMETIC_PRECISION = MAX_SIGNIFICANT_DIGITS * 2
MAX_ADJUSTED_EXPONENT = 9_999
_NUMBER_PATTERN = re.compile(
    r"^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$"
)
_OPERATION_PATTERN = re.compile(r"^[a-z][a-z0-9_]{0,31}$")
_REQUIRED_FIELDS = frozenset({"operation", "left", "right"})


def parse_decimal(value: object, field_name: str) -> Decimal:
    """Parse a finite decimal after lexical, size, and range validation."""
    if isinstance(value, bool | float):
        raise ValidationError(f"{field_name} must be a decimal string, integer, or Decimal")

    if isinstance(value, Decimal):
        number = value
    elif isinstance(value, int):
        # Bound work before converting a programmatically supplied arbitrary-size integer.
        if value.bit_length() > 114:
            raise ValidationError(f"{field_name} has too many significant digits")
        number = Decimal(value)
    elif isinstance(value, str):
        # Reject before strip(), avoiding a second large allocation for oversized strings.
        if not value or len(value) > MAX_INPUT_LENGTH:
            raise ValidationError(f"{field_name} is not a valid decimal number")
        text = value.strip()
        if not text or not _NUMBER_PATTERN.fullmatch(text):
            raise ValidationError(f"{field_name} is not a valid decimal number")
        try:
            number = Decimal(text)
        except InvalidOperation as exc:
            raise ValidationError(f"{field_name} is not a valid decimal number") from exc
    else:
        raise ValidationError(f"{field_name} must be a decimal string, integer, or Decimal")

    if not number.is_finite():
        raise ValidationError(f"{field_name} must be finite")
    if len(number.as_tuple().digits) > MAX_SIGNIFICANT_DIGITS:
        raise ValidationError(f"{field_name} has too many significant digits")
    if number and abs(number.adjusted()) > MAX_ADJUSTED_EXPONENT:
        raise ValidationError(f"{field_name} is outside the supported range")
    return number


def parse_request(payload: Mapping[str, Any]) -> CalculationRequest:
    """Validate an exact, three-field request payload."""
    if not isinstance(payload, Mapping):
        raise ValidationError("payload must be an object")
    if set(payload) != _REQUIRED_FIELDS:
        raise ValidationError("payload must contain exactly: operation, left, right")

    operation_value = payload["operation"]
    if not isinstance(operation_value, str):
        raise ValidationError("operation must be a string")
    operation = operation_value.strip().lower()
    if not _OPERATION_PATTERN.fullmatch(operation):
        raise ValidationError("operation contains invalid characters")

    return CalculationRequest(
        operation=operation,
        left=parse_decimal(payload["left"], "left"),
        right=parse_decimal(payload["right"], "right"),
    )
