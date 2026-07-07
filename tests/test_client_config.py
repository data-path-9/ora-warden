import pytest

from ora_warden import client, config


@pytest.fixture(autouse=True)
def reset_token_cache(monkeypatch):
    monkeypatch.setattr(config, "_token_cache", None)
    monkeypatch.setattr(config, "_token_loaded", False)


def test_operator_token_prefers_env(monkeypatch, tmp_path):
    token_file = tmp_path / "operator-token.env"
    token_file.write_text("ORA_OPERATOR_TOKEN=file-token\n", encoding="utf-8")
    monkeypatch.setattr(config, "TOKEN_FILE", str(token_file))
    monkeypatch.setenv("ORA_OPERATOR_TOKEN", " env-token ")

    assert config.operator_token() == "env-token"


def test_operator_token_loads_quoted_file_value(monkeypatch, tmp_path):
    token_file = tmp_path / "operator-token.env"
    token_file.write_text("ignored=true\nORA_OPERATOR_TOKEN='file-token'\n", encoding="utf-8")
    monkeypatch.setattr(config, "TOKEN_FILE", str(token_file))
    monkeypatch.delenv("ORA_OPERATOR_TOKEN", raising=False)

    assert config.operator_token() == "file-token"


def test_gated_request_fails_closed_without_token(monkeypatch):
    monkeypatch.setattr(config, "operator_token", lambda: None)

    with pytest.raises(client.TokenMissing):
        client.broker_post("/shell/run", {"command": "rm -rf /"}, gated=True)


@pytest.mark.parametrize("status", [403, 409])
def test_blocked_statuses_are_reported_as_blocked(status):
    message = client.blocked_or_error(status, {"reason": "policy"})

    assert message is not None
    assert message.startswith("BLOCKED by ORA Warden")


def test_unsafe_endpoint_is_blocked_before_http(monkeypatch):
    class FailingClient:
        def __init__(self, *args, **kwargs):
            raise AssertionError("http client should not be constructed for off-box URLs")

    monkeypatch.setattr(config, "BROKER_URL", "https://example.com")
    monkeypatch.setattr(client.httpx, "Client", FailingClient)

    with pytest.raises(client.UnsafeEndpoint):
        client.broker_get("/health")


def test_loopback_url_validation():
    assert config.is_loopback_url("http://127.0.0.1:4573")
    assert config.is_loopback_url("http://localhost:4573")
    assert config.is_loopback_url("http://[::1]:4573")
    assert not config.is_loopback_url("https://example.com")
    assert not config.is_loopback_url("file:///tmp/socket")
