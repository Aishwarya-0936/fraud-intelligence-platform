import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "app.mcp_server.server"],
        env=os.environ.copy(),
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Available MCP tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            print("\nCalling retrieve_similar_fraud_cases...")
            result = await session.call_tool(
                "retrieve_similar_fraud_cases",
                {"amount": 275000, "merchant_category": "crypto", "signals": "high_value_transfer, first_transaction"}
            )
            print("isError:", result.isError)
            print("Full result:", result)

            print("\nCalling get_related_fraud_patterns...")
            result2 = await session.call_tool(
                "get_related_fraud_patterns",
                {"signals": "geographic_impossibility, new_device"}
            )
            print("isError:", result2.isError)
            print("Full result:", result2)


if __name__ == "__main__":
    asyncio.run(main())