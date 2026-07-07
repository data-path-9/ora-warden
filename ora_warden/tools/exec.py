"""Governed execution tools (the ORA Warden broker)."""

from .. import client, config
from . import ora_tool


def register_exec_tools(server):

    @server.tool()
    @ora_tool
    def shell(command: str, cwd: str = "", authority: str = "", timeout_seconds: int = 0) -> str:
        """Run a shell command THROUGH the governed, audited broker. Prefer this over raw shell for
        anything that changes state — every command is written to a tamper-evident audit log and
        outbound network egress is kernel-locked. Destructive commands (rm -rf, git reset, dd, mkfs,
        sudo, ...) and credential-exfiltration are BLOCKED here (use shell_destructive, operator-gated,
        for a deliberately destructive command). Returns stdout, stderr, exit_code.

        Args:
            command: the shell command to run.
            cwd: working directory (default: the operator's home directory).
            authority: authority level A0-A5 (default A3 = do approved work).
            timeout_seconds: max seconds before the broker kills it (0 = broker default).
        """
        body = {
            "command": command,
            "cwd": cwd or config.DEFAULT_CWD,
            "destructive_intent": False,
            "authority": authority or config.DEFAULT_AUTHORITY,
        }
        if timeout_seconds:
            body["timeout_seconds"] = int(timeout_seconds)
        status, d = client.broker_post("/shell/run", body)
        err = client.blocked_or_error(status, d)
        if err:
            return err
        out = f"exit_code: {d.get('exit_code')}\n--- stdout ---\n{d.get('stdout', '')}"
        if d.get("stderr"):
            out += f"\n--- stderr ---\n{d.get('stderr')}"
        return out

    @server.tool()
    @ora_tool
    def shell_destructive(command: str, cwd: str = "", authority: str = "A3", confidence: int = 90) -> str:
        """HUMAN-AUTHORIZED ONLY (operator-gated). Run a deliberately DESTRUCTIVE command with
        destructive_intent=true through the broker (requires the operator token). Call this ONLY when
        the operator explicitly tells you to run a specific destructive command — never on your own
        judgement. Without a token it fails closed.

        Args:
            command: the destructive command.
            cwd: working directory (default: the operator's home directory).
            authority: authority level (default A3).
            confidence: 0-100 confidence (default 90).
        """
        body = {
            "command": command,
            "cwd": cwd or config.DEFAULT_CWD,
            "destructive_intent": True,
            "authority": authority or "A3",
            "confidence": int(confidence),
        }
        status, d = client.broker_post("/shell/run", body, gated=True)
        err = client.blocked_or_error(status, d)
        if err:
            return err
        out = f"exit_code: {d.get('exit_code')}\n--- stdout ---\n{d.get('stdout', '')}"
        if d.get("stderr"):
            out += f"\n--- stderr ---\n{d.get('stderr')}"
        return out

    @server.tool()
    @ora_tool
    def read_file(path: str) -> str:
        """Read a local file through the audited broker (approved-path enforced; secrets blocked).

        Args:
            path: absolute file path.
        """
        status, d = client.broker_get("/files/read", params={"path": path})
        err = client.blocked_or_error(status, d)
        if err:
            return err
        return d.get("content", client.pretty(d))

    @server.tool()
    @ora_tool
    def write_file(path: str, content: str, mode: str = "overwrite") -> str:
        """Write or append a local file through the audited broker (approved-path enforced, secrets
        blocked, change logged). Returns confirmation.

        Args:
            path: absolute file path.
            content: content to write.
            mode: 'overwrite' (default) or 'append'.
        """
        body = {"path": path, "content": content, "mode": mode or "overwrite"}
        status, d = client.broker_post("/files/write", body)
        err = client.blocked_or_error(status, d)
        if err:
            return err
        return f"Wrote {path} ({body['mode']}) — audited."
