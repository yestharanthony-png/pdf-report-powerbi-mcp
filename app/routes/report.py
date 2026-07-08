from pathlib import Path
import shutil
import uuid

from fastapi import APIRouter, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse

from app.services.upload_service import UploadService
from app.services.validation_service import ValidationService
from app.services.ai_service import AIService
from app.services.statistics_service import StatisticsService
from app.services.chart_service import ChartService
from app.services.pdf_service import PDFService
from app.services.powerbi_service import PowerBIService

router = APIRouter(prefix="/report")

UPLOAD_FOLDER = Path("app/uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

CHARTS_FOLDER = Path("app/static/charts")
CHARTS_FOLDER.mkdir(parents=True, exist_ok=True)

REPORT_TITLE = "AI Business Report"


@router.post("/generate", response_class=HTMLResponse)
async def generate_report(
    request: Request,
    input_type: str = Form(...),
    prompt: str = Form(""),
    file: UploadFile = File(None)
):

    html = """
    <html>
    <head>
        <title>AI Business Report Generator</title>

        <style>
            body{
                font-family:Arial;
                background:#f4f7fb;
                padding:40px;
            }

            .card{
                background:white;
                padding:30px;
                border-radius:12px;
                box-shadow:0 5px 15px rgba(0,0,0,.1);
            }

            h1{
                color:#1d4ed8;
            }

            h2{
                color:#2563eb;
            }

            table{
                width:100%;
                border-collapse:collapse;
                margin-top:15px;
            }

            table,th,td{
                border:1px solid #ddd;
            }

            th{
                background:#2563eb;
                color:white;
            }

            th,td{
                padding:10px;
            }

            pre{
                background:#f1f5f9;
                padding:15px;
                border-radius:8px;
                white-space:pre-wrap;
            }

            hr{
                margin:30px 0;
            }

            img{
                margin-top:20px;
                max-width:700px;
            }

            .btn{
                display:inline-block;
                margin-top:25px;
                padding:12px 25px;
                background:#2563eb;
                color:white;
                text-decoration:none;
                border-radius:8px;
                font-weight:bold;
            }
        </style>
    </head>

    <body>
    <div class="card">
    """

    html += "<h1>🤖 AI Business Report Generator</h1>"
    html += f"<h3>Input Type : {input_type}</h3>"

    # ---------------- PROMPT ----------------

    if input_type == "prompt":

        if not prompt.strip():
            return HTMLResponse("<h2>Please enter a business prompt.</h2>")

        html += "<hr>"
        html += "<h2>Business Prompt</h2>"
        html += f"<pre>{prompt}</pre>"

        html += "</div></body></html>"

        return HTMLResponse(content=html)

    # ---------------- CSV / EXCEL ----------------

    if input_type not in ["csv", "excel"]:
        return HTMLResponse("<h2>Invalid Input Type</h2>")

    if file is None or file.filename == "":
        return HTMLResponse("<h2>Please upload a CSV or Excel file.</h2>")

    dashboard_url = None
    screenshot_path = None

    try:

        # Upload
        file_path = UPLOAD_FOLDER / file.filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Read
        df = UploadService.read_file(str(file_path))

        # Validation
        report = ValidationService.analyze(df)

        # AI
        ai_result = AIService.generate_summary(report)

        # AI service may return either a plain string or a structured
        # dict (executive_summary / key_insights / recommendations /
        # business_risks / opportunities) - normalize both cases so the
        # PDF and HTML never show a raw Python dict.
        if isinstance(ai_result, dict):
            ai_summary_text = ai_result.get("executive_summary", "")
            ai_key_insights = ai_result.get("key_insights", [])
            ai_recommendations = ai_result.get("recommendations", [])
            ai_business_risks = ai_result.get("business_risks", [])
            ai_opportunities = ai_result.get("opportunities", [])
        else:
            ai_summary_text = str(ai_result)
            ai_key_insights = []
            ai_recommendations = []
            ai_business_risks = []
            ai_opportunities = []

        # Statistics
        stats = StatisticsService.generate_statistics(df)

        # Charts
        charts = ChartService.generate(df)

        print("Generated Charts :", charts)

        # ---------------- PDF ----------------

        run_id = str(uuid.uuid4())[:8]

        chart_paths = [
            str(Path("app/static/charts") / chart)
            for chart in charts
        ]

        # -------------------------
        # POWER BI (push data + export dashboard screenshot)
        # -------------------------

        try:
            powerbi_service = PowerBIService()

            screenshot_output_path = str(CHARTS_FOLDER / f"powerbi_dashboard_{run_id}.png")

            powerbi_result = powerbi_service.publish_and_export_screenshot(
                df=df,
                report_title=REPORT_TITLE,
                output_path=screenshot_output_path,
            )

            dashboard_url = powerbi_result["dashboard_url"]
            screenshot_path = powerbi_result.get("screenshot_path")

            print("Power BI Dashboard :", dashboard_url)
            print("Power BI Screenshot :", screenshot_path)

            if screenshot_path:
                # Embed the live dashboard screenshot in the PDF too,
                # alongside the matplotlib charts.
                chart_paths.append(screenshot_path)

        except Exception as e:
            import traceback
            traceback.print_exc()
            print("Power BI Error :", e)

        pdf_insights = [
            f"Rows : {report['rows']}",
            f"Columns : {report['columns']}",
            f"Missing Values : {report['missing_values']}",
            f"Duplicate Rows : {report['duplicate_rows']}",
        ] + ai_key_insights

        pdf_recommendations = [
            "Clean missing values.",
            "Review duplicate records.",
            "Monitor KPIs regularly.",
            "Use AI insights for business decisions.",
        ] + ai_recommendations

        pdf_service = PDFService()

        pdf_path = pdf_service.build(
            report_title=REPORT_TITLE,
            executive_summary=ai_summary_text,
            insights=pdf_insights,
            recommendations=pdf_recommendations,
            chart_paths=chart_paths,
            run_id=run_id
        )

        pdf_name = Path(pdf_path).name

    except Exception as e:
        import traceback
        traceback.print_exc()
        return HTMLResponse(
            f"<h2>Error</h2><pre>{e}</pre>"
        )

    # ---------------- HTML ----------------

    html += f"<h3>📂 Uploaded File : {file.filename}</h3>"

    html += "<hr>"
    html += "<h2>Dataset Summary</h2>"

    html += f"<p><b>Rows:</b> {report['rows']}</p>"
    html += f"<p><b>Columns:</b> {report['columns']}</p>"
    html += f"<p><b>Missing Values:</b> {report['missing_values']}</p>"
    html += f"<p><b>Duplicate Rows:</b> {report['duplicate_rows']}</p>"

    html += "<hr>"
    html += "<h2>Dataset Preview</h2>"
    html += df.head(10).to_html(index=False)

    html += "<hr>"
    html += "<h2>AI Business Summary</h2>"
    html += f"<pre>{ai_summary_text}</pre>"

    if ai_key_insights:
        html += "<h3>Key Insights</h3><ul>"
        for item in ai_key_insights:
            html += f"<li>{item}</li>"
        html += "</ul>"

    if ai_business_risks:
        html += "<h3>Business Risks</h3><ul>"
        for item in ai_business_risks:
            html += f"<li>{item}</li>"
        html += "</ul>"

    if ai_opportunities:
        html += "<h3>Opportunities</h3><ul>"
        for item in ai_opportunities:
            html += f"<li>{item}</li>"
        html += "</ul>"

    html += "<hr>"
    html += "<h2>Generated Charts</h2>"

    if charts:
        for chart in charts:
            html += f"""
            <div style="text-align:center;margin-bottom:25px;">
                <img src="/static/charts/{chart}">
            </div>
            """
    else:
        html += "<p>No charts generated.</p>"

    html += "<hr>"
    html += "<h2>Power BI Dashboard</h2>"

    if screenshot_path:
        screenshot_name = Path(screenshot_path).name
        html += f"""
        <div style="text-align:center;margin-bottom:25px;">
            <img src="/static/charts/{screenshot_name}">
        </div>
        """

    if dashboard_url:
        html += f"""
        <a class="btn"
           href="{dashboard_url}"
           target="_blank">
           📊 Open Power BI Dashboard
        </a>
        """
    else:
        html += """
        <p style="color:red;">
            Power BI Dashboard could not be created.
        </p>
        """

    html += f"""
    <hr>

    <h2>PDF Report</h2>

    <a class="btn"
       href="/generated/reports/{pdf_name}"
       target="_blank">
       📄 Download PDF Report
    </a>
    """

    html += "</div></body></html>"

    return HTMLResponse(content=html)