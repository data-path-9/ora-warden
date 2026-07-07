import jsonschema
import anyio

from ora_warden import config
from ora_warden.server import server


EXPECTED_TOOLS = [
    "shell",
    "shell_destructive",
    "read_file",
    "write_file",
    "propose",
    "queue",
    "proposals_list",
    "proposal_get",
    "proposal_approve",
    "proposal_reject",
    "proposal_execute",
    "audit_verify",
    "audit_sth",
    "audit_recent",
    "health",
]


def _tool_names_and_schemas():
    async def main():
        tools = await server.list_tools()
        return [(tool.name, tool.inputSchema) for tool in tools]

    return anyio.run(main)


def test_expected_governance_tool_set_is_registered():
    names_and_schemas = _tool_names_and_schemas()

    assert [name for name, _schema in names_and_schemas] == EXPECTED_TOOLS


def test_registered_tool_input_schemas_are_valid_json_schema():
    for name, schema in _tool_names_and_schemas():
        assert schema["type"] == "object", name
        jsonschema.Draft202012Validator.check_schema(schema)


def test_gated_tool_without_token_returns_blocked_message(monkeypatch):
    monkeypatch.setattr(config, "_token_cache", None)
    monkeypatch.setattr(config, "_token_loaded", False)
    monkeypatch.delenv("ORA_OPERATOR_TOKEN", raising=False)
    monkeypatch.setattr(config, "TOKEN_FILE", "/tmp/ora-warden-test-token-does-not-exist")

    async def main():
        content, structured = await server.call_tool(
            "shell_destructive",
            {"command": "rm -rf /tmp/ora-warden-nope"},
        )
        return content[0].text, structured["result"]

    text, structured_result = anyio.run(main)
    assert text == structured_result
    assert text.startswith("BLOCKED by ORA Warden")
    assert "operator token not loaded" in text
