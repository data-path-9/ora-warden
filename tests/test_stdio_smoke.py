import sys

import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from tests.test_server_tools import EXPECTED_TOOLS


def test_stdio_server_lists_expected_tools():
    async def main():
        params = StdioServerParameters(command=sys.executable, args=["-m", "ora_warden"])
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
                return [tool.name for tool in result.tools]

    assert anyio.run(main) == EXPECTED_TOOLS
