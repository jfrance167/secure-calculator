"""Beginner-friendly interactive terminal interface."""

import logging
from collections.abc import Callable

from secure_calculator.errors import CalculatorError
from secure_calculator.logging_config import configure_logging
from secure_calculator.presentation import format_decimal
from secure_calculator.service import Calculator

InputFunction = Callable[[str], str]
OutputFunction = Callable[[str], None]
LOGGER = logging.getLogger("secure_calculator")

MENU = """Secure Calculator
1. Add
2. Subtract
3. Multiply
4. Divide
5. Modulo
6. Power
Q. Quit"""

CHOICES = {
    "1": ("add", "+"),
    "2": ("subtract", "-"),
    "3": ("multiply", "×"),
    "4": ("divide", "÷"),
    "5": ("modulo", "%"),
    "6": ("power", "^"),
}


def run_menu(
    input_fn: InputFunction = input,
    output_fn: OutputFunction = print,
    calculator: Calculator | None = None,
) -> int:
    """Run calculations until the user chooses to quit or closes input."""
    service = calculator or Calculator()
    while True:
        output_fn(MENU)
        try:
            choice = input_fn("Select operation (1-6 or Q): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            output_fn("Goodbye.")
            return 0

        if choice == "q":
            output_fn("Goodbye.")
            return 0
        if choice not in CHOICES:
            output_fn("Invalid selection. Choose 1-6 or Q.")
            continue

        operation, symbol = CHOICES[choice]
        try:
            left = input_fn("Enter first number: ")
            right = input_fn("Enter second number: ")
            result = service.calculate(
                {"operation": operation, "left": left, "right": right}
            )
        except CalculatorError as exc:
            output_fn(f"Error [{exc.code}]: {exc}")
        except (EOFError, KeyboardInterrupt):
            output_fn("Calculation cancelled.")
            return 0
        except Exception:
            LOGGER.error("unexpected_interactive_error")
            output_fn("Error [internal_error]: internal error")
        else:
            output_fn(f"{left.strip()} {symbol} {right.strip()} = {format_decimal(result)}")


def main() -> int:
    """Configure logging and start the interactive menu."""
    configure_logging()
    return run_menu()


if __name__ == "__main__":
    raise SystemExit(main())
