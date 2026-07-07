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
        except client.TokenMissing:
            return (
                "Operator token not loaded — this is a human-authorized action and cannot run. "
                "It is only meant to be called when the operator explicitly asks for it."
            )
        except Exception as e:  # surface any unexpected error to the caller
            return f"ORA Warden error in {fn.__name__}: {type(e).__name__}: {e}"

    return wrapper
