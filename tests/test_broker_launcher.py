from ora_warden import broker


def test_broker_launcher_refuses_non_loopback_host(monkeypatch, capsys):
    monkeypatch.setenv("ORA_WARDEN_HOST", "0.0.0.0")
    monkeypatch.setenv("ORA_WARDEN_PORT", "4573")

    assert broker.main() == 2
    assert "refusing to bind outside loopback" in capsys.readouterr().err
