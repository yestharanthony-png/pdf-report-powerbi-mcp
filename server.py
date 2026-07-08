import os
from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Create MCP server
mcp = FastMCP("PDF Report Generator MCP")


# -----------------------------
# Example tool
# Replace this with your real tools
# -----------------------------
@mcp.tool()
def health_check() -> str:
    return "PDF Report Generator MCP is running successfully"


# -------------------------------------------------
# IMPORTANT:
# Expose ASGI app for Azure / gunicorn / uvicorn
# stateless_http goes HERE, not in FastMCP(...)
# -------------------------------------------------
app = mcp.http_app(
    path="/mcp",
    stateless_http=True
)


# -------------------------------------------------
# Local run only
# -------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)