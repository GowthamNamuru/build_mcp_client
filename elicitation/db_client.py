import asyncio
import json
from mcp import ClientSession, types
from mcp.client.session import RequestContext
from mcp.client.streamable_http import streamablehttp_client

SERVER_URL = "http://127.0.0.1:8000/mcp"

async def elicitation_handler(
        context: RequestContext,
        params: types.ElicitRequestParams
) -> types.ElicitResult:
    """
    This function is called automatically when the Server triggers ctx.elicit().
    """
    print("\n" + "!" * 50)
    print(f"SERVER MESSAGE: {params.message}")
    print("\n" + "!" * 50)

    print("Please provide the required safety details:")

    print("Select Environment (Development/Staging/Production):")
    env_input = input("> ").strip().title()

    print("Justification for this action:")
    reason_input = input("> ").strip()

    print("Type 'yes' to confirm execution:")
    confirm_input = input("> ").lower().strip()

    is_confirmed = (confirm_input == "yes")

    user_response_data = {
        "confirm": is_confirmed,
        "justification": reason_input,
        "environment": env_input
    }

    return types.ElicitResult(
        action="yes",
        data=user_response_data
    )


async def run_client():
    print(f"Connecting to SafeDB Server at {SERVER_URL}...")

    async with streamablehttp_client(SERVER_URL) as (read, write, _):
        async with ClientSession(
            read,
            write,
            elicitation_callback=elicitation_handler
        ) as session:
            await session.initialize()
            print("✅ Connected and Initialized!\n")

            print("--- Test 1: Running Safe Query ---")
            result_safe = await session.call_tool(
                "execute_query",
                {"query": "SELECT * FROM users;"}
            )
            print(f"Result: {result_safe.content[0].text}\n")

            print("--- Test 2: Running Destructive Query ---")
            print("Sending: DROP TABLE invoices...")

            result_dangerous = await session.call_tool(
                "execute_query",
                {"query": "DROP TABLE invoices;"}
            )
            print("\n--- Final Result from Server ---")
            if result_dangerous.isError:
                 print(f"Error: {result_dangerous.content}")
            else:
                 print(result_dangerous.content[0].text)

if __name__ == "__main__":
    asyncio.run(run_client())