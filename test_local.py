"""
Quick local test - calls generate_report() directly, no MCP client needed.

Run:
    python test_local.py
"""

from tools.generate_report import generate_report

SAMPLE_PROMPT = """Generate a professional sales report from the following data.

OrderID,Region,Sales,Profit
101,North,12000,3000
102,South,9000,1800
103,East,15000,4500
104,West,7000,1200

Generate:
Bar Chart
Pie Chart
Power BI Dashboard
Professional PDF Report
"""

if __name__ == "__main__":
    result = generate_report(SAMPLE_PROMPT)

    print("\nSTATUS:", result.status)
    print("MESSAGE:", result.message)
    print("\nEXECUTIVE SUMMARY:\n", result.executive_summary)
    print("\nINSIGHTS:")
    for i in result.insights:
        print(" -", i)
    print("\nRECOMMENDATIONS:")
    for r in result.recommendations:
        print(" -", r)
    print("\nCHART FILES:")
    for c in result.chart_paths:
        print(" -", c)
    print("\nPOWER BI DASHBOARD URL:", result.powerbi_dashboard_url)
    print("POWER BI DATASET ID:", result.powerbi_dataset_id)
    print("PDF REPORT:", result.pdf_path)
