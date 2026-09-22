"""Operation registration and lookup."""

from collections.abc import Iterable

from secure_calculator.errors import UnsupportedOperationError
from secure_calculator.operations import BinaryOperation


class OperationRegistry:
    """A small registry that makes calculator operations replaceable and extensible."""

    def __init__(self, operations: Iterable[BinaryOperation] = ()) -> None:
        self._operations: dict[str, BinaryOperation] = {}
        for operation in operations:
            self.register(operation)

    def register(self, operation: BinaryOperation) -> None:
        """Register an operation, rejecting ambiguous duplicate names."""
        name = operation.name
        if name in self._operations:
            raise ValueError(f"operation already registered: {name}")
        self._operations[name] = operation

    def get(self, name: str) -> BinaryOperation:
        """Find an operation by its validated name."""
        try:
            return self._operations[name]
        except KeyError as exc:
            raise UnsupportedOperationError(f"unsupported operation: {name}") from exc

    @property
    def names(self) -> tuple[str, ...]:
        """Return operation names in stable sorted order."""
        return tuple(sorted(self._operations))

