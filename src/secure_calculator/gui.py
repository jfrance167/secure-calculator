"""Tkinter desktop interface backed by the secure calculator service."""

import logging
from functools import partial

from secure_calculator.errors import CalculatorError
from secure_calculator.gui_model import MAX_EXPRESSION_CHARACTERS, evaluate_expression
from secure_calculator.logging_config import configure_logging

LOGGER = logging.getLogger("secure_calculator")


def main() -> int:
    """Start the calculator window, returning a nonzero code when Tk is unavailable."""
    configure_logging()
    try:
        import tkinter as tk
        from tkinter import messagebox
    except ImportError:
        LOGGER.error("gui_unavailable")
        print("The Tkinter GUI is not available in this Python installation.")
        return 1

    try:
        window = tk.Tk()
    except tk.TclError:
        LOGGER.error("gui_display_unavailable")
        print("The calculator GUI requires a graphical desktop session.")
        return 1

    window.title("Secure Calculator")
    window.resizable(False, False)
    window.configure(padx=12, pady=12)

    display = tk.StringVar()
    entry = tk.Entry(
        window,
        textvariable=display,
        justify="right",
        font=("Segoe UI", 18),
        width=22,
        relief="sunken",
        borderwidth=3,
    )
    entry.grid(row=0, column=0, columnspan=4, padx=2, pady=(0, 8), ipady=6)
    entry.focus_set()

    def append(value: str) -> None:
        candidate = display.get() + value
        if len(candidate) <= MAX_EXPRESSION_CHARACTERS:
            display.set(candidate)

    def clear() -> None:
        display.set("")

    def calculate() -> None:
        try:
            display.set(evaluate_expression(display.get()))
        except CalculatorError as exc:
            messagebox.showerror("Calculator Error", str(exc), parent=window)
        except Exception:
            LOGGER.error("unexpected_gui_error")
            messagebox.showerror("Calculator Error", "Internal error", parent=window)

    buttons = (
        ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("÷", 1, 3),
        ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("×", 2, 3),
        ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("-", 3, 3),
        ("0", 4, 0), (".", 4, 1), ("%", 4, 2), ("+", 4, 3),
        ("^", 5, 0),
    )
    for label, row, column in buttons:
        tk.Button(
            window,
            text=label,
            width=5,
            height=2,
            font=("Segoe UI", 12),
            command=partial(append, label),
        ).grid(row=row, column=column, padx=2, pady=2)

    tk.Button(window, text="Clear", command=clear, height=2).grid(
        row=5, column=1, columnspan=2, padx=2, pady=2, sticky="nsew"
    )
    tk.Button(window, text="=", command=calculate, height=2).grid(
        row=5, column=3, padx=2, pady=2, sticky="nsew"
    )
    window.bind("<Return>", lambda _event: calculate())
    window.bind("<Escape>", lambda _event: clear())
    window.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
