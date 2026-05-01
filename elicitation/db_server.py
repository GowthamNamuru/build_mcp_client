from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("SafeDB-Manager", host="127.0.0.1", port=8000)

class SafetyVerification(BaseModel):
    """Schema for validating critical operations."""

    confirm: bool = Field(
        description="Must be True to proceed with operation."
    )
    justification: str = Field(
        description="A mandatory reason for why this critical operation is being performed." 
    )
    environment: str = Field(
        description="The environment you intended to affect (Development, Staging, or Production)."
    )

@mcp.tool()
async def execute_query(query: str, ctx: Context) -> str:
    """
    Executes a database query.
    Triggers a safteru check (elicitation) for destructive commands.
    """

    query_upper = query.upper().strip()

    is_destructive = any(cmd in query_upper for cmd in ["DROP", "DELETE", "TRUNCATE"])

    if is_destructive:
        result = await ctx.elicit(
            message=f"CRITICAL WARNING: You are attempting to run a destructive query: '{query}'. Verification required.",
            schema=SafetyVerification
        )

        if result.action == "accept" and result.data:
            data = result.data

            if not data.confirm:
                return "Operation blocked: User did not confirm."
            
            if data.environment == "Production" and len(data.justification) < 10:
                return "Operation blocked: Justification for production modification must be at least 10 characters long."
            
            return (
                f"Query Executed Successfully on [{data.environment}].\n"
                f"    Query: {query}\n"
                f"    Log Reason: {data.justification}"
            )

        elif result.action == "decline":
            return "Operation declined by user."
        
        else:
            return "Operation cancelled."
        
    return f"Read-only query executed: {query}"

if __name__ == "__main__":
     print("Starting SafeDB Server on http://127.0.0.1:8000/mcp ...")
     mcp.run(transport="streamable-http")
    

