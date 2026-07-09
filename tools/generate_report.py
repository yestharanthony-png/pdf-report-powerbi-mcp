"""
Dynamic Report Generator
"""

import io
import pandas as pd

from models.report_response import ReportResponse

from services.chart_service import ChartService
from services.openai_service import OpenAIService
from services.summary_service import SummaryService

from app.services.pdf_service import PDFService
from app.services.powerbi_service import (
    PowerBIService,
    PowerBIAPIError,
    PowerBIAuthError,
)
from app.services.blob_storage_service import BlobStorageService

from utils.helpers import new_run_id
from utils.logger import get_logger

logger = get_logger(__name__)

_chart_service = ChartService()
_openai_service = OpenAIService()
_summary_service = SummaryService(_openai_service)
_pdf_service = PDFService()
_blob_service = BlobStorageService()


def generate_report(
    report_title: str,
    dataset: str,
    dashboard_items: list[str] | None = None,
    generate_pdf: bool = True,
    publish_powerbi: bool = True,
) -> ReportResponse:

    run_id = new_run_id()
    logger.info("Starting report generation")

    try:
        # --------------------------------------------------
        # Load Dataset
        # --------------------------------------------------
        df = pd.read_csv(io.StringIO(dataset))
        logger.info("Dataset loaded successfully.")

        # --------------------------------------------------
        # Dashboard Items validation
        # --------------------------------------------------
        if not dashboard_items:
            raise ValueError("dashboard_items is required.")

        # --------------------------------------------------
        # Generate Chart Plan
        # --------------------------------------------------
        chart_plan = _openai_service.generate_chart_plan(
            dataframe=df,
            dashboard_items=dashboard_items,
        )
        logger.info("Chart plan generated.")

        # --------------------------------------------------
        # Generate Charts
        # --------------------------------------------------
        chart_paths = _chart_service.generate(
            df=df,
            chart_plan=chart_plan,
            run_id=run_id,
        )
        logger.info("Charts generated.")

        # --------------------------------------------------
        # AI Summary + Dynamic Insights
        # --------------------------------------------------
        summary, insights, recommendations = _summary_service.generate_all(
            df,
            report_title,
        )
        logger.info("Summary generated.")

        # --------------------------------------------------
        # Dynamic Data Preview
        # --------------------------------------------------
        data_preview = df.fillna("").to_dict(orient="records")

        # --------------------------------------------------
        # Publish to Power BI
        # --------------------------------------------------
        powerbi_dashboard_url = None
        powerbi_dataset_id = None

        if publish_powerbi:
            try:
                logger.info("Publishing dataset to Power BI")
                powerbi = PowerBIService()

                result = powerbi.publish(
                    df=df,
                    report_title=report_title,
                )

                powerbi_dashboard_url = result.get("dashboard_url")
                powerbi_dataset_id = result.get("dataset_id")

            except (PowerBIAPIError, PowerBIAuthError) as exc:
                logger.error(f"Power BI publish failed: {exc}")

        # --------------------------------------------------
        # Generate PDF
        # --------------------------------------------------
        pdf_url = ""

        if generate_pdf:
            pdf_path = _pdf_service.build(
                report_title=report_title,
                executive_summary=summary,
                insights=insights,
                recommendations=recommendations,
                chart_paths=chart_paths,
                run_id=run_id,
                data_preview=data_preview,
                powerbi_dashboard_url=powerbi_dashboard_url,
            )

            pdf_url = _blob_service.upload_pdf(pdf_path)

        logger.info("Report generated successfully.")

        return ReportResponse(
            status="success",
            executive_summary=summary,
            insights=insights,
            recommendations=recommendations,
            chart_paths=[],   # keep empty so chat won't show chart file paths
            pdf_path=pdf_url,
            powerbi_dashboard_url=powerbi_dashboard_url,
            powerbi_dataset_id=powerbi_dataset_id,
            data_preview=data_preview,
            message="Report generated successfully.",
        )

    except Exception as exc:
        logger.exception(exc)

        return ReportResponse(
            status="error",
            executive_summary="",
            insights=[],
            recommendations=[],
            chart_paths=[],
            pdf_path="",
            powerbi_dashboard_url=None,
            powerbi_dataset_id=None,
            data_preview=[],
            message=str(exc),
        )