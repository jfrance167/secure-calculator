"""Shared presentation helpers for calculator front ends."""

from decimal import Decimal

MAX_PLAIN_OUTPUT_CHARACTERS = 256


def format_scientific(value: Decimal) -> str:
    """Render a decimal in compact scientific notation."""
    mantissa, exponent = format(value, "E").split("E", maxsplit=1)
    if "." in mantissa:
        mantissa = mantissa.rstrip("0").rstrip(".")
    return f"{mantissa}E{int(exponent):+d}"


def format_decimal(value: Decimal) -> str:
    """Render a decimal without producing an excessively long output string."""
    if value.is_zero():
        return "0"
    if abs(value.adjusted()) >= MAX_PLAIN_OUTPUT_CHARACTERS:
        return format_scientific(value)
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    if len(rendered) > MAX_PLAIN_OUTPUT_CHARACTERS:
        return format_scientific(value)
    return rendered
