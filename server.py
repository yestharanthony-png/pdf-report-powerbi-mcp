from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from fastmcp import FastMCP

from models.report_response import ReportResponse
from tools.generate_report import generate_report as _generate_report

# ---------------------------------------------------------
# MCP Server
# ---------------------------------------------------------

mcp = FastMCP("PDF Report Generator MCP")


@mcp.tool()
def generate_report(
    report_title: str,
    dataset: str,
    dashboard_items: list[str],      # REQUIRED
    generate_pdf: bool = True,
    publish_powerbi: bool = True,
) -> ReportResponse:
    """
    Generate a business report dynamically from the supplied dataset.

    Parameters
    ----------
    report_title:
        Title of the report.

    dataset:
        CSV dataset as text.

        Example:

        Region,Sales,Profit
        North,12000,3000
        South,9000,1800
        East,15000,4500
        West,11000,2500

    dashboard_items:
        Dashboard visualizations requested by the user.

        Example:

        [
            "Sales by Region",
            "Profit by Region",
            "Sales Trend",
            "Top Regions",
            "Average Sales",
            "Total Profit"
        ]

    generate_pdf:
        Generate PDF report.

    publish_powerbi:
        Publish dataset to Power BI.
    """

    return _generate_report(
        report_title=report_title,
        dataset=dataset,
        dashboard_items=dashboard_items,
        generate_pdf=generate_pdf,
        publish_powerbi=publish_powerbi,
    )


if __name__ == "__main__":
    import os

    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        path="/mcp",
    )