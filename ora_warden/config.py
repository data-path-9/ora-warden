"""Configuration + operator-token loader for ORA Warden.

Everything is loopback. The operator token gates the human-authorized actions (approve/execute a
proposal, run a deliberately destructive command). It is read once, cached in memory, and NEVER
logged or returned in a tool response. All paths come from the environment with sensible XDG-style
defaults — nothing is hardcoded to a particular machine or user.
"""

import os
import ipaddress
from urllib.parse import urlparse

# --- the local governance services Warden bridges to (loopback only) ---
BROKER_URL = os.environ.get("ORA_BROKER_URL", "http://127.0.0.1:4573").rstrip("/")
OPERATOR_URL = os.environ.get("ORA_OPERATOR_URL", "http://127.0.0.1:5577").rstrip("/")

# --- defaults ---
DEFAULT_CWD = os.environ.get("ORA_DEFAULT_CWD", os.path.expanduser("~"))
DEFAULT_AUTHORITY = os.environ.get("ORA_DEFAULT_AUTHORITY", "A3")
HTTP_TIMEOUT = float(os.environ.get("ORA_HTTP_TIMEOUT", "180"))
_LOOPBACK_HOSTNAMES = {"localhost"}


def is_loopback_url(url: str) -> bool:
    """Return True only for http(s) URLs targeting the local loopback interface."""
    try:
        parsed = urlparse(url)
    except Exception:
        return False
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False
    host = parsed.hostname.lower()
    if host in _LOOPBACK_HOSTNAMES:
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _default_token_file() -> str:
    """XDG-style default location for the operator token file."""
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "ora-warden", "operator-token.env")


TOKEN_FILE = os.environ.get("ORA_WARDEN_TOKEN_FILE", _default_token_file())

_token_cache = None
_token_loaded = False


def operator_token():
    """Return the operator token (env first, then the token file), or None. Cached in memory,
    never logged. The env var is ORA_OPERATOR_TOKEN; the token file holds a line
    ORA_OPERATOR_TOKEN=<value>."""
    global _token_cache, _token_loaded
    if _token_loaded:
        return _token_cache
    _token_loaded = True

    tok = os.environ.get("ORA_OPERATOR_TOKEN")
    if tok and tok.strip():
        _token_cache = tok.strip()
        return _token_cache

    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("ORA_OPERATOR_TOKEN="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    _token_cache = val or None
                    return _token_cache
    except Exception:
        pass

    _token_cache = None
    return None
