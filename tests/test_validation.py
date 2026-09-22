from decimal import Decimal

import pytest

from secure_calculator.errors import ValidationError
from secure_calculator.validation import parse_decimal, parse_request


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("  -12.50 ", Decimal("-12.50")),
        (".5", Decimal(".5")),
        ("5.", Decimal("5")),
        ("1e3", Decimal("1e3")),
        (4, Decimal("4")),
        (Decimal("9.1"), Decimal("9.1")),
    ],
)
def test_parse_decimal_accepts_supported_values(raw: object, expected: Decimal) -> None:
    assert parse_decimal(raw, "value") == expected


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "1 + 2",
        "__import__('os').system('whoami')",
        "NaN",
        "Infinity",
        "0x10",
        "1_000",
        "1; rm -rf /",
        True,
        0.25,
        None,
        [],
        "1" * 129,
        "9" * 35,
        "1e10000",
    ],
)
def test_parse_decimal_rejects_malformed_or_dangerous_values(raw: object) -> None:
    with pytest.raises(ValidationError):
        parse_decimal(raw, "value")


@pytest.mark.parametrize("raw", [Decimal("NaN"), Decimal("Infinity"), Decimal("-Infinity")])
def test_parse_decimal_rejects_non_finite_decimal_instances(raw: Decimal) -> None:
    with pytest.raises(ValidationError, match="finite"):
        parse_decimal(raw, "value")


def test_parse_request_normalizes_operation() -> None:
    request = parse_request({"operation": " ADD ", "left": "1", "right": "2"})
    assert request.operation == "add"
    assert request.left == Decimal("1")


@pytest.mark.parametrize(
    "payload",
    [
        "not-a-mapping",
        {},
        {"operation": "add", "left": "1"},
        {"operation": "add", "left": "1", "right": "2", "admin": True},
        {"operation": 42, "left": "1", "right": "2"},
        {"operation": "add;drop", "left": "1", "right": "2"},
        {"operation": "A" * 33, "left": "1", "right": "2"},
    ],
)
def test_parse_request_rejects_invalid_structure(payload) -> None:
    with pytest.raises(ValidationError):
        parse_request(payload)
