"""
Parses the single raw text prompt sent by the MCP client/agent into a
structured ReportRequest: extracts the embedded CSV data block, figures
out which charts were requested, and derives a report title.

Pure text/regex parsing - no LLM calls happen here.
"""

import io
import re
from typing import List

import pandas as pd

from models.report_request import ChartSpec, ChartType, ReportRequest
from utils.logger import get_logger

logger = get_logger(__name__)

_CHART_KEYWORDS = {
    ChartType.BAR: ["bar chart", "bar graph"],
    ChartType.PIE: ["pie chart"],
    ChartType.LINE: ["line chart", "line graph", "trend chart"],
    ChartType.SCATTER: ["scatter chart", "scatter plot"],
}


class PromptService:
    def parse(self, raw_prompt: str) -> ReportRequest:
        dataframe = self._extract_dataframe(raw_prompt)
        charts = self._extract_charts(raw_prompt, dataframe)
        title = self._extract_title(raw_prompt)

        return ReportRequest(
            raw_prompt=raw_prompt,
            report_title=title,
            dataframe=dataframe,
            charts=charts,
            include_powerbi="power bi" in raw_prompt.lower() or "powerbi" in raw_prompt.lower() or True,
            include_pdf=True,
        )

    def _extract_dataframe(self, raw_prompt: str) -> pd.DataFrame:
        lines = raw_prompt.splitlines()
        csv_lines: List[str] = []
        header_seen = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if header_seen and csv_lines:
                    break
                continue
            if "," in stripped and not stripped.endswith(":"):
                csv_lines.append(stripped)
                header_seen = True
            elif header_seen:
                break

        if not csv_lines:
            raise ValueError("No tabular (comma-separated) data block found in the prompt.")

        df = pd.read_csv(io.StringIO("\n".join(csv_lines)))
        df.columns = [c.strip() for c in df.columns]
        return df

    def _extract_charts(self, raw_prompt: str, df: pd.DataFrame) -> List[ChartSpec]:
        text = raw_prompt.lower()
        charts: List[ChartSpec] = []

        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        category_col = next((c for c in df.columns if c not in numeric_cols), df.columns[0])
        default_y = numeric_cols[0] if numeric_cols else df.columns[-1]

        for chart_type, keywords in _CHART_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                charts.append(
                    ChartSpec(
                        chart_type=chart_type,
                        title=f"{default_y} by {category_col} ({chart_type.value.title()} Chart)",
                        x_column=category_col,
                        y_column=default_y,
                    )
                )

        if not charts:
            charts.append(
                ChartSpec(
                    chart_type=ChartType.BAR,
                    title=f"{default_y} by {category_col}",
                    x_column=category_col,
                    y_column=default_y,
                )
            )
        return charts

    def _extract_title(self, raw_prompt: str) -> str:
        match = re.search(r"generate (?:a|an)?\s*([\w\s]+?)\s+report", raw_prompt, re.IGNORECASE)
        if match:
            return match.group(1).strip().title() + " Report"
        return "Business Report"
