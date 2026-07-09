from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet


class PDFService:

    def build(
        self,
        report_title,
        executive_summary,
        insights,
        recommendations,
        chart_paths,
        run_id,
        data_preview=None,
        powerbi_dashboard_url=None,
    ):

        reports_dir = Path("generated/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)

        pdf_path = reports_dir / f"report_{run_id}.pdf"

        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)

        story = []

        # --------------------------------------------------
        # Title
        # --------------------------------------------------
        story.append(Paragraph(report_title, styles["Title"]))
        story.append(Spacer(1, 20))

        # --------------------------------------------------
        # Executive Summary
        # --------------------------------------------------
        story.append(Paragraph("<b>Executive Summary</b>", styles["Heading2"]))
        story.append(Paragraph(executive_summary, styles["BodyText"]))
        story.append(Spacer(1, 20))

        # --------------------------------------------------
        # Business Insights
        # --------------------------------------------------
        story.append(Paragraph("<b>Business Insights</b>", styles["Heading2"]))
        for item in insights:
            story.append(Paragraph("• " + str(item), styles["BodyText"]))
        story.append(Spacer(1, 20))

        # --------------------------------------------------
        # Data Preview Table
        # --------------------------------------------------
        if data_preview:
            story.append(Paragraph("<b>Dataset Preview</b>", styles["Heading2"]))
            story.append(Spacer(1, 10))

            # data_preview is expected as list[dict]
            headers = list(data_preview[0].keys())
            table_data = [headers]

            for row in data_preview:
                table_data.append([str(row.get(col, "")) for col in headers])

            table = Table(table_data, repeatRows=1)

            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9eaf7")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ]
                )
            )

            story.append(table)
            story.append(Spacer(1, 20))

        # --------------------------------------------------
        # Recommendations
        # --------------------------------------------------
        story.append(Paragraph("<b>Recommendations</b>", styles["Heading2"]))
        for item in recommendations:
            story.append(Paragraph("• " + str(item), styles["BodyText"]))
        story.append(Spacer(1, 20))

        # --------------------------------------------------
        # Power BI Link
        # --------------------------------------------------
        if powerbi_dashboard_url:
            story.append(Paragraph("<b>Power BI Dashboard</b>", styles["Heading2"]))
            story.append(Paragraph(str(powerbi_dashboard_url), styles["BodyText"]))
            story.append(Spacer(1, 20))

        # --------------------------------------------------
        # Charts
        # --------------------------------------------------
        if chart_paths:
            story.append(Paragraph("<b>Charts</b>", styles["Heading2"]))
            story.append(Spacer(1, 10))

            for chart in chart_paths:
                if Path(chart).exists():
                    story.append(Image(chart, width=400, height=250))
                    story.append(Spacer(1, 15))

        doc.build(story)

        return str(pdf_path)