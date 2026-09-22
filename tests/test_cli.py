import json
import logging

import pytest

from secure_calculator.cli import _format_decimal, build_parser, main
from secure_calculator.logging_config import JsonFormatter, configure_logging


def test_cli_prints_result(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["multiply", "2.5", "4"]) == 0
    assert capsys.readouterr().out.strip() == "10"


def test_cli_json_success(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["add", "1", "2", "--json"]) == 0
    assert json.loads(capsys.readouterr().out) == {"result": "3"}


def test_cli_json_error(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["divide", "1", "0", "--json"]) == 2
    body = json.loads(capsys.readouterr().out)
    assert body["error"]["code"] == "division_by_zero"


def test_cli_text_error(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["add", "not-a-number", "2"]) == 2
    assert "invalid_input" in capsys.readouterr().out


def test_cli_handles_unexpected_errors(monkeypatch, capsys: pytest.CaptureFixture[str]) -> None:
    def fail(_self, _payload):
        raise RuntimeError("secret details")

    monkeypatch.setattr("secure_calculator.cli.Calculator.calculate", fail)
    assert main(["add", "1", "2", "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["error"] == {
        "code": "internal_error",
        "message": "internal error",
    }


def test_parser_rejects_unknown_operation() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args(["unknown", "1", "2"])


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("0.000", "0"), ("1.2300", "1.23"), ("-2", "-2")],
)
def test_decimal_formatting(raw: str, expected: str) -> None:
    from decimal import Decimal

    assert _format_decimal(Decimal(raw)) == expected


def test_json_formatter_uses_allowlisted_fields() -> None:
    record = logging.LogRecord("test", logging.WARNING, __file__, 1, "safe", (), None)
    record.sensitive_value = "must-not-appear"
    output = json.loads(JsonFormatter().format(record))
    assert output["message"] == "safe"
    assert "sensitive_value" not in output


def test_configure_logging_is_idempotent() -> None:
    logger = logging.getLogger("secure_calculator")
    original_handlers = logger.handlers[:]
    logger.handlers.clear()
    try:
        configure_logging()
        configure_logging()
        assert len(logger.handlers) == 1
    finally:
        logger.handlers[:] = original_handlers

