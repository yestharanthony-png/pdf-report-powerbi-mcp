from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
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
        powerbi_dashboard_url=None,
    ):

        reports_dir = Path("generated/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)

        pdf_path = reports_dir / f"report_{run_id}.pdf"

        styles = getSampleStyleSheet()

        doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)

        story = []

        story.append(Paragraph(report_title, styles["Title"]))
        story.append(Spacer(1, 20))

        story.append(Paragraph("<b>Executive Summary</b>", styles["Heading2"]))
        story.append(Paragraph(executive_summary, styles["BodyText"]))
        story.append(Spacer(1, 20))

        story.append(Paragraph("<b>Business Insights</b>", styles["Heading2"]))

        for item in insights:
            story.append(Paragraph("• " + item, styles["BodyText"]))

        story.append(Spacer(1, 20))

        story.append(Paragraph("<b>Recommendations</b>", styles["Heading2"]))

        for item in recommendations:
            story.append(Paragraph("• " + item, styles["BodyText"]))

        story.append(Spacer(1, 20))

        if powerbi_dashboard_url:
            story.append(Paragraph("<b>Power BI Dashboard</b>", styles["Heading2"]))
            story.append(Paragraph(powerbi_dashboard_url, styles["BodyText"]))
            story.append(Spacer(1, 20))

        if chart_paths:
            story.append(Paragraph("<b>Charts</b>", styles["Heading2"]))

            for chart in chart_paths:

                if Path(chart).exists():

                    story.append(Image(chart, width=400, height=250))
                    story.append(Spacer(1, 15))

        doc.build(story)

        return str(pdf_path)