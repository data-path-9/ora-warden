"""System status tool — liveness of the governance layer."""

from .. import client
from . import ora_tool


def register_status_tools(server):

    @server.tool()
    @ora_tool
    def health() -> str:
        """Liveness of the ORA Warden governance layer: the broker (shell/file/audit) and, if you run
        it, the approval queue. Use this to confirm the governance layer is up before relying on the
        other tools."""
        out = {}
        for name, getter in (("broker", client.broker_get), ("approval_queue", client.operator_get)):
            try:
                st, d = getter("/health")
                out[name] = {"http": st, "status": d.get("status") or d.get("ok") or "up"}
            except client.OraDown:
                out[name] = {"http": "down", "status": "UNREACHABLE"}
        try:
            st, d = client.broker_get("/services/status")
            if st < 400:
                out["services"] = d
        except client.OraDown:
            pass
        return client.pretty(out)
