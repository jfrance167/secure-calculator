import logging
from decimal import Decimal
from io import StringIO

import pytest

from secure_calculator.errors import (
    ArithmeticDomainError,
    ArithmeticOverflowError,
    DivisionByZeroError,
    UnsupportedOperationError,
    ValidationError,
)
from secure_calculator.operations import Add, BinaryOperation
from secure_calculator.registry import OperationRegistry
from secure_calculator.service import Calculator


def test_calculator_executes_request() -> None:
    result = Calculator().calculate({"operation": "add", "left": "0.1", "right": "0.2"})
    assert result == Decimal("0.3")


def test_calculator_rejects_unknown_operation() -> None:
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger = logging.getLogger("secure_calculator")
    logger.addHandler(handler)
    try:
        with pytest.raises(UnsupportedOperationError):
            Calculator().calculate({"operation": "delete", "left": "1", "right": "2"})
    finally:
        logger.removeHandler(handler)
    assert "unsupported_operation" in stream.getvalue()
    assert "delete" not in stream.getvalue()


def test_calculator_rejects_division_by_zero() -> None:
    with pytest.raises(DivisionByZeroError):
        Calculator().calculate({"operation": "divide", "left": "5", "right": "0"})


def test_calculator_translates_overflow() -> None:
    with pytest.raises(ArithmeticOverflowError):
        Calculator().calculate({"operation": "multiply", "left": "1e9999", "right": "1e9999"})


def test_calculator_translates_decimal_domain_error() -> None:
    class Invalid(BinaryOperation):
        name = "invalid"

        def execute(self, left: Decimal, right: Decimal) -> Decimal:
            return Decimal("0") / Decimal("0")

    registry = OperationRegistry([Invalid()])
    with pytest.raises(ArithmeticDomainError):
        Calculator(registry).calculate({"operation": "invalid", "left": "1", "right": "2"})


def test_calculator_logs_no_operand_values() -> None:
    operand_value = "987654321.123456789"
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger = logging.getLogger("secure_calculator")
    logger.addHandler(handler)
    try:
        with pytest.raises(ValidationError):
            Calculator().calculate(
                {"operation": "add", "left": operand_value + "!", "right": "1"}
            )
    finally:
        logger.removeHandler(handler)
    assert operand_value not in stream.getvalue()
    assert "invalid_input" in stream.getvalue()


def test_registry_supports_extension() -> None:
    class Maximum(BinaryOperation):
        name = "maximum"

        def execute(self, left: Decimal, right: Decimal) -> Decimal:
            return max(left, right)

    registry = OperationRegistry([Maximum()])
    assert registry.names == ("maximum",)
    assert Calculator(registry).calculate(
        {"operation": "maximum", "left": "4", "right": "9"}
    ) == Decimal("9")


def test_registry_rejects_duplicate_names() -> None:
    operation = Add()
    with pytest.raises(ValueError, match="already registered"):
        OperationRegistry([operation, operation])
