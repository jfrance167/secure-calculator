# Secure Calculator

A production-oriented Python calculator with command-line, interactive-menu, and optional
Tkinter desktop interfaces, built around strict input validation,
bounded decimal arithmetic, typed extension points, structured errors, privacy-conscious
logging, automated tests, and a non-root container image.

The application deliberately does **not** accept free-form expressions and never calls
`eval`, `exec`, or a shell. A calculation consists of one allowlisted operation and exactly
two decimal operands.

## Directory structure

```text
secure-calculator/
├── .github/dependabot.yml
├── .github/workflows/test.yml
├── src/secure_calculator/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── errors.py
│   ├── gui.py
│   ├── gui_model.py
│   ├── interactive.py
│   ├── logging_config.py
│   ├── models.py
│   ├── operations.py
│   ├── presentation.py
│   ├── py.typed
│   ├── registry.py
│   ├── service.py
│   └── validation.py
├── tests/
│   ├── test_cli.py
│   ├── test_gui_model.py
│   ├── test_interactive.py
│   ├── test_operations.py
│   ├── test_security_properties.py
│   ├── test_service.py
│   └── test_validation.py
├── .dockerignore
├── .gitignore
├── Dockerfile
├── LICENSE
├── compose.yaml
├── pyproject.toml
├── README.md
└── SECURITY.md
```

## Features and security controls

- Addition, subtraction, multiplication, division, modulo, and integer exponentiation.
- Exact decimal inputs with a documented 34-significant-digit operand limit and a
  68-digit arithmetic context, sufficient for exact multiplication of two accepted operands.
- Binary floating-point values are rejected by the library API; callers must pass strings,
  integers, or `Decimal` instances.
- Exact request schema and allowlisted numeric grammar; non-finite values and unexpected
  fields are rejected.
- Resource-abuse limits on input length, significant digits, and exponentiation.
- Stable domain exceptions and CLI exit codes instead of raw tracebacks.
- JSON logs contain event/error codes, never operand values or complete payloads.
- Pluggable `BinaryOperation` registry for adding operations without changing the service.
- Test, lint, type-check, coverage, and container smoke-test jobs in GitHub Actions.

## Prerequisites

- Python 3.11 or newer
- `pip`
- Docker 24+ (optional)

## Local setup

```bash
python -m venv .venv
```

Activate the environment:

```bash
# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install the package and development tools:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Usage

### Interactive menu

For a beginner-friendly numbered menu similar to a traditional classroom calculator:

```bash
secure-calculator-menu
```

Choose an operation, enter two numbers, and continue calculating until you select `Q`.

### Desktop interface

Launch the button-based Tkinter calculator:

```bash
secure-calculator-gui
```

Enter one operation at a time, such as `0.1 + 0.2`, by using the buttons or keyboard and
press `=` or Enter. The GUI strictly parses the expression and delegates to the same secure
calculator service; it never uses Python's `eval` or executes arbitrary input. Tkinter is
included with standard Windows and macOS Python installations, while some Linux distributions
provide it as a separate system package.

### Direct command

```bash
secure-calculator add 12.5 7.5
# 20

secure-calculator power 2 10 --json
# {"result": "1024"}

python -m secure_calculator divide 10 4
# 2.5
```

Invalid input returns exit code `2` and a stable error code:

```bash
secure-calculator divide 10 0 --json
# {"error": {"code": "division_by_zero", "message": "division by zero is undefined"}}
```

### Arithmetic semantics

- Modulo uses the General Decimal Arithmetic convention: the remainder has the sign of the
  dividend. Consequently, `modulo -7 3` returns `-1`, unlike Python integer `-7 % 3`.
- `0` raised to the power `0` is undefined under the decimal arithmetic specification and
  returns the `arithmetic_domain` error rather than `1`.
- Results that would require more than 256 characters in ordinary fixed-point notation are
  emitted in scientific notation. For example, `1E-9999` remains `1E-9999` rather than
  expanding into a roughly 10,000-character line.

### Library API

```python
from secure_calculator import Calculator

result = Calculator().calculate(
    {"operation": "multiply", "left": "6.25", "right": "4"}
)
print(result)  # Decimal('25.00')
```

To add an operation, implement `BinaryOperation`, register it in an `OperationRegistry`,
and inject the registry into `Calculator`. Keep operation names lowercase and compatible
with the validator (`[a-z][a-z0-9_]{0,31}`).

## Quality checks

```bash
ruff check .
mypy
pytest
```

The test configuration enforces at least 95% branch coverage. CI performs these checks on
Python 3.11 and 3.12 for every push and pull request.

## Container

Build and run the multi-stage, non-root image:

```bash
docker build -t secure-calculator:1.0.0 .
docker run --rm secure-calculator:1.0.0 modulo 17 5
# 2
```

For a locally hardened one-shot deployment with no network, a read-only filesystem,
dropped capabilities, a fixed non-root identity, and CPU/memory/process limits:

```bash
docker compose run --rm calculator add 20 22
# 42
```

For reproducible releases, pin the Python base image by digest through your dependency
update process and publish images by immutable digest.

## Operational behavior

- Normal result: exit code `0`.
- Validation/domain error: exit code `2`.
- Unexpected internal failure: exit code `1`, generic client message, detailed server-side
  exception log.
- Logs are written to standard error as one JSON object per line for collection by the
  container runtime or observability platform.

Do not pass secrets as operands. Although operand values are intentionally excluded from
application logs, command-line arguments may be visible to operating-system process tools.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
