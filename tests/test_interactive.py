from collections.abc import Callable, Iterator

from secure_calculator.interactive import run_menu


def _input_from(values: Iterator[str]) -> Callable[[str], str]:
    def read(_prompt: str) -> str:
        try:
            return next(values)
        except StopIteration as exc:
            raise EOFError from exc

    return read


def test_menu_calculates_and_quits() -> None:
    output: list[str] = []
    values = iter(["1", "0.1", "0.2", "q"])

    assert run_menu(_input_from(values), output.append) == 0

    assert "0.1 + 0.2 = 0.3" in output
    assert output[-1] == "Goodbye."


def test_menu_recovers_from_invalid_selection_and_calculation() -> None:
    output: list[str] = []
    values = iter(["invalid", "4", "5", "0", "q"])

    assert run_menu(_input_from(values), output.append) == 0

    assert "Invalid selection. Choose 1-6 or Q." in output
    assert any("division_by_zero" in line for line in output)


def test_menu_handles_closed_input() -> None:
    output: list[str] = []

    def closed(_prompt: str) -> str:
        raise EOFError

    assert run_menu(closed, output.append) == 0
    assert output[-1] == "Goodbye."


def test_menu_handles_input_closed_during_operands() -> None:
    output: list[str] = []
    values = iter(["1"])

    assert run_menu(_input_from(values), output.append) == 0
    assert output[-1] == "Calculation cancelled."


def test_menu_hides_unexpected_error_details() -> None:
    output: list[str] = []
    values = iter(["1", "1", "2", "q"])

    class FailingCalculator:
        def calculate(self, _payload):
            raise RuntimeError("sensitive detail")

    assert (
        run_menu(
            _input_from(values), output.append, FailingCalculator()  # type: ignore[arg-type]
        )
        == 0
    )
    assert "Error [internal_error]: internal error" in output
    assert all("sensitive detail" not in line for line in output)
