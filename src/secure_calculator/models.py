"""Immutable application data models."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class CalculationRequest:
    """A validated calculation request."""

    operation: str
    left: Decimal
    right: Decimal

