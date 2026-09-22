"""Display-expression adapter for the graphical calculator."""

import re

from secure_calculator.errors import ValidationError
from secure_calculator.presentation import format_decimal
from secure_calculator.service import Calculator

_NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
_EXPRESSION = re.compile(
    rf"\A\s*(?P<left>{_NUMBER})\s*(?P<operator>[+\-×÷*/%^])\s*"
    rf"(?P<right>{_NUMBER})\s*\Z",
    re.ASCII,
)
_OPERATIONS = {
    "+": "add",
    "-": "subtract",
    "×": "multiply",
    "*": "multiply",
    "÷": "divide",
    "/": "divide",
    "%": "modulo",
    "^": "power",
}
MAX_EXPRESSION_CHARACTERS = 160


def evaluate_expression(expression: str, calculator: Calculator | None = None) -> str:
    """Evaluate one strictly parsed binary expression without using ``eval``."""
    if not isinstance(expression, str) or len(expression) > MAX_EXPRESSION_CHARACTERS:
        raise ValidationError("expression is too long")
    match = _EXPRESSION.fullmatch(expression)
    if match is None:
        raise ValidationError("enter two numbers separated by one operation")

    service = calculator or Calculator()
    result = service.calculate(
        {
            "operation": _OPERATIONS[match.group("operator")],
            "left": match.group("left"),
            "right": match.group("right"),
        }
    )
    return format_decimal(result)
