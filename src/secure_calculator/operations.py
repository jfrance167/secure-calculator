"""Arithmetic operation implementations."""

from abc import ABC, abstractmethod
from decimal import Decimal

from secure_calculator.errors import ArithmeticDomainError, DivisionByZeroError

MAX_ABSOLUTE_EXPONENT = 10_000


class BinaryOperation(ABC):
    """Extension point for a named binary operation."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique operation name."""

    @abstractmethod
    def execute(self, left: Decimal, right: Decimal) -> Decimal:
        """Apply the operation to two validated operands."""


class Add(BinaryOperation):
    name = "add"

    def execute(self, left: Decimal, right: Decimal) -> Decimal:
        return left + right


class Subtract(BinaryOperation):
    name = "subtract"

    def execute(self, left: Decimal, right: Decimal) -> Decimal:
        return left - right


class Multiply(BinaryOperation):
    name = "multiply"

    def execute(self, left: Decimal, right: Decimal) -> Decimal:
        return left * right


class Divide(BinaryOperation):
    name = "divide"

    def execute(self, left: Decimal, right: Decimal) -> Decimal:
        if right.is_zero():
            raise DivisionByZeroError("division by zero is undefined")
        return left / right


class Modulo(BinaryOperation):
    name = "modulo"

    def execute(self, left: Decimal, right: Decimal) -> Decimal:
        if right.is_zero():
            raise DivisionByZeroError("modulo by zero is undefined")
        return left % right


class Power(BinaryOperation):
    name = "power"

    def execute(self, left: Decimal, right: Decimal) -> Decimal:
        if right != right.to_integral_value():
            raise ArithmeticDomainError("the exponent must be an integer")
        if abs(right) > MAX_ABSOLUTE_EXPONENT:
            raise ArithmeticDomainError("the exponent exceeds the configured limit")
        if left.is_zero() and right < 0:
            raise DivisionByZeroError("zero cannot be raised to a negative exponent")
        return left**int(right)


def default_operations() -> tuple[BinaryOperation, ...]:
    """Return fresh instances of all built-in operations."""
    return (Add(), Subtract(), Multiply(), Divide(), Modulo(), Power())

