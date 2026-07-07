# ORA Warden

**A fail-closed MCP server for local AI agents. Your agent does the work — you keep the keys.**

ORA Warden sits between your AI agent and your machine and enforces a hard floor:

- 🛑 **Destructive actions are blocked by default** — `rm -rf`, `git reset`, `dd`, `mkfs`, `sudo`, and
  friends are refused. If the broker is unsure, the answer is no.
- 🔒 **Secrets can't be touched** — `.ssh`, `.gnupg`, `.env`, keyrings, and shell rc files are blocked
  from writes, even by you in a hurry.
- 📤 **Egress is locked** — the governed shell can work on your files without reaching the internet, so
  a hijacked tool call can't ship your data off the box.
- ✋ **Risky work waits for you** — anything impactful can be routed to a human approval queue with a
  plain-English summary. Nothing runs until you say yes.
- 🧾 **Everything is audited** — every action lands on a tamper-evident, hash-chained, signed log that
  can only ever grow. A rewrite breaks the chain and gets caught.

It's **local-first** (loopback only, nothing phones home) and works with any MCP client — Claude
Desktop, Cursor, Cline, or Claude Code.

> ORA Warden is the free, open core of [**ORA**](https://ora.3d3d.ca) — the full governed AI operator
> (plain-English control room, business operations, and more) is the paid product.

## What it gives your agent (tools)

| Tool | What it does |
|------|--------------|
| `shell` | Run a shell command through the governed, audited broker (destructive + exfil blocked) |
| `read_file` / `write_file` | Read/write local files, approved-path enforced, secrets blocked, change logged |
| `shell_destructive` | Run a deliberately destructive command — **operator-token gated**, fails closed without it |
| `propose` | Queue an impactful action for human approval instead of doing it |
| `queue` / `proposals_list` / `proposal_get` | Inspect the approval queue |
| `proposal_approve` / `reject` / `execute` | Dispose of a queued proposal — **operator-token gated** |
| `audit_verify` / `audit_sth` / `audit_recent` | Prove the audit log is intact; show recent actions |
| `health` | Confirm the governance layer is up |

## Install

```bash
# 1. the governance broker (the enforcement layer)
#    see INSTALL for the ora-warden-broker binary + a default constitution.

# 2. the MCP server (this package)
uvx ora-warden        # or:  pipx install ora-warden
```

Register it with your MCP client, e.g. Claude Code:

```bash
claude mcp add ora-warden -- uvx ora-warden
```

Or in a Claude Desktop / Cursor MCP config:

```json
{
  "mcpServers": {
    "ora-warden": { "command": "uvx", "args": ["ora-warden"] }
  }
}
```

## Configure (all optional, sensible defaults)

| Env var | Default | Meaning |
|---------|---------|---------|
| `ORA_BROKER_URL` | `http://127.0.0.1:4573` | the governance broker |
| `ORA_OPERATOR_URL` | `http://127.0.0.1:5577` | the approval queue (optional) |
| `ORA_DEFAULT_CWD` | your home directory | default working directory for `shell` |
| `ORA_WARDEN_TOKEN_FILE` | `$XDG_CONFIG_HOME/ora-warden/operator-token.env` | operator token for gated actions |

The operator token gates the human-authorized tools (`shell_destructive`, `proposal_*`). Without it,
those tools **fail closed** — the point is that your agent can't perform them on its own.

## Why

Autonomous coding agents are useful right up until one runs `rm -rf`, leaks a key, or racks up spend
at 2am. ORA Warden is the leash: it can't happen without your yes, and there's a signed record of
everything that did.

Apache-2.0. Built by [3D3D](https://3d3d.ca). Questions: info@3d3d.ca.
