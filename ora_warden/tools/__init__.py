"""Shared helpers for ORA Warden tool modules."""

import functools

from .. import client


def ora_tool(fn):
    """Wrap a tool so governance outages / missing-token / unexpected errors become friendly strings
    instead of MCP exceptions. Signature is preserved (functools.wraps) so FastMCP still builds the
    correct input schema."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except client.OraDown as e:
            return client.down_message(e)
        except client.UnsafeEndpoint:
            return (
                "BLOCKED by ORA Warden (loopback-only, fail-closed): a governance endpoint is "
                "configured outside localhost/127.0.0.1/::1."
            )
        except client.TokenMissing:
            return (
                "BLOCKED by ORA Warden (operator approval required, fail-closed): operator token "
                "not loaded for this human-authorized action."
            )
        except Exception as e:  # surface any unexpected error to the caller
            return f"ORA Warden error in {fn.__name__}: {type(e).__name__}: {e}"

    return wrapper
