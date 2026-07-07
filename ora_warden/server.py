"""ORA Warden — a fail-closed MCP server for local AI agents.

FastMCP over stdio. Presents a governed shell + file layer, a human approval queue, and a
tamper-evident audit log to any MCP client (Claude Desktop, Cursor, Cline, Claude Code). Every
state-changing action is audited and fail-closed; destructive/exfiltrating actions are blocked
unless the operator explicitly authorizes them. Loopback only — nothing leaves the box.
"""

from mcp.server.fastmcp import FastMCP

from .tools.exec import register_exec_tools
from .tools.queue import register_queue_tools
from .tools.audit import register_audit_tools
from .tools.status import register_status_tools

server = FastMCP(
    "ora-warden",
    instructions=(
        "ORA Warden is a local, loopback-only GOVERNED tool layer for AI agents. Prefer these tools "
        "over any raw shell for anything that changes state: `shell` and `write_file` are audited and "
        "fail-closed — they BLOCK destructive commands (rm -rf, git reset, dd, sudo, ...), secret files "
        "(.ssh, .env, keyrings), and network exfiltration. Use `propose` to queue anything that should "
        "be reviewed before it runs (deliverables, outreach, external sends, deploys, spends) for the "
        "operator's approval — nothing impactful happens without their yes. Use `audit_verify` / "
        "`audit_recent` to show the tamper-evident action log, and `health` to confirm the governance "
        "layer is up. NEVER call `shell_destructive` or `proposal_approve` / `proposal_reject` / "
        "`proposal_execute` unless the operator explicitly tells you to."
    ),
)

register_exec_tools(server)
register_queue_tools(server)
register_audit_tools(server)
register_status_tools(server)


def main():
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
