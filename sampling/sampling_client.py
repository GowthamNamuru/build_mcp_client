import asyncio
import os
from anthropic import Anthropic
from mcp import ClientSession, types
from mcp.client.session import RequestContext
from mcp.client.streamable_http import streamablehttp_client

SERVER_URL = "http://127.0.0.1:8000/mcp"

llm_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

async def sampling_handler(
    context: RequestContext,
    params: types.CreateMessageRequestParams
) -> types.CreateMessageResult:
    """
    This function triggers when the Server asks for an LLM completion.
    We bridge the request to the real Anthropic API.
    """
    server_prompt = params.messages[0].content.text
    print(f"\n[Client] Server requested LLM generation for: '{server_prompt}'")

    print(f"[Client] Forwarding request to Claude...")

    message = llm_client.messages.create(
        max_tokens=params.maxTokens or 1024,
        messages=[
            {
                "role": "user",
                "content": server_prompt,
            }
        ],
        model="claude-sonnet-4-5-20250929",
    )

    ai_response = message.content[0].text
    print(f"[Client] Received answer from Claude: '{ai_response}'")

    return types.CreateMessageResult(
        model="claude-sonnet-4-5",
        role="assistant",
        content=types.TextContent(type="text", text=ai_response)
    )

async def run_client():
    print(f"Connecting to Server at {SERVER_URL}...")

    async with streamablehttp_client(SERVER_URL) as (read, write, _):
        async with ClientSession(
            read,
            write,
            sampling_callback=sampling_handler
        ) as session:
            await session.initialize()
            print("Connected.\n")

            print("--- Test: Archiving Complex Error ---")

            complex_error = (
                "2025-12-21 14:02:11 UTC [821] ERROR:  deadlock detected "
                "DETAIL:  Process 821 waits for ShareLock on transaction 456; process 999 waits for ShareLock on transaction 821. "
                "HINT:  See server log for query details."
            )

            result = await session.call_tool(
                "process_log_entry",
                arguments={"log_line": complex_error}
            )

            print(f"\nFinal Tool Result:\n{result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(run_client())
