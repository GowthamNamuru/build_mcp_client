from pathlib import Path
from mcp.server.fastmcp import FastMCP, Context
import os

mcp = FastMCP("Secure-FS")

def extract_path_from_uri(uri) -> Path:
    """
    Extract file path from URI, handling both string URIs and FileUrl objects.
    """
    uri_str = str(uri)

    if uri_str.startswith('file://'):
        path_part = uri_str[7:]
    else:
        path_part = uri_str

    if os.name == 'nt' and path_part.startswith('/') and len(path_part) > 1 and path_part[1] != '/':
        path_part = path_part[1:]
    
    return Path(path_part)

@mcp.tool()
async def read_secure_file(path: str, ctx: Context) -> str:
    """
    Reads a file ONLY if it is inside the client-provided root directories.
    Respects MCP roots as advisory boundaries for file access.
    """

    try:
        roots_list = await ctx.session.list_roots()

        if not roots_list.roots:
            fallback_sandbox = Path.cwd() / "sandbox"
            allowed_dirs = [fallback_sandbox.resolve()]
        else:
            allowed_dirs = []
            for root in roots_list.roots:
                try:
                    root_path = extract_path_from_uri(root.uri)
                    allowed_dirs.append(root_path.resolve())
                except Exception as e:
                    continue

            if not allowed_dirs:
                fallback_sandbox = Path.cwd() / "sandbox"
                allowed_dirs = [fallback_sandbox.resolve()]
    except Exception as e:
        fallback_sandbox = Path.cwd() / "sandbox"
        allowed_dirs = [fallback_sandbox.resolve()]
    
    try:
        target_path = Path(path).resolve()
    except Exception as e:
        return f"Error: Invalid path structure: {e}"
    
    is_allowed = False
    for root in allowed_dirs:
        if target_path.is_relative_to(root):
            is_allowed = True
            break

    if not is_allowed:
        if len(allowed_dirs) == 1 and allowed_dirs[0] == Path.cwd() / "sandbox":
            sandbox_path = Path.cwd() / "sandbox"
            return f"ACCESS DENIED: '{path}' is outside the allowed sandbox ({sandbox_path})."
        else:
            roots_str = ", ".join(str(d) for d in allowed_dirs)
            return f"ACCESS DENIED: '{path}' is outside the allowed root directories: {roots_str}."
        
    try:
        if not target_path.exists():
            return "Error: File not found."
        return target_path.read_text(encoding='utf-8')
    except Exception as e:
        return f"Error reading file: {e}"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")