# Contributing

Thanks for helping harden ORA Warden. This project is a fail-closed local MCP bridge, so changes
should be small, testable, and conservative.

## Local setup

```bash
python3 -m venv .venv
./.venv/bin/pip install -e '.[test]'
./.venv/bin/pytest
./.venv/bin/python -m build
```

## Rules for changes

- Do not weaken destructive-command blocks, secret-path blocks, egress controls, audit behavior, or
  operator-token gates.
- Keep bridge HTTP calls loopback-only and centralized in `ora_warden/client.py`.
- Do not add telemetry, analytics, hosted callbacks, or off-box network calls.
- Do not log, echo, serialize, or return the operator token.
- Keep the paid ORA operator out of this repo; this package is the free core only.
- Update tests and docs when tool names, config variables, or packaging behavior changes.

## Verification

Before opening a PR, run:

```bash
./.venv/bin/pytest
./.venv/bin/python -m build
```

For user-facing MCP behavior, also run a client `list_tools` smoke test or use one of the examples
in `examples/`.
