# PowerSniffer Dashboard

Dashboard for **PowerSniffer** — a hardware device for real-time voltage and current monitoring.

## Stack

* Python
* uv
* FastAPI
* pytest
* Ruff

## Structure

```text
powersniffer-dashboard/
├── pyproject.toml
├── uv.lock
├── README.md
├── src/
│   └── powersniffer/
│       ├── __init__.py
│       └── main.py
└── tests/
```

## Development

Install dependencies:

```bash
uv sync
```

Run:

```bash
uv run python -m powersniffer.main
```

Tests:

```bash
uv run pytest
```

Lint:

```bash
uv run ruff check .
```

## Status

Work in progress.
