# AGENTS.md — ora-warden

Guidance for AI coding agents working in this repo.

## What this is
`ora-warden` is the free, open (Apache-2.0) core of [ORA](https://ora.3d3d.ca): a stdio **MCP
server** that gives any AI agent a *governed* shell + file layer, a human approval queue, and a
tamper-evident audit log. It is a thin, loopback-only bridge — the actual enforcement lives in a
local **broker** (the `ora-runtime` binary) that this server calls over HTTP.

## Stack + layout
- Python ≥3.10, `FastMCP` (the `mcp` package) over stdio, `httpx` for the bridge. No async in tools.
- `ora_warden/server.py` — `FastMCP("ora-warden")`; registers the tool modules.
- `ora_warden/config.py` — env/XDG config + operator-token loader (env-only, never logged).
- `ora_warden/client.py` — the ONLY place that opens HTTP; governance-aware error mapping (403/409 → BLOCKED).
- `ora_warden/tools/{exec,queue,audit,status}.py` — one module per surface; `@server.tool()` + `@ora_tool`.
- `scripts/ora-warden-broker` — portable launcher for the enforcement broker.
- `server.json` / `smithery.yaml` — marketplace manifests. `docs/LISTINGS.md` — listing packs.

## Build / run / test
- Install: `python -m venv .venv && ./.venv/bin/pip install -e .`
- Run the MCP server: `ora-warden` (stdio) — or register with a client: `claude mcp add ora-warden -- uvx ora-warden`.
- Smoke test: connect an MCP client and `list_tools()` — expect the 15 governance-core tools.
- The broker must be running for the tools to do anything (`scripts/ora-warden-broker`).

## Hard rules
- **Never weaken the floors.** Destructive-block, sensitive-path block, egress lock, and the audit
  chain are the product. A 403/409 from the broker is a BLOCK — surface it, never retry around it.
- Gated tools (`shell_destructive`, `proposal_approve`/`reject`/`execute`) require the operator token
  and must fail closed without it. The agent proposes; the human disposes.
- Loopback only. Never add external network calls. Never log or echo the operator token.
- Keep the shipped package free of machine-specific paths and personal data (it's public).
- This repo is the FREE core only. Do not add the paid ORA operator's business logic here.
