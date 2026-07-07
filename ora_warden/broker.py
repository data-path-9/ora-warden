"""Portable launcher for the separate ORA runtime broker binary."""

from __future__ import annotations

import os
import shutil
import sys
from importlib import resources
from pathlib import Path

from .config import is_loopback_url


def _default_runtime_root() -> Path:
    data_home = os.environ.get("XDG_DATA_HOME")
    if data_home:
        return Path(data_home).expanduser() / "ora-warden" / "runtime"
    return Path.home() / ".local" / "share" / "ora-warden" / "runtime"


def _default_constitution_path() -> str:
    return str(resources.files("ora_warden.data").joinpath("odin-constitution.yaml"))


def main() -> int:
    host = os.environ.get("ORA_WARDEN_HOST", "127.0.0.1")
    port = os.environ.get("ORA_WARDEN_PORT", "4573")
    url_host = f"[{host}]" if ":" in host and not host.startswith("[") else host
    if not is_loopback_url(f"http://{url_host}:{port}"):
        print("ora-warden-broker: refusing to bind outside loopback.", file=sys.stderr)
        print("  Set ORA_WARDEN_HOST to 127.0.0.1, localhost, or ::1.", file=sys.stderr)
        return 2

    runtime_root = Path(os.environ.get("ORA_RUNTIME_ROOT", _default_runtime_root())).expanduser()
    (runtime_root / "state").mkdir(parents=True, exist_ok=True)
    (runtime_root / "audit").mkdir(parents=True, exist_ok=True)
    os.environ["ORA_RUNTIME_ROOT"] = str(runtime_root)

    os.environ.setdefault("ORA_CONSTITUTION_PATH", _default_constitution_path())

    broker_bin = os.environ.get("ORA_WARDEN_BROKER_BIN", "ora-runtime")
    broker_path = shutil.which(broker_bin) or (broker_bin if os.access(broker_bin, os.X_OK) else None)
    if not broker_path:
        print(f"ora-warden-broker: broker binary '{broker_bin}' not found.", file=sys.stderr)
        print("  Install the separate ora-runtime broker, or set ORA_WARDEN_BROKER_BIN.", file=sys.stderr)
        return 127

    print(f"ora-warden-broker: starting on http://{host}:{port}", file=sys.stderr)
    print(f"  runtime root : {runtime_root}", file=sys.stderr)
    print(f"  constitution : {os.environ['ORA_CONSTITUTION_PATH']}", file=sys.stderr)
    os.execvp(broker_path, [broker_path, "broker", "--host", host, "--port", port])
    return 127


if __name__ == "__main__":
    raise SystemExit(main())
