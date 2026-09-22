"""Secure calculator public API."""

from secure_calculator.errors import CalculatorError
from secure_calculator.service import Calculator

__all__ = ["Calculator", "CalculatorError"]
__version__ = "1.0.0"

