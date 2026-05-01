import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import TextContent

SERVER_URL = "http://127.0.0.1:8000/mcp"

async def run_cleint():
    print(f"  Connecting to server at {SERVER_URL}...")

    async with streamablehttp_client(SERVER_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ Connected and Initialized!\n")

            print("--- 1. Testing Resource Travel Alerts ----")

            resources = await session.list_resources()
            print(f"Found {len(resources.resources)} available resources.")

            resource_uri = "travel://alerts/london"
            print(f"Reading: {resource_uri}")

            res_result = await session.read_resource(resource_uri)

            for content in res_result.contents:
                if hasattr(content, "text"):
                    print(f"📜 CONTENT: {content.text}")
            
            print("")

            print("--- 2. Testing Tool: Calculate Trip Budget ---")

            tool_name = "calculate_trip_budget"
            tool_args = {
                "days": 5,
                "travelers": 2,
                "daily_spend": 150,
                "currency_rate": 0.85
            }

            print(f"Calling tool '{tool_name}' with args: {tool_args}")

            tool_result = await session.call_tool(tool_name, tool_args)

            for content in tool_result.content:
                if isinstance(content, TextContent):
                    print(f"🛠️ RESULT:\n{content.text}")
                
            print("")

            print("--- 3. Testing Prompt: Draft Travel Plan ---")

            prompt_name = "draft_travel_plan"
            prompt_args = {
                "destination": "Paris",
                "days": "5",
                "travelers": "2"
            }

            print(f"Fetching prompt '{prompt_name}' with args: {prompt_args}")

            prompt_result = await session.get_prompt(prompt_name, prompt_args)

            for message in prompt_result.messages:
                print(f"💬 ROLE:  {message.role.upper()}")
                if hasattr(message.content, "text"):
                    print(f"📝 MESSAGE CONTENT:\n{message.content.text}")
                else:
                    print(f"📝 MESSAGE CONTENT:\n{message.content}")
                
if __name__ == "__main__":
    asyncio.run(run_cleint())
