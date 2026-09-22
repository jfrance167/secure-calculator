"""Application service coordinating validation and arithmetic."""

import logging
from collections.abc import Mapping
from decimal import (
    Decimal,
    DecimalException,
    DivisionByZero,
    InvalidOperation,
    Overflow,
    Underflow,
    localcontext,
)
from typing import Any

from secure_calculator.errors import (
    ArithmeticDomainError,
    ArithmeticOverflowError,
    CalculatorError,
    DivisionByZeroError,
)
from secure_calculator.operations import default_operations
from secure_calculator.registry import OperationRegistry
from secure_calculator.validation import ARITHMETIC_PRECISION, parse_request

LOGGER = logging.getLogger("secure_calculator")


class Calculator:
    """Secure calculator facade suitable for CLI or application integration."""

    def __init__(self, registry: OperationRegistry | None = None) -> None:
        self.registry = registry or OperationRegistry(default_operations())

    def calculate(self, payload: Mapping[str, Any]) -> Decimal:
        """Validate and execute a request with bounded decimal arithmetic."""
        try:
            request = parse_request(payload)
            operation = self.registry.get(request.operation)
            with localcontext() as context:
                context.prec = ARITHMETIC_PRECISION
                context.Emax = 9_999
                context.Emin = -9_999
                context.traps[Overflow] = True
                context.traps[Underflow] = True
                context.traps[DivisionByZero] = True
                context.traps[InvalidOperation] = True
                result = operation.execute(request.left, request.right)
            if not result.is_finite():
                raise ArithmeticOverflowError("result is outside the supported range")
            return result
        except CalculatorError as exc:
            LOGGER.warning("calculation_rejected code=%s", exc.code)
            raise
        except (Overflow, Underflow) as exc:
            LOGGER.warning("calculation_rejected code=arithmetic_overflow")
            raise ArithmeticOverflowError("result is outside the supported range") from exc
        except DivisionByZero as exc:
            LOGGER.warning("calculation_rejected code=division_by_zero")
            raise DivisionByZeroError("division by zero is undefined") from exc
        except (InvalidOperation, DecimalException) as exc:
            LOGGER.warning("calculation_rejected code=arithmetic_domain")
            raise ArithmeticDomainError("operands are invalid for this operation") from exc
