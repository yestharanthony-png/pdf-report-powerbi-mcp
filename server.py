import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from fastmcp import FastMCP
from models.report_response import ReportResponse
from tools.generate_report import generate_report as _generate_report

# --------------------------------------------------
# Create MCP Server
# --------------------------------------------------
mcp = FastMCP("PDF Report Generator MCP")

# --------------------------------------------------
# Generate Report Tool
# --------------------------------------------------
@mcp.tool()
def generate_report(
    report_title: str,
    dataset: str,
    dashboard_items: list[str],
    generate_pdf: bool = True,
    publish_powerbi: bool = True,
) -> ReportResponse:
    """
    Generate a dynamic AI-powered business report.
    """
    return _generate_report(
        report_title=report_title,
        dataset=dataset,
        dashboard_items=dashboard_items,
        generate_pdf=generate_pdf,
        publish_powerbi=publish_powerbi,
    )

# --------------------------------------------------
# Expose ASGI app for Azure / gunicorn
# --------------------------------------------------
app = mcp.http_app(
    path="/mcp",
    stateless_http=True
)

# --------------------------------------------------
# Local run only
# --------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)