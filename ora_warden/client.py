"""HTTP bridge to the local ORA governance services, with governance-aware error mapping.

A connect error means the governance layer is down. A 403/409 means a governed BLOCK (fail-closed),
surfaced verbatim to the caller. Gated calls attach the operator token and fail closed if it is not
loaded. This module is the ONLY place that opens network connections — tool modules go through it.
"""

import json as _json

import httpx

from . import config


class OraDown(Exception):
    """The targeted governance service is unreachable (governance layer down)."""


class TokenMissing(Exception):
    """A human-authorized (gated) call was attempted but no operator token is loaded."""


class UnsafeEndpoint(Exception):
    """A configured governance URL is not loopback-only."""


def _request(method, base, path, *, params=None, body=None, gated=False):
    if not config.is_loopback_url(base):
        raise UnsafeEndpoint()
    headers = {}
    if gated:
        tok = config.operator_token()
        if not tok:
            raise TokenMissing()
        headers["Authorization"] = f"Bearer {tok}"
    url = f"{base}{path}"
    try:
        with httpx.Client(timeout=config.HTTP_TIMEOUT) as c:
            if method == "GET":
                r = c.get(url, params=params, headers=headers)
            else:
                r = c.post(url, params=params, json=(body if body is not None else {}), headers=headers)
    except (httpx.ConnectError, httpx.ConnectTimeout):
        raise OraDown(base)
    try:
        data = r.json()
    except Exception:
        data = {"_raw": r.text}
    return r.status_code, data


# thin per-service wrappers -------------------------------------------------
def broker_get(path, params=None):
    return _request("GET", config.BROKER_URL, path, params=params)


def broker_post(path, body=None, gated=False):
    return _request("POST", config.BROKER_URL, path, body=body, gated=gated)


def operator_get(path, params=None):
    return _request("GET", config.OPERATOR_URL, path, params=params)


def operator_post(path, body=None, gated=False):
    return _request("POST", config.OPERATOR_URL, path, body=body, gated=gated)


# formatting helpers --------------------------------------------------------
DOWN_HINT = {
    config.BROKER_URL: "the ORA Warden broker",
    config.OPERATOR_URL: "the ORA Warden approval queue",
}


def down_message(err: OraDown) -> str:
    base = str(err.args[0]) if err.args else "?"
    unit = DOWN_HINT.get(base, base)
    return (
        f"ORA Warden is unreachable at {base} — the governance layer is not running. "
        f"Start {unit} (see the Warden README: `ora-warden-broker`)."
    )


def pretty(data) -> str:
    try:
        return _json.dumps(data, indent=2, ensure_ascii=False)
    except Exception:
        return str(data)


def blocked_or_error(status, data):
    """Return a human string if this is a governed block / error, else None."""
    if status in (403, 409):
        return f"BLOCKED by ORA Warden (governance, fail-closed): {pretty(data)}"
    if status == 429:
        return f"ORA Warden refused (budget/cap): {pretty(data)}"
    if status and status >= 400:
        return f"ORA Warden error {status}: {pretty(data)}"
    return None
