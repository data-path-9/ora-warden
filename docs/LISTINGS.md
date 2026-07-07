# ORA Warden — marketplace listing packs

Everything needed to list ORA Warden across the MCP ecosystem. **Nothing here is submitted yet** —
this is the prep. Submission is a paired session: Randall logs in / creates the accounts, Claude
drives the forms, Randall approves each submit (his explicit yes, per item). Claude never enters
passwords or creates accounts.

All listings point to the hub: **https://ora.3d3d.ca**. Contact: **info@3d3d.ca**. Public author
name: **Randall Marshall / 3D3D**.

---

## Canonical copy (reuse verbatim across channels — keep it consistent)

**Name:** ORA Warden

**One-liner (≤100 chars):**
> A fail-closed MCP server: your AI agent can't delete, spend, or exfiltrate without your yes.

**Short description (≤300 chars):**
> ORA Warden gives any AI agent a governed shell, file access, human approval queue, and
> tamper-evident audit log. Destructive commands, secret files, and network exfiltration are blocked
> by default. Local-first, loopback only. Works with Claude Desktop, Cursor, Cline, Claude Code.

**Long description:** use the README intro + the tools table.

**Tags / keywords:** `mcp`, `security`, `governance`, `guardrails`, `agent-security`, `audit`,
`fail-closed`, `human-in-the-loop`, `sandbox`, `local-first`

**Category:** Security / Developer Tools

**Links:** Homepage `https://ora.3d3d.ca` · Repo `https://github.com/3d3dcanada/ora-warden` ·
License `Apache-2.0`

**Demo hook (lead image/clip everywhere):** the clip of Warden freezing an agent's `rm -rf` mid-run
and logging it — "the agent tried; the Warden said no." (produce from the clean-room transcript /
WO-14 demo assets).

---

## 1. Official MCP Registry — registry.modelcontextprotocol.io  ★ do this first
The canonical, upstream directory. Many other marketplaces auto-index from it, so publishing here
seeds the rest. Free.

- **Account:** GitHub (namespace `io.github.3d3dcanada` must match the repo owner — verify the repo
  lives under a `3d3dcanada` GitHub org/user, or change `server.json`'s `name` to the real owner).
- **Mechanism:** the `mcp-publisher` CLI + the repo's `server.json` (already written). CLI-based, no
  web form.
- **Prereq:** the package must be published to PyPI first (see §6), because `server.json` references
  the `pypi` package `ora-warden`.
- **Steps (paired):**
  1. `curl -fsSL https://github.com/modelcontextprotocol/registry/releases/latest/download/mcp-publisher_linux_amd64.tar.gz | tar xz` (or install per current docs).
  2. `./mcp-publisher login github` → completes GitHub device-auth in Randall's browser.
  3. From `~/ora-warden`: `./mcp-publisher publish` (reads `server.json`). Randall's explicit yes.
  4. Confirm it resolves at the registry API.
- **Validate first:** `server.json` against the published schema before submit.

## 2. PyPI — pypi.org  (prerequisite for §1 and for `uvx`/`pipx`)
Not a marketplace, but the package host `uvx ora-warden` pulls from.
- **Account:** PyPI account + API token.
- **Steps (paired):** `python -m build` → `twine upload dist/*` with Randall's token. Verify
  `uvx ora-warden` works from a clean machine.

## 3. Smithery — smithery.ai
Largest discovery marketplace (~7k servers), Docker-Hub-style; can run servers on their infra.
- **Account:** GitHub sign-in.
- **Mechanism:** connect the GitHub repo; Smithery reads a `smithery.yaml` / the server metadata.
  The repo includes a local-stdio `smithery.yaml` descriptor. Note in the listing that Warden needs
  its local broker running — it is not a pure hosted server. Current Smithery local stdio
  distribution should use an MCPB bundle where required by the platform.
- **Steps (paired):** sign in → "Add server" → point at the repo → fill category/description from
  the canonical copy → submit.

## 4. mcp.so
High-traffic community directory.
- **Account:** GitHub sign-in.
- **Mechanism:** "Submit" form (name, repo URL, description, tags) — often auto-pulls from GitHub /
  the Official Registry.
- **Steps (paired):** Submit form with canonical copy + repo URL.

## 5. PulseMCP — pulsemcp.com
Curated, editorial directory with a weekly newsletter (good for launch visibility).
- **Account:** submission form (email); may not need an account.
- **Steps (paired):** use their "Submit a server" form with canonical copy + repo + homepage. Flag
  the "security / guardrails" angle for the newsletter.

## 6. MCPMarket / MCPize
Directories that also support paid listings; for us they're free distribution + a "purchase"
funnel to ora.3d3d.ca (we do NOT meter tool calls — the paid product is the full ORA operator).
- **Account:** email/GitHub sign-in.
- **Steps (paired):** submit with canonical copy; set the CTA/link to `https://ora.3d3d.ca`, not a
  per-call price.

---

## Pre-submission checklist (do before the paired session)
- [ ] Decide the GitHub owner (`3d3dcanada`?) and create the **public** `ora-warden` repo; push.
- [ ] Confirm `server.json` `name` namespace matches that owner.
- [ ] Publish `ora-warden` to **PyPI** (§2) and verify `uvx ora-warden` on a clean machine.
- [ ] Ship a real **broker binary** (release artifact) or clear build-from-source install, so a
      stranger can actually run the enforcement layer (see INSTALL / WO-18).
- [ ] Produce the **demo clip** (agent's `rm -rf` frozen + logged).
- [x] Add **`smithery.yaml`** for §3.
- [x] Validate `server.json` against the current registry schema.

## What Claude will NOT do (Randall does these)
Create accounts · enter passwords/tokens · click the final "submit/publish" without Randall's
per-item yes. Claude prepares, validates, drafts every field, and drives the browser to the point of
submission.
