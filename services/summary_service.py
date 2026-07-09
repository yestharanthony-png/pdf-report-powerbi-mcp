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

        # --------------------------------------------------
        # AI Executive Summary
        # --------------------------------------------------
        summary = self._openai.generate_summary(
            dataframe=df,
            report_title=report_title,
        )

        insights: List[str] = []
        recommendations: List[str] = []

        numeric_columns = df.select_dtypes(include="number").columns.tolist()
        categorical_columns = df.select_dtypes(include=["object", "category"]).columns.tolist()

        # --------------------------------------------------
        # Numeric KPI insights
        # Example:
        # Revenue average = 130000, min = 98000, max = 167000
        # --------------------------------------------------
        for col in numeric_columns:
            try:
                avg_value = round(df[col].mean(), 2)
                min_value = df[col].min()
                max_value = df[col].max()

                insights.append(
                    f"{col} average is {avg_value}, with a minimum of {min_value} and a maximum of {max_value}."
                )
            except Exception:
                logger.exception(f"Failed to generate numeric insight for column: {col}")

        # --------------------------------------------------
        # Category-based business insights
        # Example:
        # International has the highest average Revenue at 167000
        # South has the lowest average Revenue at 98000
        # --------------------------------------------------
        if categorical_columns and numeric_columns:
            main_category = categorical_columns[0]

            for num_col in numeric_columns:
                try:
                    grouped = (
                        df.groupby(main_category)[num_col]
                        .mean()
                        .sort_values(ascending=False)
                    )

                    if not grouped.empty:
                        top_category = grouped.idxmax()
                        top_value = round(grouped.max(), 2)

                        low_category = grouped.idxmin()
                        low_value = round(grouped.min(), 2)

                        insights.append(
                            f"{top_category} has the highest average {num_col} at {top_value}."
                        )
                        insights.append(
                            f"{low_category} has the lowest average {num_col} at {low_value}."
                        )
                except Exception:
                    logger.exception(
                        f"Failed to generate grouped insight for {num_col}"
                    )

        # --------------------------------------------------
        # Correlation insights
        # Example:
        # There is a strong positive relationship between Revenue and Profit
        # --------------------------------------------------
        if len(numeric_columns) >= 2:
            try:
                corr_matrix = df[numeric_columns].corr()

                for i in range(len(numeric_columns)):
                    for j in range(i + 1, len(numeric_columns)):
                        col1 = numeric_columns[i]
                        col2 = numeric_columns[j]
                        corr_value = corr_matrix.loc[col1, col2]

                        if pd.notna(corr_value):
                            if corr_value > 0.7:
                                insights.append(
                                    f"There is a strong positive relationship between {col1} and {col2}."
                                )
                            elif corr_value < -0.7:
                                insights.append(
                                    f"There is a strong negative relationship between {col1} and {col2}."
                                )
            except Exception:
                logger.exception("Failed to generate correlation insights")

        # --------------------------------------------------
        # Recommendations
        # --------------------------------------------------
        if numeric_columns:
            recommendations.append(
                f"Monitor trends in {numeric_columns[0]} regularly to identify performance changes."
            )

        if categorical_columns:
            recommendations.append(
                f"Compare performance across {categorical_columns[0]} segments to identify strong and weak areas."
            )

        if len(numeric_columns) >= 2:
            recommendations.append(
                "Investigate relationships between numeric KPIs to support better business decisions."
            )

        recommendations.append("Use the generated dashboard to monitor KPIs visually.")
        recommendations.append(
            "Use the executive summary and insights to support reporting and planning."
        )

        return summary, insights, recommendations