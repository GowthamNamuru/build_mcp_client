import os
import anthropic

url = os.environ.get('MCP_SERVER_URL')
api_key = os.environ.get('ANTHROPIC_API_KEY')

prompt = f"My dog is 3 years old. If my dog were a human, how old would she be?"

client = anthropic.Anthropic(api_key=api_key)

response = client.beta.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=2000,
    messages=[{"role": "user", "content": prompt}],
    mcp_servers=[
        {
            "type": "url",
            "url": url,
            "name": "dog-age-server",
        }
    ],
    tools=[
      {
        "type": "mcp_toolset",
        "mcp_server_name": "dog-age-server"
      }
    ],
    extra_headers={
        "anthropic-beta": "mcp-client-2025-11-20"
    }
)

for block in response.content:
    if block.type == "text":
        print(block.text)

    elif block.type == "mcp_tool_use":
        print(f"[System] Calling MCP Tool: '{block.name}'")
        print(f"[System] Parameters: {block.input}")

    elif block.type == "mcp_tool_result":
        result_text = " ".join([b.text for b in block.content if b.type == 'text'])
        print(f"[System] Tool Result: {result_text}\n")
