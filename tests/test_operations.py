from decimal import Decimal

import pytest

from secure_calculator import Calculator
from secure_calculator.errors import ArithmeticDomainError, DivisionByZeroError
from secure_calculator.operations import (
    Add,
    Divide,
    Modulo,
    Multiply,
    Power,
    Subtract,
    default_operations,
)


@pytest.mark.parametrize(
    ("operation", "left", "right", "expected"),
    [
        (Add(), "1.25", "2.75", "4.00"),
        (Subtract(), "5", "8", "-3"),
        (Multiply(), "1.5", "4", "6.0"),
        (Divide(), "7.5", "2.5", "3"),
        (Modulo(), "10", "3", "1"),
        (Power(), "2", "10", "1024"),
        (Power(), "2", "-2", "0.25"),
    ],
)
def test_operations(operation, left: str, right: str, expected: str) -> None:
    assert operation.execute(Decimal(left), Decimal(right)) == Decimal(expected)


@pytest.mark.parametrize("operation", [Divide(), Modulo()])
def test_zero_divisor_is_rejected(operation) -> None:
    with pytest.raises(DivisionByZeroError):
        operation.execute(Decimal("1"), Decimal("0"))


def test_power_rejects_non_integer_exponent() -> None:
    with pytest.raises(ArithmeticDomainError, match="integer"):
        Power().execute(Decimal("4"), Decimal("0.5"))


def test_power_rejects_excessive_exponent() -> None:
    with pytest.raises(ArithmeticDomainError, match="limit"):
        Power().execute(Decimal("2"), Decimal("10001"))


def test_zero_to_negative_power_is_rejected() -> None:
    with pytest.raises(DivisionByZeroError):
        Power().execute(Decimal("0"), Decimal("-1"))


def test_zero_to_zero_power_is_a_domain_error() -> None:
    with pytest.raises(ArithmeticDomainError):
        Calculator().calculate({"operation": "power", "left": "0", "right": "0"})


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [("-7", "3", "-1"), ("7", "-3", "1"), ("-7", "-3", "-1")],
)
def test_modulo_result_follows_dividend_sign(left: str, right: str, expected: str) -> None:
    assert Modulo().execute(Decimal(left), Decimal(right)) == Decimal(expected)


def test_default_operations_are_complete() -> None:
    assert {operation.name for operation in default_operations()} == {
        "add",
        "subtract",
        "multiply",
        "divide",
        "modulo",
        "power",
    }
