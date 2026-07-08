"""Builds AI summary, insights and recommendations using OpenAIService."""

from typing import List, Tuple

import pandas as pd

from services.openai_service import OpenAIService
from utils.logger import get_logger

logger = get_logger(__name__)


class SummaryService:

    def __init__(self, openai_service: OpenAIService):
        self._openai = openai_service

    def generate_all(
        self,
        df: pd.DataFrame,
        report_title: str,
    ) -> Tuple[str, List[str], List[str]]:

        # Use your existing OpenAIService.generate_summary()
        summary = self._openai.generate_summary(
            dataframe=df,
            report_title=report_title,
        )

        # Temporary default insights
        insights = [
            f"Dataset contains {len(df)} rows.",
            f"Dataset contains {len(df.columns)} columns.",
        ]

        numeric_columns = df.select_dtypes(include="number").columns.tolist()

        if numeric_columns:
            insights.append(
                f"Numeric columns detected: {', '.join(numeric_columns)}"
            )

        # Temporary recommendations
        recommendations = [
            "Review generated charts for business trends.",
            "Monitor KPIs regularly.",
            "Use Power BI dashboard for interactive analysis.",
            "Use AI summary to support business decisions."
        ]

        return summary, insights, recommendations