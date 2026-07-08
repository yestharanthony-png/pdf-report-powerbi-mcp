# PDF Report Generator MCP (with real Power BI dashboard)

FastMCP server that turns one plain-text prompt (with embedded CSV data)
into: a live Power BI dashboard, chart images, executive summary,
insights, recommendations, and a professional PDF report.

## 1. Install dependencies

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Configure `.env`

```env
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-08-01-preview

POWERBI_CLIENT_ID=your_client_id_here
POWERBI_CLIENT_SECRET=your_client_secret_here
POWERBI_TENANT_ID=your_tenant_id_here
POWERBI_WORKSPACE_ID=your_workspace_id_here

LOG_LEVEL=INFO
GENERATED_DIR=generated
```

### Getting the Power BI values
- **Client ID / Client Secret / Tenant ID**: from the Azure AD app registration
  (Azure Portal -> App registrations). The app needs the **Dataset.ReadWrite.All**
  Power BI API permission, with **admin consent granted**.
- **Workspace ID**: open your workspace at app.powerbi.com, copy the GUID from
  the URL: `app.powerbi.com/groups/<WORKSPACE_ID>/list`
- The workspace's tenant must also have **"Allow service principals to use
  Power BI APIs"** enabled (Power BI Admin Portal -> Tenant settings), and the
  app should be added as a member of the target workspace.

## 3. Test without any MCP client

```powershell
python test_local.py
```

This prints the executive summary, insights, recommendations, chart file
paths, the live Power BI dashboard URL, and the PDF path.

## 4. Run as an MCP server

```powershell
python server.py
```

## 5. Test with MCP Inspector (requires Node.js)

```powershell
npx @modelcontextprotocol/inspector python server.py
```

## Example client prompt

```
Generate a professional sales report from the following data.

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
```

## Expected output (ReportResponse)

- `powerbi_dashboard_url` -> live link to the dataset/report in app.powerbi.com
- `powerbi_dataset_id` -> the push dataset's ID
- `chart_paths` -> PNGs in `generated/charts/` (embedded in the PDF)
- `pdf_path` -> PDF in `generated/reports/`
- `executive_summary`, `insights`, `recommendations` -> LLM-generated text

## How the Power BI integration works

`services/powerbi_service.py` uses MSAL's client-credentials flow to get an
app-only access token (no human login), then:
1. Checks if a push dataset with this report's name already exists in the
   workspace; creates one if not, with a schema matching the DataFrame columns.
2. Pushes all rows into that dataset via the REST API, in batches.
3. Returns a URL to view it at `app.powerbi.com`.

If Power BI publishing fails (e.g. permission not yet active), the report
still completes with charts/PDF/summary - the error is logged and
`powerbi_dashboard_url` is left as `null` in the response.

## Extending later

- **OneDrive upload**: add `services/onedrive_service.py` using Microsoft
  Graph API (`Files.ReadWrite` permission on the same Azure AD app) to
  upload the finished PDF and return a shareable link.
- **Database/Excel input**: swap `PromptService._extract_dataframe` for a
  DB/Excel loader - the rest of the pipeline doesn't change.

## Project structure

```
pdf-report-powerbi-mcp/
    config/settings.py         # env-driven, typed settings
    models/                    # ReportRequest, ChartSpec, ReportResponse
    services/
        prompt_service.py      # raw text -> ReportRequest (CSV parsing)
        openai_service.py      # Azure OpenAI wrapper
        summary_service.py     # data profiling + summary/insights/recs
        chart_service.py       # matplotlib chart rendering (for the PDF)
        powerbi_service.py     # real Power BI push-dataset integration
        pdf_service.py         # ReportLab PDF assembly
    tools/generate_report.py   # orchestrates the full pipeline
    utils/                     # logger, helpers
    server.py                  # FastMCP entrypoint
    test_local.py              # test without an MCP client
```
