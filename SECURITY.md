# Security Policy

ORA Warden is security-sensitive software. Please report vulnerabilities privately before public
disclosure.

## Reporting a vulnerability

Email `info@3d3d.ca` with:

- affected version or commit;
- platform and client used;
- reproduction steps;
- expected vs actual behavior;
- any logs or tool outputs with secrets redacted.

Do not include real operator tokens, private keys, customer data, or `.env` contents. You should
receive an acknowledgement within 72 hours.

## Security boundaries

- The Python package is a loopback-only MCP bridge.
- Enforcement lives in the separate local `ora-runtime` broker.
- Missing broker, missing operator token, broker block responses, or unsafe endpoint configuration
  must fail closed.
- `403` and `409` responses from the broker are policy blocks, not transient errors to retry around.

## Out of scope

This repository does not contain the paid ORA operator service or business workflow logic.
