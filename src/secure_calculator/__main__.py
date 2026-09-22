"""Allow execution with ``python -m secure_calculator``."""

from secure_calculator.cli import main

if __name__ == "__main__":
    raise SystemExit(main())

