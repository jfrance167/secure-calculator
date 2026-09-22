from decimal import Decimal

import pytest

from secure_calculator.errors import DivisionByZeroError, ValidationError
from secure_calculator.gui_model import MAX_EXPRESSION_CHARACTERS, evaluate_expression


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("0.1 + 0.2", "0.3"),
        ("7-10", "-3"),
        ("-2 × -3", "6"),
        ("10 / 4", "2.5"),
        ("17%5", "2"),
        ("2^10", "1024"),
        ("1e2*3", "300"),
    ],
)
def test_evaluate_expression(expression: str, expected: str) -> None:
    assert evaluate_expression(expression) == expected


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os').system('whoami')",
        "1 + 2 + 3",
        "1; DROP TABLE calculations",
        "$(whoami)",
        "NaN + 1",
        "1 // 2",
        "１ + ２",
        "",
    ],
)
def test_evaluate_expression_rejects_malformed_or_malicious_input(expression: str) -> None:
    with pytest.raises(ValidationError):
        evaluate_expression(expression)


def test_evaluate_expression_rejects_oversized_input() -> None:
    with pytest.raises(ValidationError, match="too long"):
        evaluate_expression("1" * (MAX_EXPRESSION_CHARACTERS + 1))


def test_evaluate_expression_rejects_non_string() -> None:
    with pytest.raises(ValidationError):
        evaluate_expression(b"1+2")  # type: ignore[arg-type]


def test_evaluate_expression_preserves_domain_errors() -> None:
    with pytest.raises(DivisionByZeroError):
        evaluate_expression("10 ÷ 0")


def test_evaluate_expression_accepts_injected_calculator() -> None:
    class StubCalculator:
        def calculate(self, _payload):
            return Decimal("42")

    assert evaluate_expression("1+1", StubCalculator()) == "42"  # type: ignore[arg-type]
