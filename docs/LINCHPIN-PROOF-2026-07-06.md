# ORA Warden — linchpin proof (2026-07-06)

A real MCP client (Python `mcp` SDK stdio client, the same protocol Claude Desktop / Cursor / Cline
use) connected to the `ora-warden` stdio server, which bridged to a **portable broker run as a fresh
user** (`HOME=/tmp/wtest`, `ORA_RUNTIME_ROOT=/tmp/wtest/runtime`, spare port 4599 — a home the
broker was never built with). Every governed behavior held:

| # | Action | Result |
|---|--------|--------|
| 1 | `health` | broker up, approval queue up |
| 2 | `shell` echo | ✅ works, exit 0, audited |
| 3 | `write_file` /tmp/wtest/deliverable.txt | ✅ works, audited |
| 4 | `read_file` back | ✅ "built by the agent" |
| 5 | `shell` `rm -rf …` | 🛑 BLOCKED (destructive) |
| 6 | `write_file` `~/.ssh/authorized_keys` | 🔒 BLOCKED ("path is not approved for write") |
| 7 | `shell_destructive` (no token) | ✋ fails closed ("operator token not loaded") |
| 8 | `audit_recent` | 🧾 hash-chained entries (record_hash/prev_hash) |
| 9 | `audit_verify` | ✅ `ok: true`, `first_broken_index: null`, checked 5 |

**What this proves:** the product works — an external MCP client gets the governed, fail-closed,
audited surface, and the broker enforces correctly under a non-default home with no personal config.

**Residual (for a real install):** this ran as the same OS user with a fresh `$HOME`, not a
separate system account. The enforcement logic is fully exercised; a separate-UID install test
(needs `useradd`, i.e. sudo) is the one remaining box to tick during packaging.
