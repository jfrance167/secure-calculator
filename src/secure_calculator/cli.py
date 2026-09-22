"""Command-line interface with predictable output and exit codes."""

import argparse
import json
import logging
from collections.abc import Sequence

from secure_calculator.errors import CalculatorError
from secure_calculator.logging_config import configure_logging
from secure_calculator.operations import default_operations
from secure_calculator.presentation import format_decimal as _format_decimal
from secure_calculator.service import Calculator

LOGGER = logging.getLogger("secure_calculator")


def build_parser() -> argparse.ArgumentParser:
    operations = sorted(operation.name for operation in default_operations())
    parser = argparse.ArgumentParser(
        prog="secure-calculator",
        description="Perform bounded decimal arithmetic without evaluating expressions.",
    )
    parser.add_argument("operation", choices=operations)
    parser.add_argument("left", help="left decimal operand")
    parser.add_argument("right", help="right decimal operand")
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="return a JSON response",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    configure_logging()
    args = build_parser().parse_args(argv)
    payload = {"operation": args.operation, "left": args.left, "right": args.right}
    try:
        result = _format_decimal(Calculator().calculate(payload))
    except CalculatorError as exc:
        if args.as_json:
            print(json.dumps({"error": {"code": exc.code, "message": str(exc)}}))
        else:
            print(f"Error [{exc.code}]: {exc}")
        return exc.exit_code
    except Exception:
        # Exception text can contain request data. Record a generic event only.
        LOGGER.error("unexpected_application_error")
        if args.as_json:
            print(json.dumps({"error": {"code": "internal_error", "message": "internal error"}}))
        else:
            print("Error [internal_error]: internal error")
        return 1

    if args.as_json:
        print(json.dumps({"result": result}))
    else:
        print(result)
    return 0
