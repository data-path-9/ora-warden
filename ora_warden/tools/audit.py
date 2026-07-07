"""Tamper-evident audit tools (the ORA Warden broker)."""

from .. import client
from . import ora_tool


def register_audit_tools(server):

    @server.tool()
    @ora_tool
    def audit_verify() -> str:
        """Verify the hash-chained audit log is intact (the action log has only ever grown, never
        rewritten). Returns ok + the first broken index if any."""
        status, d = client.broker_get("/audit/verify")
        err = client.blocked_or_error(status, d)
        if err:
            return err
        return client.pretty(d)

    @server.tool()
    @ora_tool
    def audit_sth() -> str:
        """Return the RFC 6962 Signed Tree Head (tree size + ed25519-signed Merkle root) — the
        cryptographic proof of the current audit state."""
        status, d = client.broker_get("/audit/sth")
        err = client.blocked_or_error(status, d)
        if err:
            return err
        return client.pretty(d)

    @server.tool()
    @ora_tool
    def audit_recent(limit: int = 20) -> str:
        """Show the most recent audited actions (the trail of what was actually run).

        Args:
            limit: how many recent entries (default 20).
        """
        status, d = client.broker_get("/audit/recent", params={"limit": int(limit) if limit else 20})
        err = client.blocked_or_error(status, d)
        if err:
            return err
        entries = d if isinstance(d, list) else d.get("entries", d)
        return client.pretty(entries)
