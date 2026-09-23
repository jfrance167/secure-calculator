# Security Policy

## Supported version

Only the latest commit on `main` is maintained.

## Intended use

This project demonstrates defensive input validation and bounded arithmetic. It
is not a replacement for independently reviewed financial, safety-critical, or
high-assurance calculation software.

## Reporting a security issue

Use GitHub private vulnerability reporting when available. Include the affected
version, reproduction steps, impact, and a suggested mitigation if available.
Do not publish exploit details, credentials, tokens, or private data in a public
issue.

## Maintainer checks

Before publishing a change, run `ruff check .`, `mypy`, and `pytest`. Confirm
that Bandit, CodeQL, and the container smoke test succeed in GitHub Actions.
