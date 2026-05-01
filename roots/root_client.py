import asyncio
from pathlib import Path
from mcp import ClientSession, types
from mcp.client.streamable_http import streamablehttp_client

SANDBOX_DIR = Path.cwd() / "sandbox"
SANDBOX_DIR.mkdir(exist_ok=True)
SECRET_FILE = Path.cwd() / "secret.txt"
SECRET_FILE.write_text("This is top secret data!")
SAFE_FILE = SANDBOX_DIR / "hello.txt"
SAFE_FILE.write_text("This is safe to read.")

SERVER_URL = "http://127.0.0.1:8000/mcp"

async def list_roots_handler(context) -> types.ListRootsResult:
    """
    Provide MCP roots to define filesystem boundaries for the server.
    This tells the server which directories it should operate within.
    """
    return types.ListRootsResult(roots=[
        types.Root(
            uri=f"file://{SANDBOX_DIR.as_posix()}",
            name="Safe Sandbox"
        )
    ])

async def run_client():
     print(f"Connecting to server at {SERVER_URL}...")

     async with streamablehttp_client(SERVER_URL) as (read, write, _):
          async with ClientSession(
               read,
               write,
               list_roots_callback=list_roots_handler
          ) as session:
               await session.initialize()
               print("✅ Connected! (Roots provided)!\n")

               print(f"---Test 1: Reading Safe File---")
               print(f"Requesting: {(SAFE_FILE)}")
               result_safe = await session.call_tool(
                    "read_secure_file",
                    {"path": SAFE_FILE.as_posix()}
               )
               print(f"Result: {result_safe.content[0].text}\n")

               print(f"--- Test 2: Attempting Jailbreak ---")
               print(f"Requesting: {SECRET_FILE}")
               result_jailbreak = await session.call_tool(
                    "read_secure_file",
                    arguments={"path": str(SECRET_FILE)}
                )
               print(f"Result: {result_jailbreak.content[0].text}\n")

if __name__ == "__main__":
    asyncio.run(run_client())