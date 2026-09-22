"""Domain exceptions with stable, machine-readable error codes."""


class CalculatorError(Exception):
    """Base class for errors that are safe to display to a user."""

    code = "calculator_error"
    exit_code = 2


class ValidationError(CalculatorError):
    """Input failed structural or lexical validation."""

    code = "invalid_input"


class UnsupportedOperationError(CalculatorError):
    """The requested operation is not registered."""

    code = "unsupported_operation"


class DivisionByZeroError(CalculatorError):
    """Division or modulo by zero was requested."""

    code = "division_by_zero"


class ArithmeticOverflowError(CalculatorError):
    """The result exceeded the configured numeric range."""

    code = "arithmetic_overflow"


class ArithmeticDomainError(CalculatorError):
    """Operands are outside the supported domain of an operation."""

    code = "arithmetic_domain"

