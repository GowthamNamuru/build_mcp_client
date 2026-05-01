from mcp.server.fastmcp import FastMCP, Context
from mcp.types import SamplingMessage, TextContent

mcp = FastMCP("Log-Archiver")

@mcp.tool()
async def process_log_entry(log_line: str, ctx: Context) -> str:
    """
    Analyzes a log entry using the Client's LLM and saves the report to a file.
    """
    prompt = f"You are a Site Reliability Engineer. Explain this log error in one concise sentence: {log_line}"

    result = await ctx.session.create_message(
        messages=[
            SamplingMessage(
                role="user",
                content=TextContent(type="text", text=prompt),
            )
        ],
        max_tokens=100,
    )

    if result.content.type == "text":
        llm_explanation = result.content.text
    else:
        llm_explanation = str(result.content)

    report_file = "incident_report.txt"
    with open(report_file, "a") as f:
        f.write(f"--- INCIDENT REPORT ---\n")
        f.write(f"RAW: {log_line}\n")
        f.write(f"ANALYSIS: {llm_explanation}\n")
        f.write("-" * 30 + "\n")

    return f"Success: Log analyzed and appended to '{report_file}'."

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
